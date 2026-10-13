# Phase 7B.1: citation and abstention integrity

## Root cause and boundary

The frozen Phase 7A.3 Dobbs draft correctly acknowledged insufficient evidence,
but varied from the exact required refusal sentence. `citation_problem` treated
it as an uncited answer. The correction requested a rewrite with S1–S3 or the
exact refusal. The model retained its abstention and added citations to unrelated
Obergefell excerpts; valid IDs then passed. Nonempty retrieval and valid IDs did
not establish source support.

This phase replaces phrase-based abstention recognition with explicit response
states and removes corrective generation. It does not repair Miranda's omitted
alternative-safeguards qualification or Obergefell's overextended holding summary.
No semantic verification, judge, NLI, claim decomposition, query rewriting,
reranking, or automatic factual correction is implemented.

## Response envelope

The existing OpenAI-compatible Chat Completions call remains unchanged. No
`response_format`, JSON-mode, or schema capability is assumed or added. The prompt
requests a JSON envelope, validated locally:

```json
{"state": "ANSWERED", "answer": "Evidence-based answer [S1]."}
```

```json
{"state": "INSUFFICIENT_EVIDENCE", "answer": ""}
```

```json
{"state": "VALIDATION_FAILED", "answer": ""}
```

Exact keys and string types are required. Unknown states, duplicate keys, extra
fields, non-JSON prose, markdown fences, and empty answered bodies fail safely.
Plain historical model output is not upgraded by interpreting its phrases.
Incorrectly formatted output can therefore produce more validation failures;
there is no live evidence yet of the configured model's envelope adherence.

`ANSWERED` means the envelope and citation identifiers passed, not that the
answer is true, complete, or supported. The model's declaration of insufficient
evidence is not independently verified. A model can still declare ANSWERED and
cite an unrelated but valid passage; resolving that is Phase 7B.2 work.

## Abstention and correction policy

An INSUFFICIENT_EVIDENCE envelope requires an empty body. The application renders
the fixed sentence: “The available Supreme Court documents do not provide enough
evidence to answer this question.” No citation is needed and no corrective call
occurs. Citation-bearing or claim-bearing abstention bodies are rejected instead
of being silently edited. Empty selected evidence also produces explicit
INSUFFICIENT_EVIDENCE locally without constructing a generation client.

ANSWERED responses require canonical [S1], [S2], … syntax and at least one
citation. Membership uses only `EvidenceContext.sources` for the exact current
formatted evidence. Existing malformed/unknown-ID checks remain unchanged;
[S01], [S999], malformed brackets, and bare IDs fail. History sanitization and
current-turn source mapping remain unchanged. Valid historical/current S1
collisions cannot prove which passage the model meant; membership validation is
not semantic support or historical claim verification.

There is **no automatic citation-correction generation**, including for missing
citations in ANSWERED responses. Invalid identifiers or envelopes produce
VALIDATION_FAILED with a safe fixed message rather than a repaired answer.
The original raw model envelope is available on `ResponseText.raw_draft` for
local debugging. It is not logged, persisted to user session messages, or rendered
as a verified answer. Generic validation reasons can appear in session diagnostics.
Provider/configuration failures retain the existing safe exception handling;
no new provider retries, model fallback, or model selection changes occur.

## Interfaces and UI

`generate_grounded_answer_from_evidence` still returns a string-compatible value;
`generate_grounded_answer` still returns `(answer, selected_evidence)`.
`ResponseText`, a str subclass, additionally carries `response_state`,
`validation_errors`, and the local-only draft. JSON/string conversion loses these
attributes: callers needing state must explicitly carry it separately.

`answer_question` retains its dictionary shape and evidence mapping with additive
`response_state`, `validation_errors`, and `citation_validation_scope`. The
session `content` is a plain string without raw diagnostics. Legacy plain-string
integration substitutes are treated only as ANSWERED and checked for identifiers;
no abstention is inferred from their text. Production generation always parses
the envelope first. Existing saved messages remain renderable without new fields.

The UI distinguishes answered/insufficient/failed outcomes and does not describe
abstentions or validation failures as grounded answers. Evidence inspection is
still available as retrieved material, not proof of the displayed refusal. For
ANSWERED responses the caption explicitly says factual support is not verified.
Compare Models remains disabled. The smoke runner's standalone identifier check
now passes explicit response state; its frozen reports and request ledger were
not changed or rerun.

## Tests and protected artifacts

Offline regressions use fake clients and the frozen Phase 7A.3 answers as inputs.
They cover valid Dobbs abstention, unsafe citation insertion, plain old refusal
failing without repair, exact Miranda/Obergefell answers retaining valid IDs despite
manual grounding weaknesses, malformed/unknown IDs, schema errors, source/history
isolation, empty evidence/model output, mixed opinions, string/tuple compatibility,
and session/UI states with drafts excluded. The unsafe second reply is installed
as a fake response but is never requested.

Full test runs block DNS, socket connections, and requests HTTP dispatch and use
verified local vocabulary. No live generation or embedding calls occur.

Before/after SHA-256 verification covers all 133 existing data files (frozen
chunks/indexes, Benchmark v2, dense/BM25/hybrid/cross-encoder results, and both
Phase 7A.3 smoke artifacts), plus six retrieval/provider configuration modules.
All 139 hashes must match. No protected data files are added, deleted, or modified.

READY for Phase 7B.2 implementation on this deterministic integrity foundation.
This is not a claim that legal grounding is solved or a live rollout is validated.

## Completion evidence

- New deterministic response-integrity tests: 17 passed.
- Focused contract/application/retrieval integration tests: 94 passed with network guards.
- Full repository suite: 312 passed with network guards.
- Before/after verification: all 139 protected hashes match; all 133 data files
  retain their names/content, including both frozen smoke reports.
- No live provider calls, embeddings, index rebuilds, benchmark changes,
  dependency changes, commits, or pushes.

Created `response_contract.py`, `tests/test_response_integrity.py`, and this guide.
Modified `rag.py`, `assistant_integration.py`, `app.py`, the standalone smoke
runner's state-aware validation call, README, and the three existing application,
Assistant integration, and evidence-context test modules. `evidence_context.py`
and all retrieval/provider configuration implementations remain unchanged.
