# CourtLens Phase 6A — local cross-encoder evidence reranking

Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`, immutable model/config/tokenizer revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`. Device `mps`; batch size 8; max paired sequence 512 tokens; `Identity` activation; `torch.float32`. Pretrained and unmodified; eval/inference mode; no gradients or fine-tuning. Framework versions and model-file hashes are in manifests and cross_encoder_environment.json.

Inference inputs are only the original question and original frozen passage. Complete saved hybrid unions are reranked separately. No dense, BM25, or RRF retrieval is performed. Score descending; original corpus order resolves ties. Existing Benchmark v2 Top-5 metrics and MRR are unchanged.

Truncation is tokenizer longest_first on the paired input, right side, to 512 INCLUDING special tokens. Query tokens normally survive because questions are shorter; token-level retained query/passage counts and passage end-character offsets are saved. No sentence/window selection or chunk-text editing occurs.

## Hybrid and cross-encoder comparison

| Collection | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| fixed_900_150 | hybrid | 0.700 | 0.950 | 0.975 | 0.822917 |
| fixed_900_150 | cross_encoder | 0.725 | 0.875 | 0.900 | 0.796667 |
| structure_aware_v1 | hybrid | 0.850 | 0.950 | 0.975 | 0.900833 |
| structure_aware_v1 | cross_encoder | 0.725 | 0.900 | 0.925 | 0.805000 |

## fixed_900_150

Absolute changes (reranked minus hybrid): {'hit_at_1': 0.025000000000000022, 'hit_at_3': -0.07499999999999996, 'hit_at_5': -0.07499999999999996, 'mrr': -0.026249999999999996}.

First-relevant-rank changes: {'improved': 5, 'worsened': 7, 'tie': 27, 'shared_miss': 1}. Rescued misses: []; lost hits: ['MAR-05', 'DRE-04', 'MIR-05'].

Analysis-only oracle: 40/40 questions have any label-relevant union candidate. Maximum possible Hit@1, Hit@3, Hit@5, and MRR each 1.000. This theoretical ceiling is not an achieved ranking and never influences actual scores.

Truncation: {'candidate_count': 318, 'truncated_count': 235, 'truncated_percentage': 73.8993710691824, 'passage_token_lengths': {'min': 404, 'max': 880, 'mean': 574.3899371069182, 'median': 531.0, 'p90_nearest_rank': 822}, 'full_pair_token_lengths': {'min': 421, 'max': 903, 'mean': 597.3427672955975, 'median': 550.5, 'p90_nearest_rank': 842}, 'query_truncated_count': 0, 'label_relevant_candidate_count': 123, 'label_relevant_truncated_count': 96, 'answer_outside_window': 'Possible, not established by page labels. Retained passage end-character offsets are saved for direct source inspection.'}.

### All question changes

| Question | Hybrid first rank | Reranked first rank | Change |
|---|---:|---:|---|
| MAR-01 | 1 | 1 | tie |
| MAR-02 | 1 | 2 | worsened |
| MAR-03 | 1 | 1 | tie |
| MAR-04 | 2 | 2 | tie |
| MAR-05 | 2 | miss | worsened |
| DRE-01 | 4 | 2 | improved |
| DRE-02 | 1 | 1 | tie |
| DRE-03 | 1 | 1 | tie |
| DRE-04 | 3 | miss | worsened |
| DRE-05 | 1 | 1 | tie |
| PLE-01 | 1 | 3 | worsened |
| PLE-02 | 1 | 1 | tie |
| PLE-03 | 1 | 1 | tie |
| PLE-04 | 1 | 1 | tie |
| PLE-05 | 1 | 1 | tie |
| GID-01 | 1 | 1 | tie |
| GID-02 | 2 | 1 | improved |
| GID-03 | 1 | 1 | tie |
| GID-04 | 1 | 1 | tie |
| GID-05 | 1 | 1 | tie |
| MIR-01 | 1 | 1 | tie |
| MIR-02 | 2 | 3 | worsened |
| MIR-03 | 1 | 1 | tie |
| MIR-04 | 2 | 5 | worsened |
| MIR-05 | 1 | miss | worsened |
| TIN-01 | 1 | 1 | tie |
| TIN-02 | 2 | 2 | tie |
| TIN-03 | 2 | 1 | improved |
| TIN-04 | 1 | 1 | tie |
| TIN-05 | 1 | 1 | tie |
| NYT-01 | 2 | 1 | improved |
| NYT-02 | 1 | 1 | tie |
| NYT-03 | 1 | 1 | tie |
| NYT-04 | 1 | 1 | tie |
| NYT-05 | 1 | 1 | tie |
| OBE-01 | miss | miss | shared_miss |
| OBE-02 | 3 | 1 | improved |
| OBE-03 | 1 | 1 | tie |
| OBE-04 | 1 | 1 | tie |
| OBE-05 | 1 | 1 | tie |

