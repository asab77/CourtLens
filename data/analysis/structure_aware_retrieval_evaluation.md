# CourtLens Phase 4B.2 — structure-aware retrieval evaluation

Frozen 433-chunk corpus; reviewed 40-query benchmark. Ranking uses normalized 1536-dimensional openai/text-embedding-3-small vectors and IndexFlatIP through the existing Vercel experiment path. Top-5, unfiltered; opinion/author/type metadata is analysis-only.

## Overall comparison

| Strategy | Chunks | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|---:|
| 600_100 | 1163 | 0.650 | 0.900 | 0.925 | 0.777 |
| 900_150 | 598 | 0.725 | 0.900 | 0.900 | 0.808 |
| 1200_200 | 447 | 0.675 | 0.850 | 0.900 | 0.765 |
| 1500_200 | 287 | 0.700 | 0.800 | 0.900 | 0.764 |
| structure_aware_v1 | 433 | 0.725 | 0.875 | 0.900 | 0.802 |

Primary baseline: fixed 900/150. Absolute differences (structure-aware minus fixed):

```json
{
  "fixed_900_150": {
    "question_count": 40,
    "hit_at_1": 0.725,
    "hit_at_3": 0.9,
    "hit_at_5": 0.9,
    "mrr": 0.8083333333333333
  },
  "structure_aware_v1": {
    "question_count": 40,
    "hit_at_1": 0.725,
    "hit_at_3": 0.875,
    "hit_at_5": 0.9,
    "mrr": 0.8020833333333334
  },
  "absolute_differences": {
    "hit_at_1": 0.0,
    "hit_at_3": -0.025000000000000022,
    "hit_at_5": 0.0,
    "mrr": -0.006249999999999978
  },
  "additional_hit_at_1_successes": 0,
  "additional_top_5_successes": 0
}
```

## Question types and cases

Exploratory only; small samples do not support routing or causal conclusions.

### Question type

| Question type | N | Fixed Hit@1 / Hit@3 / Hit@5 / MRR | Structure Hit@1 / Hit@3 / Hit@5 / MRR |
|---|---:|---|---|
| constitutional_principle | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 0.000 / 1.000 / 1.000 / 0.500 |
| dissent_reasoning | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |
| facts | 8 | 0.500 / 0.750 / 0.750 / 0.604 | 0.500 / 0.750 / 0.750 / 0.604 |
| holding | 7 | 0.571 / 1.000 / 1.000 / 0.786 | 0.857 / 1.000 / 1.000 / 0.929 |
| holding_detail | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |
| jurisdiction | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 1.000 / 0.250 |
| legal_principle | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |
| legal_rule | 3 | 0.667 / 0.667 / 0.667 / 0.667 | 0.333 / 0.333 / 0.333 / 0.333 |
| precedent | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |
| reasoning | 8 | 0.875 / 1.000 / 1.000 / 0.938 | 0.875 / 1.000 / 1.000 / 0.938 |
| remedy | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |
| specific_detail | 6 | 0.667 / 0.833 / 0.833 / 0.750 | 0.833 / 1.000 / 1.000 / 0.917 |
| specific_fact | 1 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |

### Case

| Case | N | Fixed Hit@1 / Hit@3 / Hit@5 / MRR | Structure Hit@1 / Hit@3 / Hit@5 / MRR |
|---|---:|---|---|
| Dred Scott v. Sandford | 5 | 0.400 / 0.800 / 0.800 / 0.567 | 0.400 / 0.600 / 0.600 / 0.500 |
| Gideon v. Wainwright | 5 | 0.400 / 0.800 / 0.800 / 0.600 | 0.600 / 1.000 / 1.000 / 0.800 |
| Marbury v. Madison | 5 | 1.000 / 1.000 / 1.000 / 1.000 | 0.600 / 0.800 / 1.000 / 0.750 |
| Miranda v. Arizona | 5 | 1.000 / 1.000 / 1.000 / 1.000 | 0.800 / 0.800 / 0.800 / 0.800 |
| New York Times Co. v. United States | 5 | 0.800 / 0.800 / 0.800 / 0.800 | 0.800 / 1.000 / 1.000 / 0.867 |
| Obergefell v. Hodges | 5 | 0.600 / 0.800 / 0.800 / 0.700 | 0.600 / 0.800 / 0.800 / 0.700 |
| Plessy v. Ferguson | 5 | 0.600 / 1.000 / 1.000 / 0.800 | 1.000 / 1.000 / 1.000 / 1.000 |
| Tinker v. Des Moines School Dist. | 5 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 |

## Per-question changes

Both misses are counted separately from equal hit ranks.

```json
{
  "counts": {
    "structure_aware_wins": 7,
    "fixed_wins": 6,
    "tie": 25,
    "both_miss_top_5": 2
  },
  "fixed_miss_to_structure_hit": [
    "GID-05",
    "NYT-01"
  ],
  "structure_miss_to_fixed_hit": [
    "DRE-01",
    "MIR-04"
  ],
  "rank_improvements": [
    "DRE-02",
    "PLE-01",
    "PLE-04",
    "GID-04",
    "GID-05",
    "NYT-01",
    "OBE-02"
  ],
  "rank_regressions": [
    "MAR-01",
    "MAR-04",
    "DRE-01",
    "DRE-03",
    "MIR-04",
    "OBE-04"
  ]
}
```

| ID | Fixed first relevant rank | Structure first relevant rank | Outcome |
|---|---:|---:|---|
| MAR-01 | 1 | 2 | fixed_wins |
| MAR-02 | 1 | 1 | tie |
| MAR-03 | 1 | 1 | tie |
| MAR-04 | 1 | 4 | fixed_wins |
| MAR-05 | 1 | 1 | tie |
| DRE-01 | 3 | miss | fixed_wins |
| DRE-02 | 2 | 1 | structure_aware_wins |
| DRE-03 | 1 | 2 | fixed_wins |
| DRE-04 | miss | miss | both_miss_top_5 |
| DRE-05 | 1 | 1 | tie |
| PLE-01 | 2 | 1 | structure_aware_wins |
| PLE-02 | 1 | 1 | tie |
| PLE-03 | 1 | 1 | tie |
| PLE-04 | 2 | 1 | structure_aware_wins |
| PLE-05 | 1 | 1 | tie |
| GID-01 | 1 | 1 | tie |
| GID-02 | 2 | 2 | tie |
| GID-03 | 1 | 1 | tie |
| GID-04 | 2 | 1 | structure_aware_wins |
| GID-05 | miss | 2 | structure_aware_wins |
| MIR-01 | 1 | 1 | tie |
| MIR-02 | 1 | 1 | tie |
| MIR-03 | 1 | 1 | tie |
| MIR-04 | 1 | miss | fixed_wins |
| MIR-05 | 1 | 1 | tie |
| TIN-01 | 1 | 1 | tie |
| TIN-02 | 1 | 1 | tie |
| TIN-03 | 1 | 1 | tie |
| TIN-04 | 1 | 1 | tie |
| TIN-05 | 1 | 1 | tie |
| NYT-01 | miss | 3 | structure_aware_wins |
| NYT-02 | 1 | 1 | tie |
| NYT-03 | 1 | 1 | tie |
| NYT-04 | 1 | 1 | tie |
| NYT-05 | 1 | 1 | tie |
| OBE-01 | miss | miss | both_miss_top_5 |
| OBE-02 | 2 | 1 | structure_aware_wins |
| OBE-03 | 1 | 1 | tie |
| OBE-04 | 1 | 2 | fixed_wins |
| OBE-05 | 1 | 1 | tie |

## DRE-04 and OBE-01 evidence

### DRE-04

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

Reviewed relevant pages: [[3, 4]]. Structure-aware first relevant rank: Top-5 miss.

| Rank | Score | Case / opinion / raw author | Pages | Section labels | Relevant | Chunk |
|---:|---:|---|---|---|---|---|
| 1 | 0.638517 | Dred Scott v. Sandford / concurrence / Campbell | 124–125 | none | False | dred_scott_v_sandford:structure_aware_v1:00095 |
| 2 | 0.636468 | Dred Scott v. Sandford / concurrence / Grier | 97–99 | none | False | dred_scott_v_sandford:structure_aware_v1:00074 |
| 3 | 0.620205 | Dred Scott v. Sandford / dissent / Mclean | 143–145 | none | False | dred_scott_v_sandford:structure_aware_v1:00111 |
| 4 | 0.618463 | Dred Scott v. Sandford / other / Oatron | 131–132 | none | False | dred_scott_v_sandford:structure_aware_v1:00101 |
| 5 | 0.617719 | Dred Scott v. Sandford / concurrence / Campbell | 116–117 | none | False | dred_scott_v_sandford:structure_aware_v1:00089 |

