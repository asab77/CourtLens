# Phase 7B.2B.2A: cumulative verifier accounting

This change is offline preparation, not authorization for benchmark inference.
The frozen prompt and benchmark, existing preflight artifacts, and metric definitions are unchanged.

The previous runner started an empty budget and repeated preflight. Live CLI execution now requires `--benchmark-only`, validates the existing preflight, and imports its three completed requests and $0.000818 reported cost. The original combined live CLI path is disabled.

The historical ledger SHA-256 is pinned in code. The preflight manifest, saved configuration, prompt, benchmark identity, responses, predictions, usage, and aggregate results are cross-checked. Missing, pending, duplicate, inconsistent, or tampered records fail closed. The historical manifest remains unchanged; the new benchmark path does not depend on the older preparation manifest's now-obsolete implementation hashes.

The cumulative budget uses Decimal arithmetic and enforces 35 combined requests, at most 32 new benchmark requests, and a $0.10 cumulative estimated ceiling. Every model input preserves complete evidence and allowlisted metadata. No gold labels or preflight expectations enter requests.

Before dispatch, an exclusive, fsynced, atomically installed journal event records the reservation. After response, another event records the prediction and reconciles reported cost, or usage-priced cost. Unknown usage retains the reservation. Events form a checksum chain and are never overwritten. A process lock prevents concurrent execution in the same output directory. Invalid transitions, missing events, partial temporary writes, or conflicting reservations require manual review.

On an explicitly authorized restart, completed predictions are reused. An uncertain dispatched request remains charged and counted, receives an execution-failure result for scoring, and is never retried. The runner proceeds only to unreserved examples in frozen order. Finalized scoring output cannot be executed again. Copying or deleting a live output directory is not a supported restart procedure; journal checksums detect consistency failures, not malicious rewriting of an entire local history.

Dry-run command (no client construction, credentials, or inference):

```sh
.venv/bin/python run_llm_citation_verifier.py --benchmark-only \
  --output data/analysis/citation_verifiers/gpt41mini_v1/benchmark_v1 \
  --max-requests 35 --max-output-tokens 512 --estimated-cost-ceiling 0.10
```

Live execution would additionally require `--live`, only after separate explicit authorization. It performs no preflight calls, retries, fallback, response repairs, or retrieval. The existing harness scores benchmark results in `benchmark_v1/scored/` and compares them with the pinned lexical baseline. Request journals retain results and usage before final scoring, so interruption during final report writing cannot cause repeated inference.

Dry-run planning: 3 historical requests, 32 pending benchmark examples, 35 planned combined requests; $0.099182 remaining allowance; $0.0476788 projected cumulative cost. These estimates are not a provider-enforced billing cap. Do not infer benchmark quality from the three synthetic preflight fixtures.