### Targeted complete candidate rankings

**MAR-05:** Why did the Court conclude that courts must follow the Constitution rather than an ordinary legislative act when the two conflict?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| plessy_v_ferguson.pdf | 22–23 | 21 | 1 | 1 | -3.568690 | False | True | 487/512 |
| obergefell_v_hodges.pdf | 34–35 | 33 | 7 | 2 | -4.368105 | False | True | 487/524 |
| obergefell_v_hodges.pdf | 54–55 | 52 | 9 | 3 | -5.668323 | False | True | 487/560 |
| gideon_v_wainwright.pdf | 5–7 | 4 | 8 | 4 | -6.930519 | False | True | 487/864 |
| obergefell_v_hodges.pdf | 2–3 | 1 | 6 | 5 | -7.260298 | False | True | 487/707 |
| dred_scott_v_sandford.pdf | 214–215 | 216 | 3 | 6 | -7.901256 | False | True | 487/660 |
| marbury_v_madison.pdf | 42–43 | 42 | 2 | 7 | -7.977530 | True | True | 487/571 |
| marbury_v_madison.pdf | 44–44 | 44 | 5 | 8 | -8.528142 | True | True | 487/590 |
| marbury_v_madison.pdf | 41–42 | 41 | 4 | 9 | -8.999654 | True | True | 487/626 |

**DRE-04:** Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| dred_scott_v_sandford.pdf | 228–229 | 230 | 4 | 1 | 3.235075 | False | True | 486/605 |
| dred_scott_v_sandford.pdf | 125–126 | 127 | 7 | 2 | 0.871363 | False | True | 486/617 |
| dred_scott_v_sandford.pdf | 72–73 | 74 | 5 | 3 | -0.118455 | False | True | 486/643 |
| dred_scott_v_sandford.pdf | 54–55 | 56 | 9 | 4 | -0.144802 | False | True | 486/628 |
| obergefell_v_hodges.pdf | 52–53 | 50 | 2 | 5 | -0.194941 | False | True | 486/505 |
| dred_scott_v_sandford.pdf | 144–145 | 146 | 1 | 6 | -0.939243 | False | True | 486/668 |
| dred_scott_v_sandford.pdf | 235–236 | 237 | 10 | 7 | -1.114547 | False | True | 486/710 |
| dred_scott_v_sandford.pdf | 3–3 | 4 | 3 | 8 | -2.357588 | True | True | 486/852 |
| dred_scott_v_sandford.pdf | 141–142 | 143 | 6 | 9 | -2.451615 | False | True | 486/638 |
| plessy_v_ferguson.pdf | 22–23 | 21 | 8 | 10 | -4.217038 | False | True | 486/512 |

**GID-05:** What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| gideon_v_wainwright.pdf | 10–12 | 8 | 1 | 1 | -1.050255 | True | True | 487/853 |
| miranda_v_arizona.pdf | 33–34 | 32 | 5 | 2 | -5.245250 | False | True | 487/546 |
| gideon_v_wainwright.pdf | 3–4 | 2 | 9 | 3 | -6.094888 | False | False | 455/455 |
| miranda_v_arizona.pdf | 38–39 | 37 | 3 | 4 | -6.290566 | False | True | 487/535 |
| miranda_v_arizona.pdf | 99–100 | 95 | 6 | 5 | -6.911368 | False | True | 487/557 |
| miranda_v_arizona.pdf | 36–37 | 35 | 7 | 6 | -6.943863 | False | False | 463/463 |
| miranda_v_arizona.pdf | 47–48 | 45 | 8 | 7 | -7.193659 | False | True | 487/521 |
| miranda_v_arizona.pdf | 35–36 | 34 | 10 | 8 | -7.413261 | False | False | 451/451 |
| miranda_v_arizona.pdf | 37–38 | 36 | 2 | 9 | -7.439264 | False | True | 487/524 |
| miranda_v_arizona.pdf | 83–84 | 79 | 4 | 10 | -7.882207 | False | False | 472/472 |