**Rank 1 evidence:** The disdnguishing features of their system consist in the exclusion of the Federal Government from the local and internal con- cerns of; and in the establishment of an independent internal Government within, the States. And it is a significant fact in the history of the Unaited States, that those controversies which have been productive of the greatest animosity, and have occasioned most peril to 

**Rank 2 evidence:** But whatever the power vested in Congress, and whatever the precise subject to which that power extended, it is clear that the power related to a subject appertaining to the UnitedStates, and one to be disposed of and regulated for the benefit and under the authority of the United States. Congress was made simply the agent or trustee for the United States, andcould not, without a breach of trust a

**Rank 3 evidence:** Under another head, I shall have occasion to examine the opinion in the case of Grace. To the position, that slavery can only exist except under the authority of law, it is objected, that in few if in any in- stances has it been established by statutory enactment. This is no answer to the doctrine laid- down by the court. Almost all the principles of the common law had their foundation in usage. S

**Rank 4 evidence:** The question was then presented, how it was possible for the judicial mind to conceive that the United States Government, created solely by the Constitution, could, by a lawful treaty, acquire territory over which the ac- quiring power had no jurisdiction to hold and govern it, by force of the instrument under whose authority the country was acquired; and the foregoing was the conclusion of this c

**Rank 5 evidence:** This was frankly scnitted at the bar; in the course of this argument. The principles which this court haveprnou ced c dentn the pretension then made on behalf of the legislative department.• Tn Groves v. Slaughter, (15 Pet.,) th~e Chief Justice said: "The power over this subject is exclu- sively with the sieveral States, and each of them has a right to decid for 'itself whether it wil or will not 

Still a Top-5 miss under the frozen reviewed labels. Saved fixed results are included for direct inspection.

**Fixed 600_100 — first relevant rank: miss**

- Rank 1; score 0.663375; Dred Scott v. Sandford; pp. 1–1; 151 tokens; relevant=False. introduced into Congress and made the basis of legislation, no
interest common to the Union would have been seriously
affected.. And, certainly, the creation, within this Union, of
large confederacies of unfriendly and frowning States, which
hal been the tendency, and, to an alarming extent, the result,
produced by the agitation arising from it, does not commend
it to the patriot or statesman. Thi
- Rank 2; score 0.629266; Dred Scott v. Sandford; pp. 98–98; 574 tokens; relevant=False. 490 SUPREME COURT.
MR. JUSTWCE DANIEL.] .red cott v. Sandford.
could claim it, have the like rights of purchase, settlement,
occupation, or any other right, in the national territory.
Nothing can be more conclusive to show the equality of this
with every other right in all the citizens of the United States,
and the iniquity and absurdity of the pretension to exclude or
to disfranchise a portion of
- Rank 3; score 0.618886; Dred Scott v. Sandford; pp. 1–1; 232 tokens; relevant=False. incorporated into the State C6nstitutions. It was certainly
understood by the Convention which framed the Constitution,
aiid has been so understood ever since, that, under tht power
to regulate commerce, Congress could prohibit the importation
of slaves; and the exercise of the power Was restrained till
1808. A citizen of the United States owns ,slaves in Cuba,
and brings them to the United States
- Rank 4; score 0.616788; Dred Scott v. Sandford; pp. 1–1; 151 tokens; relevant=False. all the rights of citizens, without being naturalized under the
acts of Congress..
There are-several important principles involved in this case,
which have been argued, and which may be eonsidered under
the following heads:
1. The locality of slavery, as settled by.this court and the
courts of the States.
2. The relation which the Federal Government -bears to
slavery in the States.
8. The power of
- Rank 5; score 0.615102; Dred Scott v. Sandford; pp. 125–125; 576 tokens; relevant=False. DECEMBER TERM, 1856. 517
Dred&otu v. Sandford. [31. JU8TICZ CAXP.t,.
sional legislation or interference. The question then arises,
whether Congress, which can exercise no jurisdiction over the
relations of master and slave withiii the limits of the Union,
and is bound to recogmise and respect the rights and relations
that validly exist under the Constitutions and laws of the
States, can deny the e

**Fixed 900_150 — first relevant rank: miss**

- Rank 1; score 0.582107; Dred Scott v. Sandford; pp. 144–145; 668 tokens; relevant=False. ===== PAGE 144 =====

5686 SUPREME COURT.
M. JusTIOE MCLEAN.] Dred Scott v. Sandford.
itors; they descend to heirs, are taxed, and in the South they
are a subject of commerce.
In the case. of Rankin v. Lydia, (2 A. K. Marshall's Rep.,)
Judgl Mills, speaking for the Court of Appeals of Kentucky,
says: "In deciding the question, (of slavery,) we disclaim the
iiafluence of the general principles of l
- Rank 2; score 0.581026; Dred Scott v. Sandford; pp. 228–229; 604 tokens; relevant=False. ===== PAGE 228 =====

620 SUPREME COURT.
MR. JUSTICE CURTIS.] . )red Ecoa vr. Sandfor&
One is, that though Congress can make a regulation pro-
hibiting slavery in a Territory, they cannot make a regulation
allowing it; another is, that it can neither be established nor pro-
hibited by Congress, but that the people of a Territory, when
organized by Congress, can establish or prohibit slavery; while
- Rank 3; score 0.578102; Dred Scott v. Sandford; pp. 72–73; 655 tokens; relevant=False. ===== PAGE 72 =====

ki. Jusmcu NELSON.) Dred Scott v. Sandford.
"The ordinance in question, he observes, if still in force,
could have no more operation than the laws of Ohio in the
State of Kentucky, and could not influence the decision upon
the rights of the -master or the slaves in that State."
This view, thus aiuthoritatively declared, furnishes a conclu-
sive answer to the distinction attemp
- Rank 4; score 0.576227; Dred Scott v. Sandford; pp. 125–126; 631 tokens; relevant=False. ===== PAGE 125 =====

DECEMBER TERM, 1856. 517
Dred&otu v. Sandford. [31. JU8TICZ CAXP.t,.
sional legislation or interference. The question then arises,
whether Congress, which can exercise no jurisdiction over the
relations of master and slave withiii the limits of the Union,
and is bound to recogmise and respect the rights and relations
that validly exist under the Constitutions and laws of the

- Rank 5; score 0.574086; Dred Scott v. Sandford; pp. 235–236; 739 tokens; relevant=False. ===== PAGE 235 =====

DECEMBER TERM, 1856.
Dred SoU v. Sandford. (lh. 3us'cr Cu.
the great charter. It existed in every political community in
America in 1787,, when- the ordinance prohibiting slavery north
and west of the Ohio was passed.
And if a prohibition of slavery in a Territory in 1820 violated
this principle of Mfagna (JkarA the ordinance of 1787 also
violated it;'and what power had, I do

**Fixed 1200_200 — first relevant rank: miss**

- Rank 1; score 0.582107; Dred Scott v. Sandford; pp. 144–145; 668 tokens; relevant=False. ===== PAGE 144 =====

5686 SUPREME COURT.
M. JusTIOE MCLEAN.] Dred Scott v. Sandford.
itors; they descend to heirs, are taxed, and in the South they
are a subject of commerce.
In the case. of Rankin v. Lydia, (2 A. K. Marshall's Rep.,)
Judgl Mills, speaking for the Court of Appeals of Kentucky,
says: "In deciding the question, (of slavery,) we disclaim the
iiafluence of the general principles of l
- Rank 2; score 0.581041; Dred Scott v. Sandford; pp. 228–229; 604 tokens; relevant=False. ===== PAGE 228 =====

620 SUPREME COURT.
MR. JUSTICE CURTIS.] . )red Ecoa vr. Sandfor&
One is, that though Congress can make a regulation pro-
hibiting slavery in a Territory, they cannot make a regulation
allowing it; another is, that it can neither be established nor pro-
hibited by Congress, but that the people of a Territory, when
organized by Congress, can establish or prohibit slavery; while
- Rank 3; score 0.578102; Dred Scott v. Sandford; pp. 72–73; 655 tokens; relevant=False. ===== PAGE 72 =====

ki. Jusmcu NELSON.) Dred Scott v. Sandford.
"The ordinance in question, he observes, if still in force,
could have no more operation than the laws of Ohio in the
State of Kentucky, and could not influence the decision upon
the rights of the -master or the slaves in that State."
This view, thus aiuthoritatively declared, furnishes a conclu-
sive answer to the distinction attemp
- Rank 4; score 0.576254; Dred Scott v. Sandford; pp. 125–126; 631 tokens; relevant=False. ===== PAGE 125 =====

