# CourtLens Phase 5A — BM25 lexical retrieval

Standard Okapi BM25, implemented locally without adding a dependency. k1=1.5; b=0.75. Settings fixed before evaluation; no tuning.

`IDF(t)=ln(1+(N-df(t)+0.5)/(df(t)+0.5))`

`score(q,d)=Σ qtf(t) × IDF(t) × tf(t,d) × (k1+1) / (tf(t,d)+k1×(1-b+b×len(d)/avgdl))`

This uses the positive smoothed Robertson IDF convention; repeated query terms contribute linearly. Lengths are lexical-term counts. The scorer accepts strings only, with no metadata, labels, or dense scores.

Unicode NFKC then casefold; contiguous Unicode letters/numbers form terms; combining marks continue an existing term. All other characters, including punctuation, apostrophes, hyphens, decimal points, and underscores, separate terms. Numeric strings remain terms. No stemming, stopword removal, OCR repair, synonyms, expansion, or legal normalization. Frozen text, including headers and PDF markers, is used as-is.

Positive scores only: zero-score chunks are excluded, not padded into Top-20. Empty/no-match queries return no results and zero official metrics. Ties use original corpus ordinal ascending: sorted fixed artifact filenames then original rows, or original structure-aware JSONL rows. Original chunk IDs and local indexes are retained; fixed chunks lacking IDs are referenced by source_file + chunk_index.

Full Top-20 lexical rankings are saved separately without relevance labels. Official metrics, including MRR, use only Top-5 and the unchanged existing case/source/page-overlap evaluator. No exploratory Top-20 metrics are reported.

## Locked dense controls and BM25 comparison

| Chunk collection | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| fixed_900_150 | Dense (saved v2) | 0.750 | 0.900 | 0.900 | 0.825000 |
| fixed_900_150 | BM25 | 0.725 | 0.875 | 0.950 | 0.805000 |
| structure_aware_v1 | Dense (saved v2) | 0.825 | 0.925 | 0.950 | 0.877083 |
| structure_aware_v1 | BM25 | 0.675 | 0.875 | 0.925 | 0.782083 |

## Complementarity

| Collection | Both hit | Dense only | BM25 only | Both miss | BM25 rank wins | Dense rank wins | Finite ties | Shared misses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_900_150 | 34 | 2 | 4 | 0 | 9 | 9 | 22 | 0 |
| structure_aware_v1 | 36 | 2 | 1 | 1 | 3 | 11 | 25 | 1 |

Rank wins mean lower first relevant rank within Top-5, with misses treated as infinity. Ties are finite equal ranks; shared misses are a separate category.

### fixed_900_150 — unique hits

BM25-only question IDs: DRE-04, GID-05, NYT-01, OBE-01.

Dense-only question IDs: MAR-05, MIR-02.

**DRE-04, BM25 rank 2: Dred Scott v. Sandford, PDF pp3–3, chunk 4.**

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

BM25 score: 20.229556. Dense Top-5: no accepted evidence.

> The territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respective rights defined and limited by the Constitution. 2. Congress have no right to prohibit the citizens of any particular State or States from taking up their home there, while it permits citizens of other States to do so. Nor has 

**GID-05, BM25 rank 1: Gideon v. Wainwright, PDF pp10–12, chunk 8.**

What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

BM25 score: 21.592464. Dense Top-5: no accepted evidence.

> heard by counsel. Even the intelligent and edu- cated layman has small and sometimes no skill in the science of law. If charged with crime, he is inca- pable, generally, of determining for himself whether the indictment is good or bad. He is unfamiliar with the rules of evidence. Left without the aid of coun- sel he may be put on trial without a proper charge, and convicted upon incompetent evidence, or evi- dence irrelevant to the issue or otherwise inadmis- sible. He lacks both the skill and knowledge ade- quately to prepare his defense, even though he have a perfect one. He requires the guiding hand of counsel at every step in the proceedi

**NYT-01, BM25 rank 1: New York Times Co. v. United States, PDF pp1–3, chunk 0.**

What classified material was the United States trying to prevent the New York Times and Washington Post from publishing?

