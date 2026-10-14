# Phase 7B.2B.2 — experimental GPT-4.1 Mini citation verifier

Implementation and offline validation only. No paid benchmark or preflight calls
occurred. This verifier is separate from the CourtLens application: grounded
answer generation, response_contract.py, evidence formatting, Streamlit and
retrieval are unchanged.

## Interface and fixed experiment

`GPT41MiniCitationVerifier.verify(claim, evidence, citation_metadata)` implements
the existing VerificationResult interface. Only the harness's allowlisted input
is sent: the exact claim, entire original passage, citation identifier, case,
raw opinion/author, PDF pages, source filename and raw-attribution flag. Extra
metadata fields are rejected. No gold label, adjudication rationale, example ID,
category, synthetic flag, question metadata, other examples or previous prediction
is sent. No claim rewriting, decomposition or example-specific prompting occurs.

Model: `openai/gpt-4.1-mini`; CourtLens AI Gateway via Vercel:
`https://ai-gateway.vercel.sh/v1`. Credentials are loaded only when explicitly
constructing a future live client, through existing secret-safe gateway helpers.
The verifier model is fixed independently of the application's generation setting.
No model fallback, NYU headers or embedding client is used. SDK retries are zero;
request timeout is 60 seconds. Live evaluation is sequential.

Ordinary Chat Completions and max_tokens previously succeeded in Phase 7A.3.
The installed SDK exposes temperature and max_tokens. Temperature is configured
as 0; the authorized contract preflight must confirm actual gateway acceptance.
No response_format/schema/JSON-mode capability is assumed. Unsupported parameters
cause a failed preflight and stop, not parameter removal or fallback. Temperature
0 is not a guarantee of deterministic hosted inference.

## Prompt and output contract

Prompt version: `citation-support-v1.0`.
SHA-256 of exact UTF-8 system prompt:
`f9b9160cd8c6f168a06d00c10dec680f4f3333ad83cdaf9f245f57b6be3cdfaa`.

The fixed prompt defines all four support labels and follows the frozen compound
policy, including explicitly identifying contradicted subcomponents in rationales.
It distinguishes quotation from endorsement, majority from concurrence/dissent,
missing evidence from contradiction, and legal exceptions from absolute claims.
Raw/OCR-derived attribution is uncertain. Claim, evidence and metadata are
explicitly untrusted data. One user JSON payload contains each complete pair.

Output must be one JSON object with exactly `label` and `rationale` string fields.
The label must be one of the four allowed labels and rationale must be nonempty.
Duplicate keys, nonfinite JSON, markdown fences, malformed/non-object JSON, extra
fields, missing fields and invalid types are rejected. Unknown labels produce
INVALID_LABEL; other schema violations produce INVALID_RESPONSE_SCHEMA. Truncated
or other non-stop completions fail rather than being repaired. No repair request
is made. Provider exceptions are safely categorized; raw response/error bodies
are not persisted. Latency, integer usage and reported/estimated cost are retained
when available, including for invalid output.

## Safety limits and accounting

The prepared configuration requires explicit CLI limits:

- At most 35 attempted requests total: three contract preflights plus 32 claims.
- At most three preflight attempts and 32 benchmark attempts independently.
- Maximum output: 512 tokens per request, or a smaller explicitly supplied cap.
- Selected conservative input budget: 8,192 estimated tokens, no truncation.
- Prepared estimated cost ceiling: $0.10, never increased automatically.
- No SDK retries, repair calls, alternate models, embedding/retrieval/application
  answer-generation requests or concurrency expansion.

Before dispatch, reserve the estimated full prompt plus maximum output cost.
On response, reconcile provider usage and reported cost when available; otherwise
apply the recorded rates. A failed request with unknown usage keeps its conservative
reservation instead of assuming zero cost. Exceeding a request/estimated-cost limit
stops dispatch. A reported overspend or token-limit breach stops subsequent requests;
client accounting cannot undo a provider charge already incurred. The ceiling is
not a provider-enforced billing cap.

The future runner writes a durable request ledger **before** each dispatch and
checkpoints completed accounting. A ledger or result directory blocks automatic
re-execution; interruptions cannot silently reset call counts. No automatic resume
or rerun is provided. An authorized operator must review any interrupted ledger
before deciding further work. Failed/stopped runs fill remaining claims with explicit
MISSING_PREDICTION records, so the unchanged harness coverage/metrics remain honest.
Preflight failures are recorded separately from claim classification failures.

