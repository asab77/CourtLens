# Phase 7B.2B.1: offline citation-verifier evaluation harness

This is a standalone evaluation framework. No semantic verifier is integrated
into CourtLens; no provider client, LLM judge, NLI model, live requests or model
downloads are implemented. Generation, response states, UI and retrieval remain
unchanged.

## Frozen benchmark boundary

The loader pins Citation Support Benchmark v1 bytes to SHA-256
`2519c6563bcd21ac651e90a0151a67cbd37d6e4d50e6681c061b78884e18cffa`.
This check is independent of the checksum sidecar, so changing both the benchmark
and sidecar cannot bypass the expected hash. The existing frozen loader additionally
validates canonical serialization, adjudication agreement and original corpus
provenance. Version/schema must be 1.0; counts remain 32 claims and six answers.
Missing/modified/invalid inputs fail; no repair is attempted. All full evidence,
metadata and gold labels retain their original order and content. Six answer-level
records remain in the loaded artifact but are excluded from classification metrics.
Programmatic evaluation also rejects a benchmark object differing from the pin.

## Verifier API and input isolation

A future implementation provides identity, configuration, and:

```python
verify(claim, evidence, citation_metadata) -> VerificationResult
```

`VerificationResult` has `predicted_label`, `verifier_name`, `verifier_version`,
`execution_status`, and optional `rationale`, `error`, `latency_seconds`,
`token_usage`, and `cost_usd`. Only SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED,
and CONTRADICTED are valid successful labels. Latency/cost must be finite,
nonnegative numbers; usage values must be nonnegative integers. Successful rows
cannot have an error; failure rows cannot have a predicted label.

The exact claim and complete evidence text are copied. Citation metadata is
allowlisted: citation identifier, case name, raw opinion type/author, PDF page
range, source filename, and an explicit raw-attribution flag. No benchmark IDs,
gold labels, synthetic/authentic flags, failure categories, adjudication rationale,
component labels, question metadata, or other benchmark fields enter `verify`.
The runner copies the payload again before each call to prevent an implementation
mutating stored inputs or later examples. Gold labels and full provenance are
attached afterward for analysis only. This is API-boundary isolation, not a security
sandbox against a malicious implementation reading local benchmark files.

## Fixed lexical demonstration baseline

`LexicalOverlapBaseline` v1.0 uses the existing, unchanged local
`bm25_retrieval.tokenize`: Unicode NFKC, casefold, contiguous Unicode letter/number
terms, combining marks continuing terms, and punctuation separating terms.
There is no stemming, stopword removal, OCR repair, random sampling or metadata use.

Let R = unique claim tokens appearing in evidence / unique claim tokens.
An empty token set has R = 0.

- R >= 0.80: SUPPORTED.
- 0.50 <= R < 0.80: PARTIALLY_SUPPORTED.
- R < 0.50: UNSUPPORTED.
- Never predicts CONTRADICTED.

These thresholds were fixed before evaluation and were not chosen by looking at
benchmark performance or labels. This heuristic does not understand negation,
opinion attribution, legal conditions, completeness or entailment. Its names are
classification outputs, not statements of legal correctness. No perfect
benchmark-aware verifier is included; perfect/all-one-class predictions occur
only in synthetic metric tests.

## Failure accounting

One call per claim, with no runner retries. Each claim has one recorded result:

- VALID_PREDICTION
- INVALID_LABEL
- INVALID_RESPONSE_SCHEMA
- TIMEOUT
- PROVIDER_ERROR
- MISSING_PREDICTION
- EXECUTION_FAILURE

A returned None is missing; bad label/schema is failure. TimeoutError is TIMEOUT;
future adapters can raise ProviderFailure for PROVIDER_ERROR; other exceptions
are EXECUTION_FAILURE. Future adapters must set their own timeout or translate
provider-specific exceptions; the synchronous runner does not forcibly terminate
a hanging implementation. There is no real provider adapter in this phase.

Exception response bodies are not stored. Errors use fixed type/message pairs.
A future adapter should translate errors to these public categories rather than
persisting raw exception strings. Optional adapter-reported rationale/accounting
is validated. Credential/config-header fields and token-like strings are rejected;
no credential is read by the harness. Adapters must never place secrets in any
output field. Malformed replay files are rejected before scoring, not repaired
into successful negatives.

## Scoring definitions

All four classes have fixed order: SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED,
CONTRADICTED. The confusion matrix has gold rows and predicted columns. It
includes valid predictions only; failures remain visible separately.

- Accuracy = correct valid predictions / all valid predictions.
- Class precision = TP / predicted class count among valid predictions.
- Class recall = TP / gold class count among valid predictions.
- Class F1 = harmonic mean of precision and recall.
- Macro-F1 = unweighted mean over the fixed four classes.
- Supported precision/recall expose that class's corresponding values separately.
- Coverage = valid predictions / all 32 claims.
- False Support Rate = non-SUPPORTED gold examples predicted SUPPORTED / all
  non-SUPPORTED gold examples **with a valid prediction**.

