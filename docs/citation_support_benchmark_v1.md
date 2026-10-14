# Citation Support Benchmark v1 — finalized adjudication

**Frozen after local integrity validation. Review method: AI-assisted, user-authorized. No independent human legal-expert adjudication.**

Original candidates, review and labeling guidelines remain unchanged historical records. This document records the finalized convention and rubric application; it does not retroactively describe prior proposals as approved expert labels.

## Claims

32 claims: SUPPORTED 10; PARTIALLY_SUPPORTED 7; UNSUPPORTED 7; CONTRADICTED 8. Only CS-012 and CS-031 labels changed, both to CONTRADICTED under explicit user instructions. Other 30 labels are retained.

## Compound convention

- All material components supported: SUPPORTED.
- Meaningful supported component plus unsupported or contradicted component: PARTIALLY_SUPPORTED.
- Central assertion directly incompatible, without an independently meaningful supported component: CONTRADICTED.
- No meaningful supported component and no affirmative contradiction: UNSUPPORTED.

Component outcomes are recorded independently and are never hidden by the aggregate label. CS-017 and CS-018 have CONTRADICTED second components but supported first components; their overall PARTIALLY_SUPPORTED labels remain. CS-011, CS-014 and CS-016 have SUPPORTED first and UNSUPPORTED second components.

## Answer-level rubric

Completeness is context/task coverage, separate from factual support. The supplied Obergefell context establishes no Dobbs answer or material answer points against which completeness can be judged. Use the existing NOT_APPLICABLE value for this dimension; do not redefine INCOMPLETE as entirely unsupported or infer COMPLETE from surface responsiveness. Certainty remains OVERSTATED and citation coverage MISLEADING. This is AI-assisted rubric application under user-authorized finalization, not a separately documented human legal-expert approval.

No new enum/status is added. INCOMPLETE continues to mean omitted requested material points against an applicable evidence-grounded task, not merely unsupported content. NOT_APPLICABLE is used when that dimension cannot meaningfully be applied, including an out-of-corpus question with no established answer in its context. This is not a correctness credit. Exclude these examples from completeness scoring denominators, report applicable counts, and still evaluate other axes. No scoring is implemented here.

| ID | Completeness | Abstention | Certainty | Citation coverage |
|---|---|---|---|---|
| AR-001 | INCOMPLETE | NOT_APPLICABLE | OVERSTATED | INCOMPLETE |
| AR-002 | COMPLETE | NOT_APPLICABLE | OVERSTATED | INCOMPLETE |
| AR-003 | NOT_APPLICABLE | APPROPRIATE | JUSTIFIED | MISLEADING |
| AR-004 | NOT_APPLICABLE | APPROPRIATE | JUSTIFIED | NOT_APPLICABLE |
| AR-005 | NOT_APPLICABLE | UNWARRANTED | OVERSTATED | NOT_APPLICABLE |
| AR-006 | NOT_APPLICABLE | NOT_APPLICABLE | OVERSTATED | MISLEADING |

AR-001 through AR-005 are retained. AR-006 changes completeness only, from INCOMPLETE to NOT_APPLICABLE; its other three assessment values remain unchanged.

## Reproduction and validation

`finalize_citation_support_benchmark.py` reads the historical artifacts, validates exact corpus provenance, applies recorded decisions, validates before freezing, and reproduces the v1 files deterministically. Existing differing outputs are rejected. `load_frozen()` verifies checksum, canonical serialization, adjudication agreement, approved revisions, component consistency, and all unchanged source fields. No provider calls or semantic verifier are involved.

Benchmark: `data/evaluation/citation_support_benchmark_v1.json`
Adjudication: `data/evaluation/citation_support_adjudication_v1.json`
Checksum: `data/evaluation/citation_support_benchmark_v1.sha256`

SHA-256: `2519c6563bcd21ac651e90a0151a67cbd37d6e4d50e6681c061b78884e18cffa`

Source hashes and each complete original provenance object are retained. Final example review statuses are FINALIZED. Original proposed labels/assessments appear only as historical fields in the adjudication record, not as pending decisions. No fabricated or normalized source text is introduced.

## Limitations

- 32 claims and 6 answers: small curated challenge set, not deployment-representative.
- 30 of 32 claim examples are synthetic pairings/claims; original source passages remain authentic.
- Concentrated on Miranda and Obergefell, with three supplementary concurrence cases.
- Example selection was influenced by observed CourtLens failures.
- AI-assisted, user-authorized adjudication; no independent human legal-expert review.
- Not an independent generalization benchmark; no held-out split or leakage-resistant evaluation design.
- Success does not establish legal accuracy, claim completeness or deployment safety.
- OCR-derived attribution remains uncertain; original metadata and text are preserved.
- No semantic verifier, LLM judge, NLI model or generation/retrieval change is implemented.