**MIR-02:** Why did the Supreme Court find Miranda's statements inadmissible?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| miranda_v_arizona.pdf | 83–84 | 79 | 1 | 1 | 2.345293 | False | False | 472/472 |
| miranda_v_arizona.pdf | 100–101 | 96 | 3 | 2 | 1.181709 | False | True | 494/502 |
| miranda_v_arizona.pdf | 1–2 | 0 | 5 | 3 | -0.697682 | True | True | 494/556 |
| miranda_v_arizona.pdf | 56–58 | 53 | 2 | 4 | -1.129817 | True | True | 494/832 |
| miranda_v_arizona.pdf | 22–23 | 21 | 4 | 5 | -1.954890 | False | False | 434/434 |
| miranda_v_arizona.pdf | 46–47 | 44 | 6 | 6 | -2.429387 | False | False | 491/491 |
| miranda_v_arizona.pdf | 94–95 | 90 | 9 | 7 | -2.545635 | False | False | 443/443 |
| miranda_v_arizona.pdf | 60–61 | 56 | 7 | 8 | -4.154068 | False | False | 464/464 |
| miranda_v_arizona.pdf | 5–6 | 4 | 8 | 9 | -5.545427 | False | True | 494/588 |

**NYT-01:** What classified material was the United States trying to prevent the New York Times and Washington Post from publishing?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| new_york_times_co_v_united_states.pdf | 1–3 | 0 | 2 | 1 | 4.478681 | True | True | 489/830 |
| new_york_times_co_v_united_states.pdf | 29–30 | 23 | 7 | 2 | 2.678282 | False | False | 478/478 |
| new_york_times_co_v_united_states.pdf | 48–49 | 39 | 5 | 3 | 1.552573 | False | False | 436/436 |
| new_york_times_co_v_united_states.pdf | 20–22 | 15 | 6 | 4 | -0.767225 | False | True | 489/823 |
| new_york_times_co_v_united_states.pdf | 23–24 | 17 | 4 | 5 | -1.796261 | False | True | 489/525 |
| new_york_times_co_v_united_states.pdf | 33–34 | 27 | 1 | 6 | -1.840764 | False | True | 489/490 |
| new_york_times_co_v_united_states.pdf | 38–39 | 31 | 9 | 7 | -2.034109 | False | False | 436/436 |
| new_york_times_co_v_united_states.pdf | 9–11 | 6 | 8 | 8 | -2.214675 | False | True | 489/870 |
| new_york_times_co_v_united_states.pdf | 31–32 | 25 | 3 | 9 | -3.603629 | False | True | 489/568 |

**OBE-01:** What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| obergefell_v_hodges.pdf | 19–20 | 18 | 5 | 1 | 4.209139 | False | True | 492/525 |
| obergefell_v_hodges.pdf | 94–95 | 91 | 2 | 2 | 1.448044 | False | False | 483/483 |
| obergefell_v_hodges.pdf | 37–39 | 36 | 1 | 3 | 1.168484 | False | True | 492/822 |
| obergefell_v_hodges.pdf | 68–69 | 66 | 4 | 4 | 0.920093 | False | False | 474/474 |
| obergefell_v_hodges.pdf | 33–34 | 32 | 6 | 5 | 0.397983 | False | False | 452/452 |
| obergefell_v_hodges.pdf | 2–3 | 1 | 10 | 6 | 0.069832 | False | True | 492/707 |
| obergefell_v_hodges.pdf | 50–51 | 48 | 3 | 7 | -0.125538 | False | False | 455/455 |
| obergefell_v_hodges.pdf | 13–14 | 12 | 7 | 8 | -0.429734 | True | False | 473/473 |
| obergefell_v_hodges.pdf | 97–98 | 94 | 8 | 9 | -0.453393 | False | True | 492/872 |
| obergefell_v_hodges.pdf | 1–2 | 0 | 9 | 10 | -2.026489 | False | True | 492/550 |


