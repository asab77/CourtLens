# CourtLens Phase 5B — reciprocal rank fusion

Rank-only RRF: `RRF(d)=Σ 1/(60+rank_i(d))`, with one-based ranks. Dense depth=5; BM25 depth=5. An absent candidate contributes zero. Duplicate cross-list identities are merged; duplicates within a list are rejected. Ties use original corpus order. Raw scores and metadata are diagnostic only.

Saved dense rankings contain exactly five results per question. BM25 saved Top-20 is validated but only Top-5 enters fusion. No dense or BM25 retrieval is rerun by this experiment. Official Hit@K and MRR use the fused Top-5 and the existing unchanged evaluator.

## Six configurations

| Collection | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| fixed_900_150 | dense | 0.750 | 0.900 | 0.900 | 0.825000 |
| fixed_900_150 | bm25 | 0.725 | 0.875 | 0.950 | 0.805000 |
| fixed_900_150 | hybrid | 0.700 | 0.950 | 0.975 | 0.822917 |
| structure_aware_v1 | dense | 0.825 | 0.925 | 0.950 | 0.877083 |
| structure_aware_v1 | bm25 | 0.675 | 0.875 | 0.925 | 0.782083 |
| structure_aware_v1 | hybrid | 0.850 | 0.950 | 0.975 | 0.900833 |

## fixed_900_150 — coverage and changes

Union sizes (unique chunks: number of questions): {5: 2, 6: 2, 7: 10, 8: 12, 9: 10, 10: 4}. Candidate union coverage: 40/40 (1.000). Final hybrid Hit@5: 39/40 (0.975). Union coverage is an availability ceiling, not achieved hybrid performance.

| Hybrid minus | ΔHit@1 | ΔHit@3 | ΔHit@5 | ΔMRR |
|---|---:|---:|---:|---:|
| dense | -0.050000 | +0.050000 | +0.075000 | -0.002083 |
| bm25 | -0.025000 | +0.075000 | +0.025000 | +0.017917 |

First relevant rank comparisons (miss treated as infinity): {'dense': {'tie': 24, 'worsened': 8, 'improved': 7, 'shared_miss': 1}, 'bm25': {'tie': 27, 'improved': 6, 'worsened': 7}}.

- rescues_dense_miss: 3 — DRE-04, GID-05, NYT-01
- rescues_bm25_miss: 2 — MAR-05, MIR-02
- rescues_shared_miss: 0 — None
- loses_dense_hit: 0 — None
- loses_bm25_hit: 1 — OBE-01
- all_relevant_candidates_fall_below_top5: 1 — OBE-01
- dense_only_hits_recovered: 2 — MAR-05, MIR-02
- bm25_only_hits_recovered: 3 — DRE-04, GID-05, NYT-01
- hybrid_top5_misses: 1 — OBE-01

### Targeted questions

| Question | Dense rank | BM25 rank | Hybrid rank | Rescues dense / BM25 miss | Relevant ranks below 5 |
|---|---:|---:|---:|---|---|
| MAR-05 | 1 | miss | 2 | False / True | [] |
| DRE-04 | miss | 2 | 3 | True / False | [] |
| GID-05 | miss | 1 | 1 | True / False | [] |
| MIR-02 | 1 | miss | 2 | False / True | [] |
| NYT-01 | miss | 1 | 2 | True / False | [] |
| OBE-01 | miss | 4 | miss | False / False | [7] |

**MAR-05:** Why did the Court conclude that courts must follow the Constitution rather than an ordinary legislative act when the two conflict?

hybrid 1: corpus ordinal 569, dense 4, BM25 1, RRF 0.032018443, benchmark relevant False; hybrid 2: corpus ordinal 301, dense 1, BM25 None, RRF 0.016393443, benchmark relevant True; hybrid 3: corpus ordinal 216, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 4: corpus ordinal 300, dense 2, BM25 None, RRF 0.016129032, benchmark relevant True; hybrid 5: corpus ordinal 303, dense 3, BM25 None, RRF 0.015873016, benchmark relevant True; hybrid 6: corpus ordinal 453, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 485, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 248, dense None, BM25 5, RRF 0.015384615, benchmark relevant False; hybrid 9: corpus ordinal 504, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