DECEMBER TERM, 1856. 517
Dred&otu v. Sandford. [31. JU8TICZ CAXP.t,.
sional legislation or interference. The question then arises,
whether Congress, which can exercise no jurisdiction over the
relations of master and slave withiii the limits of the Union,
and is bound to recogmise and respect the rights and relations
that validly exist under the Constitutions and laws of the

- Rank 5; score 0.574369; Dred Scott v. Sandford; pp. 235–236; 739 tokens; relevant=False. ===== PAGE 235 =====

DECEMBER TERM, 1856.
Dred SoU v. Sandford. (lh. 3us'cr Cu.
the great charter. It existed in every political community in
America in 1787,, when- the ordinance prohibiting slavery north
and west of the Ohio was passed.
And if a prohibition of slavery in a Territory in 1820 violated
this principle of Mfagna (JkarA the ordinance of 1787 also
violated it;'and what power had, I do

**Fixed 1500_200 — first relevant rank: miss**

- Rank 1; score 0.595997; Dred Scott v. Sandford; pp. 234–236; 1414 tokens; relevant=False. ===== PAGE 234 =====

SUPREME COURT.
ML. JUSTICE GUETIL.] Dred Scot v. Sanford.
slavery which existed in the particular State from which eabh
slave last came, what an anomaly is this? Where -else can we
find, -under the law of any civilized country; the power to
introduce and permanently continue diverse systems of foreign
municipal law, for holding persons in slavery? I say, not
x erely to introd
- Rank 2; score 0.579452; Dred Scott v. Sandford; pp. 224–226; 1280 tokens; relevant=False. ===== PAGE 224 =====

616 SUPREME COURT.
'M. JUSTICE CURTIS.] Dred Scou v. Sandford.
will respecting it, manifested in the Constitution, can be
snbject to no restriction. The purposes and objects of the
clause were the enactment of laws concerning the disposal of
the public lands, and the temporary government of the settlers
thereon until new States should be formed. It will not be
questioned that
- Rank 3; score 0.572917; Dred Scott v. Sandford; pp. 124–126; 1277 tokens; relevant=False. ===== PAGE 124 =====

516 SUPREME COURT.
H&. TUSTIOX CAMPBELL.) Dred ZcoU v. Sarford.
Eaired. A proscription, therefore, of the Constitution and
of one or more States, determining property, on the part
of the Federal Government, by which the stability of its social
s stem may be endangered, is plainly repugnant to the con-
ditions on which the Federal Constitution was adopted, or
which that Govern
- Rank 4; score 0.571091; Dred Scott v. Sandford; pp. 228–230; 1205 tokens; relevant=False. ===== PAGE 228 =====

620 SUPREME COURT.
MR. JUSTICE CURTIS.] . )red Ecoa vr. Sandfor&
One is, that though Congress can make a regulation pro-
hibiting slavery in a Territory, they cannot make a regulation
allowing it; another is, that it can neither be established nor pro-
hibited by Congress, but that the people of a Territory, when
organized by Congress, can establish or prohibit slavery; while
- Rank 5; score 0.570608; Dred Scott v. Sandford; pp. 150–152; 1274 tokens; relevant=False. ===== PAGE 150 =====

642 SUPREME COURT.
Mu. JUSTICE McLsAN.] Dred SoU v. Sandford.
But, if it be admitted that the word territory as used means
land, and nothing but land, the power of Congress to organize
a temporary Government is clear. It has power to make all
needful regulations -respecting the public lands, and the extent
of those "needful regulations" depends upon the direction of
Congress,

### OBE-01

What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

Reviewed relevant pages: [[12, 13]]. Structure-aware first relevant rank: Top-5 miss.

| Rank | Score | Case / opinion / raw author | Pages | Section labels | Relevant | Chunk |
|---:|---:|---|---|---|---|---|
| 1 | 0.677298 | Obergefell v. Hodges / majority / Kennedy | 19–20 | II | False | obergefell_v_hodges:structure_aware_v1:00014 |
| 2 | 0.669059 | Obergefell v. Hodges / majority / Kennedy | 36–39 | IV, V | False | obergefell_v_hodges:structure_aware_v1:00024 |
| 3 | 0.665197 | Obergefell v. Hodges / majority / Kennedy | 34–36 | IV | False | obergefell_v_hodges:structure_aware_v1:00023 |
| 4 | 0.658190 | Obergefell v. Hodges / syllabus / unknown | 1–2 | none | False | obergefell_v_hodges:structure_aware_v1:00001 |
| 5 | 0.646645 | Obergefell v. Hodges / dissent / Roberts | 43–45 | none | False | obergefell_v_hodges:structure_aware_v1:00029 |

**Rank 1 evidence:** In 1993, the Hawaii Supreme Court held Hawaii's law restricting marriage to opposite-sex couples constituted a classifcation on the basis of sex and was there- fore subject to strict scrutiny under the Hawaii Constitution. Baehr v. Lewin, 74 Haw. 530, 852 P. 2d 44. Although this decision did not mandate that same-sex marriage be allowed, some States were concerned by its implications and reaf- frm

**Rank 2 evidence:** Finally, it must be emphasized that religions, and those who adhere to religious doctrines, may continue to advocate with utmost, sincere conviction that, by divine precepts, same-sex marriage should not be condoned. The First Amendment ensures that religious organizations and persons are given proper protection as they seek to teach the princi- 680 OBERGEFELL v. HODGES Opinion of the Court ples t

**Rank 3 evidence:** In Bowers, a bare majority upheld a law crimi- 678 OBERGEFELL v. HODGES Opinion of the Court nalizing same-sex intimacy. See 478 U. S., at 190–195. That approach might have been viewed as a cautious en- dorsement of the democratic process, which had only just begun to consider the rights of gays and lesbians. Yet, in effect, Bowers upheld state action that denied gays and lesbi- ans a fundamental 

**Rank 4 evidence:** Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men whose same-sex partners are deceased, fled suits i

**Rank 5 evidence:** Chief Justice Roberts, with whom Justice Scalia and Justice Thomas join, dissenting. Petitioners make strong arguments rooted in social policy and considerations of fairness. They contend that same-sex couples should be allowed to affrm their love and commit- ment through marriage, just like opposite-sex couples. That position has undeniable appeal; over the past six years, vot- ers and legislator

Still a Top-5 miss under the frozen reviewed labels. Saved fixed results are included for direct inspection.

**Fixed 600_100 — first relevant rank: miss**

- Rank 1; score 0.641206; Obergefell v. Hodges; pp. 4–4; 561 tokens; relevant=False. 647 
Cite as: 576 U. S. 644 (2015) 
Syllabus 
marriage and are consigned to an instability many opposite-sex couples 
would fnd intolerable. It is demeaning to lock same-sex couples out of 
a central institution of the Nation's society, for they too may aspire to 
the transcendent purposes of marriage. 
The limitation of marriage to opposite-sex couples may long have 
seemed natural and just, but 
- Rank 2; score 0.630416; Obergefell v. Hodges; pp. 5–5; 561 tokens; relevant=False. 648 
 OBERGEFELL v. HODGES 
Syllabus 
(5) There may be an initial inclination to await further legislation, 
litigation, and debate, but referenda, legislative debates, and grassroots 
campaigns; studies and other writings; and extensive litigation in state 
and federal courts have led to an enhanced understanding of the issue. 
While the Constitution contemplates that democracy is the appropriate
- Rank 3; score 0.625040; Obergefell v. Hodges; pp. 50–51; 474 tokens; relevant=False. ===== PAGE 50 =====

693 
Cite as: 576 U. S. 644 (2015) 
Roberts, C. J., dissenting 
State Constitution to require recognition of same-sex mar-
riage, many States—including the four at issue here— 
enacted constitutional amendments formally adopting the 
longstanding defnition of marriage. 
Over the last few years, public opinion on marriage has 
shifted rapidly. In 2009, the legislatures of Vermo
- Rank 4; score 0.619915; Obergefell v. Hodges; pp. 33–34; 456 tokens; relevant=False. ===== PAGE 33 =====

676 
 OBERGEFELL v. HODGES 
Opinion of the Court 
same-sex couples from civil marriage on the same terms and 
conditions as opposite-sex couples. 
IV 
There may be an initial inclination in these cases to pro-
ceed with caution—to await further legislation, litigation, 
and debate. The respondents warn there has been insuff-
cient democratic discourse before deciding an issue 
- Rank 5; score 0.617969; Obergefell v. Hodges; pp. 38–39; 414 tokens; relevant=False. ===== PAGE 38 =====

681 
Cite as: 576 U. S. 644 (2015) 
Appendix A to opinion of the Court 
recognize those marriages performed elsewhere are under-
mined. See Tr. of Oral Arg. on Question 2, p. 44. The 
Court, in this decision, holds same-sex couples may exercise 
the fundamental right to marry in all States. It follows that 
the Court also must hold—and it now does hold—that there 
is no lawful