### Targeted retained-window source checks

The following display-only anchors were inspected in the frozen passages. They do not change labels or scores and do not establish that truncation caused a ranking failure.

**DRE-04, chunk 4:** passage truncated=True; retained end character 2253/4129.

- territorial equal-benefit statement: characters 2865–2888; anchor retained=False. Source context: territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in
- constitutional limits on Congress: characters 3030–3060; anchor retained=False. Source context: Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respec
- enslaved people as property statement: characters 3929–3946; anchor retained=False. Source context: recognises slaves as property, and pledges the Federal Government to protect it. And Congress cannot exercise any more authority over property of that description than it may constitutionally exercise

**OBE-01, chunk 12:** passage truncated=False; retained end character 2014/2014.

- explicit two-question grant: characters 719–743; anchor retained=True. Source context: limited to two questions. 574 U. S. 1118 (2015). The frst, presented by the cases from Michigan and Kentucky, is whether the Fourteenth Amendment requires a State to li- cense a marriage between two people of the same sex. The second, presented by
- second question introduction: characters 944–955; anchor retained=True. Source context: The second, presented by the cases from Ohio, Tennessee, and, again, Kentucky, is whether the Fourteenth Amendment re- quires a State to recognize a same-sex marriage licensed and performed in a State which does grant that right. II Before addre


### by_question_type

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| facts | 8 | hybrid | 0.625 | 0.750 | 0.875 | 0.718750 |
| facts | 8 | cross_encoder | 0.625 | 0.875 | 0.875 | 0.729167 |
| holding | 7 | hybrid | 0.429 | 1.000 | 1.000 | 0.690476 |
| holding | 7 | cross_encoder | 0.714 | 1.000 | 1.000 | 0.833333 |
| holding_detail | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | cross_encoder | 0.000 | 1.000 | 1.000 | 0.500000 |
| jurisdiction | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| jurisdiction | 1 | cross_encoder | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_principle | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_principle | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_rule | 3 | hybrid | 0.333 | 1.000 | 1.000 | 0.611111 |
| legal_rule | 3 | cross_encoder | 0.333 | 0.333 | 0.667 | 0.400000 |
| precedent | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| reasoning | 8 | hybrid | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | cross_encoder | 0.875 | 0.875 | 0.875 | 0.875000 |
| remedy | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | cross_encoder | 0.833 | 0.833 | 0.833 | 0.833333 |
| specific_fact | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |

### by_case

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | hybrid | 0.600 | 0.800 | 1.000 | 0.716667 |
| Dred Scott v. Sandford | 5 | cross_encoder | 0.600 | 0.800 | 0.800 | 0.700000 |
| Gideon v. Wainwright | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| Gideon v. Wainwright | 5 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| Marbury v. Madison | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Marbury v. Madison | 5 | cross_encoder | 0.400 | 0.800 | 0.800 | 0.600000 |
| Miranda v. Arizona | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Miranda v. Arizona | 5 | cross_encoder | 0.400 | 0.600 | 0.800 | 0.506667 |
| New York Times Co. v. United States | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| New York Times Co. v. United States | 5 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| Obergefell v. Hodges | 5 | hybrid | 0.600 | 0.800 | 0.800 | 0.666667 |
| Obergefell v. Hodges | 5 | cross_encoder | 0.800 | 0.800 | 0.800 | 0.800000 |
| Plessy v. Ferguson | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Plessy v. Ferguson | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.866667 |
| Tinker v. Des Moines School Dist. | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Tinker v. Des Moines School Dist. | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.900000 |

## structure_aware_v1

Absolute changes (reranked minus hybrid): {'hit_at_1': -0.125, 'hit_at_3': -0.04999999999999993, 'hit_at_5': -0.04999999999999993, 'mrr': -0.09583333333333321}.

