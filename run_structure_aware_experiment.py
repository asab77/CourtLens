"""Phase 4B.2: evaluate the frozen structure-aware corpus against reviewed labels.

Reuses existing Vercel embedding, normalization, FAISS, relevance and metric
functions. Never imports or invokes chunk generation. Only this strategy's
vector store, evaluation checkpoint/results, usage ledger and reports are written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import faiss
import numpy as np

from build_index import create_embeddings, save_vector_store
from finalize_chunking_benchmark import aggregate_by_field, score_retrieved
from gateway_config import EXPERIMENT_EMBEDDING_MODEL, EXPERIMENT_GATEWAY_BASE_URL, EXPERIMENT_GATEWAY_PROVIDER
from retrieve import embed_question, experiment_embedding_client, load_vector_store, search_vector_store
from run_chunking_experiment import aggregate_metrics, evaluate_ranked_results, load_benchmark

PROJECT_DIR = Path(__file__).resolve().parent
ROOT = PROJECT_DIR / 'data/experiments/chunking/structure_aware_v1'
CHUNKS = ROOT / 'chunks.jsonl'
CHUNK_MANIFEST = ROOT / 'manifest.json'
STORE = ROOT / 'vector_store'
BENCHMARK = PROJECT_DIR / 'data/evaluation/chunking_benchmark_reviewed.json'
FIXED_RESULTS = PROJECT_DIR / 'data/experiments/chunking/reviewed_results.json'
ANALYSIS = PROJECT_DIR / 'data/analysis/structure_aware_retrieval_evaluation'
EXPECTED_CHUNKS_HASH = '0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4'
EXPECTED_RECORDS = 433
EXPECTED_DIMENSION = 1536
TOP_K = 5
STRATEGY = 'structure_aware_v1'
SPECIAL_IDS = ('DRE-04', 'OBE-01')
METRIC_KEYS = ('hit_at_1', 'hit_at_3', 'hit_at_5', 'mrr')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def protected_hashes() -> dict[str, str]:
    roots = [PROJECT_DIR / p for p in ('data/chunks', 'data/vector_store', 'data/evaluation', 'data/processed',
             'data/analysis/structure_aware_preview.json', 'data/analysis/structure_aware_preview.md',
             'data/analysis/long_sentence_analysis.json', 'data/analysis/long_sentence_analysis.md',
             'data/analysis/structure_aware_chunking.json', 'data/analysis/structure_aware_chunking.md',
             'parse_legal_structure.py', 'generate_structure_aware_chunks.py', 'local_tokenizer.py', 'analyze_long_sentences.py')]
    roots += [p for p in (PROJECT_DIR / 'data/experiments/chunking').iterdir() if p.name != STRATEGY]
    roots += [CHUNKS, CHUNK_MANIFEST]
    files = [p for root in roots for p in (root.rglob('*') if root.is_dir() else [root]) if p.is_file()]
    return {str(p.relative_to(PROJECT_DIR)): sha256(p) for p in sorted(files)}


def load_frozen_records() -> tuple[list[dict], dict]:
    if sha256(CHUNKS) != EXPECTED_CHUNKS_HASH:
        raise ValueError('Frozen structure-aware chunk SHA-256 differs from Phase 4B.1; refusing evaluation')
    manifest = load_json(CHUNK_MANIFEST)
    records = [json.loads(line) for line in CHUNKS.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(records) != EXPECTED_RECORDS or manifest['number_of_chunks'] != EXPECTED_RECORDS or manifest['strategy'] != STRATEGY:
        raise ValueError('Frozen corpus must contain exactly 433 structure_aware_v1 records')
    seen = set()
    counts = Counter()
    source_order = []
    for record in records:
        m = record['metadata']
        if (not record['text'] or m['chunking_strategy'] != STRATEGY or m['opinion_type'] == 'foreign'
                or not 1 <= m['token_count'] <= 1100 or not isinstance(m['major_unit_id'], str)):
            raise ValueError('Invalid frozen chunk structure')
        if m['chunk_id'] in seen or m['chunk_index'] != counts[m['source_file']]:
            raise ValueError('Duplicate or unordered frozen records')
        if not 1 <= m['page_start'] <= m['page_end']:
            raise ValueError('Invalid chunk pages')
        if not m['provenance'] or any(p['major_unit_id'] != m['major_unit_id'] for p in m['provenance']):
            raise ValueError('Mixed major-unit provenance')
        seen.add(m['chunk_id'])
        counts[m['source_file']] += 1
        source_order.append(m['source_file'])
    if source_order != sorted(source_order) or len(counts) != 8:
        raise ValueError('Frozen corpus has invalid document ordering/count')
    return records, manifest


def load_reviewed_benchmark() -> list[dict]:
    payload = load_json(BENCHMARK)
    if payload.get('status') != 'reviewed':
        raise ValueError('Only the reviewed benchmark is eligible')
    questions = load_benchmark(BENCHMARK)
    if len(questions) != 40 or payload.get('question_count') != 40:
        raise ValueError('Reviewed benchmark must contain 40 questions')
    if any(not q.get('type') or not q.get('expected_source_file') or 'relevant_ranges' not in q for q in questions):
        raise ValueError('Reviewed question metadata incomplete')
    return questions


class UsageLedger:
    """Persist SDK-level attempts and returned usage without credentials/headers.

    SDK-internal HTTP retries are not observable here, so these are explicitly
    counts of calls to the SDK create method, not guaranteed wire-request counts.
    """
    def __init__(self, path: Path, identity: dict):
        self.path = path
        self.identity = identity
        if path.exists():
            self.data = load_json(path)
            if self.data['identity'] != identity:
                raise ValueError('Usage ledger belongs to another frozen experiment')
        else:
            self.data = {'identity': identity, 'attempts': [], 'cost': None,
                         'cost_note': 'No reliable currency-denominated gateway cost returned; no cost estimate made.',
                         'request_count_scope': 'SDK create calls including bounded helper retries; SDK-internal HTTP retries may add wire requests.'}

    def client(self, original, phase: str):
        def create(**kwargs):
            entry = {'phase': phase, 'sdk_call_number': len(self.data['attempts']) + 1,
                     'status': 'started', 'returned_prompt_tokens': None, 'returned_total_tokens': None}
            self.data['attempts'].append(entry)
            atomic_json(self.path, self.data)
            try:
                response = original.embeddings.create(**kwargs)
            except Exception as error:
                # Accounting only: every error is immediately re-raised to the
                # unchanged bounded retry helper. Never log error text/headers.
                entry.update(status='failed', error_type=type(error).__name__)
                atomic_json(self.path, self.data)
                raise
            usage = getattr(response, 'usage', None)
            entry['status'] = 'succeeded'
            for attr in ('prompt_tokens', 'total_tokens'):
                value = getattr(usage, attr, None)
                entry['returned_' + attr] = value if type(value) is int and value >= 0 else None
            atomic_json(self.path, self.data)
            return response
        return SimpleNamespace(embeddings=SimpleNamespace(create=create))

    def summary(self) -> dict:
        result = {}
        for phase in ('document', 'query'):
            attempts = [e for e in self.data['attempts'] if e['phase'] == phase]
            successes = [e for e in attempts if e['status'] == 'succeeded']
            known = [e['returned_prompt_tokens'] for e in successes if e['returned_prompt_tokens'] is not None]
            result[phase] = {'sdk_embedding_calls': len(attempts), 'successful_responses': len(successes),
                             'failed_calls': sum(e['status'] == 'failed' for e in attempts),
                             'unfinished_calls': sum(e['status'] == 'started' for e in attempts),
                             'input_tokens_returned': sum(known) if len(known) == len(successes) and successes else None,
                             'responses_missing_token_usage': len(successes) - len(known)}
        result.update(cost=self.data['cost'], cost_note=self.data['cost_note'], request_count_scope=self.data['request_count_scope'])
        return result


def validate_store(path: Path, records: list[dict], identity: dict):
    store = load_vector_store(path, expected_embedding_model=EXPERIMENT_EMBEDDING_MODEL,
                              expected_gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL)
    index, stored, manifest = store
    if (type(index).__name__ != 'IndexFlatIP' or index.d != EXPECTED_DIMENSION
            or index.ntotal != len(records) or len(records) != EXPECTED_RECORDS
            or manifest.get('record_count') != len(records)
            or manifest.get('dimension') != EXPECTED_DIMENSION):
        raise ValueError('Structure-aware FAISS type/dimension/count invalid')
    if (manifest.get('strategy') != STRATEGY or manifest.get('chunks_sha256') != identity['chunks_sha256']
            or manifest.get('chunk_manifest_sha256') != identity['chunk_manifest_sha256']
            or manifest.get('normalization') != 'L2_unit_length' or manifest.get('faiss_index_type') != 'IndexFlatIP'
            or manifest.get('provider') != EXPERIMENT_GATEWAY_PROVIDER or manifest.get('similarity') != 'cosine'
            or manifest.get('logic_version') != load_json(CHUNK_MANIFEST)['logic_version']):
        raise ValueError('Structure-aware store provenance/configuration mismatch')
    if any(s['text'] != r['text'] or s['metadata'] != r['metadata'] for s, r in zip(stored, records)):
        raise ValueError('FAISS records differ from frozen chunks/order')
    vectors = index.reconstruct_n(0, index.ntotal)
    if not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5):
        raise ValueError('Document vectors are not finite normalized unit vectors')
    return store


def build_or_load_store(records: list[dict], manifest: dict, identity: dict, client_factory):
    if STORE.exists():
        if not all((STORE / name).is_file() for name in ('index.faiss', 'records.jsonl', 'manifest.json')):
            raise ValueError('Incomplete structure-aware final store; refusing to treat it as complete or overwrite it')
        return validate_store(STORE, records, identity)
    embeddings = create_embeddings(client_factory(), [r['text'] for r in records], model=EXPERIMENT_EMBEDDING_MODEL)
    if (embeddings.shape != (EXPECTED_RECORDS, EXPECTED_DIMENSION) or not np.isfinite(embeddings).all()
            or np.any(np.linalg.norm(embeddings, axis=1) == 0)):
        raise ValueError('Incomplete/invalid embedding matrix; no final store will be published')
    if sha256(CHUNKS) != identity['chunks_sha256'] or sha256(CHUNK_MANIFEST) != identity['chunk_manifest_sha256']:
        raise ValueError('Frozen input changed during embedding; refusing to publish store')
    # Stage on the same filesystem, validate completely, then publish atomically.
    with tempfile.TemporaryDirectory(prefix='.structure-aware-store-', dir=ROOT) as temporary:
        staged = Path(temporary) / 'vector_store'
        save_vector_store(records, embeddings, ['chunks.jsonl'], vector_store_dir=staged,
                          gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
                          gateway_provider=EXPERIMENT_GATEWAY_PROVIDER,
                          embedding_model=EXPERIMENT_EMBEDDING_MODEL,
                          build_metadata={'experiment': 'structure_aware_retrieval', 'strategy': STRATEGY,
                                          'logic_version': manifest['logic_version'],
                                          'chunks_sha256': identity['chunks_sha256'],
                                          'chunk_manifest_sha256': identity['chunk_manifest_sha256'],
                                          'normalization': 'L2_unit_length', 'faiss_index_type': 'IndexFlatIP',
                                          'generated_at': datetime.now(timezone.utc).isoformat()})
        validate_store(staged, records, identity)
        if STORE.exists():
            raise ValueError('Final store appeared concurrently; refusing overwrite')
        os.rename(staged, STORE)
    return validate_store(STORE, records, identity)


def score_question(item: dict, ranked: list[dict]) -> dict:
    metrics = evaluate_ranked_results(ranked, item, max_rank=TOP_K)
    for detail, result in zip(metrics['retrieved'], ranked[:TOP_K]):
        m = result['metadata']
        detail.update(chunk_id=m['chunk_id'], major_unit_id=m['major_unit_id'],
                      major_unit_type=m['major_unit_type'], opinion_type=m['opinion_type'],
                      author=m.get('author'), sections=m['sections'], text=result['text'],
                      evidence_excerpt=result['text'][:400])
    return {'id': item['id'], 'type': item['type'], 'question': item['question'],
            'expected_case': item['expected_case'], 'expected_source_file': item['expected_source_file'],
            'relevant_ranges': item['relevant_ranges'], 'metrics': metrics}


def validate_saved_questions(completed: list[dict], questions: list[dict], store) -> None:
    if len(completed) > len(questions):
        raise ValueError('Too many saved questions')
    for saved, item in zip(completed, questions):
        for field in ('id', 'type', 'question', 'expected_case', 'expected_source_file', 'relevant_ranges'):
            if saved[field] != item[field]:
                raise ValueError('Saved question differs from reviewed benchmark')
        details = saved['metrics']['retrieved']
        if len(details) != TOP_K:
            raise ValueError('Saved question lacks Top-5')
        if score_retrieved(details, item) != saved['metrics']:
            raise ValueError('Saved relevance/metric calculations mismatch')
        for detail in details:
            vector_id = detail['vector_id']
            if not 0 <= vector_id < len(store[1]):
                raise ValueError('Invalid saved vector ID')
            record = store[1][vector_id]
            m = record['metadata']
            for field in ('chunk_id', 'chunk_index', 'case_name', 'source_file', 'page_start', 'page_end',
                          'major_unit_id', 'major_unit_type', 'opinion_type', 'author', 'sections', 'token_count'):
                if detail[field] != m.get(field):
                    raise ValueError('Saved result differs from aligned store metadata')
            if detail['text'] != record['text'] or not math.isfinite(detail['similarity']):
                raise ValueError('Invalid saved text/similarity')


def evaluate(questions: list[dict], store, identity: dict, client_factory) -> list[dict]:
    progress_path = ROOT / 'evaluation_progress.json'
    progress_identity = {**identity, 'index_sha256': sha256(STORE / 'index.faiss'),
                         'store_manifest_sha256': sha256(STORE / 'manifest.json')}
    completed = []
    if progress_path.exists():
        progress = load_json(progress_path)
        if progress['identity'] != progress_identity:
            raise ValueError('Query progress belongs to another corpus/benchmark/index')
        completed = progress['questions']
        validate_saved_questions(completed, questions, store)
    client = None
    for item in questions[len(completed):]:
        if client is None:
            client = client_factory()
        # ONLY question text is sent for embedding. No labels/metadata/filter.
        vector = embed_question(item['question'], client=client, model=EXPERIMENT_EMBEDDING_MODEL)
        if vector.shape != (1, EXPECTED_DIMENSION) or not np.isfinite(vector).all():
            raise ValueError('Invalid query vector dimensionality/values')
        ranked = search_vector_store(vector, store, top_k=TOP_K)
        completed.append(score_question(item, ranked))
        validate_saved_questions(completed[-1:], [item], store)
        atomic_json(progress_path, {'status': 'evaluating' if len(completed) < len(questions) else 'complete',
                                    'identity': progress_identity, 'questions': completed})
        print(f"Evaluated {len(completed)}/{len(questions)}: {item['id']}")
    return completed


def win_analysis(new: dict, fixed: dict) -> dict:
    old_map = {q['id']: q for q in fixed['questions']}
    if set(old_map) != {q['id'] for q in new['questions']}:
        raise ValueError('Comparison question IDs differ')
    details, counts = [], Counter()
    for q in new['questions']:
        a = q['metrics']['first_relevant_rank']
        b = old_map[q['id']]['metrics']['first_relevant_rank']
        if a is None and b is None:
            category = 'both_miss_top_5'
        elif (a or 6) < (b or 6):
            category = 'structure_aware_wins'
        elif (b or 6) < (a or 6):
            category = 'fixed_wins'
        else:
            category = 'tie'
        counts[category] += 1
        details.append({'id': q['id'], 'case_name': q['expected_case'], 'type': q['type'],
                        'structure_aware_first_relevant_rank': a, 'fixed_first_relevant_rank': b,
                        'classification': category, 'fixed_miss_to_structure_hit': b is None and a is not None,
                        'structure_miss_to_fixed_hit': a is None and b is not None})
    return {'counts': {key: counts[key] for key in ('structure_aware_wins', 'fixed_wins', 'tie', 'both_miss_top_5')},
            'fixed_miss_to_structure_hit': [q['id'] for q in details if q['fixed_miss_to_structure_hit']],
            'structure_miss_to_fixed_hit': [q['id'] for q in details if q['structure_miss_to_fixed_hit']],
            'rank_improvements': [q['id'] for q in details if q['classification'] == 'structure_aware_wins'],
            'rank_regressions': [q['id'] for q in details if q['classification'] == 'fixed_wins'],
            'questions': details}


def opinion_observations(configuration: dict) -> dict:
    """Post-retrieval review flags; never changes ranks or relevance decisions."""
    candidates, dominance = [], []
    for q in configuration['questions']:
        retrieved = q['metrics']['retrieved']
        kinds = Counter(r['opinion_type'] for r in retrieved)
        for kind in ('unknown', 'syllabus'):
            if kinds[kind] >= 3:
                dominance.append({'id': q['id'], 'type': kind, 'top_5_count': kinds[kind],
                                  'first_relevant_rank': q['metrics']['first_relevant_rank']})
        # Explicit author requests are unambiguous. Court-oriented wording only
        # suggests a majority intent; it is NOT a definitive opinion classifier.
        explicit = {'PLE-05': ('dissent', 'Harlan'), 'NYT-04': ('concurrence', 'Black'),
                    'NYT-05': ('concurrence', 'Brennan')}.get(q['id'])
        majority_candidate = bool(re.search(r'\b(?:the Court|the majority|Supreme Court)\b', q['question'], re.I)) and explicit is None
        for r in retrieved:
            if r['case_name'] != q['expected_case']:
                continue
            mismatch = explicit and (r['opinion_type'], r['author']) != explicit
            separate = majority_candidate and r['opinion_type'] in ('concurrence', 'dissent', 'other')
            if mismatch or separate:
                candidates.append({'id': q['id'], 'rank': r['rank'], 'chunk_id': r['chunk_id'],
                                   'opinion_type': r['opinion_type'], 'author': r['author'],
                                   'page_start': r['page_start'], 'page_end': r['page_end'],
                                   'reviewed_relevant': r['relevant'], 'evidence_excerpt': r['evidence_excerpt'],
                                   'reason': 'Explicit author/opinion mismatch' if mismatch else 'Separate opinion for Court-oriented wording; manual review needed',
                                   'top_5_miss': q['metrics']['first_relevant_rank'] is None})
    return {'note': 'Review flags only. Correct case plus a different opinion is not automatically irrelevant; reviewed page labels remain authoritative.',
            'wrong_opinion_candidates': candidates, 'unknown_or_syllabus_dominance': dominance,
            'candidate_count': len(candidates), 'candidate_question_count': len({r['id'] for r in candidates}),
            'dissent_candidates': sum(r['opinion_type'] == 'dissent' for r in candidates),
            'concurrence_candidates': sum(r['opinion_type'] == 'concurrence' for r in candidates)}


def fixed_evidence(config: dict, question_id: str) -> dict:
    question = next(q for q in config['questions'] if q['id'] == question_id)
    path = PROJECT_DIR / 'data/experiments/chunking' / config['id'] / 'chunks' / (Path(question['expected_source_file']).stem + '.jsonl')
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    by_index = {r['metadata']['chunk_index']: r for r in records}
    details = []
    for saved in question['metrics']['retrieved']:
        row = dict(saved)
        if row['source_file'] == question['expected_source_file']:
            record = by_index[row['chunk_index']]
        else:
            other_path = path.parent / (Path(row['source_file']).stem + '.jsonl')
            other = [json.loads(line) for line in other_path.read_text().splitlines() if line.strip()]
            record = next(r for r in other if r['metadata']['chunk_index'] == row['chunk_index'])
        row['evidence_excerpt'] = record['text'][:400]
        row['text'] = record['text']
        details.append(row)
    return {'configuration': config['id'], 'first_relevant_rank': question['metrics']['first_relevant_rank'], 'retrieved': details}



def qualitative_review(configuration: dict) -> list[dict]:
    """Evidence notes added after retrieval; never used by embedding/search."""
    by_id = {q['id']: q for q in configuration['questions']}
    notes = []
    q = by_id.get('MIR-04')
    if q and q['expected_source_file'] == 'miranda_v_arizona.pdf':
        top = q['metrics']['retrieved'][0]
        if (top['opinion_type'] == 'majority' and top['page_start'] == 9 and top['page_end'] == 10
                and not top['relevant'] and 'right to remain silent' in top['text']):
            notes.append({'id': 'MIR-04', 'finding': 'The rank-1 Warren majority passage on PDF pages 9–10 explicitly lists interrogation safeguards, including silence, evidentiary use, counsel, and stopping questioning. It remains irrelevant under frozen ranges [2,2] and [34,40]. This measured regression exposes a possible reviewed-label coverage gap; the metric and labels were not changed.'})
    for qid, author in (('DRE-03', 'Curtis'), ('OBE-04', 'Roberts')):
        q = by_id.get(qid)
        if q:
            top = q['metrics']['retrieved'][0]
            if top.get('author') == author and top.get('opinion_type') == 'dissent' and not top['relevant']:
                notes.append({'id': qid, 'finding': f"Rank 1 is the parser-labeled {author} dissent, while the first reviewed-relevant result is at rank {q['metrics']['first_relevant_rank']}. Opinion separation retained the distinction but did not prevent an opposing discussion from outranking the target passage."})
    q = by_id.get('DRE-04')
    if q and q['expected_source_file'] == 'dred_scott_v_sandford.pdf' and q['metrics']['first_relevant_rank'] is None:
        notes.append({'id': 'DRE-04', 'finding': 'All five results are parser-labeled separate opinions: Campbell, Grier, McLean, Oatron, Campbell. None intersects frozen pages 3–4. Keeping opinions separate did not itself resolve this miss.'})
    q = by_id.get('OBE-01')
    if q and q['expected_source_file'] == 'obergefell_v_hodges.pdf' and q['metrics']['first_relevant_rank'] is None:
        notes.append({'id': 'OBE-01', 'finding': 'The first three results are Kennedy majority passages on pages 19–20, 36–39, and 34–36; syllabus is fourth and Roberts dissent fifth. None intersects frozen pages 12–13. Correct opinion identity alone did not retrieve the question-specific labeled passage.'})
    q = by_id.get('PLE-05')
    if q and q['metrics']['retrieved'][0].get('author') == 'Uamla':
        notes.append({'id': 'PLE-05', 'finding': 'The author mismatch flag comes from preserved OCR value Uamla. The result is a dissent and benchmark-relevant. This raw-string flag is not evidence of an established wrong-author or wrong-opinion retrieval.'})
    q = by_id.get('NYT-02')
    if q and q['metrics']['retrieved'][0].get('author') == 'White' and q['metrics']['retrieved'][0]['relevant']:
        notes.append({'id': 'NYT-02', 'finding': 'The rank-1 White concurrence is relevant under the reviewed labels despite a Court-oriented wording flag. Separate-opinion flags must not be treated as automatic retrieval errors.'})
    q = by_id.get('MAR-03')
    if q and sum(r['opinion_type'] == 'unknown' for r in q['metrics']['retrieved']) >= 3:
        notes.append({'id': 'MAR-03', 'finding': 'Unknown/front matter occupies three Top-5 positions, but the first result is relevant. Front-matter dominance is not automatically a failure. No question has three or more syllabus results.'})
    return notes


def analyze(output: dict, fixed: dict) -> dict:
    configuration = output['configurations'][0]
    baseline = next(c for c in fixed['configurations'] if c['id'] == '900_150')
    primary = {
        'fixed_900_150': baseline['metrics'], 'structure_aware_v1': configuration['metrics'],
        'absolute_differences': {k: configuration['metrics'][k] - baseline['metrics'][k] for k in METRIC_KEYS},
        'additional_hit_at_1_successes': int(sum(q['metrics']['hit_at_1'] for q in configuration['questions']) - sum(q['metrics']['hit_at_1'] for q in baseline['questions'])),
        'additional_top_5_successes': int(sum(q['metrics']['hit_at_5'] for q in configuration['questions']) - sum(q['metrics']['hit_at_5'] for q in baseline['questions'])),
    }
    special = {}
    for qid in SPECIAL_IDS:
        new = next(q for q in configuration['questions'] if q['id'] == qid)
        special[qid] = {'structure_aware': new,
                        'fixed_results': [fixed_evidence(c, qid) for c in fixed['configurations']],
                        'interpretation_note': 'Read evidence/opinion/size together. A page-overlap hit does not establish causal benefit from structure or independently establish doctrinal appropriateness.'}
    return {'primary_comparison': primary,
            'secondary_comparison': [{'strategy': c['id'], 'chunks': c['vector_count'], **c['metrics']} for c in fixed['configurations']] + [{'strategy': STRATEGY, 'chunks': EXPECTED_RECORDS, **configuration['metrics']}],
            'question_type_metrics': {'structure_aware': aggregate_by_field(configuration, 'type'), 'fixed_900_150': aggregate_by_field(baseline, 'type')},
            'case_metrics': {'structure_aware': aggregate_by_field(configuration, 'expected_case'), 'fixed_900_150': aggregate_by_field(baseline, 'expected_case')},
            'per_question_comparison': win_analysis(configuration, baseline),
            'special_questions': special, 'opinion_aware_observations': opinion_observations(configuration),
            'qualitative_review': qualitative_review(configuration),
            'embedding_usage': output['embedding_usage'], 'protected_artifacts': output['protected_artifacts'],
            'limitations': ['Structure-aware_v1 changes both boundary selection and the realized chunk-size distribution relative to the existing fixed 900/150 implementation.',
                            'Fixed mean 602.51 / median 614.5; structure-aware mean 805.48 / median 873 tokens.',
                            'The experiment evaluates the complete strategy; changes cannot be attributed solely to legal structure.',
                            '40 questions; five per case; many type samples are tiny. No statistical significance testing performed.',
                            'Reviewed ranges came from the fixed Top-5 pool and may omit answer-bearing structure-aware passages. Labels remain frozen.',
                            'Inclusive page intersection can count passages without independent answer-bearing text; opinion correctness requires qualitative review.',
                            'Same provider/model, but query/document calls occur later than the saved fixed experiment; provider deployment determinism is not guaranteed.']}


def cells(metrics: dict) -> str:
    return ' | '.join(f'{metrics[k]:.3f}' for k in METRIC_KEYS)


def render_report(output: dict, analysis: dict) -> str:
    lines = ['# CourtLens Phase 4B.2 — structure-aware retrieval evaluation', '',
             'Frozen 433-chunk corpus; reviewed 40-query benchmark. Ranking uses normalized 1536-dimensional openai/text-embedding-3-small vectors and IndexFlatIP through the existing Vercel experiment path. Top-5, unfiltered; opinion/author/type metadata is analysis-only.', '',
             '## Overall comparison', '', '| Strategy | Chunks | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---:|---:|---:|---:|---:|']
    for row in analysis['secondary_comparison']:
        lines.append(f"| {row['strategy']} | {row['chunks']} | {cells(row)} |")
    primary = analysis['primary_comparison']
    lines += ['', 'Primary baseline: fixed 900/150. Absolute differences (structure-aware minus fixed):', '',
              '```json', json.dumps(primary, indent=2), '```', '',
              '## Question types and cases', '', 'Exploratory only; small samples do not support routing or causal conclusions.', '']
    for field, title in (('question_type_metrics', 'Question type'), ('case_metrics', 'Case')):
        lines += [f'### {title}', '', f'| {title} | N | Fixed Hit@1 / Hit@3 / Hit@5 / MRR | Structure Hit@1 / Hit@3 / Hit@5 / MRR |', '|---|---:|---|---|']
        for key, new in analysis[field]['structure_aware'].items():
            old = analysis[field]['fixed_900_150'][key]
            compact = lambda m: ' / '.join(f'{m[k]:.3f}' for k in METRIC_KEYS)
            lines.append(f"| {key} | {new['question_count']} | {compact(old)} | {compact(new)} |")
        lines.append('')
    wins = analysis['per_question_comparison']
    lines += ['## Per-question changes', '', 'Both misses are counted separately from equal hit ranks.', '',
              '```json', json.dumps({k: v for k, v in wins.items() if k != 'questions'}, indent=2), '```', '',
              '| ID | Fixed first relevant rank | Structure first relevant rank | Outcome |', '|---|---:|---:|---|']
    for q in wins['questions']:
        lines.append(f"| {q['id']} | {q['fixed_first_relevant_rank'] or 'miss'} | {q['structure_aware_first_relevant_rank'] or 'miss'} | {q['classification']} |")
    lines += ['', '## DRE-04 and OBE-01 evidence', '']
    for qid, details in analysis['special_questions'].items():
        q = details['structure_aware']
        rank = q['metrics']['first_relevant_rank']
        lines += [f'### {qid}', '', q['question'], '', f"Reviewed relevant pages: {q['relevant_ranges']}. Structure-aware first relevant rank: {rank or 'Top-5 miss'}.", '',
                  '| Rank | Score | Case / opinion / raw author | Pages | Section labels | Relevant | Chunk |', '|---:|---:|---|---|---|---|---|']
        for r in q['metrics']['retrieved']:
            labels = ', '.join(s['marker'] + (f" {s['title']}" if s['title'] else '') for s in r['sections']) or 'none'
            lines.append(f"| {r['rank']} | {r['similarity']:.6f} | {r['case_name']} / {r['opinion_type']} / {r['author'] or 'unknown'} | {r['page_start']}–{r['page_end']} | {labels} | {r['relevant']} | {r['chunk_id']} |")
        lines.append('')
        for r in q['metrics']['retrieved']:
            lines += [f"**Rank {r['rank']} evidence:** {r['evidence_excerpt']}", '']
        if rank is not None:
            lines += ['**Qualitative comparison evidence:** all four saved fixed rankings are shown below. Consider evidence preservation, opinion separation, realized size, and legally appropriate source separately. The benchmark hit alone cannot distinguish those explanations.', '']
        else:
            lines += ['Still a Top-5 miss under the frozen reviewed labels. Saved fixed results are included for direct inspection.', '']
        for fixed in details['fixed_results']:
            lines += [f"**Fixed {fixed['configuration']} — first relevant rank: {fixed['first_relevant_rank'] or 'miss'}**", '']
            for r in fixed['retrieved']:
                lines += [f"- Rank {r['rank']}; score {r['similarity']:.6f}; {r['case_name']}; pp. {r['page_start']}–{r['page_end']}; {r['token_count']} tokens; relevant={r['relevant']}. {r['evidence_excerpt']}"]
            lines.append('')
    lines += ['## Qualitative findings from retrieved evidence', '']
    for note in analysis['qualitative_review']:
        lines += [f"**{note['id']}:** {note['finding']}", '']
    observations = analysis['opinion_aware_observations']
    lines += ['## Opinion-aware review flags', '', observations['note'], '',
              'Court-oriented wording is a transparent heuristic for possible majority intent. Explicit Harlan, Black, and Brennan requests are checked against the requested author/opinion after ranking. Flags can still be benchmark-relevant.', '',
              f"{observations['candidate_count']} candidate passages across {observations['candidate_question_count']} questions; {observations['dissent_candidates']} dissent and {observations['concurrence_candidates']} concurrence candidates.", '',
              '| Question | Rank | Opinion / author | Pages | Relevant | Reason |', '|---|---:|---|---|---|---|']
    for r in observations['wrong_opinion_candidates']:
        lines.append(f"| {r['id']} | {r['rank']} | {r['opinion_type']} / {r['author']} | {r['page_start']}–{r['page_end']} | {r['reviewed_relevant']} | {r['reason']} |")
    lines += ['', 'Unknown/front-matter or syllabus dominance (at least three Top-5 results):', '',
              '```json', json.dumps(observations['unknown_or_syllabus_dominance'], indent=2), '```', '',
              '## Request accounting and resume behavior', '', '```json', json.dumps(analysis['embedding_usage'], indent=2), '```', '',
              'Document embedding uses 100-record batches with the existing 10-second successful-batch pacing and 60/120/240-second bounded rate-limit retry schedule. Authentication failures propagate. No document-batch checkpoint exists: a failed document build restarts embedding from record 1. No incomplete final store is published. A complete validated store is reused, and successfully evaluated queries resume from the saved checkpoint.', '',
              '## Limitations', '']
    lines += ['- ' + note for note in analysis['limitations']]
    lines += ['', '## Protected artifacts', '', '```json', json.dumps(analysis['protected_artifacts'], indent=2), '```', '',
              'Chunk construction and labels remained frozen. No fixed retrieval was rerun, no production artifact was modified, and no v2, BM25, hybrid search, reranking or routing was implemented.', '',
              '## Next experiment', '',
              'First manually review the listed regressions and DRE-04/OBE-01 evidence under the frozen labels. A separately designed, size-matched comparison would help distinguish boundary effects from realized granularity; these results alone cannot establish causation. No next experiment was implemented.', '']
    return '\n'.join(lines)


def run(check_only: bool = False) -> dict:
    before = protected_hashes()
    try:
        records, chunk_manifest = load_frozen_records()
        questions = load_reviewed_benchmark()
        fixed = load_json(FIXED_RESULTS)
        if fixed['embedding_model'] != EXPERIMENT_EMBEDDING_MODEL or fixed['gateway_base_url'] != EXPERIMENT_GATEWAY_BASE_URL:
            raise ValueError('Saved fixed comparison uses another embedding configuration')
        benchmark_by_id = {q['id']: q for q in questions}
        if {c['id'] for c in fixed['configurations']} != {'600_100', '900_150', '1200_200', '1500_200'}:
            raise ValueError('Saved fixed comparison lacks the four reviewed configurations')
        for configuration in fixed['configurations']:
            if {q['id'] for q in configuration['questions']} != set(benchmark_by_id):
                raise ValueError('Saved fixed comparison has different question IDs')
            for saved in configuration['questions']:
                question = benchmark_by_id[saved['id']]
                for field in ('type', 'question', 'expected_case', 'expected_source_file', 'relevant_ranges'):
                    if saved[field] != question[field]:
                        raise ValueError('Saved fixed results differ from reviewed benchmark metadata')
            if configuration['metrics'] != aggregate_metrics(configuration['questions']):
                raise ValueError('Saved fixed aggregate metrics do not match question scores')
        baseline_manifest = load_json(PROJECT_DIR / 'data/experiments/chunking/900_150/vector_store/manifest.json')
        if baseline_manifest['dimension'] != EXPECTED_DIMENSION:
            raise ValueError('Baseline dimension differs')
        identity = {'chunks_sha256': sha256(CHUNKS), 'chunk_manifest_sha256': sha256(CHUNK_MANIFEST),
                    'benchmark_sha256': sha256(BENCHMARK), 'embedding_model': EXPERIMENT_EMBEDDING_MODEL,
                    'gateway_base_url': EXPERIMENT_GATEWAY_BASE_URL, 'ranking_depth': TOP_K}
        if check_only:
            print('Local preflight passed: frozen 433 chunks, reviewed 40 questions, matching Vercel 1536-dimensional baseline. No API request made.')
            return identity
        ledger = UsageLedger(ROOT / 'embedding_usage.json', identity)
        original = None
        def client_for(phase):
            nonlocal original
            if original is None:
                original = experiment_embedding_client()
            return ledger.client(original, phase)
        store = build_or_load_store(records, chunk_manifest, identity, lambda: client_for('document'))
        result_path = ROOT / 'results.json'
        if result_path.exists():
            output = load_json(result_path)
            if output['identity'] != identity or output['index_sha256'] != sha256(STORE / 'index.faiss'):
                raise ValueError('Completed evaluation belongs to another frozen input')
            validate_saved_questions(output['configurations'][0]['questions'], questions, store)
            if len(output['configurations'][0]['questions']) != 40:
                raise ValueError('Completed evaluation lacks 40 questions')
            if output['configurations'][0]['metrics'] != aggregate_metrics(output['configurations'][0]['questions']):
                raise ValueError('Completed aggregate metrics differ from saved question scores')
        else:
            completed = evaluate(questions, store, identity, lambda: client_for('query'))
            configuration = {'id': STRATEGY, 'vector_count': store[0].ntotal,
                             'metrics': aggregate_metrics(completed), 'questions': completed}
            output = {'experiment': 'structure_aware_retrieval', 'generated_at': datetime.now(timezone.utc).isoformat(),
                      'identity': identity, 'embedding_model': EXPERIMENT_EMBEDDING_MODEL,
                      'gateway_base_url': EXPERIMENT_GATEWAY_BASE_URL, 'similarity': 'cosine_via_normalized_inner_product',
                      'ranking_depth': TOP_K, 'benchmark_path': str(BENCHMARK.relative_to(PROJECT_DIR)),
                      'index_sha256': sha256(STORE / 'index.faiss'), 'configurations': [configuration],
                      'embedding_usage': ledger.summary()}
        after = protected_hashes()
        if after != before:
            raise ValueError('Protected artifacts changed during evaluation')
        output['protected_artifacts'] = {'checked_files': len(before), 'unchanged': True,
                                         'chunks_sha256_before': before[str(CHUNKS.relative_to(PROJECT_DIR))],
                                         'chunks_sha256_after': after[str(CHUNKS.relative_to(PROJECT_DIR))],
                                         'protected_before': before, 'protected_after': after}
        analysis = analyze(output, fixed)
        atomic_json(result_path, output)
        atomic_json(ANALYSIS.with_suffix('.json'), analysis)
        ANALYSIS.with_suffix('.md').write_text(render_report(output, analysis), encoding='utf-8')
        print('Structure-aware metrics:', json.dumps(output['configurations'][0]['metrics']))
        return output
    finally:
        if protected_hashes() != before:
            raise RuntimeError('Protected-artifact hash audit failed')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Local frozen-input preflight only; no APIs or output writes')
    args = parser.parse_args()
    try:
        run(args.check)
    except Exception as error:
        # Error class is enough for authentication failures; never print SDK
        # response bodies, client state, request headers, or credential values.
        message = str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__
        print(f'Experiment stopped: {message}')
        print('No incomplete final index is valid. A failed document build restarts from batch 1; a complete validated store and completed query checkpoint can be reused.')
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
