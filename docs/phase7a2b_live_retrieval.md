# Phase 7A.2B: live structure-aware hybrid adapter

This phase adds `live_retrieval.py` only as a retrieval adapter. Streamlit and
`rag.py` are not wired to it. No provider request or document embedding occurred,
and existing BM25, RRF, dense search and query normalization implementations were
not modified. No reranking, query rewriting or new citation behavior is added.

## Small public API and initialization

```python
from live_retrieval import load_live_resources, retrieve_hybrid

# Once per application resource lifetime; local, read-only asset loading.
resources = load_live_resources()
# Later, with a configured Vercel client; this example is not executed here:
# evidence = retrieve_hybrid(question, resources, case_name=None, client=client)
```

`load_live_resources(vector_store_dir: Path | None = None)` uses the existing
validated runtime loader. Its default follows `COURTLENS_VECTOR_STORE_PATH`, or
`data/experiments/chunking/structure_aware_v1/vector_store`. Validation includes
433 records/vectors, dimension 1536, IndexFlatIP, unit norms, model/gateway
compatibility, frozen text/metadata/order and source hashes.

The returned `LiveResources` bundle retains the validated FAISS store, identity
catalog, case names, a records/manifest fingerprint, and one BM25 index built
from the full corpus's frozen texts in the exact original order. Vector IDs are
checked against record positions and catalog identities. BM25 is initialized
once per bundle, then reused across questions and filters. There is no hidden
global cache: the future application integration owns the bundle's lifetime.
Treat all contained records and index objects as read-only. Returned evidence
metadata is copied, so editing a result does not modify cached records. The
fingerprint rejects changed records/manifests before using stale BM25 statistics;
it does not defend against arbitrary mutation of FAISS/BM25 internals by callers.

`retrieve_hybrid(question, resources, *, case_name=None, client=None)` returns
up to five hydrated ranked evidence records. A supplied client must be configured
for Vercel; if omitted, the existing factory requires `AI_GATEWAY_API_KEY`. There
is no NYU fallback. No generation model setting is required for retrieval.

## Locked retrieval behavior

| Component | Settings and implementation |
|---|---|
| Query embedding | Existing `embed_question`, `openai/text-embedding-3-small`, existing L2 normalization and bounded 429 retry helper |
| Dense candidates | Existing FAISS `search_vector_store`, Top-5 |
| Lexical candidates | Existing Phase 5A `BM25` and tokenizer, k1=1.5, b=0.75, Top-5 positive scores |
| Fusion | Existing Phase 5B `fuse`, RRF k=60, one-based ranks |
| Final evidence | First five fused candidates |

Fusion uses `sum(1/(60 + rank))`, one contribution per retriever. It merges
verified identities within the same structure-aware corpus, never page overlap.
Raw dense/BM25 scores are diagnostics, not fusion inputs. RRF ties use original
corpus ordinal. Opinion, author, question type, benchmark labels and other metadata
do not boost rankings. Dense tie behavior and lexical tokenization remain those
of the existing tested implementations.

For an exact case-name filter, dense search ranks across the existing index and
selects matching records before taking five. BM25 ranks using full-corpus IDF and
length statistics, then selects matching records before taking five. The BM25
corpus is never rebuilt for a filter. Unknown/empty filters fail before embedding.

## Evidence schema

Each result contains:

- Stable `chunk_id`, `collection`, `corpus_index`, `vector_id`, and `chunk_reference`.
- `case_name`, `source_file`, `original_source_file`, `chunk_index`, `page_start`,
  `page_end`, and full `text`.
- `opinion_type`, raw `author`, `sections`, token/major-unit fields as preserved
  by the existing fusion implementation.
- Complete copied `metadata`, including original provenance, suitable for
  adapting to existing `rag.py` formatting and source-ID assignment.
- `rank` and `hybrid_rank`, final `rrf_score`, and `score_type="rrf"`.
- `dense_rank`, `bm25_rank`, `dense_similarity`, and `bm25_score`; missing values
  are explicitly `None`.

There is no ambiguous top-level `similarity`: the RRF score is never presented
as cosine similarity. Dense similarity is retained under `dense_similarity`.

## Error handling

Empty/non-string questions, invalid filters, mismatched/changed corpus resources,
invalid query dimensions/norms, and identity mismatches fail clearly. Missing
assets propagate from the validated read-only loader, without any rebuild.
Missing credentials and provider errors propagate; authentication and unrelated
errors are not swallowed. Only the existing bounded RateLimitError retry policy
applies during query embedding (60/120/240 seconds, at most three retries).

No lexical matches contribute an empty BM25 list to the same RRF formula. This
is not an algorithm switch or fallback. If both candidate lists are empty, the
result is empty; configuration/provider errors do not become empty results.

## Offline parity and tests

The parity test uses all 40 frozen Benchmark v2 questions. It reads saved dense
Top-5 rankings, reconstructs candidate records by saved vector IDs, and mocks the
embedding/dense paths. BM25 runs locally on the actual validated 433-record store.
Its Top-5 ordinals and scores are compared exactly with saved Phase 5A results;
final hybrid identities, ordering, RRF scores, component ranks and diagnostic
scores are compared exactly with saved Phase 5B results. All 40 questions match.
This validates adapter/lexical/fusion parity with saved dense candidates; it does
not establish new live embedding or provider availability. No metrics or labels
are recalculated, and no experiment outputs are rewritten.

Synthetic fixtures cover resource initialization/reuse, Top-5 depths, normalized
queries, filters before truncation, full-corpus statistics, identities, RRF scores,
stable ties, hydrated opinion/provenance metadata, absent scores, empty candidates,
invalid questions/filters, missing credentials/assets, provider failures, malformed
vectors, changed records, and cross-corpus/mismatched candidates.

Run focused tests locally:

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_live_retrieval.py'
```

The existing `run_phase4c2_tests.py` also runs the full repository suite with DNS
and network connections blocked and a verified local tokenizer cache.

## Next integration boundary

The adapter is ready for Phase 7A.2C integration, but is not yet used by the UI.
Fresh deployment still requires the ignored frozen runtime bundle. Grounded
answer generation separately requires a verified `VERCEL_GENERATION_MODEL`.
Neither model verification nor paid provider requests are part of this phase.

## Completion evidence

- Focused adapter tests: 13 passed, including exact parity for all 40 questions.
- Full offline repository suite: 243 passed; existing relevant groups passed.
- Actual runtime resources loaded from the validated 433-vector/record,
  1536-dimensional IndexFlatIP store; BM25 uses the same 433 frozen texts.
- Before/after SHA-256 comparison: all 131 existing data files unchanged, with
  no added or deleted data files. This includes every existing vector store,
  frozen chunk collection, benchmark, saved retrieval result and analysis report.
- Created only `live_retrieval.py`, `tests/test_live_retrieval.py`, and this guide.
  No existing application or retrieval implementation was modified in this phase.
- No provider/network calls, document embeddings, FAISS rebuilds, commits or pushes.

**READY for Phase 7A.2C.** UI integration and live provider verification remain
outside this phase; deployment assets and generation-model configuration retain
the prerequisites described above.