First-relevant-rank changes: {'improved': 3, 'worsened': 9, 'tie': 27, 'shared_miss': 1}. Rescued misses: []; lost hits: ['MAR-04', 'DRE-04'].

Analysis-only oracle: 39/40 questions have any label-relevant union candidate. Maximum possible Hit@1, Hit@3, Hit@5, and MRR each 0.975. This theoretical ceiling is not an achieved ranking and never influences actual scores.

Truncation: {'candidate_count': 294, 'truncated_count': 275, 'truncated_percentage': 93.5374149659864, 'passage_token_lengths': {'min': 9, 'max': 943, 'mean': 823.8877551020408, 'median': 881.0, 'p90_nearest_rank': 918}, 'full_pair_token_lengths': {'min': 32, 'max': 966, 'mean': 846.8027210884354, 'median': 903.0, 'p90_nearest_rank': 942}, 'query_truncated_count': 0, 'label_relevant_candidate_count': 111, 'label_relevant_truncated_count': 101, 'answer_outside_window': 'Possible, not established by page labels. Retained passage end-character offsets are saved for direct source inspection.'}.

### All question changes

| Question | Hybrid first rank | Reranked first rank | Change |
|---|---:|---:|---|
| MAR-01 | 1 | 1 | tie |
| MAR-02 | 1 | 1 | tie |
| MAR-03 | 1 | 2 | worsened |
| MAR-04 | 5 | miss | worsened |
| MAR-05 | 1 | 5 | worsened |
| DRE-01 | 1 | 1 | tie |
| DRE-02 | 1 | 1 | tie |
| DRE-03 | 2 | 1 | improved |
| DRE-04 | 1 | miss | worsened |
| DRE-05 | 1 | 1 | tie |
| PLE-01 | 1 | 3 | worsened |
| PLE-02 | 1 | 1 | tie |
| PLE-03 | 1 | 1 | tie |
| PLE-04 | 1 | 1 | tie |
| PLE-05 | 1 | 1 | tie |
| GID-01 | 1 | 1 | tie |
| GID-02 | 2 | 1 | improved |
| GID-03 | 2 | 3 | worsened |
| GID-04 | 1 | 3 | worsened |
| GID-05 | 1 | 1 | tie |
| MIR-01 | 1 | 1 | tie |
| MIR-02 | 3 | 2 | improved |
| MIR-03 | 1 | 1 | tie |
| MIR-04 | 1 | 1 | tie |
| MIR-05 | 1 | 1 | tie |
| TIN-01 | 1 | 1 | tie |
| TIN-02 | 1 | 1 | tie |
| TIN-03 | 1 | 2 | worsened |
| TIN-04 | 1 | 1 | tie |
| TIN-05 | 1 | 1 | tie |
| NYT-01 | 1 | 1 | tie |
| NYT-02 | 1 | 1 | tie |
| NYT-03 | 1 | 1 | tie |
| NYT-04 | 1 | 2 | worsened |
| NYT-05 | 1 | 1 | tie |
| OBE-01 | miss | miss | shared_miss |
| OBE-02 | 1 | 1 | tie |
| OBE-03 | 1 | 1 | tie |
| OBE-04 | 1 | 1 | tie |
| OBE-05 | 1 | 1 | tie |

### Targeted complete candidate rankings

**MAR-05:** Why did the Court conclude that courts must follow the Constitution rather than an ordinary legislative act when the two conflict?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| tinker_v_des_moines_school_dist.pdf | 17–19 | 13 | 10 | 1 | -1.988891 | False | True | 487/835 |
| obergefell_v_hodges.pdf | 53–55 | 35 | 4 | 2 | -2.161524 | False | True | 487/716 |
| dred_scott_v_sandford.pdf | 53–54 | 40 | 5 | 3 | -2.712223 | False | True | 487/862 |
| dred_scott_v_sandford.pdf | 214–215 | 164 | 7 | 4 | -4.709158 | False | True | 487/814 |
| marbury_v_madison.pdf | 41–43 | 30 | 1 | 5 | -5.898506 | True | True | 487/917 |
| obergefell_v_hodges.pdf | 65–67 | 42 | 8 | 6 | -6.164797 | False | True | 487/918 |
| dred_scott_v_sandford.pdf | 171–172 | 131 | 3 | 7 | -6.362593 | False | True | 487/841 |
| plessy_v_ferguson.pdf | 21–23 | 15 | 2 | 8 | -7.389890 | False | True | 487/908 |
| marbury_v_madison.pdf | 40–41 | 29 | 6 | 9 | -8.292088 | True | True | 487/900 |
| marbury_v_madison.pdf | 42–44 | 31 | 9 | 10 | -9.709759 | True | True | 487/938 |

