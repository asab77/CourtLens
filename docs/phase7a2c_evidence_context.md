# Phase 7A.2C: evidence formatting, attribution and context budgeting

This phase creates a local evidence bridge and updates generation context
construction. It does not connect hybrid retrieval to Streamlit. UI, session
management, live retrieval, BM25, RRF, dense embeddings/search and frozen artifacts
remain unchanged. No provider requests, semantic citation verification, query
rewriting, reranking, embeddings or index rebuilds occurred.

## Public API

```python
from evidence_context import build_evidence_context

context = build_evidence_context(
    retrieved_results, token_budget=12000, safety_margin=0.10, tokenizer=None
)
```

Inputs are hydrated ranked records, a token budget, and an optional tokenizer
with the tiktoken-compatible `encode(text, disallowed_special=())` interface.
`None` uses the project's hash-verified, local-only cl100k_base loader, cached
once per process. It never downloads vocabulary.

`EvidenceContext` returns:

- `evidence`: copied, selected records with current-turn `source_id`, exact text
  and original metadata; `truncated=False`, original/included text token counts.
- `text`: the exact formatted evidence serialization used for generation.
- `sources`: each S-number mapped to its original retrieved position, stable
  chunk ID (when supplied), corpus collection and complete source metadata.
- `usage`: configured/effective budget, safety margin, actual serialized token
  count, tokenizer name, selection counts, approximation flag and policy.
- `skipped`: original positions/identities, reason, original text token count,
  and included count zero.
- `status`: `ready` or explicit `insufficient_context`.

`format_sources` validates already labeled evidence. `citation_errors` checks
canonical citation syntax and membership. Neither performs retrieval nor model
calls. `sanitize_history_citations` operates only on the prompt copy of history.

## Evidence format and opinion attribution

```text
[S1]
Case: <original case name>
Source: <original PDF filename, or source filename>
PDF pages: <original page_start>-<original page_end>
Chunk ID: <original ID, or Not supplied>
Original chunk index: <original index>
Opinion (source metadata): <original opinion label, or Unknown>
Author (raw source metadata): <original author, or Unknown>
Sections (source metadata): <original section markers/titles, or Unknown>
Text: <exact original passage>
```

The adapter preserves full metadata/provenance. It does not guess an author,
repair OCR, infer majority status, or turn unknown attribution into certainty.
Missing optional metadata remains missing in the evidence object; display
placeholders are not fabricated metadata. Raw uncertain author strings and labels
are retained verbatim. Distinct majority/concurrence/dissent chunks on overlapping
PDF pages remain separate sources, never merged or deduplicated by page overlap.

Inputs require nonempty text, case/source names, original nonnegative integer
chunk index and valid integer PDF page ranges. Conflicting flattened hybrid
metadata is rejected. Duplicate collection/source/index identities or duplicate
stable chunk IDs are rejected before selection, including nonfitting records.
Legacy dense records without chunk IDs retain their source/index identity;
no replacement stable chunk ID is invented.

## Budget and skip policy

`COURTLENS_EVIDENCE_TOKEN_BUDGET` defaults to 12000 estimated tokens;
`COURTLENS_EVIDENCE_SAFETY_MARGIN` defaults to 0.10. Both use the existing
Streamlit-secret-first/environment-fallback configuration convention. Explicit
keyword arguments can override them. The effective limit is
`floor(token_budget * (1 - safety_margin))`, or 10800 by default.

Selection processes evidence in fused ranking order. Each complete passage is
included if the complete tentative joined serialization fits; otherwise it is
recorded as skipped and selection continues to later records. Selected records
preserve relative ranking order. Counting includes all source headers, metadata,
text and separators, not merely raw chunk tokens. Every trial counts the joined
string directly to include token-boundary effects between blocks.

There is no truncation, OCR repair, passage splitting, opinion merging or extra
source made from a partial chunk. Included text token counts equal original text
counts. Skipped chunks have included count zero and a recorded reason. Empty
input or no fitting chunk returns `insufficient_context`; generation returns the
existing insufficient-evidence sentence without constructing a provider client.

cl100k_base is an approximation for an independently configured generation
model, not a claim to match its tokenizer. The margin is configurable, not a
mathematical guarantee of fitting every model. Prompt instructions, question,
history, correction messages and output allowance are outside this evidence-only
budget. Future integration must reserve those separately for the chosen model's
total context window; this phase does not claim to enforce a model-wide limit.

## Canonical IDs and citations