**DRE-04:** Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

hybrid 1: corpus ordinal 146, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 2: corpus ordinal 502, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 4, dense None, BM25 2, RRF 0.016129032, benchmark relevant True; hybrid 4: corpus ordinal 230, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 74, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 143, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 127, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 569, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 56, dense None, BM25 5, RRF 0.015384615, benchmark relevant False; hybrid 10: corpus ordinal 237, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


**GID-05:** What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

hybrid 1: corpus ordinal 252, dense None, BM25 1, RRF 0.016393443, benchmark relevant True; hybrid 2: corpus ordinal 340, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 341, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 4: corpus ordinal 383, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 336, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 399, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 339, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 349, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 246, dense None, BM25 5, RRF 0.015384615, benchmark relevant False; hybrid 10: corpus ordinal 338, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


**MIR-02:** Why did the Supreme Court find Miranda's statements inadmissible?

hybrid 1: corpus ordinal 383, dense 2, BM25 3, RRF 0.032002048, benchmark relevant False; hybrid 2: corpus ordinal 357, dense 1, BM25 None, RRF 0.016393443, benchmark relevant True; hybrid 3: corpus ordinal 400, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 4: corpus ordinal 325, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 304, dense 3, BM25 None, RRF 0.015873016, benchmark relevant True; hybrid 6: corpus ordinal 348, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 7: corpus ordinal 360, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 308, dense None, BM25 5, RRF 0.015384615, benchmark relevant False; hybrid 9: corpus ordinal 394, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


**NYT-01:** What classified material was the United States trying to prevent the New York Times and Washington Post from publishing?

hybrid 1: corpus ordinal 437, dense 4, BM25 5, RRF 0.031009615, benchmark relevant False; hybrid 2: corpus ordinal 410, dense None, BM25 1, RRF 0.016393443, benchmark relevant True; hybrid 3: corpus ordinal 435, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 4: corpus ordinal 427, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 449, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 6: corpus ordinal 425, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 433, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 8: corpus ordinal 416, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 441, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


**OBE-01:** What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

hybrid 1: corpus ordinal 488, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 2: corpus ordinal 543, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 500, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 4: corpus ordinal 518, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 470, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 484, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 464, dense None, BM25 4, RRF 0.015625000, benchmark relevant True; hybrid 8: corpus ordinal 546, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 452, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False; hybrid 10: corpus ordinal 453, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


### by_question_type

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | bm25 | 0.000 | 0.000 | 1.000 | 0.250000 |
| dissent_reasoning | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| facts | 8 | dense | 0.625 | 0.750 | 0.750 | 0.687500 |
| facts | 8 | bm25 | 0.750 | 0.875 | 1.000 | 0.822917 |
| facts | 8 | hybrid | 0.625 | 0.750 | 0.875 | 0.718750 |
| holding | 7 | dense | 0.571 | 1.000 | 1.000 | 0.785714 |
| holding | 7 | bm25 | 0.714 | 0.857 | 0.857 | 0.761905 |
| holding | 7 | hybrid | 0.429 | 1.000 | 1.000 | 0.690476 |
| holding_detail | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.333333 |
| jurisdiction | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_principle | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_rule | 3 | dense | 0.667 | 0.667 | 0.667 | 0.666667 |
| legal_rule | 3 | bm25 | 0.667 | 1.000 | 1.000 | 0.833333 |
| legal_rule | 3 | hybrid | 0.333 | 1.000 | 1.000 | 0.611111 |
| precedent | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| reasoning | 8 | dense | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | bm25 | 0.625 | 0.750 | 0.875 | 0.712500 |
| reasoning | 8 | hybrid | 0.875 | 1.000 | 1.000 | 0.937500 |
| remedy | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | dense | 0.667 | 0.833 | 0.833 | 0.750000 |
| specific_detail | 6 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |

### by_case

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Dred Scott v. Sandford | 5 | bm25 | 0.400 | 0.800 | 1.000 | 0.606667 |
| Dred Scott v. Sandford | 5 | hybrid | 0.600 | 0.800 | 1.000 | 0.716667 |
| Gideon v. Wainwright | 5 | dense | 0.400 | 0.800 | 0.800 | 0.600000 |
| Gideon v. Wainwright | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| Gideon v. Wainwright | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| Marbury v. Madison | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Marbury v. Madison | 5 | bm25 | 0.600 | 0.800 | 0.800 | 0.666667 |
| Marbury v. Madison | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Miranda v. Arizona | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Miranda v. Arizona | 5 | bm25 | 0.800 | 0.800 | 0.800 | 0.800000 |
| Miranda v. Arizona | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| New York Times Co. v. United States | 5 | dense | 0.800 | 0.800 | 0.800 | 0.800000 |
| New York Times Co. v. United States | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| New York Times Co. v. United States | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| Obergefell v. Hodges | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Obergefell v. Hodges | 5 | bm25 | 0.600 | 0.800 | 1.000 | 0.716667 |
| Obergefell v. Hodges | 5 | hybrid | 0.600 | 0.800 | 0.800 | 0.666667 |
| Plessy v. Ferguson | 5 | dense | 0.600 | 1.000 | 1.000 | 0.800000 |
| Plessy v. Ferguson | 5 | bm25 | 0.600 | 0.800 | 1.000 | 0.750000 |
| Plessy v. Ferguson | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | bm25 | 0.800 | 1.000 | 1.000 | 0.900000 |
| Tinker v. Des Moines School Dist. | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |

## structure_aware_v1 — coverage and changes

Union sizes (unique chunks: number of questions): {5: 1, 6: 8, 7: 16, 8: 8, 9: 5, 10: 2}. Candidate union coverage: 39/40 (0.975). Final hybrid Hit@5: 39/40 (0.975). Union coverage is an availability ceiling, not achieved hybrid performance.

| Hybrid minus | ΔHit@1 | ΔHit@3 | ΔHit@5 | ΔMRR |
|---|---:|---:|---:|---:|
| dense | +0.025000 | +0.025000 | +0.025000 | +0.023750 |
| bm25 | +0.175000 | +0.075000 | +0.050000 | +0.118750 |

First relevant rank comparisons (miss treated as infinity): {'dense': {'tie': 33, 'worsened': 3, 'improved': 3, 'shared_miss': 1}, 'bm25': {'tie': 30, 'improved': 9, 'shared_miss': 1}}.

- rescues_dense_miss: 1 — DRE-04
- rescues_bm25_miss: 2 — MAR-05, MIR-02
- rescues_shared_miss: 0 — None
- loses_dense_hit: 0 — None
- loses_bm25_hit: 0 — None
- all_relevant_candidates_fall_below_top5: 0 — None
- dense_only_hits_recovered: 2 — MAR-05, MIR-02
- bm25_only_hits_recovered: 1 — DRE-04
- hybrid_top5_misses: 1 — OBE-01

### Targeted questions

| Question | Dense rank | BM25 rank | Hybrid rank | Rescues dense / BM25 miss | Relevant ranks below 5 |
|---|---:|---:|---:|---|---|
| MAR-05 | 1 | miss | 1 | False / True | [6, 9] |
| DRE-04 | miss | 1 | 1 | True / False | [] |
| GID-05 | 2 | 1 | 1 | False / False | [] |
| MIR-02 | 1 | miss | 3 | False / True | [8] |
| NYT-01 | 3 | 1 | 1 | False / False | [] |
| OBE-01 | miss | miss | miss | False / False | [] |

**MAR-05:** Why did the Court conclude that courts must follow the Constitution rather than an ordinary legislative act when the two conflict?

hybrid 1: corpus ordinal 229, dense 1, BM25 None, RRF 0.016393443, benchmark relevant True; hybrid 2: corpus ordinal 410, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 131, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 4: corpus ordinal 366, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 40, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 228, dense 3, BM25 None, RRF 0.015873016, benchmark relevant True; hybrid 7: corpus ordinal 164, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 373, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 230, dense 5, BM25 None, RRF 0.015384615, benchmark relevant True; hybrid 10: corpus ordinal 428, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


**DRE-04:** Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