**DRE-04:** Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| dred_scott_v_sandford.pdf | 135–136 | 104 | 8 | 1 | 2.371573 | False | True | 486/906 |
| dred_scott_v_sandford.pdf | 124–125 | 95 | 2 | 2 | 1.991605 | False | True | 486/877 |
| dred_scott_v_sandford.pdf | 131–132 | 101 | 7 | 3 | 1.965426 | False | True | 486/877 |
| obergefell_v_hodges.pdf | 52–53 | 34 | 4 | 4 | 0.832172 | False | True | 486/872 |
| dred_scott_v_sandford.pdf | 97–99 | 74 | 3 | 5 | 0.794467 | False | True | 486/881 |
| dred_scott_v_sandford.pdf | 3–4 | 2 | 1 | 6 | 0.694587 | True | True | 486/729 |
| dred_scott_v_sandford.pdf | 143–145 | 111 | 6 | 7 | -0.108630 | False | True | 486/907 |
| dred_scott_v_sandford.pdf | 53–54 | 40 | 5 | 8 | -1.293810 | False | True | 486/862 |
| dred_scott_v_sandford.pdf | 141–142 | 109 | 10 | 9 | -1.856225 | False | True | 486/880 |
| dred_scott_v_sandford.pdf | 116–117 | 89 | 9 | 10 | -4.253070 | False | True | 486/908 |

**GID-05:** What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| gideon_v_wainwright.pdf | 11–11 | 7 | 2 | 1 | -0.297773 | True | False | 316/316 |
| miranda_v_arizona.pdf | 82–84 | 50 | 7 | 2 | -4.574809 | False | True | 487/919 |
| miranda_v_arizona.pdf | 33–36 | 21 | 3 | 3 | -5.265565 | False | True | 487/901 |
| miranda_v_arizona.pdf | 32–34 | 20 | 6 | 4 | -5.985070 | False | True | 487/906 |
| miranda_v_arizona.pdf | 36–37 | 22 | 4 | 5 | -6.396449 | False | True | 487/830 |
| gideon_v_wainwright.pdf | 2–4 | 2 | 5 | 6 | -7.374424 | False | True | 487/613 |
| gideon_v_wainwright.pdf | 9–11 | 6 | 1 | 7 | -8.833972 | True | True | 487/897 |

**MIR-02:** Why did the Supreme Court find Miranda's statements inadmissible?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| miranda_v_arizona.pdf | 82–84 | 50 | 7 | 1 | 2.803503 | False | True | 494/919 |
| miranda_v_arizona.pdf | 56–58 | 34 | 3 | 2 | 2.315407 | True | True | 494/875 |
| miranda_v_arizona.pdf | 89–91 | 54 | 4 | 3 | 1.953724 | False | True | 494/847 |
| miranda_v_arizona.pdf | 1–2 | 0 | 8 | 4 | -0.608418 | True | True | 494/873 |
| miranda_v_arizona.pdf | 93–95 | 57 | 5 | 5 | -2.350582 | False | True | 494/856 |
| miranda_v_arizona.pdf | 20–22 | 13 | 1 | 6 | -2.872704 | False | True | 494/886 |
| miranda_v_arizona.pdf | 4–6 | 3 | 2 | 7 | -3.277329 | False | True | 494/845 |
| miranda_v_arizona.pdf | 41–43 | 25 | 6 | 8 | -4.408991 | False | True | 494/881 |
| miranda_v_arizona.pdf | 58–60 | 35 | 9 | 9 | -8.545641 | False | True | 494/865 |

