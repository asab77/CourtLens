# Reviewed Fixed-Chunking Evaluation

This report rescored the unchanged saved Top-5 rankings against the human-reviewed page ranges. No retrieval, embedding, or index operation was run.

## Old vs. reviewed metrics

| Configuration | Old Hit@1 | New Hit@1 | Old Hit@3 | New Hit@3 | Old Hit@5 | New Hit@5 | Old MRR | New MRR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 600/100 | 0.350 | 0.650 | 0.625 | 0.900 | 0.725 | 0.925 | 0.495 | 0.777 |
| 900/150 | 0.475 | 0.725 | 0.625 | 0.900 | 0.650 | 0.900 | 0.544 | 0.808 |
| 1200/200 | 0.425 | 0.675 | 0.600 | 0.850 | 0.700 | 0.900 | 0.525 | 0.765 |
| 1500/200 | 0.500 | 0.700 | 0.625 | 0.800 | 0.775 | 0.900 | 0.583 | 0.764 |

The content review expanded relevance for **22 of 40 questions**. It converted **31 configuration-question misses** across **13 distinct questions** into Top-5 hits. Metrics changed only because saved passages now intersect additional human-reviewed answer-bearing ranges.

Ordering by MRR is: 900/150, 600/100, 1200/200, 1500/200. Among the tested configurations on the reviewed 40-question CourtLens benchmark, **900/150** has the highest MRR. This is evidence for this benchmark, not a universal optimum.

## Breakdown by question type

Many types contain very few questions, so these results are exploratory.

| Question type | Configuration | N | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| constitutional_principle | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| constitutional_principle | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| constitutional_principle | 1200/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| constitutional_principle | 1500/200 | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| dissent_reasoning | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| dissent_reasoning | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| dissent_reasoning | 1200/200 | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| dissent_reasoning | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| facts | 600/100 | 8 | 0.500 | 0.750 | 0.875 | 0.656 |
| facts | 900/150 | 8 | 0.500 | 0.750 | 0.750 | 0.604 |
| facts | 1200/200 | 8 | 0.500 | 0.750 | 0.750 | 0.604 |
| facts | 1500/200 | 8 | 0.500 | 0.625 | 0.750 | 0.567 |
| holding | 600/100 | 7 | 0.571 | 1.000 | 1.000 | 0.786 |
| holding | 900/150 | 7 | 0.571 | 1.000 | 1.000 | 0.786 |
| holding | 1200/200 | 7 | 0.857 | 1.000 | 1.000 | 0.929 |
| holding | 1500/200 | 7 | 0.857 | 1.000 | 1.000 | 0.905 |
| holding_detail | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| holding_detail | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| holding_detail | 1200/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| holding_detail | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| jurisdiction | 600/100 | 1 | 0.000 | 1.000 | 1.000 | 0.333 |
| jurisdiction | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| jurisdiction | 1200/200 | 1 | 0.000 | 0.000 | 0.000 | 0.000 |
| jurisdiction | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| legal_principle | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| legal_principle | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| legal_principle | 1200/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| legal_principle | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| legal_rule | 600/100 | 3 | 0.667 | 0.667 | 0.667 | 0.667 |
| legal_rule | 900/150 | 3 | 0.667 | 0.667 | 0.667 | 0.667 |
| legal_rule | 1200/200 | 3 | 0.333 | 0.667 | 0.667 | 0.444 |
| legal_rule | 1500/200 | 3 | 0.333 | 0.333 | 0.667 | 0.417 |
| precedent | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| precedent | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| precedent | 1200/200 | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| precedent | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| reasoning | 600/100 | 8 | 0.875 | 1.000 | 1.000 | 0.938 |
| reasoning | 900/150 | 8 | 0.875 | 1.000 | 1.000 | 0.938 |
| reasoning | 1200/200 | 8 | 1.000 | 1.000 | 1.000 | 1.000 |
| reasoning | 1500/200 | 8 | 0.750 | 0.875 | 1.000 | 0.844 |
| remedy | 600/100 | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| remedy | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| remedy | 1200/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| remedy | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| specific_detail | 600/100 | 6 | 0.500 | 0.833 | 0.833 | 0.667 |
| specific_detail | 900/150 | 6 | 0.667 | 0.833 | 0.833 | 0.750 |
| specific_detail | 1200/200 | 6 | 0.667 | 0.833 | 1.000 | 0.783 |
| specific_detail | 1500/200 | 6 | 0.667 | 0.667 | 0.833 | 0.700 |
| specific_fact | 600/100 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| specific_fact | 900/150 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| specific_fact | 1200/200 | 1 | 0.000 | 0.000 | 1.000 | 0.250 |
| specific_fact | 1500/200 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |

## Breakdown by case

