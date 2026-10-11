# Phase 7A.2D: Streamlit integration of live hybrid retrieval

The AI Assistant now defaults to structure-aware hybrid retrieval, using the
unchanged Phase 7A.2B adapter. The original dense algorithm remains available
only through an explicit **Dense only** strategy option. Retrieval errors do not
switch algorithms. The separate Retrieval tab retains dense inspection, Top-K,
case filtering and passage cards.

## Files and small integration boundary

Created `assistant_integration.py` for testable resource initialization and the
retrieve/context/generate/validate workflow; added local tests and this guide.
Modified `app.py` and the existing application tests. No retrieval algorithm,
RAG prompt, evidence selection policy or model selection implementation changed.

## Resource cache

Streamlit caches `initialize_resources` by resolved runtime asset path and
SHA-256 provenance identity: index, records, store manifest, frozen chunks,
chunk manifest and structural preview. A cache miss uses the existing validated
loader and initializes full-corpus BM25 exactly once for that cached version.
Path or content changes produce a different key; assets changing during a load
are rejected. Cache hits reuse FAISS, catalog and BM25. Hashing the asset files
on reruns adds local disk work but prevents stale resources being selected by
path alone. Missing/invalid files produce a safe startup error, never a rebuild.

Credentials and user histories are not cache inputs or globally cached values.
Only immutable corpus resources are shared across sessions; chat messages remain
in each session's `court_messages`. Cached index objects must be treated as read-only.

## Normal Chat flow

For a submitted question, the existing session flow stores the user message,
then calls `answer_question` with unchanged question text, current history,
case filter, configured model and explicitly selected strategy:

1. Check Vercel credential and independently configured generation model before
   any retrieval request.
2. Hybrid: call unchanged `retrieve_hybrid` (dense depth=5, BM25 depth=5, k=60,
   five final results). Dense only: call unchanged `semantic_search` with Top-K.
3. Build the existing bounded evidence context using the configured token budget
   and safety margin. No additional source labeling or text modification occurs.
4. If no context fits, return the existing insufficient-evidence sentence without
   calling generation or constructing a generation client.
5. Pass the exact prepared `EvidenceContext` to existing grounded Vercel generation.
6. Check returned canonical citation syntax and membership against that context,
   including after mocked generation in tests. Invalid answers are not stored
   as successful grounded responses.
7. Store the answer, selected evidence, source mapping, budget/skipped details,
   strategy/model and separate prompt-planning estimates in the current session.
8. Render only this answer's evidence/IDs. Prompt history sanitization remains
   the existing Phase 7A.2C rule; saved historical answers keep their own mappings.

No query rewriting, reranking or semantic citation verification is introduced.
Canonical IDs identify included sources; they do not prove claim support.
Compare Models remains explicitly disabled with its existing explanation.

## Context capacity accounting

The exact formatted evidence remains constrained by the existing evidence-only
budget and margin. Session diagnostics separately record estimated system,
history, question and evidence tokens. `COURTLENS_EXPECTED_ANSWER_TOKENS`
(default 1024) is a planning allowance only, not a new API output limit. It must
be a positive integer. Component counts exclude message-framing overhead and
are not a model-wide context guarantee. The generation model's total capacity
is unknown here; no guaranteed-fit claim is made. cl100k_base remains an
approximation, and the locally verified vocabulary must be available.

Future controlled testing must choose sufficient capacity for instructions,
history, evidence, message framing, correction attempts and expected output.
No paid requests or model-capacity trials are performed by this phase.

## Rendering and errors

Assistant evidence cards show canonical source ID, case, original source file,
PDF pages, original chunk index/text, source opinion label, raw author (or Unknown),
sections when supplied, and hybrid rank. RRF, dense similarity and BM25 score
are labeled separately. Scores are not displayed as correctness probabilities.
Original source text including extraction markers is retained in Assistant cards;
the Retrieval tab keeps its existing compact preview/inspection layout.

Fixed safe messages cover missing credentials/model, invalid runtime assets,
retrieval/filter/provider failures, budget/tokenizer problems and generation/citation
failures. Provider response bodies, arbitrary exception messages, credentials and
stack traces are not rendered. Hybrid failure never invokes dense fallback.
Safe error messages are recorded in the current session using the existing flow.

## Tests and implementation incident

Tests mock both retrieval branches and generation. They cover hybrid default,
explicit dense selection, path/provenance caching, Normal Chat, exact context and
source mapping, empty/insufficient context, missing configuration/assets, invalid
filters, provider/citation errors, safe error messages, session isolation, historical
source IDs, Compare Models remaining disabled and Retrieval tab compatibility.
Existing offline parity tests continue to cover all 40 Benchmark v2 rankings.

The first focused test run exposed an unmocked dense branch. It may have attempted
an unauthenticated embedding request with the fake test credential; no real
credential was used and no paid generation request was made. There was no request
logging to confirm whether a network request occurred, so this phase does not
claim zero network attempts across that initial run. The mock was corrected,
permanent UI-test DNS/socket guards were added, and subsequent focused/full runs
block network access. No document embeddings or index writes occurred.

## Smoke-test readiness

The local integration is ready for a controlled smoke test once configuration is
complete. A verified `VERCEL_GENERATION_MODEL`, Vercel key/credits, frozen runtime
bundle, verified local tokenizer vocabulary and an appropriate total-context plan
are required. The implementation does not substitute a model or silently reduce
retrieval to overcome missing configuration. No smoke test, commit or push was run.

## Completion evidence

- Final focused integration tests: 19 passed with network guards.
- Full offline repository suite: 284 passed; all existing relevant groups passed.
- All 138 protected SHA-256 hashes are unchanged: 131 data artifacts plus the
  live adapter, dense retrieval, BM25, RRF, runtime validator, evidence builder
  and RAG implementation. No protected files or data outputs were added/deleted.
- Created this guide, `assistant_integration.py`, and integration tests. Modified
  `app.py`, the existing application test mocks/guards, and current README.
- No real credential was used for provider requests; no paid generation calls,
  document embeddings, index rebuilds, commits or pushes occurred. The initial
  unmocked fake-credential test branch is disclosed above; subsequent runs are
  network-blocked.

**NOT READY for a live controlled end-to-end smoke test yet:** the Vercel key is
configured locally, but `VERCEL_GENERATION_MODEL` is absent. Once an independently
verified model ID is supplied and total-context planning is confirmed, the local
implementation is ready for that separately authorized test. No model is selected
or tested automatically.