**NYT-01:** What classified material was the United States trying to prevent the New York Times and Washington Post from publishing?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| new_york_times_co_v_united_states.pdf | 1–2 | 1 | 2 | 1 | 5.114372 | True | False | 394/394 |
| new_york_times_co_v_united_states.pdf | 2–2 | 2 | 1 | 2 | 3.310567 | True | False | 327/327 |
| new_york_times_co_v_united_states.pdf | 20–22 | 14 | 3 | 3 | -0.112169 | False | True | 489/896 |
| new_york_times_co_v_united_states.pdf | 18–20 | 13 | 8 | 4 | -1.821677 | False | True | 489/883 |
| new_york_times_co_v_united_states.pdf | 22–24 | 15 | 4 | 5 | -2.328939 | False | True | 489/913 |
| new_york_times_co_v_united_states.pdf | 47–49 | 30 | 5 | 6 | -2.903895 | False | True | 489/877 |
| new_york_times_co_v_united_states.pdf | 1–1 | 0 | 7 | 7 | -3.490433 | False | False | 9/9 |
| new_york_times_co_v_united_states.pdf | 8–10 | 6 | 6 | 8 | -3.892795 | False | True | 489/862 |

**OBE-01:** What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |
|---|---|---:|---:|---:|---:|---|---|---|
| obergefell_v_hodges.pdf | 93–95 | 60 | 8 | 1 | 5.092501 | False | True | 492/702 |
| obergefell_v_hodges.pdf | 22–23 | 16 | 3 | 2 | 3.420247 | False | True | 492/882 |
| obergefell_v_hodges.pdf | 43–45 | 29 | 9 | 3 | 2.917621 | False | True | 492/905 |
| obergefell_v_hodges.pdf | 19–20 | 14 | 2 | 4 | 2.453674 | False | True | 492/721 |
| obergefell_v_hodges.pdf | 74–76 | 48 | 7 | 5 | 1.463720 | False | True | 492/905 |
| obergefell_v_hodges.pdf | 36–39 | 24 | 4 | 6 | 0.235292 | False | True | 492/900 |
| obergefell_v_hodges.pdf | 67–69 | 43 | 5 | 7 | 0.135405 | False | True | 492/910 |
| obergefell_v_hodges.pdf | 1–2 | 1 | 1 | 8 | -0.792083 | False | True | 492/881 |
| obergefell_v_hodges.pdf | 34–36 | 23 | 6 | 9 | -1.195626 | False | True | 492/931 |


### Targeted retained-window source checks

The following display-only anchors were inspected in the frozen passages. They do not change labels or scores and do not establish that truncation caused a ranking failure.

**DRE-04, chunk 2:** passage truncated=True; retained end character 2391/3557.

- territorial equal-benefit statement: characters 1839–1862; anchor retained=True. Source context: territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in
- constitutional limits on Congress: characters 2004–2034; anchor retained=True. Source context: Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respec
- enslaved people as property statement: characters 2903–2920; anchor retained=False. Source context: recognises slaves as property, and pledges the Federal Government to protect it. And Congress cannot exercise any more authority over property of that description than it may constitutionally exercise over property of any other kind. 5. The act of Co


### by_question_type

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| facts | 8 | hybrid | 0.875 | 0.875 | 0.875 | 0.875000 |
| facts | 8 | cross_encoder | 0.750 | 0.875 | 0.875 | 0.791667 |
| holding | 7 | hybrid | 0.714 | 1.000 | 1.000 | 0.833333 |
| holding | 7 | cross_encoder | 0.857 | 1.000 | 1.000 | 0.928571 |
| holding_detail | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | hybrid | 0.000 | 0.000 | 1.000 | 0.200000 |
| jurisdiction | 1 | cross_encoder | 0.000 | 0.000 | 0.000 | 0.000000 |
| legal_principle | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | cross_encoder | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_rule | 3 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_rule | 3 | cross_encoder | 0.667 | 0.667 | 0.667 | 0.666667 |
| precedent | 1 | hybrid | 0.000 | 1.000 | 1.000 | 0.500000 |
| precedent | 1 | cross_encoder | 0.000 | 1.000 | 1.000 | 0.333333 |
| reasoning | 8 | hybrid | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | cross_encoder | 0.625 | 0.875 | 1.000 | 0.754167 |
| remedy | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | cross_encoder | 0.000 | 1.000 | 1.000 | 0.500000 |
| specific_detail | 6 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | cross_encoder | 1.000 | 1.000 | 1.000 | 1.000000 |