Thus FSR is conditional on prediction validity, like the other classification
metrics. The report records numerator, valid denominator, and all-example
non-SUPPORTED count (22 in this benchmark). A failed non-supported example is
neither a false support nor a correct negative. Report FSR together with coverage
and failure counts; it is not an end-to-end reliability rate.

With at least one valid prediction, zero denominators for individual class
precision/recall produce 0, and F1 is 0 if both are 0; all four classes still enter
macro-F1. No valid predictions means accuracy, per-class precision/recall/F1,
macro-F1 and supported precision/recall are null; coverage is 0. FSR is null when
no valid non-supported denominator exists. An all-failing verifier earns no
classification success. Counts/matrix remain available even when metrics are null.

## Runner and new-only outputs

Offline execution:

```bash
.venv/bin/python run_citation_verifier_evaluation.py \
  --output data/analysis/citation_verifiers/NEW_RUN_DIRECTORY
```

Output directories must not exist. No prior experiment directory is overwritten.
Each run stores:

- `results.json`: pin/version, verifier identity, configuration digest, ordered
  inputs/results/gold labels/provenance, metrics, timestamp, runtime environment,
  failures, excluded-answer count, zero retries and limitations.
- `configuration.json`: verifier configuration and implementation/tokenizer hashes,
  stored separately from the benchmark; no prompts exist for this baseline.
- `predictions.json`: credential-free external replay schema, with exactly one
  result per original claim ID.
- `report.md`: readable metrics, confusion matrix and limitations.
- `manifest.json`: SHA-256 checksums for the four run artifacts.

The baseline records no latency, token consumption or inference cost; these
optional fields remain null. No paid inference occurred. Python version,
implementation/platform, installed dependency versions, random seed (null), and
configuration are recorded. Metrics never depend on timestamps. Specify a
consistent timezone-aware ISO-8601 `--timestamp` for exact reproduction in the
same environment. Different environments/config implementations can change
metadata even when predictions and metrics match.

## Strict external prediction replay

```bash
.venv/bin/python run_citation_verifier_evaluation.py \
  --replay PATH_TO_PREDICTIONS.json \
  --verifier-id lexical-overlap --verifier-version 1.0 \
  --output data/analysis/citation_verifiers/NEW_REPLAY_DIRECTORY
```

Use the generated `predictions.json` as the schema template. Top-level fields are
`schema_version`, `benchmark_version`, `benchmark_sha256`, `verifier`
(id/name/version), `configuration`, and `predictions`.
Each prediction has `example_id` and `result`. Required result fields are
`predicted_label`, `verifier_name`, `verifier_version`, `execution_status`.
Optional fields may be omitted or null; failed results require their canonical
error object. Example explicit failure:

```json
{
  "example_id": "CS-001",
  "result": {
    "predicted_label": null,
    "verifier_name": "FutureVerifier",
    "verifier_version": "1.0",
    "execution_status": "TIMEOUT",
    "error": {"type": "TIMEOUT", "message": "timeout"}
  }
}
```

Every claim ID must appear once; missing IDs require explicit failure records,
not omission. Unknown/answer IDs, duplicates, invalid labels/schema, incompatible
checksum/version, identity mismatch, and duplicate JSON fields are rejected.
Replay row order can differ, but scoring restores the benchmark's fixed order.
No verifier is called during replay. Replay uses exactly the same scoring logic.

## Saved baseline results

Run: `data/analysis/citation_verifiers/lexical_overlap_v1/`.
Coverage 32/32 (100%); no execution failures.

| Metric | Value |
|---|---:|
| Accuracy | 0.562500 |
| Macro-F1 | 0.500644 |
| False Support Rate | 2/22 = 0.090909 |
| Supported precision | 7/9 = 0.777778 |
| Supported recall | 7/10 = 0.700000 |

| Gold / predicted | SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED |
|---|---:|---:|---:|---:|
| SUPPORTED | 7 | 3 | 0 | 0 |
| PARTIALLY_SUPPORTED | 0 | 7 | 0 | 0 |
| UNSUPPORTED | 0 | 3 | 4 | 0 |
| CONTRADICTED | 2 | 6 | 0 | 0 |

The eight contradiction examples receive no correct contradiction prediction,
consistent with the baseline's deliberate lack of contradiction reasoning. These
results illustrate scoring; they do not establish an effective semantic verifier.
The 32-example, mostly synthetic, failure-informed and AI-assisted-adjudicated
set is not an independent generalization benchmark or proof of legal accuracy.

READY for Phase 7B.2B.2 on this offline harness foundation. Any future real
inference requires separate authorization; no provider/model integration begins
in this phase.

## Completion validation

- 22 focused offline harness tests passed.
- Complete repository suite: 356 tests passed with DNS/connections/HTTP blocked.
- Offline CLI replay reproduced every saved baseline metric without calling a verifier.
- All 208 protected before/after hashes match: historical data, benchmark/checksum,
  adjudication/candidates, prior documentation/tests, and existing Python modules.
- Five new run files only were added under data; all manifest hashes match.
- No existing files modified, no real API calls, no paid inference, no model
  downloads, no UI/generation/retrieval changes, and no commits or pushes.