hybrid 1: corpus ordinal 2, dense None, BM25 1, RRF 0.016393443, benchmark relevant True; hybrid 2: corpus ordinal 95, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 74, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 4: corpus ordinal 365, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 40, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 111, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 101, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 104, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 89, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False; hybrid 10: corpus ordinal 109, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


**GID-05:** What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

hybrid 1: corpus ordinal 192, dense 3, BM25 1, RRF 0.032266458, benchmark relevant True; hybrid 2: corpus ordinal 193, dense 2, BM25 2, RRF 0.032258065, benchmark relevant True; hybrid 3: corpus ordinal 253, dense 5, BM25 3, RRF 0.031257631, benchmark relevant False; hybrid 4: corpus ordinal 254, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 5: corpus ordinal 188, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 6: corpus ordinal 252, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 7: corpus ordinal 282, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


**MIR-02:** Why did the Supreme Court find Miranda's statements inadmissible?

hybrid 1: corpus ordinal 245, dense 2, BM25 2, RRF 0.032258065, benchmark relevant False; hybrid 2: corpus ordinal 235, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 266, dense 1, BM25 None, RRF 0.016393443, benchmark relevant True; hybrid 4: corpus ordinal 286, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 5: corpus ordinal 289, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 257, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 7: corpus ordinal 282, dense 4, BM25 None, RRF 0.015625000, benchmark relevant False; hybrid 8: corpus ordinal 232, dense 5, BM25 None, RRF 0.015384615, benchmark relevant True; hybrid 9: corpus ordinal 267, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


**NYT-01:** What classified material was the United States trying to prevent the New York Times and Washington Post from publishing?

hybrid 1: corpus ordinal 301, dense 3, BM25 1, RRF 0.032266458, benchmark relevant True; hybrid 2: corpus ordinal 300, dense 4, BM25 2, RRF 0.031754032, benchmark relevant True; hybrid 3: corpus ordinal 313, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 4: corpus ordinal 314, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 329, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 6: corpus ordinal 305, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 7: corpus ordinal 299, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False; hybrid 8: corpus ordinal 312, dense None, BM25 5, RRF 0.015384615, benchmark relevant False


**OBE-01:** What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

hybrid 1: corpus ordinal 332, dense 4, BM25 5, RRF 0.031009615, benchmark relevant False; hybrid 2: corpus ordinal 345, dense 1, BM25 None, RRF 0.016393443, benchmark relevant False; hybrid 3: corpus ordinal 347, dense None, BM25 1, RRF 0.016393443, benchmark relevant False; hybrid 4: corpus ordinal 355, dense 2, BM25 None, RRF 0.016129032, benchmark relevant False; hybrid 5: corpus ordinal 374, dense None, BM25 2, RRF 0.016129032, benchmark relevant False; hybrid 6: corpus ordinal 354, dense 3, BM25 None, RRF 0.015873016, benchmark relevant False; hybrid 7: corpus ordinal 379, dense None, BM25 3, RRF 0.015873016, benchmark relevant False; hybrid 8: corpus ordinal 391, dense None, BM25 4, RRF 0.015625000, benchmark relevant False; hybrid 9: corpus ordinal 360, dense 5, BM25 None, RRF 0.015384615, benchmark relevant False


### by_question_type

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.333333 |
| dissent_reasoning | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| facts | 8 | dense | 0.750 | 0.875 | 0.875 | 0.791667 |
| facts | 8 | bm25 | 0.500 | 0.875 | 0.875 | 0.687500 |
| facts | 8 | hybrid | 0.875 | 0.875 | 0.875 | 0.875000 |
| holding | 7 | dense | 0.857 | 1.000 | 1.000 | 0.928571 |
| holding | 7 | bm25 | 0.571 | 0.857 | 0.857 | 0.714286 |
| holding | 7 | hybrid | 0.714 | 1.000 | 1.000 | 0.833333 |
| holding_detail | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | dense | 0.000 | 0.000 | 1.000 | 0.250000 |
| jurisdiction | 1 | bm25 | 0.000 | 0.000 | 1.000 | 0.200000 |
| jurisdiction | 1 | hybrid | 0.000 | 0.000 | 1.000 | 0.200000 |
| legal_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_rule | 3 | dense | 0.667 | 0.667 | 0.667 | 0.666667 |
| legal_rule | 3 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_rule | 3 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.500000 |
| precedent | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| reasoning | 8 | dense | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | bm25 | 0.625 | 0.750 | 0.875 | 0.718750 |
| reasoning | 8 | hybrid | 0.875 | 1.000 | 1.000 | 0.937500 |
| remedy | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | dense | 0.833 | 1.000 | 1.000 | 0.916667 |
| specific_detail | 6 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |

### by_case

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Dred Scott v. Sandford | 5 | bm25 | 0.400 | 0.800 | 1.000 | 0.650000 |
| Dred Scott v. Sandford | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| Gideon v. Wainwright | 5 | dense | 0.600 | 1.000 | 1.000 | 0.800000 |
| Gideon v. Wainwright | 5 | bm25 | 0.600 | 1.000 | 1.000 | 0.800000 |
| Gideon v. Wainwright | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Marbury v. Madison | 5 | dense | 0.800 | 0.800 | 1.000 | 0.850000 |
| Marbury v. Madison | 5 | bm25 | 0.600 | 0.600 | 0.800 | 0.640000 |
| Marbury v. Madison | 5 | hybrid | 0.800 | 0.800 | 1.000 | 0.840000 |
| Miranda v. Arizona | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Miranda v. Arizona | 5 | bm25 | 0.800 | 0.800 | 0.800 | 0.800000 |
| Miranda v. Arizona | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.866667 |
| New York Times Co. v. United States | 5 | dense | 0.800 | 1.000 | 1.000 | 0.866667 |
| New York Times Co. v. United States | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| New York Times Co. v. United States | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Obergefell v. Hodges | 5 | dense | 0.800 | 0.800 | 0.800 | 0.800000 |
| Obergefell v. Hodges | 5 | bm25 | 0.600 | 0.800 | 0.800 | 0.700000 |
| Obergefell v. Hodges | 5 | hybrid | 0.800 | 0.800 | 0.800 | 0.800000 |
| Plessy v. Ferguson | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Plessy v. Ferguson | 5 | bm25 | 0.600 | 1.000 | 1.000 | 0.766667 |
| Plessy v. Ferguson | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | bm25 | 0.800 | 1.000 | 1.000 | 0.900000 |
| Tinker v. Des Moines School Dist. | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |

## Identity verification and reproducibility

Each corpus uses its own namespace plus source_file + original chunk_index. Structure-aware chunk IDs are also verified exactly. Dense vector_id is verified against saved vector-store records, which are matched by complete text/metadata to frozen chunks. BM25 corpus_index and chunk_reference are verified. Page overlap never defines identity. Corpus counts are 598 and 433; all 40 questions follow benchmark order.

The complete deduplicated union, including relevance decisions below rank five, is saved separately from official Top-5 metrics. Reproduce with `.venv/bin/python run_hybrid_experiment.py`. Conflicting output files are rejected; identical replay is a no-op. Manifests record input/source hashes and fixed parameters.

All 115 pre-existing data files are SHA-256 identical. Full before/after hashes are in the analysis JSON. No API, embedding, index rebuild, label change, commit, or push.

## Limitations

- Benchmark v2 was refined using evaluated dense candidates; it is not an independent holdout.
- Case/source/page-overlap relevance is a coarse proxy and can produce false positives and negatives.
- Only saved dense Top-5 and BM25 Top-5 are fused. The union has at most ten unique chunks; relevant union candidates can fall below hybrid rank five. Deeper fusion is a future experiment.
- Chunk-size distributions differ; structure-aware excludes 200 tokenizer tokens of foreign Sturgis/Honold material retained in fixed chunks.
- RRF k=60 and both candidate depths=5 were fixed before evaluation and never tuned. Raw scores, labels, and opinion/case metadata do not affect fusion.
- Findings and small subgroup comparisons are descriptive; no statistical significance, general superiority, or routing rule is implied.

READY for Phase 6 as an evaluation baseline, not a claim that RRF improves every metric. Phase 6 has not started; no reranking, query expansion, or routing is implemented.