### by_case

| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.900000 |
| Dred Scott v. Sandford | 5 | cross_encoder | 0.800 | 0.800 | 0.800 | 0.800000 |
| Gideon v. Wainwright | 5 | hybrid | 0.600 | 1.000 | 1.000 | 0.800000 |
| Gideon v. Wainwright | 5 | cross_encoder | 0.600 | 1.000 | 1.000 | 0.733333 |
| Marbury v. Madison | 5 | hybrid | 0.800 | 0.800 | 1.000 | 0.840000 |
| Marbury v. Madison | 5 | cross_encoder | 0.400 | 0.600 | 0.800 | 0.540000 |
| Miranda v. Arizona | 5 | hybrid | 0.800 | 1.000 | 1.000 | 0.866667 |
| Miranda v. Arizona | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.900000 |
| New York Times Co. v. United States | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| New York Times Co. v. United States | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.900000 |
| Obergefell v. Hodges | 5 | hybrid | 0.800 | 0.800 | 0.800 | 0.800000 |
| Obergefell v. Hodges | 5 | cross_encoder | 0.800 | 0.800 | 0.800 | 0.800000 |
| Plessy v. Ferguson | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Plessy v. Ferguson | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.866667 |
| Tinker v. Des Moines School Dist. | 5 | hybrid | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | cross_encoder | 0.800 | 1.000 | 1.000 | 0.900000 |

## OBE-01 availability and input window

Fixed OBE-01 has an accepted pp13–14 candidate originally at hybrid rank 7; its cross-encoder rank is shown above. Structure-aware OBE-01 has no accepted candidate anywhere in its saved union, so reranking cannot solve that missing-candidate problem. Neither labels nor the prior Phase 5A possible-gap annotations were changed.

Relevant page overlap does not prove that the answer survives truncation. Inspect the original chunk at the recorded retained end-character offset; pages alone cannot identify answer spans.

## Limitations

- Benchmark v2 is not an independent holdout: it was refined using evaluated dense candidates.
- Case/source/page-overlap relevance is coarse and can misclassify actual answer-bearing content.
- Candidate availability limits reranking. Only complete saved hybrid unions are used; no new retrieval candidates are generated.
- This unmodified MS MARCO pretrained cross-encoder is not specialized in Supreme Court law. No fine-tuning, model selection, legal boosts, or label-informed scoring occurs.
- Long passages are deterministically truncated with longest_first, right truncation, to a 512-token paired input. Actual evidence can fall outside the retained prefix. There are no labeled answer spans, so page labels alone cannot establish whether the answer was seen.
- Frozen chunk sizes and coverage differ; structure-aware excludes 200 foreign Sturgis/Honold tokens retained in fixed chunks.
- Differences and small subgroup results are descriptive; no statistical significance or general superiority is implied.
- Saved scores support deterministic replay. Bit-identical new neural inference across hardware/framework versions is not guaranteed; device and versions are frozen and recorded.

## Reproducibility and protection

All 123 protected pre-existing data files remain SHA-256 identical. Full before/after hashes are in JSON. No production retrieval, chunks, benchmarks, prior reports, or vector stores were changed. No Vercel calls, new embeddings, fine-tuning, commits, or pushes.

Network was used only for authorized dependency installation and pinned Hugging Face model download. Benchmark inference is local. `.venv/bin/python run_cross_encoder_experiment.py --replay` validates and reconstructs results from saved scores without loading a model or repeating inference. Real-inference reruns require an explicit `--infer` and refuse overwriting existing results.

READY for the next phase as a completed evaluation baseline, not evidence that this reranker improves every metric. No subsequent phase has started.
