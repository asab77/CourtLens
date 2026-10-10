# CourtLens Phase 4C.2 — Benchmark v2 finalization

Benchmark v2 applies exactly seven human-approved additions to five questions. The other 35 question records are byte-identical, including their literal JSON object spans. The original benchmark, audit, rankings, chunks, vector stores, and reports remain unchanged.

Inherited benchmark metadata describes the v1 review and is preserved; version_metadata separately records v2 approval and provenance.

Evaluation date: 2026-10-09 (America/New_York). Method: CourtLens Phase 4C.2 saved-top5 page-overlap evaluator v1. Forty questions per strategy; saved Top-5 only. Existing score_retrieved and aggregate functions are reused without changes.

## Approved additions and traceability

| Question | Added PDF range | Human-approved justification |
|---|---|---|
| DRE-01 | [39, 40] | Majority restatement of Scott’s Illinois/Fort Snelling residence. |
| DRE-01 | [167, 167] | McLean’s factual account of Scott’s Illinois/Fort Snelling residence. |
| MIR-04 | [9, 10] | Warren majority explicitly enumerates custodial interrogation safeguards. |
| MAR-01 | [32, 32] | Commission withholding and legal entitlement. |
| MAR-01 | [36, 36] | Requested mandamus delivery remedy and vested commission right. |
| DRE-03 | [33, 34] | Majority’s constitutional and founding-era citizenship reasoning. |
| OBE-04 | [64, 64] | Roberts dissent explicitly quotes and attributes the majority’s Due Process / Equal Protection reasoning. |

Audit reference: `data/evaluation/chunking_benchmark_phase4c_audit.json`. MIR-04 page 67 remains unapproved/deferred. All 12 ambiguous audit judgments remain unresolved and untouched. DRE-04 and OBE-01 receive no new ranges. Mechanical page-overlap relevance flags are not new manual passage judgments.

## Five-strategy comparison

| Strategy | Chunks | v1 H@1 | v2 H@1 | v1 H@3 | v2 H@3 | v1 H@5 | v2 H@5 | v1 MRR | v2 MRR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600_100 | 1163 | 0.650000 | 0.675000 | 0.900000 | 0.900000 | 0.925000 | 0.925000 | 0.777083 | 0.789583 |
| 900_150 | 598 | 0.725000 | 0.750000 | 0.900000 | 0.900000 | 0.900000 | 0.900000 | 0.808333 | 0.825000 |
| 1200_200 | 447 | 0.675000 | 0.700000 | 0.850000 | 0.850000 | 0.900000 | 0.900000 | 0.765417 | 0.782083 |
| 1500_200 | 287 | 0.700000 | 0.750000 | 0.800000 | 0.825000 | 0.900000 | 0.900000 | 0.764167 | 0.796667 |
| structure_aware_v1 | 433 | 0.725000 | 0.825000 | 0.875000 | 0.925000 | 0.900000 | 0.950000 | 0.802083 | 0.877083 |

Absolute differences below are v2 − v1, not relative percentages.

| Strategy | Δ Hit@1 | Δ Hit@3 | Δ Hit@5 | Δ MRR | Improved questions | Added rank-1 successes | Miss → Top-5 hit |
|---|---:|---:|---:|---:|---:|---:|---:|
| 600_100 | +0.025000 | +0.000000 | +0.000000 | +0.012500 | 1 | 1 | 0 |
| 900_150 | +0.025000 | +0.000000 | +0.000000 | +0.016667 | 1 | 1 | 0 |
| 1200_200 | +0.025000 | +0.000000 | +0.000000 | +0.016667 | 1 | 1 | 0 |
| 1500_200 | +0.050000 | +0.025000 | +0.000000 | +0.032500 | 2 | 2 | 0 |
| structure_aware_v1 | +0.100000 | +0.050000 | +0.050000 | +0.075000 | 4 | 4 | 2 |

## Per-question improvements and remaining misses

### 600_100

| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |
|---|---:|---:|---|---|
| MAR-01 | 1 | 1 | unchanged | r4; pp32–33; chunk 61 |
| DRE-01 | 2 | 1 | improved rank | r1; pp167–167; chunk 489; r5; pp39–39; chunk 108 |
| OBE-04 | 1 | 1 | unchanged | r3; pp64–65; chunk 90; r4; pp63–64; chunk 89 |