BM25 score: 34.555987. Dense Top-5: no accepted evidence.

> We granted certiorari in these cases in which the United States seeks to enjoin the New York Times and the Wash- ington Post from publishing the contents of a classified study entitled "History of U. S. Decision-Making Process on Viet Nam Policy." Post, pp. 942, 943. "Any system of prior restraints of expression comes to this Court bearing a heavy presumption against its con- stitutional validity." Bantam Books, Inc. v. Sullivan, 372 U. S. 58, 70 (1963); see also Near v. Minnesota, 283 U. S. 697 (1931). The Government "thus carries a heavy burden of showing justification for the imposition of such a restraint." Organization for a Better Austi

**OBE-01, BM25 rank 4: Obergefell v. Hodges, PDF pp13–14, chunk 12.**

What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

BM25 score: 15.764982. Dense Top-5: no accepted evidence.

> The petitioners sought certiorari. This Court granted re- view, limited to two questions. 574 U. S. 1118 (2015). The frst, presented by the cases from Michigan and Kentucky, is whether the Fourteenth Amendment requires a State to li- cense a marriage between two people of the same sex. The second, presented by the cases from Ohio, Tennessee, and, again, Kentucky, is whether the Fourteenth Amendment re- quires a State to recognize a same-sex marriage licensed and performed in a State which does grant that right. II Before addressing the principles and precedents that gov- ern these cases, it is appropriate to note the history of the subject no

### structure_aware_v1 — unique hits

BM25-only question IDs: DRE-04.

Dense-only question IDs: MAR-05, MIR-02.

**DRE-04, BM25 rank 1: Dred Scott v. Sandford, PDF pp3–4, chunk 2.**

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

BM25 score: 19.241548. Dense Top-5: no accepted evidence.

> The territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respective rights defined and limited by the Constitution. 2. Congress have no right to prohibit the citizens of any particular State or States from taking up their home there, while it permits citizens of other States to do so. Nor has 

## DRE-04 and OBE-01 — targeted source inspection

Relevance below is the benchmark’s mechanical page-overlap decision. Manual possible-gap annotations do not alter labels, rankings, or metrics. Opinion/author fields are preserved as recorded; fixed chunks have no opinion attribution. Full text remains in the frozen source artifacts, avoiding a duplicate corpus.

### fixed_900_150 — DRE-04

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

Accepted PDF ranges: [[3, 4]]. Dense first relevant rank: miss; BM25: 2. BM25 finds accepted evidence dense missed: True.

**Rank 1; score 20.999541; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp52–53; chunk 50.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> The need for restraint in administering the strong medi- cine of substantive due process is a lesson this Court has learned the hard way. The Court frst applied substantive due process to strike down a statute in Dred Scott v. Sand- ford, 19 How. 393 (1857). There the Court invalidated the Missouri Compromise on the ground that legislation restrict- ing the institution of slavery violated the implied rights of slaveholders. The Court relied on its own conception of lib- erty and property in doing so. It asserted that “an act of Congress which deprives a citizen of the United States of his liberty or property, merely because he came himself or

**CROSS-CASE QUOTATION:** Roberts quotes Dred Scott property/due-process reasoning in Obergefell. This is a cross-case citation, not a missing Dred Scott page range; the required case/source gate fails.

Obergefell, Roberts dissent, identified from source headings; absent from fixed metadata.

**Rank 2; score 20.229556; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp3–3; chunk 4.**

Opinion: not recorded; author: not recorded. Benchmark relevant: True.

> The territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respective rights defined and limited by the Constitution. 2. Congress have no right to prohibit the citizens of any particular State or States from taking up their home there, while it permits citizens of other States to do so. Nor has 

**ACCEPTED EVIDENCE:** The accepted headnote passage states equal territorial access, constitutional limits on Congress, and protection of enslaved people as property.

Dred Scott syllabus/headnotes; fixed metadata has no attribution.