**Fixed 900_150 — first relevant rank: miss**

- Rank 1; score 0.630623; Obergefell v. Hodges; pp. 37–39; 859 tokens; relevant=False. ===== PAGE 37 =====

680 
 OBERGEFELL v. HODGES 
Opinion of the Court 
ples that are so fulflling and so central to their lives and 
faiths, and to their own deep aspirations to continue the fam-
ily structure they have long revered. The same is true of 
those who oppose same-sex marriage for other reasons. In 
turn, those who believe allowing same-sex marriage is 
proper or indeed essential, whet
- Rank 2; score 0.625040; Obergefell v. Hodges; pp. 50–51; 474 tokens; relevant=False. ===== PAGE 50 =====

693 
Cite as: 576 U. S. 644 (2015) 
Roberts, C. J., dissenting 
State Constitution to require recognition of same-sex mar-
riage, many States—including the four at issue here— 
enacted constitutional amendments formally adopting the 
longstanding defnition of marriage. 
Over the last few years, public opinion on marriage has 
shifted rapidly. In 2009, the legislatures of Vermo
- Rank 3; score 0.619915; Obergefell v. Hodges; pp. 33–34; 456 tokens; relevant=False. ===== PAGE 33 =====

676 
 OBERGEFELL v. HODGES 
Opinion of the Court 
same-sex couples from civil marriage on the same terms and 
conditions as opposite-sex couples. 
IV 
There may be an initial inclination in these cases to pro-
ceed with caution—to await further legislation, litigation, 
and debate. The respondents warn there has been insuff-
cient democratic discourse before deciding an issue 
- Rank 4; score 0.616240; Obergefell v. Hodges; pp. 97–98; 893 tokens; relevant=False. ===== PAGE 97 =====

740 
 OBERGEFELL v. HODGES 
Alito, J., dissenting 
marriage's further decay. It is far beyond the outer reaches 
of this Court's authority to say that a State may not adhere 
to the understanding of marriage that has long prevailed, not 
just in this country and others with similar cultural roots, 
but also in a great variety of countries and cultures all 
around the globe. 
A
- Rank 5; score 0.610681; Obergefell v. Hodges; pp. 1–2; 577 tokens; relevant=False. ===== PAGE 1 =====

644 
 OCTOBER TERM, 2014 
Syllabus 
OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO 
DEPARTMENT OF HEALTH 
certiorari to the united states court of appeals for 
the sixth circuit 
No. 14–556. Argued April 28, 2015—Decided June 26, 2015* 
Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be-
tween one man and one woman. The petitioners, 14 same-sex couples 
and two m

**Fixed 1200_200 — first relevant rank: miss**

- Rank 1; score 0.634330; Obergefell v. Hodges; pp. 35–37; 1006 tokens; relevant=False. ===== PAGE 35 =====

678 
 OBERGEFELL v. HODGES 
Opinion of the Court 
nalizing same-sex intimacy. See 478 U. S., at 190–195. 
That approach might have been viewed as a cautious en-
dorsement of the democratic process, which had only just 
begun to consider the rights of gays and lesbians. Yet, in 
effect, Bowers upheld state action that denied gays and lesbi-
ans a fundamental right and caused th
- Rank 2; score 0.630623; Obergefell v. Hodges; pp. 37–39; 859 tokens; relevant=False. ===== PAGE 37 =====

680 
 OBERGEFELL v. HODGES 
Opinion of the Court 
ples that are so fulflling and so central to their lives and 
faiths, and to their own deep aspirations to continue the fam-
ily structure they have long revered. The same is true of 
those who oppose same-sex marriage for other reasons. In 
turn, those who believe allowing same-sex marriage is 
proper or indeed essential, whet
- Rank 3; score 0.610639; Obergefell v. Hodges; pp. 1–2; 577 tokens; relevant=False. ===== PAGE 1 =====

644 
 OCTOBER TERM, 2014 
Syllabus 
OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO 
DEPARTMENT OF HEALTH 
certiorari to the united states court of appeals for 
the sixth circuit 
No. 14–556. Argued April 28, 2015—Decided June 26, 2015* 
Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be-
tween one man and one woman. The petitioners, 14 same-sex couples 
and two m
- Rank 4; score 0.609878; Obergefell v. Hodges; pp. 42–44; 1165 tokens; relevant=False. ===== PAGE 42 =====