Remaining Top-5 misses: DRE-04, GID-05, OBE-01.

All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.

### 900_150

| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |
|---|---:|---:|---|---|
| MAR-01 | 1 | 1 | unchanged | r3; pp32–33; chunk 32 |
| DRE-01 | 3 | 1 | improved rank | r1; pp167–168; chunk 169 |
| OBE-04 | 1 | 1 | unchanged | r2; pp64–65; chunk 62; r3; pp63–64; chunk 61 |

Remaining Top-5 misses: DRE-04, GID-05, NYT-01, OBE-01.

All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.

### 1200_200

| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |
|---|---:|---:|---|---|
| MAR-01 | 1 | 1 | unchanged | r2; pp31–33; chunk 23 |
| DRE-01 | 3 | 1 | improved rank | r1; pp167–168; chunk 165 |
| OBE-04 | 1 | 1 | unchanged | r4; pp62–64; chunk 38 |

Remaining Top-5 misses: MAR-04, DRE-04, NYT-01, OBE-01.

All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.

### 1500_200

| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |
|---|---:|---:|---|---|
| MAR-01 | 1 | 1 | unchanged | r3; pp32–34; chunk 16 |
| DRE-01 | 5 | 1 | improved rank | r1; pp166–168; chunk 84 |
| OBE-04 | 2 | 1 | improved rank | r1; pp63–65; chunk 32 |

Remaining Top-5 misses: DRE-04, GID-05, NYT-01, OBE-01.

All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.

### structure_aware_v1

| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |
|---|---:|---:|---|---|
| MAR-01 | 2 | 1 | improved rank | r1; pp31–33; chunk 23 |
| DRE-01 | miss | 1 | miss → hit | r1; pp166–167; chunk 127; r2; pp38–40; chunk 29 |
| DRE-03 | 2 | 2 | unchanged | r5; pp33–34; chunk 25 |
| MIR-04 | miss | 1 | miss → hit | r1; pp9–10; chunk 6; r5; pp10–11; chunk 7 |
| OBE-04 | 2 | 1 | improved rank | r1; pp63–65; chunk 41 |

Remaining Top-5 misses: DRE-04, OBE-01.

All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.

## Experimental limitations

- Benchmark v2 labels were refined after inspecting retrieval candidates from the evaluated systems.
- Benchmark v2 is NOT an independent holdout benchmark.
- Page-range intersection is a coarse relevance proxy that can generate both false negatives and false positives, including credit from trailing page markers or non-answer-bearing text on a labeled page.
- Structure-aware and fixed chunking differ in realized chunk-size distributions; nominal fixed sizes are not equivalent to the structure-aware distribution.
- Any apparent advantage is descriptive performance on this benchmark, not proof of general superiority.
- No statistical significance claim is made.

## Reproducibility and protected artifacts

Local reproduction: `.venv/bin/python finalize_benchmark_v2.py --evaluation-date 2026-10-09`. No API credentials, network, embeddings, or FAISS retrieval required. Existing versioned outputs are only accepted if identical; conflicting outputs are not overwritten.

| Artifact | SHA-256 |
|---|---|
| Benchmark v1 | `7cbfa42bf480717df7b7982297f8ea648a30a8d100d86ccdcaa5371b410b7595` |
| Benchmark v2 | `aec09e3d75f9f18aec5b2448e7f420c0443bf9eb8a59e135f4a900f8a2ffd668` |
| Phase 4C audit | `495aeabbda165b8e9d3bb98df895ec1f513188be889d232688903a99bb90ecb5` |
| `data/experiments/chunking/reviewed_results.json` | `2e0d3d287b3e880dff3227939dbc796a75296986b9bbef9e86907e1d5c6e32ee` |
| `data/experiments/chunking/structure_aware_v1/results.json` | `8928b1e1ec80881acdd7a4664c57661e1aa9df847691996db6229057acc081aa` |

All 103 pre-existing data artifacts were verified byte-identical by SHA-256 before and after processing/writing. This includes all five strategies’ saved rankings, fixed and structure-aware chunks/stores, production store, original/reviewed benchmarks, Phase 4C audit, and existing analysis reports. Full before/after hashes are in the analysis JSON.

**READY for Phase 5A** on benchmark/versioning and local reproducibility checks, with the stated methodological limitations. Phase 5A has not been started.