**Rank 3; score 16.677530; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp141–142; chunk 143.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> ===== PAGE 141 ===== DECEMBER TERM, 1856. 533 .Dred ,.oU v. Randford. [M. Jusncx McLwr. in the act of 1789. - The above argument is properly met by saying that the Constitution was intended to be a practical instrument; and.where its language is too plain to be misun- derstood, the argument ends." In Chiri v. Chir, (2 Wheat., 261 4 Curtis, 99,) this court says: "That the power of naturalization v exclusively in Con- gress does not seem to be, and certainly ought not to be, con- troverted." No person can legall be made a citizen of a State, and consequently a citizen of the Unted States, of foreign birth, unless he be naturalized under the act

**NO CONFIRMED LABEL GAP:** McLean discusses citizenship and outlines territorial-power issues; this dissent does not give the Court’s controlling property/due-process rationale.

McLean dissent, identified from source headings.

**Rank 4; score 15.997147; Plessy v. Ferguson; `plessy_v_ferguson.pdf`; pp22–23; chunk 21.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> ===== PAGE 22 ===== OCTOBER TERM, 1895. Dissenting Opinion: Harlan, J. or street? Why-may it not require sheriffs to assign whites to one side of a court-room and blacks to the other? And why may it not also prohibit the commingling of the two races in the galleries of legislative halls or in public assemblages con- vened for the consideration of the political questions of the day? Further, if this statute of Louisiana is consistent with the per- sonal liberty of citizens, why may not the State require the sep- aration in railroad coaches of native and naturalized citizens of the United States, or of Protestants and Roman Catholics? The answe

**NO CONFIRMED LABEL GAP:** Harlan discusses judicial restraint and segregation in Plessy. The case/source is wrong and the passage does not supply the requested territorial reasoning.

Plessy, Harlan dissent, identified from source headings.

**Rank 5; score 15.440948; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp54–55; chunk 56.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> ===== PAGE 54 ===== Oenuom or Ton COURT.] Dred Scott v. Sandford. court with admiralty jurisdiction, over which the General Gov- ernment had exclusive jurisdiction in the Territory. No one, we presume, will question the correctness of that opinion; nor is there anything in conflict with it in the opinion now given; The point decided in the case cited has no rela- tion to the question now before the court. That depended on the construction of the third article of the Constitution, in re- lation to the judiciary of the United States, and the power which Congress might exercise in a Territory in organizing the judicial department of the Governme

**NO CONFIRMED LABEL GAP:** Taney distinguishes the Canter judicial-jurisdiction precedent and introduces territorial acquisition. This passage does not independently state the complete property/due-process rationale.

Taney majority, identified from source headings.

### fixed_900_150 — OBE-01

What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

Accepted PDF ranges: [[12, 13]]. Dense first relevant rank: miss; BM25: 4. BM25 finds accepted evidence dense missed: True.

**Rank 1; score 16.598280; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp94–95; chunk 91.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> The Constitution says nothing about a right to same-sex marriage, but the Court holds that the term “liberty” in the Due Process Clause of the Fourteenth Amendment encom- passes this right. Our Nation was founded upon the princi- ple that every person has the unalienable right to liberty, but liberty is a term of many meanings. For classical liberals, it may include economic rights now limited by government regulation. For social democrats, it may include the right to a variety of government benefts. For today's majority, it has a distinctively postmodern meaning. To prevent fve unelected Justices from imposing their per- sonal vision of libe

**NO CONFIRMED LABEL GAP:** Alito criticizes the constitutional basis for the new marriage right; this does not identify both questions in the limited certiorari grant.

Alito dissent, identified from source headings.

**Rank 2; score 16.222581; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp68–69; chunk 66.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> Federal courts are blunt instruments when it comes to creating rights. They have constitutional power only to re- solve concrete cases or controversies; they do not have the fexibility of legislatures to address concerns of parties not before the court or to anticipate problems that may arise from the exercise of a new right. Today's decision, for ex- ample, creates serious questions about religious liberty. Many good and decent people oppose same-sex marriage as a tenet of faith, and their freedom to exercise religion is— unlike the right imagined by the majority—actually spelled out in the Constitution. Amdt. 1. Respect for sincere religiou

**NO CONFIRMED LABEL GAP:** Roberts discusses religious-liberty consequences and judicial policymaking, not the two questions the Court agreed to decide.