685 
Cite as: 576 U. S. 644 (2015) 
Appendix B to opinion of the Court 
Li v. State, 338 Ore. 376, 110 P. 3d 91 (2005) 
Cote-Whitacre v. Department of Public Health, 446 Mass. 
350, 844 N. E. 2d 623 (2006) 
Lewis v. Harris, 188 N. J. 415, 908 A. 2d 196 (2006) 
Andersen v. King County, 158 Wash. 2d 1, 138 P. 3d 963 
(2006) 
Hernandez v. Robles, 7 N. Y . 3d 338, 855 N. E. 2d 1 (
- Rank 5; score 0.600879; Obergefell v. Hodges; pp. 33–35; 996 tokens; relevant=False. ===== PAGE 33 =====

676 
 OBERGEFELL v. HODGES 
Opinion of the Court 
same-sex couples from civil marriage on the same terms and 
conditions as opposite-sex couples. 
IV 
There may be an initial inclination in these cases to pro-
ceed with caution—to await further legislation, litigation, 
and debate. The respondents warn there has been insuff-
cient democratic discourse before deciding an issue 

**Fixed 1500_200 — first relevant rank: miss**

- Rank 1; score 0.632290; Obergefell v. Hodges; pp. 35–38; 1451 tokens; relevant=False. ===== PAGE 35 =====

678 
 OBERGEFELL v. HODGES 
Opinion of the Court 
nalizing same-sex intimacy. See 478 U. S., at 190–195. 
That approach might have been viewed as a cautious en-
dorsement of the democratic process, which had only just 
begun to consider the rights of gays and lesbians. Yet, in 
effect, Bowers upheld state action that denied gays and lesbi-
ans a fundamental right and caused th
- Rank 2; score 0.626666; Obergefell v. Hodges; pp. 1–3; 1300 tokens; relevant=False. ===== PAGE 1 =====

644 
 OCTOBER TERM, 2014 
Syllabus 
OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO 
DEPARTMENT OF HEALTH 
certiorari to the united states court of appeals for 
the sixth circuit 
No. 14–556. Argued April 28, 2015—Decided June 26, 2015* 
Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be-
tween one man and one woman. The petitioners, 14 same-sex couples 
and two m
- Rank 3; score 0.609878; Obergefell v. Hodges; pp. 42–44; 1165 tokens; relevant=False. ===== PAGE 42 =====

685 
Cite as: 576 U. S. 644 (2015) 
Appendix B to opinion of the Court 
Li v. State, 338 Ore. 376, 110 P. 3d 91 (2005) 
Cote-Whitacre v. Department of Public Health, 446 Mass. 
350, 844 N. E. 2d 623 (2006) 
Lewis v. Harris, 188 N. J. 415, 908 A. 2d 196 (2006) 
Andersen v. King County, 158 Wash. 2d 1, 138 P. 3d 963 
(2006) 
Hernandez v. Robles, 7 N. Y . 3d 338, 855 N. E. 2d 1 (
- Rank 4; score 0.603382; Obergefell v. Hodges; pp. 96–99; 1451 tokens; relevant=False. ===== PAGE 96 =====

739 
Cite as: 576 U. S. 644 (2015) 
Alito, J., dissenting 
Adherents to different schools of philosophy use different 
terms to explain why society should formalize marriage and 
attach special benefts and obligations to persons who marry. 
Here, the States defending their adherence to the traditional 
understanding of marriage have explained their position 
using the pragmati
- Rank 5; score 0.598917; Obergefell v. Hodges; pp. 38–40; 1091 tokens; relevant=False. ===== PAGE 38 =====

681 
Cite as: 576 U. S. 644 (2015) 
Appendix A to opinion of the Court 
recognize those marriages performed elsewhere are under-
mined. See Tr. of Oral Arg. on Question 2, p. 44. The 
Court, in this decision, holds same-sex couples may exercise 
the fundamental right to marry in all States. It follows that 
the Court also must hold—and it now does hold—that there 
is no lawful

## Qualitative findings from retrieved evidence

**MIR-04:** The rank-1 Warren majority passage on PDF pages 9–10 explicitly lists interrogation safeguards, including silence, evidentiary use, counsel, and stopping questioning. It remains irrelevant under frozen ranges [2,2] and [34,40]. This measured regression exposes a possible reviewed-label coverage gap; the metric and labels were not changed.

**DRE-03:** Rank 1 is the parser-labeled Curtis dissent, while the first reviewed-relevant result is at rank 2. Opinion separation retained the distinction but did not prevent an opposing discussion from outranking the target passage.

**OBE-04:** Rank 1 is the parser-labeled Roberts dissent, while the first reviewed-relevant result is at rank 2. Opinion separation retained the distinction but did not prevent an opposing discussion from outranking the target passage.

**DRE-04:** All five results are parser-labeled separate opinions: Campbell, Grier, McLean, Oatron, Campbell. None intersects frozen pages 3–4. Keeping opinions separate did not itself resolve this miss.

**OBE-01:** The first three results are Kennedy majority passages on pages 19–20, 36–39, and 34–36; syllabus is fourth and Roberts dissent fifth. None intersects frozen pages 12–13. Correct opinion identity alone did not retrieve the question-specific labeled passage.

**PLE-05:** The author mismatch flag comes from preserved OCR value Uamla. The result is a dissent and benchmark-relevant. This raw-string flag is not evidence of an established wrong-author or wrong-opinion retrieval.

**NYT-02:** The rank-1 White concurrence is relevant under the reviewed labels despite a Court-oriented wording flag. Separate-opinion flags must not be treated as automatic retrieval errors.

**MAR-03:** Unknown/front matter occupies three Top-5 positions, but the first result is relevant. Front-matter dominance is not automatically a failure. No question has three or more syllabus results.

## Opinion-aware review flags

Review flags only. Correct case plus a different opinion is not automatically irrelevant; reviewed page labels remain authoritative.

Court-oriented wording is a transparent heuristic for possible majority intent. Explicit Harlan, Black, and Brennan requests are checked against the requested author/opinion after ranking. Flags can still be benchmark-relevant.

46 candidate passages across 19 questions; 31 dissent and 13 concurrence candidates.

| Question | Rank | Opinion / author | Pages | Relevant | Reason |
|---|---:|---|---|---|---|
| DRE-02 | 4 | dissent / Curtis | 195–197 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-02 | 5 | dissent / Mclean | 138–139 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-03 | 1 | dissent / Curtis | 182–184 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-03 | 3 | dissent / Curtis | 195–197 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-04 | 1 | concurrence / Campbell | 124–125 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-04 | 2 | concurrence / Grier | 97–99 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-04 | 3 | dissent / Mclean | 143–145 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-04 | 4 | other / Oatron | 131–132 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-04 | 5 | concurrence / Campbell | 116–117 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-05 | 3 | dissent / Curtis | 194–195 | False | Separate opinion for Court-oriented wording; manual review needed |
| DRE-05 | 5 | dissent / Curtis | 187–188 | False | Separate opinion for Court-oriented wording; manual review needed |
| PLE-02 | 3 | dissent / Uamla | 16–18 | True | Separate opinion for Court-oriented wording; manual review needed |
| PLE-03 | 2 | dissent / Uamla | 20–21 | False | Separate opinion for Court-oriented wording; manual review needed |
| PLE-03 | 5 | dissent / Uamla | 25–26 | False | Separate opinion for Court-oriented wording; manual review needed |
| PLE-05 | 1 | dissent / Uamla | 23–25 | True | Explicit author/opinion mismatch |
| PLE-05 | 2 | dissent / Uamla | 26–28 | True | Explicit author/opinion mismatch |
| PLE-05 | 3 | dissent / Uamla | 20–21 | True | Explicit author/opinion mismatch |
| PLE-05 | 4 | dissent / Uamla | 21–23 | True | Explicit author/opinion mismatch |
| PLE-05 | 5 | dissent / Uamla | 25–26 | True | Explicit author/opinion mismatch |
| GID-03 | 2 | concurrence / Harlan | 15–17 | False | Separate opinion for Court-oriented wording; manual review needed |
| GID-03 | 4 | concurrence / Harlan | 17–18 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-02 | 3 | dissent / White | 93–95 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-02 | 4 | dissent / Harlan | 82–84 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-03 | 3 | dissent / White | 98–100 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-03 | 4 | dissent / White | 100–102 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-04 | 2 | dissent / White | 98–100 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-04 | 3 | other / Clark | 66–67 | False | Separate opinion for Court-oriented wording; manual review needed |
| MIR-04 | 4 | dissent / White | 96–98 | False | Separate opinion for Court-oriented wording; manual review needed |
| TIN-02 | 4 | dissent / Black | 13–15 | False | Separate opinion for Court-oriented wording; manual review needed |
| TIN-03 | 2 | dissent / Black | 19–20 | False | Separate opinion for Court-oriented wording; manual review needed |
| TIN-03 | 5 | dissent / Black | 20–22 | False | Separate opinion for Court-oriented wording; manual review needed |
| NYT-02 | 1 | concurrence / White | 18–20 | True | Separate opinion for Court-oriented wording; manual review needed |
| NYT-02 | 2 | concurrence / White | 20–22 | True | Separate opinion for Court-oriented wording; manual review needed |
| NYT-02 | 3 | dissent / Burger | 37–40 | False | Separate opinion for Court-oriented wording; manual review needed |
| NYT-02 | 5 | concurrence / Brennan | 13–15 | True | Separate opinion for Court-oriented wording; manual review needed |
| NYT-04 | 2 | concurrence / White | 18–20 | False | Explicit author/opinion mismatch |
| NYT-04 | 3 | concurrence / White | 20–22 | False | Explicit author/opinion mismatch |
| NYT-04 | 4 | concurrence / Douglas | 10–12 | False | Explicit author/opinion mismatch |
| NYT-04 | 5 | dissent / Burger | 36–38 | False | Explicit author/opinion mismatch |
| NYT-05 | 3 | concurrence / White | 18–20 | False | Explicit author/opinion mismatch |
| NYT-05 | 4 | dissent / Burger | 36–38 | False | Explicit author/opinion mismatch |
| NYT-05 | 5 | concurrence / White | 20–22 | False | Explicit author/opinion mismatch |
| OBE-01 | 5 | dissent / Roberts | 43–45 | False | Separate opinion for Court-oriented wording; manual review needed |
| OBE-02 | 5 | dissent / Scalia | 71–73 | False | Separate opinion for Court-oriented wording; manual review needed |
| OBE-04 | 1 | dissent / Roberts | 63–65 | False | Separate opinion for Court-oriented wording; manual review needed |
| OBE-04 | 5 | dissent / Roberts | 50–52 | False | Separate opinion for Court-oriented wording; manual review needed |

Unknown/front-matter or syllabus dominance (at least three Top-5 results):

```json
[
  {
    "id": "MAR-03",
    "type": "unknown",
    "top_5_count": 3,
    "first_relevant_rank": 1
  }
]
```

## Request accounting and resume behavior

```json
{
  "document": {
    "sdk_embedding_calls": 6,
    "successful_responses": 5,
    "failed_calls": 1,
    "unfinished_calls": 0,
    "input_tokens_returned": 348772,
    "responses_missing_token_usage": 0
  },
  "query": {
    "sdk_embedding_calls": 40,
    "successful_responses": 40,
    "failed_calls": 0,
    "unfinished_calls": 0,
    "input_tokens_returned": 776,
    "responses_missing_token_usage": 0
  },
  "cost": null,
  "cost_note": "No reliable currency-denominated gateway cost returned; no cost estimate made.",
  "request_count_scope": "SDK create calls including bounded helper retries; SDK-internal HTTP retries may add wire requests."
}
```

Document embedding uses 100-record batches with the existing 10-second successful-batch pacing and 60/120/240-second bounded rate-limit retry schedule. Authentication failures propagate. No document-batch checkpoint exists: a failed document build restarts embedding from record 1. No incomplete final store is published. A complete validated store is reused, and successfully evaluated queries resume from the saved checkpoint.

## Limitations

- Structure-aware_v1 changes both boundary selection and the realized chunk-size distribution relative to the existing fixed 900/150 implementation.
- Fixed mean 602.51 / median 614.5; structure-aware mean 805.48 / median 873 tokens.
- The experiment evaluates the complete strategy; changes cannot be attributed solely to legal structure.
- 40 questions; five per case; many type samples are tiny. No statistical significance testing performed.
- Reviewed ranges came from the fixed Top-5 pool and may omit answer-bearing structure-aware passages. Labels remain frozen.
- Inclusive page intersection can count passages without independent answer-bearing text; opinion correctness requires qualitative review.
- Same provider/model, but query/document calls occur later than the saved fixed experiment; provider deployment determinism is not guaranteed.

## Protected artifacts

```json
{
  "checked_files": 81,
  "unchanged": true,
  "chunks_sha256_before": "0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4",
  "chunks_sha256_after": "0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4",
  "protected_before": {
    "analyze_long_sentences.py": "8d416faa7509a57c5b416eef084a1fe08ab12b0c8231be2f8b05f29483b8bcbb",
    "data/analysis/long_sentence_analysis.json": "3fc7987789e3eac714f3ffc1a4badac762a6a89455b943298fede200c7a80418",
    "data/analysis/long_sentence_analysis.md": "2ce3d588d1b2e13eb91d66c2c450dc2ecc9612d7dc746f35fbc486fe79c95ca2",
    "data/analysis/structure_aware_chunking.json": "90fda71f43c598a1cc24815c1201e776b48220750e42712d5a83c9dc1bc90bbd",
    "data/analysis/structure_aware_chunking.md": "a84560f5ecf32faa71afdaf5bb8af6ce50343daafbd4838eb1b48c5ac2740b29",
    "data/analysis/structure_aware_preview.json": "0ade8e9853a10b8a57b0962ceeb839ed7493892caab903dd3b1b8dbfa9fa8442",
    "data/analysis/structure_aware_preview.md": "5d913b2f88147fd9152890cf4402269f47a42c16d20494d9472f4e183bdca48c",
    "data/chunks/dred_scott_v_sandford.jsonl": "6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34",
    "data/chunks/gideon_v_wainwright.jsonl": "c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15",
    "data/chunks/marbury_v_madison.jsonl": "3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a",
    "data/chunks/miranda_v_arizona.jsonl": "8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b",
    "data/chunks/new_york_times_co_v_united_states.jsonl": "bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1",
    "data/chunks/obergefell_v_hodges.jsonl": "d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8",
    "data/chunks/plessy_v_ferguson.jsonl": "5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647",
    "data/chunks/tinker_v_des_moines_school_dist.jsonl": "15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768",
    "data/evaluation/chunking_benchmark.json": "00fc21f465043a09a209e8509f0513378cd6e385d62ca6dbfc7e09940a7eda3d",
    "data/evaluation/chunking_benchmark_review.json": "0cf60ecefd0e39df07d2eb76d8f8e629f499d92a190b293ffa70013795869370",
    "data/evaluation/chunking_benchmark_review.md": "13637d6f8dcd2f46a568085f4c22d9898301ddd45a2438da0ed6610c5ea09a15",
    "data/evaluation/chunking_benchmark_reviewed.json": "7cbfa42bf480717df7b7982297f8ea648a30a8d100d86ccdcaa5371b410b7595",
    "data/experiments/chunking/1200_200/chunks/dred_scott_v_sandford.jsonl": "6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34",
    "data/experiments/chunking/1200_200/chunks/gideon_v_wainwright.jsonl": "c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15",
    "data/experiments/chunking/1200_200/chunks/marbury_v_madison.jsonl": "3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a",
    "data/experiments/chunking/1200_200/chunks/miranda_v_arizona.jsonl": "8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b",
    "data/experiments/chunking/1200_200/chunks/new_york_times_co_v_united_states.jsonl": "bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1",
    "data/experiments/chunking/1200_200/chunks/obergefell_v_hodges.jsonl": "d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8",
    "data/experiments/chunking/1200_200/chunks/plessy_v_ferguson.jsonl": "5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647",
    "data/experiments/chunking/1200_200/chunks/tinker_v_des_moines_school_dist.jsonl": "15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768",
    "data/experiments/chunking/1200_200/vector_store/index.faiss": "b8b7eb8795c385630cde542a8ec080cfd3db45eace57fcb741390d73f1214398",
    "data/experiments/chunking/1200_200/vector_store/manifest.json": "5c7c2d0550c78829d9d1b462bf97e19a31a96665f5dd99e993158c88de1f75b8",
    "data/experiments/chunking/1200_200/vector_store/records.jsonl": "0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648",
    "data/experiments/chunking/1500_200/chunks/dred_scott_v_sandford.jsonl": "10fae0685c82e38a761c0a4ea1d0071cd786e235a1dfc7a9c28f8de37c8e2742",
    "data/experiments/chunking/1500_200/chunks/gideon_v_wainwright.jsonl": "e8bd0ecadc3796c4db4985c10908008c139099c5b62cd6bfea2194ea7e645b28",
    "data/experiments/chunking/1500_200/chunks/marbury_v_madison.jsonl": "80e45c23b528fb783921f120237b5e27bf3063b8e2d0bfa0e2b9bc948971ef67",
    "data/experiments/chunking/1500_200/chunks/miranda_v_arizona.jsonl": "83d06f72d784b34fb414533653b1b80b17c213c82b99d00d0d3f5731999e92ef",
    "data/experiments/chunking/1500_200/chunks/new_york_times_co_v_united_states.jsonl": "87664a9f120da592273464784219306c2fe365438a54909a215d5938a0e89153",
    "data/experiments/chunking/1500_200/chunks/obergefell_v_hodges.jsonl": "3de38ca2d4fb4583ef212b45c71d0a51d69c7f4a241281fa3616eaf54effa11e",
    "data/experiments/chunking/1500_200/chunks/plessy_v_ferguson.jsonl": "f1dcc04ad0f49021e96df4781dedd9afcdcbe71d91d4a76f4de70eac4a3a56d6",
    "data/experiments/chunking/1500_200/chunks/tinker_v_des_moines_school_dist.jsonl": "81f365dd0aeea97e9faf0e4e7ebe9db7650b05f8a200945e86df39180e4c97dd",
    "data/experiments/chunking/1500_200/vector_store/index.faiss": "2e2a48e74ca9838482e4e091c20143b5c2d86282efd4588952329e13528184b2",
    "data/experiments/chunking/1500_200/vector_store/manifest.json": "6ab26c41d30b64583060470fde6704689f0053566b6947bbc7d83ddb1f01ef65",
    "data/experiments/chunking/1500_200/vector_store/records.jsonl": "42ffe0a0695d22b097bf8a2697f79d7ba549b4660d92f6e791e3f21b3afdc3b3",
    "data/experiments/chunking/600_100/chunks/dred_scott_v_sandford.jsonl": "c1609a75f1a36e53a097220f6c2dcb453f1216a768450c5b6071701e1ca71080",
    "data/experiments/chunking/600_100/chunks/gideon_v_wainwright.jsonl": "71459a6ad063507872da02249c2cdd4ecdafee1c6704b10d7a3ebe5c9265e410",
    "data/experiments/chunking/600_100/chunks/marbury_v_madison.jsonl": "a0cac67fddac8a95120c9d8c71dd372251c289a4cf79c03ae34e767ba4df593c",
    "data/experiments/chunking/600_100/chunks/miranda_v_arizona.jsonl": "fb5f22856d7410cac34b0ab71ec7defb82d19be231504036ab2f56bb8c0cb0e9",
    "data/experiments/chunking/600_100/chunks/new_york_times_co_v_united_states.jsonl": "a5f350297a6c5d3332149c38dfcea9a041b78e85e29fb55a011278055d5e94f2",
    "data/experiments/chunking/600_100/chunks/obergefell_v_hodges.jsonl": "2b0b30dfc0b05ae2e7d70111f0443740db5512b6192014c7c386211e1cbf9916",
    "data/experiments/chunking/600_100/chunks/plessy_v_ferguson.jsonl": "805a90d67ec45dc7ae6100cede7e3f745fa9d8fd5cf9fbeef1fcf7500a7e4108",
    "data/experiments/chunking/600_100/chunks/tinker_v_des_moines_school_dist.jsonl": "8066cc3b9ad15af0e214662003ca4c26c495b92d2ddd1bd184f79f388fb14ee3",
    "data/experiments/chunking/600_100/vector_store/index.faiss": "8e3ff55615273bc2c6e2b8f6831f276f9d6c38380c99acd09f744b897528e721",
    "data/experiments/chunking/600_100/vector_store/manifest.json": "6aff4f97e7314fb5e32369ee843f1b9debbbee303d132a11129905dac5b889d5",
    "data/experiments/chunking/600_100/vector_store/records.jsonl": "ef7c320e39ff67ebc5671a1f0e4473840cb314a88774a389ac580011c727e98d",
    "data/experiments/chunking/900_150/chunks/dred_scott_v_sandford.jsonl": "adaf3e4ebcc1f39a4de19548a4757ea57ad248a49eebaeef8ad55a3123432c40",
    "data/experiments/chunking/900_150/chunks/gideon_v_wainwright.jsonl": "2254a634b4c027e8049ee0488dfed74454388d805fa5e6a06f3baa0a001c8713",
    "data/experiments/chunking/900_150/chunks/marbury_v_madison.jsonl": "eb15fe41780d6e0451f637bbb1a62ee2a5f2f57e3f6cdd857df12e31cdf2edd4",
    "data/experiments/chunking/900_150/chunks/miranda_v_arizona.jsonl": "e62baecf9c2b45c05fc41ded6420f9951b87b816a0de8b2738d04308a7f8ada0",
    "data/experiments/chunking/900_150/chunks/new_york_times_co_v_united_states.jsonl": "a13bd800e9efe0fa3bc16127e0f7574a7f802b11719533aa19d6f9c762190ce0",
    "data/experiments/chunking/900_150/chunks/obergefell_v_hodges.jsonl": "2ab41ed081307b758da2ce031174e0815eef6622a2659b4b7871e1148c54368d",
    "data/experiments/chunking/900_150/chunks/plessy_v_ferguson.jsonl": "fd71d62c3f41f0cba8eeb960dc950a77a17b0d50a69c7fa83402ebed283e4203",
    "data/experiments/chunking/900_150/chunks/tinker_v_des_moines_school_dist.jsonl": "a68cd3727081d496f32e22828fdf7b4eab5882d5e541f2b7273d24ce624341eb",
    "data/experiments/chunking/900_150/vector_store/index.faiss": "e12f8a02f9b35fa9326fb830b917bdfdf41e5ba4aceccb0c2b806329770cc2a8",
    "data/experiments/chunking/900_150/vector_store/manifest.json": "846e19759df7714867d5353a60401e326439bb4fb92d9454986b9ce2124a4c99",
    "data/experiments/chunking/900_150/vector_store/records.jsonl": "f56cbda97ec73461c0c35f97cbc7575ce9ecf55c77beb5873377285c9d595f69",
    "data/experiments/chunking/results.json": "95ca699ef2be19f511d1a98508deeb6fb7c458228ee770e79f7afe83d7e6a123",
    "data/experiments/chunking/reviewed_results.json": "2e0d3d287b3e880dff3227939dbc796a75296986b9bbef9e86907e1d5c6e32ee",
    "data/experiments/chunking/structure_aware_v1/chunks.jsonl": "0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4",
    "data/experiments/chunking/structure_aware_v1/manifest.json": "d72c5703be6121228a107611ed47d0926424fa86a983ac83e747fe305f7d9e5d",
    "data/processed/dred_scott_v_sandford.txt": "1eb4617eebf3647626d7d3d4e142615c99d3cfbfdb7de80ce9c39b97b05b80ed",
    "data/processed/gideon_v_wainwright.txt": "10e0e4b6a2a7382d913a3cf3c1a8a3fa99aecdbbb14cfcee19011a4adce5db35",
    "data/processed/marbury_v_madison.txt": "85f4f933f9614718ca426da9545ae101778d39f88ee3fecd9bbb02081da74da1",
    "data/processed/miranda_v_arizona.txt": "872ba83c615f9d35e3f7ac841bc441d21dbc9e6ca22756314b42d12bb8cf9e6d",
    "data/processed/new_york_times_co_v_united_states.txt": "59a716ac534351d0ca21b10620ae31a2f27f9de4609feafbe1be9e8719496d49",
    "data/processed/obergefell_v_hodges.txt": "50267b559e1daf5e1c7859f8d3a167db54d128df11fc8ed9bfedbf33f5062b0b",
    "data/processed/plessy_v_ferguson.txt": "c15341b4e08e7060b6f089b1d2ee43ce0fc760020d53e0e943e88931a0fd191f",
    "data/processed/tinker_v_des_moines_school_dist.txt": "0d534a5e970cd117e9a397b6859ea4cb33c8f47a880d3c31e39a767e93df9dd7",
    "data/vector_store/index.faiss": "b81997170c48a649b84613ba4376c982c231acd27e610bda6e460c66a5d58a1c",
    "data/vector_store/manifest.json": "a97cecfdf385a49513c82b5fff1909053a77c74e833beffd773d3e54bffd5933",
    "data/vector_store/records.jsonl": "0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648",
    "generate_structure_aware_chunks.py": "00d5e378f93dad3edee8e90a7219b5f47aebf4cdb02a2460df304f530fd6bcb9",
    "local_tokenizer.py": "244bc3c2d7e613f6fc61b33e217deb0ec59554a7787217528e2ed22a4f55c5ee",
    "parse_legal_structure.py": "78d83a625d3316598c68bb92fd5c32d8e327c1f86698b48021bb38d5940e8ff3"
  },
  "protected_after": {
    "analyze_long_sentences.py": "8d416faa7509a57c5b416eef084a1fe08ab12b0c8231be2f8b05f29483b8bcbb",
    "data/analysis/long_sentence_analysis.json": "3fc7987789e3eac714f3ffc1a4badac762a6a89455b943298fede200c7a80418",
    "data/analysis/long_sentence_analysis.md": "2ce3d588d1b2e13eb91d66c2c450dc2ecc9612d7dc746f35fbc486fe79c95ca2",
    "data/analysis/structure_aware_chunking.json": "90fda71f43c598a1cc24815c1201e776b48220750e42712d5a83c9dc1bc90bbd",
    "data/analysis/structure_aware_chunking.md": "a84560f5ecf32faa71afdaf5bb8af6ce50343daafbd4838eb1b48c5ac2740b29",
    "data/analysis/structure_aware_preview.json": "0ade8e9853a10b8a57b0962ceeb839ed7493892caab903dd3b1b8dbfa9fa8442",
    "data/analysis/structure_aware_preview.md": "5d913b2f88147fd9152890cf4402269f47a42c16d20494d9472f4e183bdca48c",
    "data/chunks/dred_scott_v_sandford.jsonl": "6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34",
    "data/chunks/gideon_v_wainwright.jsonl": "c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15",
    "data/chunks/marbury_v_madison.jsonl": "3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a",
    "data/chunks/miranda_v_arizona.jsonl": "8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b",
    "data/chunks/new_york_times_co_v_united_states.jsonl": "bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1",
    "data/chunks/obergefell_v_hodges.jsonl": "d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8",
    "data/chunks/plessy_v_ferguson.jsonl": "5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647",
    "data/chunks/tinker_v_des_moines_school_dist.jsonl": "15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768",
    "data/evaluation/chunking_benchmark.json": "00fc21f465043a09a209e8509f0513378cd6e385d62ca6dbfc7e09940a7eda3d",
    "data/evaluation/chunking_benchmark_review.json": "0cf60ecefd0e39df07d2eb76d8f8e629f499d92a190b293ffa70013795869370",
    "data/evaluation/chunking_benchmark_review.md": "13637d6f8dcd2f46a568085f4c22d9898301ddd45a2438da0ed6610c5ea09a15",
    "data/evaluation/chunking_benchmark_reviewed.json": "7cbfa42bf480717df7b7982297f8ea648a30a8d100d86ccdcaa5371b410b7595",
    "data/experiments/chunking/1200_200/chunks/dred_scott_v_sandford.jsonl": "6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34",
    "data/experiments/chunking/1200_200/chunks/gideon_v_wainwright.jsonl": "c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15",
    "data/experiments/chunking/1200_200/chunks/marbury_v_madison.jsonl": "3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a",
    "data/experiments/chunking/1200_200/chunks/miranda_v_arizona.jsonl": "8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b",
    "data/experiments/chunking/1200_200/chunks/new_york_times_co_v_united_states.jsonl": "bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1",
    "data/experiments/chunking/1200_200/chunks/obergefell_v_hodges.jsonl": "d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8",
    "data/experiments/chunking/1200_200/chunks/plessy_v_ferguson.jsonl": "5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647",
    "data/experiments/chunking/1200_200/chunks/tinker_v_des_moines_school_dist.jsonl": "15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768",
    "data/experiments/chunking/1200_200/vector_store/index.faiss": "b8b7eb8795c385630cde542a8ec080cfd3db45eace57fcb741390d73f1214398",
    "data/experiments/chunking/1200_200/vector_store/manifest.json": "5c7c2d0550c78829d9d1b462bf97e19a31a96665f5dd99e993158c88de1f75b8",
    "data/experiments/chunking/1200_200/vector_store/records.jsonl": "0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648",
    "data/experiments/chunking/1500_200/chunks/dred_scott_v_sandford.jsonl": "10fae0685c82e38a761c0a4ea1d0071cd786e235a1dfc7a9c28f8de37c8e2742",
    "data/experiments/chunking/1500_200/chunks/gideon_v_wainwright.jsonl": "e8bd0ecadc3796c4db4985c10908008c139099c5b62cd6bfea2194ea7e645b28",
    "data/experiments/chunking/1500_200/chunks/marbury_v_madison.jsonl": "80e45c23b528fb783921f120237b5e27bf3063b8e2d0bfa0e2b9bc948971ef67",
    "data/experiments/chunking/1500_200/chunks/miranda_v_arizona.jsonl": "83d06f72d784b34fb414533653b1b80b17c213c82b99d00d0d3f5731999e92ef",
    "data/experiments/chunking/1500_200/chunks/new_york_times_co_v_united_states.jsonl": "87664a9f120da592273464784219306c2fe365438a54909a215d5938a0e89153",
    "data/experiments/chunking/1500_200/chunks/obergefell_v_hodges.jsonl": "3de38ca2d4fb4583ef212b45c71d0a51d69c7f4a241281fa3616eaf54effa11e",
    "data/experiments/chunking/1500_200/chunks/plessy_v_ferguson.jsonl": "f1dcc04ad0f49021e96df4781dedd9afcdcbe71d91d4a76f4de70eac4a3a56d6",
    "data/experiments/chunking/1500_200/chunks/tinker_v_des_moines_school_dist.jsonl": "81f365dd0aeea97e9faf0e4e7ebe9db7650b05f8a200945e86df39180e4c97dd",
    "data/experiments/chunking/1500_200/vector_store/index.faiss": "2e2a48e74ca9838482e4e091c20143b5c2d86282efd4588952329e13528184b2",
    "data/experiments/chunking/1500_200/vector_store/manifest.json": "6ab26c41d30b64583060470fde6704689f0053566b6947bbc7d83ddb1f01ef65",
    "data/experiments/chunking/1500_200/vector_store/records.jsonl": "42ffe0a0695d22b097bf8a2697f79d7ba549b4660d92f6e791e3f21b3afdc3b3",
    "data/experiments/chunking/600_100/chunks/dred_scott_v_sandford.jsonl": "c1609a75f1a36e53a097220f6c2dcb453f1216a768450c5b6071701e1ca71080",
    "data/experiments/chunking/600_100/chunks/gideon_v_wainwright.jsonl": "71459a6ad063507872da02249c2cdd4ecdafee1c6704b10d7a3ebe5c9265e410",
    "data/experiments/chunking/600_100/chunks/marbury_v_madison.jsonl": "a0cac67fddac8a95120c9d8c71dd372251c289a4cf79c03ae34e767ba4df593c",
    "data/experiments/chunking/600_100/chunks/miranda_v_arizona.jsonl": "fb5f22856d7410cac34b0ab71ec7defb82d19be231504036ab2f56bb8c0cb0e9",
    "data/experiments/chunking/600_100/chunks/new_york_times_co_v_united_states.jsonl": "a5f350297a6c5d3332149c38dfcea9a041b78e85e29fb55a011278055d5e94f2",
    "data/experiments/chunking/600_100/chunks/obergefell_v_hodges.jsonl": "2b0b30dfc0b05ae2e7d70111f0443740db5512b6192014c7c386211e1cbf9916",
    "data/experiments/chunking/600_100/chunks/plessy_v_ferguson.jsonl": "805a90d67ec45dc7ae6100cede7e3f745fa9d8fd5cf9fbeef1fcf7500a7e4108",
    "data/experiments/chunking/600_100/chunks/tinker_v_des_moines_school_dist.jsonl": "8066cc3b9ad15af0e214662003ca4c26c495b92d2ddd1bd184f79f388fb14ee3",
    "data/experiments/chunking/600_100/vector_store/index.faiss": "8e3ff55615273bc2c6e2b8f6831f276f9d6c38380c99acd09f744b897528e721",
    "data/experiments/chunking/600_100/vector_store/manifest.json": "6aff4f97e7314fb5e32369ee843f1b9debbbee303d132a11129905dac5b889d5",
    "data/experiments/chunking/600_100/vector_store/records.jsonl": "ef7c320e39ff67ebc5671a1f0e4473840cb314a88774a389ac580011c727e98d",
    "data/experiments/chunking/900_150/chunks/dred_scott_v_sandford.jsonl": "adaf3e4ebcc1f39a4de19548a4757ea57ad248a49eebaeef8ad55a3123432c40",
    "data/experiments/chunking/900_150/chunks/gideon_v_wainwright.jsonl": "2254a634b4c027e8049ee0488dfed74454388d805fa5e6a06f3baa0a001c8713",
    "data/experiments/chunking/900_150/chunks/marbury_v_madison.jsonl": "eb15fe41780d6e0451f637bbb1a62ee2a5f2f57e3f6cdd857df12e31cdf2edd4",
    "data/experiments/chunking/900_150/chunks/miranda_v_arizona.jsonl": "e62baecf9c2b45c05fc41ded6420f9951b87b816a0de8b2738d04308a7f8ada0",
    "data/experiments/chunking/900_150/chunks/new_york_times_co_v_united_states.jsonl": "a13bd800e9efe0fa3bc16127e0f7574a7f802b11719533aa19d6f9c762190ce0",
    "data/experiments/chunking/900_150/chunks/obergefell_v_hodges.jsonl": "2ab41ed081307b758da2ce031174e0815eef6622a2659b4b7871e1148c54368d",
    "data/experiments/chunking/900_150/chunks/plessy_v_ferguson.jsonl": "fd71d62c3f41f0cba8eeb960dc950a77a17b0d50a69c7fa83402ebed283e4203",
    "data/experiments/chunking/900_150/chunks/tinker_v_des_moines_school_dist.jsonl": "a68cd3727081d496f32e22828fdf7b4eab5882d5e541f2b7273d24ce624341eb",
    "data/experiments/chunking/900_150/vector_store/index.faiss": "e12f8a02f9b35fa9326fb830b917bdfdf41e5ba4aceccb0c2b806329770cc2a8",
    "data/experiments/chunking/900_150/vector_store/manifest.json": "846e19759df7714867d5353a60401e326439bb4fb92d9454986b9ce2124a4c99",
    "data/experiments/chunking/900_150/vector_store/records.jsonl": "f56cbda97ec73461c0c35f97cbc7575ce9ecf55c77beb5873377285c9d595f69",
    "data/experiments/chunking/results.json": "95ca699ef2be19f511d1a98508deeb6fb7c458228ee770e79f7afe83d7e6a123",
    "data/experiments/chunking/reviewed_results.json": "2e0d3d287b3e880dff3227939dbc796a75296986b9bbef9e86907e1d5c6e32ee",
    "data/experiments/chunking/structure_aware_v1/chunks.jsonl": "0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4",
    "data/experiments/chunking/structure_aware_v1/manifest.json": "d72c5703be6121228a107611ed47d0926424fa86a983ac83e747fe305f7d9e5d",
    "data/processed/dred_scott_v_sandford.txt": "1eb4617eebf3647626d7d3d4e142615c99d3cfbfdb7de80ce9c39b97b05b80ed",
    "data/processed/gideon_v_wainwright.txt": "10e0e4b6a2a7382d913a3cf3c1a8a3fa99aecdbbb14cfcee19011a4adce5db35",
    "data/processed/marbury_v_madison.txt": "85f4f933f9614718ca426da9545ae101778d39f88ee3fecd9bbb02081da74da1",
    "data/processed/miranda_v_arizona.txt": "872ba83c615f9d35e3f7ac841bc441d21dbc9e6ca22756314b42d12bb8cf9e6d",
    "data/processed/new_york_times_co_v_united_states.txt": "59a716ac534351d0ca21b10620ae31a2f27f9de4609feafbe1be9e8719496d49",
    "data/processed/obergefell_v_hodges.txt": "50267b559e1daf5e1c7859f8d3a167db54d128df11fc8ed9bfedbf33f5062b0b",
    "data/processed/plessy_v_ferguson.txt": "c15341b4e08e7060b6f089b1d2ee43ce0fc760020d53e0e943e88931a0fd191f",
    "data/processed/tinker_v_des_moines_school_dist.txt": "0d534a5e970cd117e9a397b6859ea4cb33c8f47a880d3c31e39a767e93df9dd7",
    "data/vector_store/index.faiss": "b81997170c48a649b84613ba4376c982c231acd27e610bda6e460c66a5d58a1c",
    "data/vector_store/manifest.json": "a97cecfdf385a49513c82b5fff1909053a77c74e833beffd773d3e54bffd5933",
    "data/vector_store/records.jsonl": "0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648",
    "generate_structure_aware_chunks.py": "00d5e378f93dad3edee8e90a7219b5f47aebf4cdb02a2460df304f530fd6bcb9",
    "local_tokenizer.py": "244bc3c2d7e613f6fc61b33e217deb0ec59554a7787217528e2ed22a4f55c5ee",
    "parse_legal_structure.py": "78d83a625d3316598c68bb92fd5c32d8e327c1f86698b48021bb38d5940e8ff3"
  }
}
```

Chunk construction and labels remained frozen. No fixed retrieval was rerun, no production artifact was modified, and no v2, BM25, hybrid search, reranking or routing was implemented.

## Next experiment

First manually review the listed regressions and DRE-04/OBE-01 evidence under the frozen labels. A separately designed, size-matched comparison would help distinguish boundary effects from realized granularity; these results alone cannot establish causation. No next experiment was implemented.
