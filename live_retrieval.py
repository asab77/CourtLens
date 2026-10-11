"""Live structure-aware Dense + BM25 + RRF adapter; no Streamlit integration.

Initialize resources once, then reuse them for requests. This module never builds
FAISS or document embeddings and never chooses another retrieval algorithm.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np

from bm25_retrieval import BM25, K1, B
from gateway_config import VERCEL_EMBEDDING_MODEL
from hybrid_retrieval import ChunkCatalog, fuse, DEPTH, K
from retrieve import embed_question, embedding_client, search_vector_store
from runtime_assets import load_runtime_vector_store, STRATEGY

DENSE_DEPTH = 5
BM25_DEPTH = 5
FINAL_DEPTH = 5
RRF_K = 60


def _digest(store):
    # Detect changed records/manifests before using precomputed lexical statistics.
    return hashlib.sha256(json.dumps({'records': store[1], 'manifest': store[2]},
                                     sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class LiveResources:
    """One validated corpus and its reusable BM25 statistics/identity catalog.

    Treat contained FAISS/BM25 objects and records as read-only. Initialize via
    load_live_resources, not by assembling components from different corpora.
    """
    vector_store: tuple
    bm25: BM25
    catalog: ChunkCatalog
    cases: frozenset[str]
    fingerprint: str


def load_live_resources(vector_store_dir: Path | None = None) -> LiveResources:
    """Validate frozen assets, build full-corpus BM25 once, and retain row order.

    There is deliberately no global cache: the caller owns/reuses this returned
    bundle and can choose its application resource lifetime in the next phase.
    """
    store = load_runtime_vector_store(vector_store_dir)
    records = store[1]
    catalog = ChunkCatalog(STRATEGY, records)
    for ordinal, record in enumerate(records):
        if type(record.get('vector_id')) is not int or record['vector_id'] != ordinal:
            raise ValueError('Live vector records are not aligned with frozen chunk order')
        catalog.verify({**record['metadata'], 'text': record['text'], 'corpus_index': ordinal})
    if not records or store[0].ntotal != len(records):
        raise ValueError('Live vector/record identities require a nonempty aligned corpus')
    lexical = BM25([record['text'] for record in records], k1=K1, b=B)
    return LiveResources(store, lexical, catalog,
                         frozenset(record['metadata']['case_name'] for record in records), _digest(store))


def retrieve_hybrid(question: str, resources: LiveResources, *,
                    case_name: str | None = None, client=None) -> list[dict]:
    """Return up to five hydrated evidence records using frozen Top-5 RRF.

    client is an optional configured Vercel embedding client (fake in tests).
    If absent, the existing configured factory requires AI_GATEWAY_API_KEY.
    Provider exceptions propagate through the existing bounded 429 retry helper.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError('Please enter a non-empty question.')
    question = question.strip()
    if not isinstance(resources, LiveResources):
        raise ValueError('Initialize validated resources with load_live_resources first')
    if case_name is not None and (not isinstance(case_name, str) or case_name not in resources.cases):
        raise ValueError('Invalid case filter: choose an exact case name from the runtime corpus')
    if (resources.catalog.collection != STRATEGY
            or resources.catalog.records is not resources.vector_store[1]
            or resources.bm25.document_count != len(resources.vector_store[1])
            or _digest(resources.vector_store) != resources.fingerprint):
        raise ValueError('Live resources have changed or contain mismatched corpus identities')
    if DEPTH != 5 or K != 60 or resources.bm25.k1 != 1.5 or resources.bm25.b != .75:
        raise ValueError('Live retrieval parameters differ from the frozen Phase 5A/5B configuration')
    query = embed_question(question, client=client if client is not None else embedding_client(),
                           model=VERCEL_EMBEDDING_MODEL)
    if (query.shape != (1, resources.vector_store[0].d) or not np.isfinite(query).all()
            or not np.allclose(np.linalg.norm(query, axis=1), 1., atol=1e-5, rtol=0)):
        raise ValueError('Query embedding must have the runtime dimension and finite unit norm')
    dense_results = search_vector_store(query, resources.vector_store, top_k=DENSE_DEPTH, case_name=case_name)
    dense = []
    for rank, result in enumerate(dense_results, 1):
        dense.append({**result['metadata'], 'rank': rank, 'collection': STRATEGY,
                      'corpus_index': result['vector_id'], 'text': result['text'],
                      'similarity': result['similarity']})
    # Select within the case before truncation, while retaining full-corpus IDF
    # and length statistics. BM25.rank already orders ties by original ordinal.
    matches = resources.bm25.rank(question, limit=resources.bm25.document_count if case_name else BM25_DEPTH)
    lexical = []
    for ordinal, score in matches:
        record = resources.catalog.records[ordinal]
        if case_name is not None and record['metadata']['case_name'] != case_name:
            continue
        lexical.append({**record['metadata'], 'rank': len(lexical) + 1, 'collection': STRATEGY,
                        'corpus_index': ordinal, 'bm25_score': score})
        if len(lexical) == BM25_DEPTH:
            break
    fused = fuse(resources.catalog, dense, lexical)
    evidence = []
    for row in fused[:FINAL_DEPTH]:
        record = resources.catalog.records[row['corpus_index']]
        evidence.append({**row, 'text': record['text'], 'metadata': deepcopy(record['metadata']),
                         'vector_id': row['corpus_index'], 'score_type': 'rrf'})
    return evidence