Roberts dissent, identified from source headings.

**Rank 3; score 15.972176; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp19–20; chunk 18.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> Against this background, the legal question of same-sex marriage arose. In 1993, the Hawaii Supreme Court held Hawaii's law restricting marriage to opposite-sex couples constituted a classifcation on the basis of sex and was there- fore subject to strict scrutiny under the Hawaii Constitution. Baehr v. Lewin, 74 Haw. 530, 852 P. 2d 44. Although this decision did not mandate that same-sex marriage be allowed, some States were concerned by its implications and reaf- frmed in their laws that marriage is defned as a union be- tween opposite-sex partners. So too in 1996, Congress passed the Defense of Marriage Act (DOMA), 110 Stat. 2419, defning m

**NO CONFIRMED LABEL GAP:** The passage recounts Baehr, DOMA, Goodridge, and Windsor history; it does not state the two granted questions.

Kennedy majority, identified from source headings.

**Rank 4; score 15.764982; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp13–14; chunk 12.**

Opinion: not recorded; author: not recorded. Benchmark relevant: True.

> The petitioners sought certiorari. This Court granted re- view, limited to two questions. 574 U. S. 1118 (2015). The frst, presented by the cases from Michigan and Kentucky, is whether the Fourteenth Amendment requires a State to li- cense a marriage between two people of the same sex. The second, presented by the cases from Ohio, Tennessee, and, again, Kentucky, is whether the Fourteenth Amendment re- quires a State to recognize a same-sex marriage licensed and performed in a State which does grant that right. II Before addressing the principles and precedents that gov- ern these cases, it is appropriate to note the history of the subject no

**ACCEPTED EVIDENCE:** The passage explicitly says review was limited to two questions and states the licensing and out-of-state recognition questions under the Fourteenth Amendment.

Kennedy majority, identified from source headings.

**Rank 5; score 15.624750; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp2–3; chunk 1.**

Opinion: not recorded; author: not recorded. Benchmark relevant: False.

> ===== PAGE 2 ===== 645 Cite as: 576 U. S. 644 (2015) Syllabus a Nation where new dimensions of freedom become apparent to new generations. This dynamic can be seen in the Nation's experience with gay and lesbian rights. Well into the 20th century, many States condemned same-sex intimacy as immoral, and homosexuality was treated as an illness. Later in the century, cultural and political developments al- lowed same-sex couples to lead more open and public lives. Extensive public and private dialogue followed, along with shifts in public atti- tudes. Questions about the legal treatment of gays and lesbians soon reached the courts, where they co

**NO CONFIRMED LABEL GAP:** This syllabus portion discusses history and the licensing holding, rather than both questions granted for review.

Syllabus, identified from source headings.

### structure_aware_v1 — DRE-04

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

Accepted PDF ranges: [[3, 4]]. Dense first relevant rank: miss; BM25: 1. BM25 finds accepted evidence dense missed: True.

**Rank 1; score 19.241548; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp3–4; chunk 2.**

Opinion: unknown; author: not recorded. Benchmark relevant: True.

> The territory thus acquired, is acquired by the people of the United States for their common and equal benefit, through their agent and trustee, the Federal Government. Congress can exercise no power over the rights of persons or property of a citizen in the Territory which is prohibited by the Constitution. The Government and the citizen, whenever the Territory is open to settlement, both enter it with their respective rights defined and limited by the Constitution. 2. Congress have no right to prohibit the citizens of any particular State or States from taking up their home there, while it permits citizens of other States to do so. Nor has 

**ACCEPTED EVIDENCE:** The accepted headnote passage states territorial/property protections and the constitutional invalidity of the prohibition.

Syllabus/headnotes in source; preserved chunk metadata says unknown.

**Rank 2; score 18.245976; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp52–53; chunk 34.**

Opinion: dissent; author: Roberts. Benchmark relevant: False.

> The need for restraint in administering the strong medi- cine of substantive due process is a lesson this Court has learned the hard way. The Court frst applied substantive due process to strike down a statute in Dred Scott v. Sand- ford, 19 How. 393 (1857). There the Court invalidated the Missouri Compromise on the ground that legislation restrict- ing the institution of slavery violated the implied rights of slaveholders. The Court relied on its own conception of lib- erty and property in doing so. It asserted that “an act of Congress which deprives a citizen of the United States of his liberty or property, merely because he came himself or