Each case contributes five questions. Differences may reflect question wording, opinion structure, extraction quality, or retrieval behavior; this table cannot isolate causation.

| Case | Configuration | N | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Dred Scott v. Sandford | 600/100 | 5 | 0.400 | 0.800 | 0.800 | 0.600 |
| Dred Scott v. Sandford | 900/150 | 5 | 0.400 | 0.800 | 0.800 | 0.567 |
| Dred Scott v. Sandford | 1200/200 | 5 | 0.400 | 0.800 | 0.800 | 0.567 |
| Dred Scott v. Sandford | 1500/200 | 5 | 0.400 | 0.600 | 0.800 | 0.507 |
| Gideon v. Wainwright | 600/100 | 5 | 0.600 | 0.800 | 0.800 | 0.700 |
| Gideon v. Wainwright | 900/150 | 5 | 0.400 | 0.800 | 0.800 | 0.600 |
| Gideon v. Wainwright | 1200/200 | 5 | 0.600 | 0.800 | 1.000 | 0.740 |
| Gideon v. Wainwright | 1500/200 | 5 | 0.600 | 0.600 | 0.800 | 0.650 |
| Marbury v. Madison | 600/100 | 5 | 0.600 | 1.000 | 1.000 | 0.767 |
| Marbury v. Madison | 900/150 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Marbury v. Madison | 1200/200 | 5 | 0.800 | 0.800 | 0.800 | 0.800 |
| Marbury v. Madison | 1500/200 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Miranda v. Arizona | 600/100 | 5 | 0.800 | 1.000 | 1.000 | 0.900 |
| Miranda v. Arizona | 900/150 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Miranda v. Arizona | 1200/200 | 5 | 0.600 | 1.000 | 1.000 | 0.767 |
| Miranda v. Arizona | 1500/200 | 5 | 0.600 | 0.800 | 1.000 | 0.717 |
| New York Times Co. v. United States | 600/100 | 5 | 0.800 | 0.800 | 1.000 | 0.850 |
| New York Times Co. v. United States | 900/150 | 5 | 0.800 | 0.800 | 0.800 | 0.800 |
| New York Times Co. v. United States | 1200/200 | 5 | 0.800 | 0.800 | 0.800 | 0.800 |
| New York Times Co. v. United States | 1500/200 | 5 | 0.600 | 0.800 | 0.800 | 0.700 |
| Obergefell v. Hodges | 600/100 | 5 | 0.600 | 0.800 | 0.800 | 0.700 |
| Obergefell v. Hodges | 900/150 | 5 | 0.600 | 0.800 | 0.800 | 0.700 |
| Obergefell v. Hodges | 1200/200 | 5 | 0.600 | 0.600 | 0.800 | 0.650 |
| Obergefell v. Hodges | 1500/200 | 5 | 0.600 | 0.800 | 0.800 | 0.700 |
| Plessy v. Ferguson | 600/100 | 5 | 0.400 | 1.000 | 1.000 | 0.700 |
| Plessy v. Ferguson | 900/150 | 5 | 0.600 | 1.000 | 1.000 | 0.800 |
| Plessy v. Ferguson | 1200/200 | 5 | 0.600 | 1.000 | 1.000 | 0.800 |
| Plessy v. Ferguson | 1500/200 | 5 | 0.800 | 0.800 | 1.000 | 0.840 |
| Tinker v. Des Moines School Dist. | 600/100 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Tinker v. Des Moines School Dist. | 900/150 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Tinker v. Des Moines School Dist. | 1200/200 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Tinker v. Des Moines School Dist. | 1500/200 | 5 | 1.000 | 1.000 | 1.000 | 1.000 |

## Best first-relevant ranks

A sole win means one configuration had the best first relevant rank for that question. Equal ranks are ties; an all-configuration miss is kept separate.

| Configuration | Sole best-rank questions |
|---|---:|
| 600/100 | 2 |
| 900/150 | 0 |
| 1200/200 | 2 |
| 1500/200 | 1 |

Ties for best rank: **33**. All four configurations still miss Top-5 for **2** questions: DRE-04, OBE-01.

## Interpretation and limitations

The type and case tables show that the best observed configuration varies across subsets, but most type groups are tiny and every case has only five questions. These descriptive differences can motivate later investigation of structure and multi-granularity retrieval; they do not establish that a type or document requires a particular chunk size.

The review packet contains only passages retrieved in the saved Top-5 by at least one configuration. The reviewed ranges can correct false negatives visible in that pool, but they are not an exhaustive map of every answer-bearing page. Page intersection also gives full credit to a chunk that merely overlaps a labeled page, and the 40-question benchmark is too small for strong subgroup claims.

No era split was added. Choosing a historical/modern boundary would add an arbitrary assumption without strengthening this local rescoring analysis.