The three preflights are fixed fictional non-benchmark pairs; only output-contract
validity is checked, not expected gold predictions. A failed preflight aborts the
benchmark. Provider/timeout/unexpected execution failures during the benchmark
also stop further requests. Schema failures are recorded without another request.

## Offline dry run

Preparation directory:
`data/analysis/citation_verifiers/gpt41mini_v1/`.
It contains `configuration.json`, `system_prompt.txt`, `dry_run.json`, and
`preparation_manifest.json`. No live predictions or classification metrics exist.
Preparation refuses to overwrite existing directories. The manifest pins prepared
files and implementation hashes; a future live command refuses changed preparation.

Executed offline:

```bash
.venv/bin/python run_llm_citation_verifier.py \
  --max-requests 35 --max-output-tokens 512 --estimated-cost-ceiling 0.10
```

The dry run loads the pinned frozen benchmark, constructs all 32 inputs, checks
payload/evidence preservation, and estimates tokens with locally verified
cl100k_base. Prompt estimates add 100 framing tokens and a 20% margin. This is an
approximation of generation tokenization, not an exact provider count or a verified
model context-window claim. Every complete passage fits the selected 8,192-token
application input budget. No passage is truncated.

Results:

- Zero real provider requests; 32 claim inputs and six answers excluded.
- Maximum evidence length: 900 cl100k_base tokens.
- Maximum reserved input per benchmark request: 1,842 tokens.
- Total reserved input including three preflights: 53,805 tokens.
- Total possible output: 17,920 tokens (35 × 512).
- Maximum estimated cost: $0.050194; below the prepared $0.10 ceiling.
- No input-length, request-count or estimated-cost blockers in this configuration.

Pricing is the locally archived Vercel listing verified on **2026-10-11**:
$0.40/million input tokens and $1.60/million output tokens. Source:
https://vercel.com/ai-gateway/models/gpt-4.1-mini . No network pricing refresh
occurred in this offline phase. Reconfirm pricing before live authorization;
this estimate is conditional on those recorded rates and does not guarantee billing.

## Future execution artifacts and harness reuse

A subsequently authorized `--live` invocation uses the prepared inputs/limits and
writes a new `gpt41mini_v1/live_run/`, leaving preparation intact. Do not run that
mode during this implementation phase. Its adjacent durable request ledger records
attempts, category, estimates, actual usage/cost and safe errors. No credentials or
provider exception bodies are saved.

The existing harness produces configuration, per-claim predictions/rationales,
usage, latency, errors, gold labels for analysis only, aggregate metrics, confusion
matrix, replay JSON and artifact checksums. Supplemental prompt/comparison files
have a separate manifest. Comparison references the lexical baseline checksum and
uses exactly the existing accuracy, per-class precision/recall/F1, macro-F1, FSR,
supported precision/recall, coverage and failure definitions. The six answer examples
remain excluded. The only harness modification is verifier-neutral report wording;
no scoring definition or previous baseline artifact changes.

## Readiness and limitations

READY for a separately authorized contract preflight followed by evaluation if
preflight succeeds. No paid execution is authorized by this document. Reconfirm
current pricing/credential access, and require gateway acceptance of temperature
0 and the strict output contract. Failures stop safely; no fallback is implemented.

The frozen set is small, mostly synthetic, failure-informed and AI-assisted in
adjudication, with no independent legal-expert review. An LLM rationale is not proof
of support or legal accuracy. Inference may vary despite temperature 0. No production
citation verification, legal-rule checking or automatic answer correction is added.

## Completion evidence

- 18 focused tests passed using fake provider clients only.
- Full offline repository suite: 374 tests passed with network guards.
- All 143 prior data hashes match, including frozen benchmark/checksum,
  adjudication/candidates, vector stores, retrieval results and smoke artifacts.
- Of 217 pre-existing file hashes, only the explicitly scoped harness report-text
  change differs; all other 216 hashes match. Application behavior is unchanged.
- Four preparation files added; all prepared-file/implementation checksums match.
- Rebuilding the dry-run report in memory produces exactly the saved JSON.
- No live execution directory or request ledger exists: no real requests,
  spending, embeddings, retrieval, application generation, commits or pushes.

Created the adapter, standalone runner, fake-client tests, this guide, and four
preparation artifacts. Modified only the harness's report wording for non-lexical
verifiers; metric definitions and prior experiment outputs remain unchanged.