**CROSS-CASE QUOTATION:** Roberts quotes the Dred Scott property/due-process rationale in Obergefell. This fails the benchmark case/source gate and is not a Dred Scott page-label gap.



**Rank 3; score 16.445263; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp53–54; chunk 40.**

Opinion: majority; author: Tane. Benchmark relevant: False.

> Hence it has been argued that Congress cannot vest admiralty jurisdiction in courts created by the Territorial Legislature." And after thus clearly stating the point before them, and which they were about to decide, they proceed to show that these Territorial tribunals -were not constitutional courts, but merely legislative, and that Congress might, therefore, delegate the bower to the Territorial Government to establish the court in question; and they conclude that part of the opinion in the following words: "Although admiralty jurisdiction can be ex- ercised in the States in those courts only which are established in pursuance of the third 

**NO CONFIRMED LABEL GAP:** The Canter discussion distinguishes judicial jurisdiction from Congress’s regulation of property; it sets up rather than independently supplies the requested controlling rationale.

Taney majority in source; recorded author Tane is preserved unchanged.

**Rank 4; score 16.163379; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp135–136; chunk 104.**

Opinion: other; author: Oatron. Benchmark relevant: False.

> We must meet the question, whether Congress had the power to declare that a citizen of a State, carrying with him his equal rights, secured to him through his State, could be stripped of his goods and slaves, and be deprived of any participation in the common property? If this be the true meaning of the Constitution, equality' of rights to enjoy a common country (equal to a thousand miles square) may be cut off by a geographical line, and a. great portion of our citizens excluded from it. ;ngenious, indirect evasions of the Constitution have been attempted and defeated heretofore. In the passenger cases, (7 How. R.,) the attempt was made to i

**POSSIBLE LABEL GAP:** Catron argues that Congress cannot strip a citizen of property or equal participation in common territory. This is concrete supporting reasoning outside accepted pages, but it is a separate-opinion argument: whether it answers “the Court” requires human review under the existing controlling-reasoning standard. Not a confirmed addition; no relevance credit or label change.

Catron separate opinion in source; recorded opinion other and OCR author Oatron are preserved unchanged.

**Rank 5; score 15.591071; Dred Scott v. Sandford; `dred_scott_v_sandford.pdf`; pp141–142; chunk 109.**

Opinion: dissent; author: Mclean. Benchmark relevant: False.