Each selected chunk receives exactly one contiguous source ID S1, S2, ... in
selected order. Incoming IDs are not reused by the builder. `sources` preserves
the original retrieved position even when an earlier passage was skipped.
Already labeled evidence must have unique, contiguous canonical IDs.

Citation checking accepts only `[S1]`, `[S2]`, etc., with ASCII digits, no leading
zeros, and membership in the current context. It flags noncanonical/unknown IDs,
source-like malformed bracket references, and bare S-number references. Repeated
citations to the same valid source are allowed. `[S01]`, `[S999]`, `[S 1]`, `[s1]`,
unclosed source references and nested brackets are rejected/flagged.

This establishes syntax and source-reference integrity only. A syntactically
valid citation may still fail to support the claim. Semantic support verification
is reserved for Phase 7B. The existing single correction attempt for deterministic
ID failures remains; no new LLM verification process is implemented. The exact
insufficient-evidence sentence alone can omit citations; adding uncited assertions
to it no longer bypasses the citation requirement.

## History rule and legal grounding

Historical source-like citation IDs are replaced with an explicit removed-reference
marker in both user and assistant history supplied to the model. Stored messages,
answers and their historical evidence mappings are unchanged. The current question
is not rewritten. History remains wording context, not evidence; current evidence
IDs alone are eligible references for the current answer.

Generation instructions require grounding only in current evidence, accurate
quotation/argument attribution, distinction between majority/concurrence/dissent,
no dissent-as-controlling-holding, no assumption that retrieved opinions agree,
no invented case facts or holdings, and acknowledged attribution uncertainty.
Metadata labels are explicitly imperfect source metadata, not verified identities.

## Generation compatibility and safety

`generate_grounded_answer` retains its `(answer, selected_evidence)` return shape
and now returns the exact selected source mapping used for generation. It accepts
optional `context_token_budget`, `safety_margin` and `tokenizer` keywords.

`generate_grounded_answer_from_evidence` accepts either a prepared `EvidenceContext`
or the existing source-labeled list. Prepared contexts are checked for matching
serialization, source mapping and token counts before requests. A custom tokenizer
must be supplied again when consuming a context built with it. For already labeled
legacy lists, any budget selection that would renumber a source fails explicitly:
use a prepared context or the wrapper instead. This prevents old caller/UI mappings
from silently pointing at different chunks. Prefix-only selections retain IDs.

Generation model selection and Vercel configuration are unchanged. Missing
model/credential errors remain explicit. Empty generation questions are rejected.
No Streamlit changes are required in this phase; the current dense workflow keeps
its public interfaces. Hybrid retrieval integration remains for a later phase.

## Local tokenizer and deployment prerequisites

`tiktoken` is now declared in the runtime requirements; it was already installed
locally, and no dependency installation occurred. A deployment must also provide
the verified local cl100k_base vocabulary at `TIKTOKEN_CACHE_DIR` under the project's
existing cache key. Missing vocabulary fails locally rather than downloading.
The existing local loader also supports installed VS Code vocabulary paths, which
must not be assumed on a deployment server. Refer to `local_tokenizer.py` for the
canonical vocabulary SHA-256 and cache filename. No vocabulary artifact is added,
modified or uploaded in this phase.

Fresh deployment still needs the ignored structure-aware asset bundle and a
verified Vercel generation model. The evidence budget must be selected with room
for the generation model's instructions/history/output and tokenizer differences.

## Completion evidence

- Focused evidence/generation tests: 22 passed.
- Existing application migration/UI tests: 12 passed.
- Full offline repository suite: 265 passed (network connections and DNS blocked).
- All 136 protected SHA-256 hashes unchanged: 131 data files plus `app.py`,
  `live_retrieval.py`, `retrieve.py`, `bm25_retrieval.py` and `hybrid_retrieval.py`.
  No data files added or deleted; saved experiment artifacts and benchmarks remain frozen.
- Created this guide, `evidence_context.py`, and `tests/test_evidence_context.py`.
- Modified `rag.py`, `gateway_config.py`, runtime requirements, and the existing
  application test fixture to supply required original source/chunk metadata.
- No provider/network calls, dependency installations, UI changes, commits or pushes.

**READY for Phase 7A.2D implementation.** Remaining live/deployment prerequisites
are a verified generation model, packaged runtime assets and local vocabulary,
model-wide prompt/output capacity planning, and later authorized UI integration.
Semantic citation support verification remains Phase 7B work.