> 533 .Dred ,.oU v. Randford. [M. Jusncx McLwr. in the act of 1789. - The above argument is properly met by saying that the Constitution was intended to be a practical instrument; and.where its language is too plain to be misun- derstood, the argument ends." In Chiri v. Chir, (2 Wheat., 261 4 Curtis, 99,) this court says: "That the power of naturalization v exclusively in Con- gress does not seem to be, and certainly ought not to be, con- troverted." No person can legall be made a citizen of a State, and consequently a citizen of the Unted States, of foreign birth, unless he be naturalized under the acts of Congress. Congress has power "to esta

**NO CONFIRMED LABEL GAP:** McLean discusses citizenship, outlines issues, and advances the locality-of-slavery principle in dissent; this does not provide the Court’s supporting rationale.

McLean dissent in source; original OCR author Mclean retained.

### structure_aware_v1 — OBE-01

What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

Accepted PDF ranges: [[12, 13]]. Dense first relevant rank: miss; BM25: miss. BM25 finds accepted evidence dense missed: False.

**Rank 1; score 17.880398; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp22–23; chunk 16.**

Opinion: majority; author: Kennedy. Benchmark relevant: False.

> This analysis compels the conclusion that same-sex couples may exercise the right to marry. The four principles and traditions to be discussed demonstrate that the reasons mar- riage is fundamental under the Constitution apply with equal force to same-sex couples. A frst premise of the Court's relevant precedents is that the right to personal choice regarding marriage is inherent in the concept of individual autonomy. This abiding connection between marriage and liberty is why Loving invalidated in- terracial marriage bans under the Due Process Clause. See 388 U. S., at 12; see also Zablocki, supra, at 384 (observing Loving held “the right to

**NO CONFIRMED LABEL GAP:** The majority explains fundamental-marriage-right principles and autonomy, not the two questions granted for review.



**Rank 2; score 17.285142; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp67–69; chunk 43.**

Opinion: dissent; author: Roberts. Benchmark relevant: False.

> Federal courts are blunt instruments when it comes to creating rights. They have constitutional power only to re- solve concrete cases or controversies; they do not have the fexibility of legislatures to address concerns of parties not before the court or to anticipate problems that may arise from the exercise of a new right. Today's decision, for ex- ample, creates serious questions about religious liberty. Many good and decent people oppose same-sex marriage as a tenet of faith, and their freedom to exercise religion is— unlike the right imagined by the majority—actually spelled out in the Constitution. Amdt. 1. Respect for sincere religiou

**NO CONFIRMED LABEL GAP:** Roberts discusses democracy and religious-liberty consequences; the limited certiorari questions are not stated.



**Rank 3; score 17.249911; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp74–76; chunk 48.**

Opinion: dissent; author: Scalia. Benchmark relevant: False.

> 718 OBERGEFELL v. HODGES Scalia, J., dissenting tive character of the body voting on today's social upheaval would be irrelevant if they were functioning as judges, an- swering the legal question whether the American people had ever ratifed a constitutional provision that was understood to proscribe the traditional defnition of marriage. But of course the Justices in today's majority are not voting on that basis; they say they are not. And to allow the policy ques- tion of same-sex marriage to be considered and resolved by a select, patrician, highly unrepresentative panel of nine is to violate a principle even more fundamental than no taxati

**NO CONFIRMED LABEL GAP:** Scalia criticizes democratic representation and the majority’s reasoning, not the two granted questions.



**Rank 4; score 16.151934; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp93–95; chunk 60.**

Opinion: dissent; author: Alito. Benchmark relevant: False.

> The question in these cases, however, is not what States should do about same-sex mar- riage but whether the Constitution answers that question for them. It does not. The Constitution leaves that question to be decided by the people of each State. 1 I use the phrase “recognize marriage” as shorthand for issuing mar- riage licenses and conferring those special benefts and obligations pro- vided under state law for married persons. 737 Cite as: 576 U. S. 644 (2015) Alito, J., dissenting I The Constitution says nothing about a right to same-sex marriage, but the Court holds that the term “liberty” in the Due Process Clause of the Fourteenth Amen

**NO CONFIRMED LABEL GAP:** Alito discusses whether the Constitution supplies a marriage right. The footnote’s shorthand “recognize” is not an explicit statement of the distinct out-of-state recognition question.



**Rank 5; score 15.727287; Obergefell v. Hodges; `obergefell_v_hodges.pdf`; pp1–2; chunk 1.**

Opinion: syllabus; author: not recorded. Benchmark relevant: False.

> Held: The Fourteenth Amendment requires a State to license a marriage between two people of the same sex and to recognize a marriage be- tween two people of the same sex when their marriage was lawfully licensed and performed out of State. Pp. 656–681. (a) Before turning to the governing principles and precedents, it is appropriate to note the history of the subject now before the Court. Pp. 656–663. (1) The history of marriage as a union between two persons of the opposite sex marks the beginning of these cases. To the respondents, it would demean a timeless institution if marriage were extended to same-sex couples. But the petitioners, far 

**AMBIGUOUS — PRIOR AUDIT UNRESOLVED:** The syllabus reports licensing/recognition claims and holdings, allowing a holding-based reconstruction. It does not explicitly identify the two limited certiorari questions. Preserve the prior audit’s unresolved ambiguity; do not automatically expand labels.



## Question-type and case metrics

Small subgroups; these comparisons do not establish statistically reliable routing rules.

### fixed_900_150 — by_question_type

| Group | N | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | bm25 | 0.000 | 0.000 | 1.000 | 0.250000 |
| facts | 8 | dense | 0.625 | 0.750 | 0.750 | 0.687500 |
| facts | 8 | bm25 | 0.750 | 0.875 | 1.000 | 0.822917 |
| holding | 7 | dense | 0.571 | 1.000 | 1.000 | 0.785714 |
| holding | 7 | bm25 | 0.714 | 0.857 | 0.857 | 0.761905 |
| holding_detail | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.333333 |
| legal_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.500000 |
| legal_rule | 3 | dense | 0.667 | 0.667 | 0.667 | 0.666667 |
| legal_rule | 3 | bm25 | 0.667 | 1.000 | 1.000 | 0.833333 |
| precedent | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| reasoning | 8 | dense | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | bm25 | 0.625 | 0.750 | 0.875 | 0.712500 |
| remedy | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | dense | 0.667 | 0.833 | 0.833 | 0.750000 |
| specific_detail | 6 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |

### fixed_900_150 — by_case

| Group | N | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Dred Scott v. Sandford | 5 | bm25 | 0.400 | 0.800 | 1.000 | 0.606667 |
| Gideon v. Wainwright | 5 | dense | 0.400 | 0.800 | 0.800 | 0.600000 |
| Gideon v. Wainwright | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| Marbury v. Madison | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Marbury v. Madison | 5 | bm25 | 0.600 | 0.800 | 0.800 | 0.666667 |
| Miranda v. Arizona | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Miranda v. Arizona | 5 | bm25 | 0.800 | 0.800 | 0.800 | 0.800000 |
| New York Times Co. v. United States | 5 | dense | 0.800 | 0.800 | 0.800 | 0.800000 |
| New York Times Co. v. United States | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| Obergefell v. Hodges | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Obergefell v. Hodges | 5 | bm25 | 0.600 | 0.800 | 1.000 | 0.716667 |
| Plessy v. Ferguson | 5 | dense | 0.600 | 1.000 | 1.000 | 0.800000 |
| Plessy v. Ferguson | 5 | bm25 | 0.600 | 0.800 | 1.000 | 0.750000 |
| Tinker v. Des Moines School Dist. | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | bm25 | 0.800 | 1.000 | 1.000 | 0.900000 |

### structure_aware_v1 — by_question_type

| Group | N | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| constitutional_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| constitutional_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| dissent_reasoning | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.333333 |
| facts | 8 | dense | 0.750 | 0.875 | 0.875 | 0.791667 |
| facts | 8 | bm25 | 0.500 | 0.875 | 0.875 | 0.687500 |
| holding | 7 | dense | 0.857 | 1.000 | 1.000 | 0.928571 |
| holding | 7 | bm25 | 0.571 | 0.857 | 0.857 | 0.714286 |
| holding_detail | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| holding_detail | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| jurisdiction | 1 | dense | 0.000 | 0.000 | 1.000 | 0.250000 |
| jurisdiction | 1 | bm25 | 0.000 | 0.000 | 1.000 | 0.200000 |
| legal_principle | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_principle | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| legal_rule | 3 | dense | 0.667 | 0.667 | 0.667 | 0.666667 |
| legal_rule | 3 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| precedent | 1 | bm25 | 0.000 | 1.000 | 1.000 | 0.500000 |
| reasoning | 8 | dense | 0.875 | 1.000 | 1.000 | 0.937500 |
| reasoning | 8 | bm25 | 0.625 | 0.750 | 0.875 | 0.718750 |
| remedy | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| remedy | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_detail | 6 | dense | 0.833 | 1.000 | 1.000 | 0.916667 |
| specific_detail | 6 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| specific_fact | 1 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |

### structure_aware_v1 — by_case

| Group | N | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| Dred Scott v. Sandford | 5 | dense | 0.600 | 0.800 | 0.800 | 0.700000 |
| Dred Scott v. Sandford | 5 | bm25 | 0.400 | 0.800 | 1.000 | 0.650000 |
| Gideon v. Wainwright | 5 | dense | 0.600 | 1.000 | 1.000 | 0.800000 |
| Gideon v. Wainwright | 5 | bm25 | 0.600 | 1.000 | 1.000 | 0.800000 |
| Marbury v. Madison | 5 | dense | 0.800 | 0.800 | 1.000 | 0.850000 |
| Marbury v. Madison | 5 | bm25 | 0.600 | 0.600 | 0.800 | 0.640000 |
| Miranda v. Arizona | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Miranda v. Arizona | 5 | bm25 | 0.800 | 0.800 | 0.800 | 0.800000 |
| New York Times Co. v. United States | 5 | dense | 0.800 | 1.000 | 1.000 | 0.866667 |
| New York Times Co. v. United States | 5 | bm25 | 1.000 | 1.000 | 1.000 | 1.000000 |
| Obergefell v. Hodges | 5 | dense | 0.800 | 0.800 | 0.800 | 0.800000 |
| Obergefell v. Hodges | 5 | bm25 | 0.600 | 0.800 | 0.800 | 0.700000 |
| Plessy v. Ferguson | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Plessy v. Ferguson | 5 | bm25 | 0.600 | 1.000 | 1.000 | 0.766667 |
| Tinker v. Des Moines School Dist. | 5 | dense | 1.000 | 1.000 | 1.000 | 1.000000 |
| Tinker v. Des Moines School Dist. | 5 | bm25 | 0.800 | 1.000 | 1.000 | 0.900000 |

## Corpus validation and coverage

- fixed_900_150: 598 chunks; corpus SHA-256 `6c727ec3e5f67400ecbee75ff5c0d5f4e230159826bdbd88623bea4f7cf559ba`; average BM25 term length 422.480; frozen tokenizer-token distribution {'min': 5, 'max': 897, 'mean': 602.5117056856187, 'median': 614.5}.
- structure_aware_v1: 433 chunks; corpus SHA-256 `c49afef180f2d0a1c2d055f72136879447d182e682de57ac0c36c286f2c28f7f`; average BM25 term length 602.875; frozen tokenizer-token distribution {'min': 9, 'max': 900, 'mean': 805.4780600461894, 'median': 873}.

Structure-aware excludes 200 cl100k_base tokens of foreign Sturgis/Honold material from the opening Dred Scott extraction. Fixed retains that material. These are the existing frozen corpora, not newly equalized inputs.

## Experimental limitations

- Benchmark v2 was refined using retrieval candidates from the evaluated dense systems and is not an independent holdout test.
- Page-overlap relevance can produce false positives and false negatives, including a chunk carrying only a page marker or lacking the actual answer.
- The chunk collections differ in realized size distributions and source coverage: structure-aware excludes 200 cl100k_base tokens of foreign Sturgis/Honold material retained in fixed chunks. No corpus was altered to equalize them.
- No hyperparameter tuning or label-driven tokenization choices were conducted. k1=1.5, b=.75, tokenizer, IDF convention, tie and zero-score policies were fixed before evaluation.
- Frozen OCR, headers, footnotes, and page-marker text remain in lexical inputs. No OCR repair, stemming, stopword removal, synonyms, expansion, or legal ranking boosts are applied.
- Observed differences are descriptive performance on these forty questions, not proof of general superiority. No statistical significance or reliable subgroup routing claim is made.
- Higher lexical scores do not establish greater semantic or legal correctness. Existing opinion metadata may be absent, uncertain, or inaccurate; it never affects ranking.

## Reproducibility and protected artifacts

Evaluation date: 2026-10-10, America/New_York. Reproduce locally with `.venv/bin/python run_bm25_experiment.py`. Existing output conflicts are rejected; identical replay is a no-op.

Benchmark v2 SHA-256: `aec09e3d75f9f18aec5b2448e7f420c0443bf9eb8a59e135f4a900f8a2ffd668`. Saved dense v2 SHA-256: `715c27443df5fafe5054e4ae5629bb58a611daeeb0ecc15edf9f168b47856504`.

All 107 pre-existing data files verified byte-identical by SHA-256. Full before/after hashes are recorded in the analysis JSON. No API, embedding, dense retrieval, FAISS rebuild, corpus modification, commit, or push.

READY for Phase 5B on local lexical ranking/artifact reproducibility checks. Phase 5B has not been started; no hybrid retrieval, RRF, or reranking is implemented.
