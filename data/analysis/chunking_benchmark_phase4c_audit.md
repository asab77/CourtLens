# CourtLens Phase 4C — targeted benchmark audit

**PROPOSED AUDIT — LABELS NOT APPLIED.** Exactly eight questions; 80 candidate appearances (five saved results from each strategy per question).

Manual passage-level judgments, source-verified against extracted CourtLens texts. Rank/similarity are navigation only. No automatic relevance classifier.

Require independent substantive evidence for the question. Components of a multi-part safeguards answer may qualify, as in the previous review. For Court-reasoning questions, distinguish supporting controlling reasoning from opposing theories. Accurate attributed majority quotations can answer even when embedded in a dissent; factual residence narratives are not excluded by opinion type. Ambiguous procedural/holding and concurrence boundaries are not proposed as additions.

Decisions were made from the question and complete source-verified text before computing any proposed metric impact. The initial JSON was written without a simulation; its questions are frozen by SHA-256. The optional simulation reads that frozen artifact.

PDF page numbers are extraction markers, not printed reporter pagination. Evidence excerpts normalize whitespace only; full retrieved text and canonical proposed-page text are in the JSON. OCR spellings and dates are not silently repaired. Similarity does not determine a decision.

## Proposed additions — do not apply

| Question | Current ranges | Proposed additions | Conclusion |
|---|---|---|---|
| DRE-01 | [[5, 6]] | [[39, 40], [167, 167]] | Confirmed incomplete: majority restatement on pages 39–40 and Scott-specific factual narrative in McLean’s dissent on page 167 independently answer the question. A blanket exclusion of separate opinions was too restrictive for residence facts. |
| MIR-04 | [[2, 2], [34, 40]] | [[9, 10], [67, 67]] | Confirmed incomplete: Warren’s pages 9–10 give the required safeguards independently. Clark’s page 67 also accurately lists several new requirements while criticizing them. The question asks what safeguards were required, so accurate reports are admissible evidence; it does not ask for Clark’s rationale. |
| MAR-01 | [[2, 2], [18, 19], [37, 38]] | [[32, 32], [36, 36]] | Confirmed incomplete: pages 32 and 36 expressly give the violated commission right and the delivery remedy. Topic-only mandamus discussions remain ambiguous or irrelevant. |
| MAR-04 | [[37, 40]] | None | No confirmed addition from these candidates. The accepted source pages 38–40 explain Article III’s allocation and why this writ would be original. Fixed rank 1 only previews unconstitutionality on page 37 and carries an empty page-38 marker: an apparent page-level false positive/incomplete answer, not evidence that every accepted page range is wrong. |
| DRE-03 | [[10, 12], [24, 28]] | [[33, 34]] | Confirmed incomplete on pages 33–34. Curtis’s high-ranked dissent provides the contrary citizenship theory, not the Court’s exclusion rationale. The issue-framing chunks on pages 10–11/11–12 also illustrate overinclusive page-level credit. |
| OBE-04 | [[4, 4], [28, 32]] | [[64, 64]] | Confirmed incomplete on page 64: Roberts reproduces the majority’s actual explanation, verified on majority page 29. This is relevant quoted majority reasoning, although Roberts’s own criticism is not controlling reasoning. The preceding page-63 summary is ambiguous. |
| DRE-04 | [[3, 4]] | None | No unambiguous addition from the saved Top-5. The question asks for the Court’s reason, and the accepted pages 3–4 summarize constitutional property/equal-access limits. Majority pages 58–60 confirm the property/due-process rationale as context only, not an addition proposed in this candidate-limited audit. Campbell and Daniel concurrences need human judgment; McLean, Curtis, Nelson, and Catron passages do not independently establish that controlling rationale. The Grier/Daniel attribution discrepancy is documented, not repaired. |
| OBE-01 | [[12, 13]] | None | No unambiguous addition. Page 13 explicitly enumerates the two limited granted questions: Fourteenth Amendment licensing and recognition of lawful out-of-state same-sex marriages. A holding/syllabus reconstruction is ambiguous under this procedural wording. Retain the current ranges pending human judgment. |

## All candidate decisions

R = RELEVANT; N = NOT_RELEVANT; A = AMBIGUOUS. Columns list ranks 1–5 in order. See evidence and rationale below for each appearance.

| Question | Fixed 900/150 ranks 1–5 | Structure-aware ranks 1–5 |
|---|---|---|
| DRE-01 | R, N, R, N, N | R, R, N, N, N |
| MIR-04 | R, A, N, R, N | R, N, R, N, N |
| MAR-01 | R, R, R, A, R | R, R, R, A, R |
| MAR-04 | A, N, N, N, N | N, N, N, N, N |
| DRE-03 | R, N, R, N, N | N, R, N, N, R |
| OBE-04 | R, R, A, N, R | R, R, R, R, N |
| DRE-04 | N, N, N, A, N | A, A, N, N, N |
| OBE-01 | A, N, N, N, A | N, A, N, A, N |

## Limitations and human judgments

- This audit only assesses the selected eight questions and their saved Top-5 candidates. “No confirmed addition” does not establish that every relevant passage in the entire opinion is labeled.
- Page ranges are a coarse proxy. MAR-04 fixed rank 1 lacks the original/appellate rationale, DRE-03 issue-framing chunks lack the supporting citizenship rationale, and MIR-04 fixed rank 5 lacks the page-44 warning list. Official page-overlap credit is preserved in the simulation, not mistaken for manual relevance.
- MIR-04 fixed rank 2 ends with a page-67 marker before the actual explicit list. Adding page 67 can credit that chunk mechanically even though its FBI comparison remains ambiguous. OBE-04 fixed rank 3 similarly ends with a page-64 marker before the majority quotation.
- OBE-01 holding/syllabus passages identify licensing and recognition substantively but do not explicitly identify both limited granted questions. Four candidates remain ambiguous; source page 13 is the clear procedural answer.
- DRE-04 Campbell and Daniel supporting concurrences remain ambiguous under “the Court”: shared themes/conclusions alone do not establish the controlling reason. Curtis/McLean rebuttals and Nelson/Catron alternative grounds are not added.
- DRE-01 fixed rank 4 and DRE-04 structure rank 2 have Daniel source headings, although the existing parser page span labels the material Grier. This annotation corrects the audit attribution only; parser, chunks, and metadata remain untouched. Other OCR names are normalized only for audit display; uncertain authors remain null.
- The original accepted ranges are not removed or narrowed. Previously credited passages can be incomplete answers; resolving that scoring limitation requires a separately approved benchmark decision.

## Per-question evidence

### DRE-01 — Dred Scott v. Sandford

What facts about Dred Scott's residence in Illinois and Fort Snelling formed the basis of his claim to freedom?

Type: `facts`. Current ranges: [[5, 6]]. Proposed additions: [[39, 40], [167, 167]].

Confirmed incomplete: majority restatement on pages 39–40 and Scott-specific factual narrative in McLean’s dissent on page 167 independently answer the question. A blanket exclusion of separate opinions was too restrictive for residence facts.

**fixed_900_150, rank 1, PDF pp167–168, chunk 169: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.617992; official page-overlap relevance: False.

> a slave is brought from Missouri to Rock Island, in the State of Illinois, and is retained there as a slave for two years, -ard then taken to Fort Snelling, where slavery is prohibited by the Missouri compromise act, and there he is detained two years longer in a state of slavery. Harriet, his wife, was also kept at the same place four years as a slave, having been purchased in Missouri. They were then removed to the State of Missouri, and sold as slaves, and in the action before us they are not only claimed as slaves, but a majority of my brethren have held that on their being returned to Missouri the status of slavery attached to them. I am not able to reconcile this result with the respect due to the State of Illinois. Having the same rights of sovereignty As the State of Missouri in adopting a Constitution, I can perceive no reason wh

McLean recounts this plaintiff moving from Missouri to Rock Island for two years, then Fort Snelling for two years where the Missouri Compromise prohibited slavery. These residence facts answer a factual question; his opposing legal conclusion does not invalidate the facts.

Proposed addition: [[167, 167]]. Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp162–163, chunk 164: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.615849; official page-overlap relevance: False.

> When Dred Scott, his wife and children, were removed from Fort Snelling to Missouri, in 1838, they were free, as the law was then settled, and continued for fourteen years afterwards, up to 1852, when the above decision was made. Prior to this, for nearly thirty years, as Chief Justice Gamble declares, tl~e residence of a master with his slave in the State of Illinois, or in the Territory north of Missouri,.where slavery was prohibited

Discusses emancipation precedents and the return from Fort Snelling to Missouri; does not independently give Scott’s residence history in both Illinois and Fort Snelling.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp5–6, chunk 7: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.580507; official page-overlap relevance: True.

> In the year 1834, the plaintiff was negro slave belonging to Dr. Emerson, who was a surgeon in the army of the United States. In that year, 1834, said Dr. Emerson took the plain- tiff from the State of Missouri to the military post at Rock Island, in the State of Illinois, and held him there as a slave until the month of April or May, 1836. At the time last mentioned, said Dr. Emerson removed the plaintiff~from said military post at Rock Island to the military post, at Fort Snelling, situate on the west bank of the Mississippi I'iver, in the Territory known as Upper Louisiana, acquired, by 'the United States of France, and situate north of the latitude of thirty-six degrees thirty minutes north, and north of the State of Missouri. Said Dr. Emerson held the plaintiff in slavery at said Fort Snelling, from said last-mentioned date until the

The agreed statement of facts identifies Emerson’s removal of Scott to Rock Island in 1834, the 1836 move to Fort Snelling north of 36°30′, and residence there until 1838. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp79–80, chunk 81: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: concurrence; author: Daniel; similarity (navigation only): 0.578692; official page-overlap relevance: False.

> Fort Snelling, from said last-mentioned date until the year 1838. "In the year 1835, Harriet, who is named in the second count of the plaintiff's declaration, was -the negro slave of Major Taliaferro, who belonged to the army of the .Uhited States. In that year, 1835, said Major Taliaferro took said Harriet to said Fort Snelling, a military post situated as herein- before stated, and kept her there as a slave until the year 1836, and then sold and delivered. her as a slave at said Fort Snel- ling unto the said Dr. Emerson, hereinbefore named. Said Dr. Emerson held said Harriet in slavery at said Fort Snelling until the year 1838. "In the year 1836, the- plaintiff and said Harriet, at said Fort Snelling, with the consent of said Dr. Emerson, who then claimed to be their master and owner, intermarried, and took each other for husband and wi

Continues the Fort Snelling/family facts and return to Missouri, but the Illinois residence facts are in the preceding source page, outside this retrieved text. Daniel’s source heading also contradicts the coarse Grier attribution.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

Source pp77–79 show Daniel begins after Grier on p77; running headings confirm Daniel. Saved parser attribution remains untouched.

**fixed_900_150, rank 5, PDF pp159–160, chunk 161: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.578641; official page-overlap relevance: False.

> Rachel v. Walker (4 Missouri Rep., 350, June term, 1836) is a case involving, in every particular, the principles of the" case before us. Rachel sued for her freedom; and it appeared that she had been bought as a slave in Missouri, by Stockton, an officer of the army, taken to Fort.Suelling, where he was. stationed, and she was retained there as- a slave a -year;- and then Stockton removed to Prairie du Chien, .taking Rachel with him as a slave, where he continued to hold her-three years, and then he took her to the State of Missouri, aid sold her as a slave. "Fort Snelling was admitted to be on the west side of the Mississippi river, and north of the State of Missouri, in.the ter- ritory of the United States. That Prairie du Chien was'in the Michigan Territory, on the east side of the-Mississippi river. Walker, the defendant, held Rachel

The Illinois and Fort Snelling facts concern the analogous Rachel v. Walker litigation, not Scott’s own residence history.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp166–167, chunk 127: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.625593; official page-overlap relevance: False.

> a slave is brought from Missouri to Rock Island, in the State of Illinois, and is retained there as a slave for two years, -ard then taken to Fort Snelling, where slavery is prohibited by the Missouri compromise act, and there he is detained two years longer in a state of slavery. Harriet, his wife, was also kept at the same place four years as a slave, having been purchased in Missouri.

Independently contains McLean’s concrete account of Scott’s two Illinois years and two Fort Snelling years under a slavery prohibition. The factual wording permits evidence in a dissent.

Proposed addition: [[167, 167]]. Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp38–40, chunk 29: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.625444; official page-overlap relevance: False.

> The case, as he himself states it, on the record brought here by his writ of error, is this: The plaintiff was a negro slave, belonging to Dr. Emerson, who was a surgeon in the army of the United States. In the year 1834, he took the -plaintiff from the State of Missouri to the military post at Rock Island, in the State of fli- nois, and held him there as a slave until the month. of April or May, 1886. At the time last mentioned, said Dr. Em- erson removed the plaintiff from said military post at Rock Island to the military post at Fort Snelling, situate on the west bank of the Mississippi river, in the Territory known as Upper Louisiana, acquired by the United States of France, and situate north of the latitude of thirty-six degrees thirty minutes north, and north of the State of Missouri. Said Dr. Emerson held the plaintiff in slavery a

Taney’s opinion repeats the agreed Rock Island/Fort Snelling residence facts and expressly links those stays to the two freedom questions. This is also a majority source, not just a separate-opinion gap.

Proposed addition: [[39, 40]]. Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp159–160, chunk 122: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.621583; official page-overlap relevance: False.

> Rachel v. Walker (4 Missouri Rep., 350, June term, 1836) is a case involving, in every particular, the principles of the" case before us. Rachel sued for her freedom; and it appeared that she had been bought as a slave in Missouri, by Stockton, an officer of the army, taken to Fort.Suelling, where he was. stationed, and she was retained there as- a slave a -year;- and then Stockton removed to Prairie du Chien, .taking Rachel with him as a slave, where he continued to hold her-three years, and then he took her to the State of Missouri, aid sold her as a slave. "Fort Snelling was admitted to be on the west side of the Mississippi river, and north of the State of Missouri, in.the ter- ritory of the United States. That Prairie du Chien was'in the Michigan Territory, on the east side of the-Mississippi river. Walker, the defendant, held Rachel

Describes Rachel v. Walker and other emancipation precedents; these are not the plaintiff’s own Illinois and Fort Snelling residence facts.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp60–61, chunk 45: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.614731; official page-overlap relevance: False.

> But there is another point in the case which depends on State power and State law. And it is contended, on the part of the plaintif, that he is made free by being taken to Rock Island, in the State of Illinois, independently of his residence in the territory of the United States; and being so made free, h6 was not again reduced to a state of slavery by being brought back to Missouri. Our notice of this part of the case will be very brief; for the principle on which it depends was decided in this court, upon much consideration, in the case of Stpader et al. v. Graham, reported in 10th Howard, 82. In that case, the slaves had been taken from Kentucky to Ohio, with the consent of the owner, and afterwards brought back to Kentucky. And this court held that their status or condition, as free or sjave, depended upon the laws of Kentucky, when t

Gives the legal rejection of territorial freedom and the Illinois/Missouri choice-of-law issue, rather than the specific residence history asked for.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp157–159, chunk 121: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.611038; official page-overlap relevance: False.

> Winny v. Whitesides, (1 Missouri Rep., 473,) at October term, 1824. It appeared that, more than twenty-five years before, the defendant, with her husband, had removed from Carolina to Illinois, and brought with them the plaintiff; that they continued to reside in Illi- nois three or four years, retaining the plaintiff as a slave; after which, they removed to Missouri, taling her with them. The court held, that if a slave be detained in Illinois until he be entitled to freedom, the right of the owner does not re- vive when he finds the negro in a slave State. DECEMBER TERM, 1856. 551 Dred Scott v. Sandford. [MI. JUSTICE McLw. That when a slave is taken to Illinois by his owner, who takes up his residence there, the slave is entitled to freedom. In the case of Lagrange v. Chouteau, (2 Missouri Rep., 20, at May term, 1828,) it was decided th

Discusses Illinois law and the Winny v. Whitesides analogy, not Scott’s own residence in both named places.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### MIR-04 — Miranda v. Arizona

What safeguards did the Court require before custodial interrogation?

Type: `legal_rule`. Current ranges: [[2, 2], [34, 40]]. Proposed additions: [[9, 10], [67, 67]].

Confirmed incomplete: Warren’s pages 9–10 give the required safeguards independently. Clark’s page 67 also accurately lists several new requirements while criticizing them. The question asks what safeguards were required, so accurate reports are admissible evidence; it does not ask for Clark’s rationale.

**fixed_900_150, rank 1, PDF pp39–40, chunk 38: RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: majority; author: Warren; similarity (navigation only): 0.614384; official page-overlap relevance: True.

> If the individual states that he wants an attorney, the interrogation must cease until an attorney is present. At that time, the in- dividual must have an opportunity to confer with the attorney and to have him present during any subsequent questioning. If the individual cannot obtain an attorney and he indicates that he wants one before speaking to police, they must respect his decision to remain silent. This does not mean, as some have suggested, that each police station must have a "station house lawyer" present at all times to advise prisoners. It does mean, however, that if police propose to interrogate a person they must make known to him that he is entitled to a lawyer and that if he cannot afford one, a lawyer will be provided for him prior to any interrogation. If authorities con- clude that they will not provide counsel during a

Warren states cessation on silence/counsel requests, provision of counsel for indigent suspects, and the prosecution’s burden to establish a knowing, intelligent waiver. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**fixed_900_150, rank 2, PDF pp66–67, chunk 62: AMBIGUOUS**

Source: `data/processed/miranda_v_arizona.txt`; opinion: other; author: Clark; similarity (navigation only): 0.611007; official page-overlap relevance: False.

> The offer of coun- sel is articulated only as "a right to counsel"; nothing is said about a right to have counsel present at the custodial interrogation. (See also the examples cited by the Solicitor General, Westover v. United States, 342 F. 2d 684, 685 (1965) ("right to consult counsel"); Jackson v. United States, 337 F. 2d 136, 138 (1964) (accused "en- titled to an attorney").) Indeed, the practice is that whenever the suspect "decides that he wishes to consult with counsel before making a statement, the interview is terminated at thai point .... When counsel appears in person, he is permitted to confer with his client in private." This clearly indicates that~the FBI does not warn that counsel may be present during custodial interrogation. (2) The Solicitor General's letter states: "[T]hose who have been arrested for an offense under F

Clark’s FBI comparison implies counsel-presence and appointment requirements, but the retrieved text largely contrasts FBI practice with the new rule. It ends at the page-67 marker before Clark’s explicit list; accepting the indirect comparison needs human judgment.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp99–100, chunk 95: NOT_RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: dissent; author: White; similarity (navigation only): 0.608583; official page-overlap relevance: False.

> totality of circumstances deprived the defendant of a "free choice to admit, to deny, or to refuse to answer," Lisenba v. California, 314 U. S. 219, 241, and whether physical or psychological coercion was of such a degree that "the defendant'i will was overborne at the time he confessed," Haynes v. Washington, 373 U. S. 503, 513; Lynumn v. Illinois, 372 U. S. 528, 534. The duration and nature of incommunicado custody, the presence or absence of advice concerning the defendant's constitutional rights, and the granting or refusal of re- quests to communicate with lawyers, relatives or friends have all been rightly regarded as important data bearing on the basic inquiry. See, e. g., Ashcraft v. Tennessee, 322 U. S. 143; Haynes v. Washington, 373 U. S. 503.1 3 By contrast, the Court indicates that in applying.this new.rule it "will not pause 

White criticizes the automatic-coercion premise and discusses the prior totality standard, without independently stating the required safeguards.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp34–35, chunk 33: RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: majority; author: Warren; similarity (navigation only): 0.606048; official page-overlap relevance: True.

> warning is a clearcut fact. More important, whatever the background of the person interrogated, a warning at the time of the interrogation is indispensable to overcome its pressures and- to insure that the indi- vidual knows he is free to exercise the privilege at that. point in time. The warning of the right to remain silent must be accompanied by the explanation that anything said can and will be used against the individual in court. This warning is needed in order'to make him aware not only of the privilege, but also of the consequences of for- going it. It is only through an awareness of these con- sequences that there can be any assurance of real under- standing and intelligent exercise of the privilege. More- over, this warning may serve to make the individual more acutely aware that he is faced with a phase of the ad- versary syste

Warren expressly requires warning that statements can be used in court and describes the right to counsel present during interrogation. This answers safeguards under the prior standard allowing substantive components, not necessarily the entire rule in every chunk. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp43–44, chunk 41: NOT_RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: majority; author: Warren; similarity (navigation only): 0.605843; official page-overlap relevance: False.

> Procedural safeguards must be employed to 4 6 The distinction and its significance has been aptly desdribed in the opinion of a Scottish court: "In former times such questioning, if undertaken, would be con-. ducted by police officers- visiting the house or place of business of the suspect and there questioning him, probably in the presence of a relation or friend. However convenient the modem practice may be, it must normally create a situation very unfavourable to the suspect." Chalmers v. H. M. Advocate, [1954] Sess. Cas. 66, 78 (J. C.). 47 See People v. Dorado, 62 Cal. 2d 338, 354, 398 P. 2d 361, 371, 42 Cal. Rptr. 169, 179 (1965).

General statements about voluntariness and procedural safeguards do not enumerate the safeguards. The chunk ends at the page-44 marker; the concrete warning list on source page 44 is absent.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp9–10, chunk 6: RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: majority; author: Warren; similarity (navigation only): 0.667849; official page-overlap relevance: False.

> Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that

Warren independently lists silence, evidentiary-use, retained/appointed counsel, knowing and intelligent waiver, and cessation when counsel or silence is invoked.

Proposed addition: [[9, 10]]. Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp98–100, chunk 60: NOT_RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: dissent; author: White; similarity (navigation only): 0.658634; official page-overlap relevance: False.

> coercion was of such a degree that "the defendant'i will was overborne at the time he confessed," Haynes v. Washington, 373 U. S. 503, 513; Lynumn v. Illinois, 372 U. S. 528, 534. The duration and nature of incommunicado custody, the presence or absence of advice concerning the defendant's constitutional rights, and the granting or refusal of re- quests to communicate with lawyers, relatives or friends have all been rightly regarded as important data bearing on the basic inquiry. See, e. g., Ashcraft v. Tennessee, 322 U. S. 143; Haynes v. Washington, 373 U. S. 503.1 3 By contrast, the Court indicates that in applying.this new.rule it "will not pause to inquire in individual cases whether the defend- ant was aware of his rights without a warning being given." Ante, at 468. 'The reason given is that assessment of the knowledge of the defend

White disputes coercion and the old voluntariness standard; this does not independently state the new required safeguards.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp66–67, chunk 40: RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: other; author: Clark; similarity (navigation only): 0.654270; official page-overlap relevance: False.

> an affirmative "waiver" was a prerequisite to questioning; that the burden of proof as to waiver was on the prosecution; that the presence of counsel- absent a waiver-during interrogation was required; that ,a waiver can be withdrawn at the will-of the accused; that counsel must be furnished during an accusatory stage to those unable to pay; nor that admissions and exculpatory statements are "confessions." To require all those things at one gulp should cause the Court to choke over more cases than Crooker v. California, 357 U. S. 433 (1958), and Cicenia v. Lagay, 357 U. S. 504 (1958), which it expressly overrules today. The rule prior to today-as Mr. Justice Goldberg, the author of the Court's opinion in Escobedo, stated it in Haynes v. Washington-depended upon "a totality of circumstances evidencing an involuntary ...admission of guilt."

Clark explicitly reports the majority’s new waiver, prosecution-burden, counsel-presence, withdrawal-of-waiver, and indigent-counsel requirements on source page 67. His criticism is separate from this accurate report of safeguards; the question asks what was required, not why the majority justified it.

Proposed addition: [[67, 67]]. Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp96–98, chunk 59: NOT_RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: dissent; author: White; similarity (navigation only): 0.622591; official page-overlap relevance: False.

> confessions, it most assuredly does not follow that each and every case will disclose this kind of interrogation or this kind of consequence. - Insofar as appears from the Court's opinion, it has not examined a single transcript of any police interrogation, let alone the interrogation that took place in any one of these cases which it decides today. Judged by any of the standards for empirical investigation utilized in the social sciences the factual basis for the Court's premise is patently inadequate. Although in the Court's view in-custody interrogation is inherently coercive, the Court says that the sponta- neous product of the coercion of arrest and detention is still to be deemed voluntary. An accused, arrested on probable cause, may blurt out a confession which will be admissible despite the fact that he is alone and in cus- tody, 

White disputes the factual/constitutional premise for the new rules and contrasts spontaneous and interrogated confessions; it does not state the concrete safeguards.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp10–11, chunk 7: NOT_RELEVANT**

Source: `data/processed/miranda_v_arizona.txt`; opinion: majority; author: Warren; similarity (navigation only): 0.619067; official page-overlap relevance: False.

> warnings of constitutional rights. An understanding of the nature and setting of this in-custody interrogation is essential to. our decisions today. The difficulty in depicting what transpires at such interrogations stems from the fact that in this coun- try they have largely taken place incommunicado. From extensive factual studies undertaken in the early 1930's, including the famous Wickersham Report to Congress' by a Presidential Commission, it is clear that police vio- lence and the "third degree" flourished at that time.5 5 See, for example, IV National Commission on Law Observance and Enforcement, Report on Lawlessness in Law Enforcement (1931) 446 OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. In a series of cases decided by this Court long after these studies, the police resorted to physical brutality-beat- ing, hanging, whip

Warren describes lack of warnings in the four underlying cases and coercive interrogation history. It does not independently tell the reader which warnings and counsel procedures are required.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### MAR-01 — Marbury v. Madison

Why did William Marbury ask the Supreme Court to issue a writ of mandamus against James Madison?

Type: `facts`. Current ranges: [[2, 2], [18, 19], [37, 38]]. Proposed additions: [[32, 32], [36, 36]].

Confirmed incomplete: pages 32 and 36 expressly give the violated commission right and the delivery remedy. Topic-only mandamus discussions remain ambiguous or irrelevant.

**fixed_900_150, rank 1, PDF pp37–38, chunk 37: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.618288; official page-overlap relevance: True.

> commifflon which has been withheld from Mr. Marbury ; in which cafe a mandamus would be improper. But this doubt has yielded to the confideration that the judgment in detinue is for the thing itfelf, or its value. The value of a public office not to be fold, is incapable of being afcertained ; and the applicant has a right to the office itfelf, or to nothing. He will obtain the office by obtaining the com- miffion, or a cqpy of it from the record. This, then, is a plain cafe for a mandamus, either to deliver the commi~fion, or a copy of it from the record; :and it only remains to be enquired, Whether it can iffue from this court. The a& to eftabli{h the judicial courts of the United States authorizes the fupreme court " to iffue writs of " mandamus, in cafes warranted by the principles and " ufages of law, to aipy courts appointed, or per

Marshall identifies Marbury’s withheld commission and mandamus to deliver the commission or its recorded copy. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp18–19, chunk 18: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.587468; official page-overlap relevance: True.

> deliver'to William V. Marbury his commiffion as a juftice of the peace for the MADISON. county of Waflhington, in the diftrid of Columbia. No caufe has been fhewn, and the ptefent motion is for a man,4amus. The peculiar delicacy of this cafe, the novelty of fome of its circumftances, and the real diffi, culty attending the points which occur in it, require a complete expofition of the principles, on which the opi- nion to be given by the court, is founded. . Thefe principles have been, on the fide of the appli- cant, very ably. argued at the bar. In rendering the opi- nion of the court, there will be fome departure in form, though not in fubfcaice, from the points flated in that. argument. In the order in which the court has viewed this fubje&, the following queflions have becen confidered and decid- ed. ift Has the applicant a right, to 

The Court describes the motion directing delivery to Marbury of his justice-of-the-peace commission and the asserted violated right. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp32–33, chunk 32: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.566661; official page-overlap relevance: False.

> 2dly. That, having this legal title to the office, he has a confequent right, to the commiffion ; a re fufal to deliver which, is a plain violation of that right, for which the laws of his country afford him a remedy. It remains to be enquired whether, 3dly. He is entitled to the remedy for which he ap- plies. This depends on, ift. The nature of the wriE applied for, and, 2dly. The power of this court. ift. The nature of the writ. Blackftone, in the 3 d volume of his commentaries, page i 1o, defines a mandamus to be, " a command if- cc Cuing in the king's name from the court of king'6 bench, ,, and dire&ed to any perfon, corporati n, or inferior " court of judicature within the king's dominions, re- ,, quiring them to do fome particular thing therein fpeci- c fled, which appertains to their office and duty, and "which the court of king's 

Marshall states that Marbury has legal title to the office, a consequent right to the commission, and that refusal to deliver violates that right and warrants a remedy.

Proposed addition: [[32, 32]]. Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp33–34, chunk 33: AMBIGUOUS**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.554737; official page-overlap relevance: False.

> Or, in the words of Lord Mansfield, the appli- cant, in this cafe, has a right to execute an office of pub- lic concern, and is kept out of poffeffion of that right. Thefe circumftances certainly concur in this cafe. Still, to render the mandamus a proper remedy, the officer to whom it is to be direed, muft be one to whom, on legal principles, fuch writ may be direted ; and the perfon applying for it muft be without any other fpecific and legal remedy. ift. With refpe& to the officer to whom it would.I direaed. The intimate political relation,' fubfifting be- tween the prefident of, the United States and the heads of departments, neceffarily renders any legal inveftigation of the aks of one of thofe high officers peculiarly irkfome, as well as delicate; and excites fome hefitation with refpe& to the propriety of entering into fuch invefti

Describes an applicant kept out of an office and the conditions for mandamus, but the excerpt does not itself specify Marbury’s withheld commission or Madison’s refusal. A broad partial-answer standard might accept it; no addition proposed.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp36–37, chunk 36: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.549260; official page-overlap relevance: True.

> It is true that the mandamus, now moved for, is not for the peiformance of an aCt exprefsly enjoined by ftatute. It is to dpliver a commiffion ; on which fubjeS the afts of Congrefs are filent. Tlhis difference is not con- fidered as affe~ting the cafe. It has already been ftated that the applicant has, to that commiffion, a vefted legal right, of which the executive cannot deprive him. He has been appointed to an office, from which he is not removable at the will of the executive ; and being fo

The Court expressly says the mandamus now sought is to deliver a commission to which the applicant has a vested legal right that the executive cannot take away.

Proposed addition: [[36, 36]]. Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp31–33, chunk 23: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.654463; official page-overlap relevance: False.

> 2dly. That, having this legal title to the office, he has a confequent right, to the commiffion ; a re fufal to deliver which, is a plain violation of that right, for which the laws of his country afford him a remedy. It remains to be enquired whether, 3dly. He is entitled to the remedy for which he ap- plies. This depends on, ift. The nature of the wriE applied for, and, 2dly. The power of this court. ift. The nature of the writ. Blackftone, in the 3 d volume of his commentaries, page i 1o, defines a mandamus to be, " a command if- cc Cuing in the king's name from the court of king'6 bench, ,, and dire&ed to any perfon, corporati n, or inferior " court of judicature within the king's dominions, re- ,, quiring them to do fome particular thing therein fpeci- c fled, which appertains to their office and duty, and "which the court of king's 

Marshall explains the completed appointment, right to the commission, refusal to deliver, and availability of a legal remedy; substantively answers why he sought the writ.

Proposed addition: [[32, 32]]. Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp1–2, chunk 0: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.640540; official page-overlap relevance: True.

> WILLIAM MARBURY v. JAMES MADISON, SECRETARY OF STATE OF THE UNITED STATES. FEBRUARY, 1803. AT the laft term, viz. December term, X8or, MARIlURY William Marbury, Dennis Ramfay, Robert Townfend v. Hooe, and William Harper, by their counfel, Charles MADISON. Lee, efq. late- attorney general of the United States, S SUPREME COURT U. S. MA .IBUPY feverally moved the court for a rule to Jatnes Madifon*l 'v. fecrtary of fRate of the United States, tc fhew caufe MADIsoW. why a mandamus flhould not iffue commanding him.to Scaufe to be delivered to them refpedively their feveral Th fupreme commiffions as juftices of the~peace in the diftri& of Co. court of the U States has n lumbia.

The matching Marbury case caption and motion seek an order compelling Madison to deliver the justice-of-the-peace commissions. The preceding Turner/Fendall material is not evidence for this answer. The Marbury portion on page 2 is already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp35–37, chunk 26: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.628311; official page-overlap relevance: True.

> It is true that the mandamus, now moved for, is not for the peiformance of an aCt exprefsly enjoined by ftatute. It is to dpliver a commiffion ; on which fubjeS the afts of Congrefs are filent. Tlhis difference is not con- fidered as affe~ting the cafe. It has already been ftated that the applicant has, to that commiffion, a vefted legal right, of which the executive cannot deprive him. He has been appointed to an office, from which he is not removable at the will of the executive ; and being fo FEBRUARY, 1803. appointed, he has a right to the commiffion which the MARDURY fecretary has 'received from the prefident for his ufe. V, The a& of congrefs does not indeed order the fecretary MADISON. of ftate to: fend it to him, but it is placed in his hands '*Y for the perfon entitled to it; and cannot be more law- fully withheld by him, than by

The Marbury-specific portion says the writ seeks delivery of the commission and a vested right prevents the executive from withholding it. The earlier pension-law analogy is not the answer.

Proposed addition: [[36, 36]]. Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp16–17, chunk 13: AMBIGUOUS**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.626053; official page-overlap relevance: False.

> affidavit of Hazen Kimball, who had been a clerk in the office of the Secretary. of State, and had been to a diftant part of the United States, but whofe return was not known to the applicant till after the argument of the cafe. It fated that on the third of March, 8oi, he was a clerk in the department of flate. That there were in the office, on that day, commiffions made out and fAgned by the prefident, appointing William Marbury a juftice of peace for the county of Wafhington ; and Robert r. Hooe a juftice of the peace for the county of Alexandria, in the diftri&l of Columbia. Afterwards, on the 24 th of February the following

An affidavit proves the commission was signed and a general account explains mandamus procedure, but it does not independently establish the withheld commission as the reason for Marbury’s request.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp17–19, chunk 14: RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.610430; official page-overlap relevance: True.

> the commiffion has never reached the perfon for whom it was made out. In order to determine whether he is entitled to this commiffion, it becomes neceffary to enquire whetiher he has been appointed to the 6ffice. For if he has been ap- pointed, the law continues him in office for five years, and he is entitled to the poffcffion of thofe evidences of Qffice, which, being completed, became his property. The 2d feaion of the 2d article of the conifitution, declares, that, 1' the prefident (hall nominate, and, by ,' and with the advice and confent of the fenate, fhall " appoint ambaffadors, other public minifters and confuls, " and all other officers of the United States, whofe ap- " pointments are not otherwife ptovided for." The third fe&ion declares, that ", he fhall commiffion ,, all the officers of the United States."

The opinion opens with the delivery motion and states that the signed, sealed commission never reached Marbury. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### MAR-04 — Marbury v. Madison

Why could the Supreme Court not exercise original jurisdiction to issue the writ of mandamus requested by Marbury?

Type: `jurisdiction`. Current ranges: [[37, 40]]. Proposed additions: None.

No confirmed addition from these candidates. The accepted source pages 38–40 explain Article III’s allocation and why this writ would be original. Fixed rank 1 only previews unconstitutionality on page 37 and carries an empty page-38 marker: an apparent page-level false positive/incomplete answer, not evidence that every accepted page range is wrong.

**fixed_900_150, rank 1, PDF pp37–38, chunk 37: AMBIGUOUS**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.592551; official page-overlap relevance: True.

> unconflitutional, and therefore abfolutely incapable of conferring the authority, and affigning the duties which its words purport to confer and affign. The conftitution vefts the who]- judicial power of the United States in one fupreme court, and fuch inferior courts as congrefs fhall, from time to time, ordain and efta- blifh. This power is exprefsly extended to all cafes arifing under the laws of the United States ; and confe- quently, in fome form, may be exercifed over the prefent

States that authority would fail if the statute is unconstitutional, but does not yet give the Article III allocation or explain why this request is original rather than appellate. Page 38 is only a trailing marker. The conditional preview is an incomplete answer, despite its official page-overlap hit.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp12–13, chunk 12: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.570523; official page-overlap relevance: False.

> Congrcfs is not r~ftrained from conferring original jurisdifion in -other cafes than thofe mentioned in til conflitution. 2 Dal. Rep. 298. This court has entertained jurisdiCion on a mandamus in one cafe, and or, a prohibition in another. In the cafe of the Un *'ted States v.judge Lawrence, 3. Dal. Rep. 42, a mandamus was moved for by. the attorney general at the inflance of the French minifter, to compel judge Lawrence to iffue a warrant againif captain Barre, com- mander of the French fhip of war Le Perdrix, grounded on an article of the confular convention with France. In this cafe the power of the court to ifflue writs of mandamus, was taken for granted in the arguments of counfel on both fides, and feems to have been fo confidered by the court. The mandamus was refutfed, becaufe the cafe in which it was required, was not a proper one

This is counsel’s argument that Congress can confer original jurisdiction and that mandamus is appellate, the position the Court rejects—not the Court’s holding.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp6–7, chunk 6: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.561545; official page-overlap relevance: False.

> The court ordered the witneffes to be fworn and their anfwers taken in writing, but informed them that when the queftions were afked they might ifate their obje&ions to anfwering each particular queftion, if they had any. . Mr. Wagner being examined upon interrogatories, teftified,.that at this diftance of time he could not recol- left whether he had feen any commiffion in the office, conftituting the applicants, or either of them juftices of the peace.. That Mr Marbury and Mr, Ramfay called on the fecretary of ifate refpefting their commiffions. That the fecretary referred them to him ; he took therm into another room and mentioned to them, that two of the commiffions had been figned, but the other had not. That he did not know that fa& of 'his own knowledge, but by the information of others. Mr. Wagner declined anfwering the queftion ,,

Witness examination and examples of access to government records do not explain the Court’s original-jurisdiction limit.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp32–33, chunk 32: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.545724; official page-overlap relevance: False.

> power of this court. ift. The nature of the writ. Blackftone, in the 3 d volume of his commentaries, page i 1o, defines a mandamus to be, " a command if- cc Cuing in the king's name from the court of king'6 bench, ,, and dire&ed to any perfon, corporati n, or inferior " court of judicature within the king's dominions, re- ,, quiring them to do fome particular thing therein fpeci- c fled, which appertains to their office and duty, and "which the court of king's bench has previoufly deter- cc mined, or at leaf fuppofes, to be confonant to right cc and juftice." Lord Mansfield, in 3 d Burrows 1266, in the cafr of the King v. Baker, et al. fates with much precifion and ex- plicitnefs the cafes in which this writ may be ufed. ,W Whenevir," fays that very able judge, " there is a " right to execute an office, perform a fervice, or exercife cc a

The right to a commission and generic mandamus definition do not answer the separate Article III jurisdiction problem.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp18–19, chunk 18: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.543793; official page-overlap relevance: False.

> following queflions have becen confidered and decid- ed. ift Has the applicant a right, to the commiffion he demands? 2dly. If he has a'right, and that right has been violated, do the laws of his country afford him a remedy ? 3dly. If they do afford him a remedy, is it a mianda- mus iffluing from this court ? The firft obje& of enquiry is, ift. Has the applicant a right to the commiffion he de- mands ? His right originat s in an ad of congrefs paffed in February 8oi, concerning the diftri, of Columbia. After dividing the diftri& into two counties, the i Ith fedion of this law, enats, " that there fhall be ap- pointed in and for each of. the faid counties, fuch num- ber of difcreet perfons to be juilices of the peace as the prefident of the United States fhall, from time to time, think expedient, to continue in office for five years.

Introduces the three questions and Marbury’s asserted commission right; gives no reason the Court cannot exercise original jurisdiction.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp31–33, chunk 23: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.626271; official page-overlap relevance: False.

> power of this court. ift. The nature of the writ. Blackftone, in the 3 d volume of his commentaries, page i 1o, defines a mandamus to be, " a command if- cc Cuing in the king's name from the court of king'6 bench, ,, and dire&ed to any perfon, corporati n, or inferior " court of judicature within the king's dominions, re- ,, quiring them to do fome particular thing therein fpeci- c fled, which appertains to their office and duty, and "which the court of king's bench has previoufly deter- cc mined, or at leaf fuppofes, to be confonant to right cc and juftice." Lord Mansfield, in 3 d Burrows 1266, in the cafr of the King v. Baker, et al. fates with much precifion and ex- plicitnefs the cafes in which this writ may be ufed. ,W Whenevir," fays that very able judge, " there is a " right to execute an office, perform a fervice, or exercife cc a

Addresses appointment, commission rights, and generic mandamus, not the constitutional allocation of original jurisdiction.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp16–17, chunk 13: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.616284; official page-overlap relevance: False.

> affidavit of Hazen Kimball, who had been a clerk in the office of the Secretary. of State, and had been to a diftant part of the United States, but whofe return was not known to the applicant till after the argument of the cafe. It fated that on the third of March, 8oi, he was a clerk in the department of flate. That there were in the office, on that day, commiffions made out and fAgned by the prefident, appointing William Marbury a juftice of peace for the county of Wafhington ; and Robert r. Hooe a juftice of the peace for the county of Alexandria, in the diftri&l of Columbia. Afterwards, on the 24 th of February the following

General mandamus procedure and an affidavit that commissions were signed do not state the Court’s jurisdictional holding.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp11–12, chunk 9: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: unknown; author: not established; similarity (navigation only): 0.604600; official page-overlap relevance: False.

> Congrcfs is not r~ftrained from conferring original jurisdifion in -other cafes than thofe mentioned in til conflitution. 2 Dal. Rep. 298. This court has entertained jurisdiCion on a mandamus in one cafe, and or, a prohibition in another. In the cafe of the Un *'ted States v.judge Lawrence, 3. Dal. Rep. 42, a mandamus was moved for by. the attorney general at the inflance of the French minifter, to compel judge Lawrence to iffue a warrant againif captain Barre, com- mander of the French fhip of war Le Perdrix, grounded on an article of the confular convention with France. In this cafe the power of the court to ifflue writs of mandamus, was taken for granted in the arguments of counfel on both fides, and feems to have been fo confidered by the court. The mandamus was refutfed, becaufe the cafe in which it was required, was not a proper one

Reports counsel’s assertion that Congress is not restrained from conferring original jurisdiction and mandamus can be appellate. This is the argument rejected on source pages 38–40.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp35–37, chunk 26: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.587191; official page-overlap relevance: True.

> It is true that the mandamus, now moved for, is not for the peiformance of an aCt exprefsly enjoined by ftatute. It is to dpliver a commiffion ; on which fubjeS the afts of Congrefs are filent. Tlhis difference is not con- fidered as affe~ting the cafe. It has already been ftated that the applicant has, to that commiffion, a vefted legal right, of which the executive cannot deprive him. He has been appointed to an office, from which he is not removable at the will of the executive ; and being fo FEBRUARY, 1803. appointed, he has a right to the commiffion which the MARDURY fecretary has 'received from the prefident for his ufe. V, The a& of congrefs does not indeed order the fecretary MADISON. of ftate to: fend it to him, but it is placed in his hands '*Y for the perfon entitled to it; and cannot be more law- fully withheld by him, than by

The pension-case analogy and proper-remedy discussion do not reach the original/appellate distinction or Article III’s exclusive allocation.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp17–19, chunk 14: NOT_RELEVANT**

Source: `data/processed/marbury_v_madison.txt`; opinion: majority; author: not established; similarity (navigation only): 0.578032; official page-overlap relevance: False.

> following queflions have becen confidered and decid- ed. ift Has the applicant a right, to the commiffion he demands? 2dly. If he has a'right, and that right has been violated, do the laws of his country afford him a remedy ? 3dly. If they do afford him a remedy, is it a mianda- mus iffluing from this court ? The firft obje& of enquiry is, ift. Has the applicant a right to the commiffion he de- mands ? His right originat s in an ad of congrefs paffed in February 8oi, concerning the diftri, of Columbia. After dividing the diftri& into two counties, the i Ith fedion of this law, enats, " that there fhall be ap- pointed in and for each of. the faid counties, fuch num- ber of difcreet perfons to be juilices of the peace as the prefident of the United States fhall, from time to time, think expedient, to continue in office for five years. FEBRU

Sets out the motion, appointment, and delivery facts; no constitutional jurisdictional holding appears.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### DRE-03 — Dred Scott v. Sandford

What reasoning did the Court use to support its conclusion about whether people of African descent were included as citizens under the Constitution?

Type: `reasoning`. Current ranges: [[10, 12], [24, 28]]. Proposed additions: [[33, 34]].

Confirmed incomplete on pages 33–34. Curtis’s high-ranked dissent provides the contrary citizenship theory, not the Court’s exclusion rationale. The issue-framing chunks on pages 10–11/11–12 also illustrate overinclusive page-level credit.

**fixed_900_150, rank 1, PDF pp26–27, chunk 28: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.627916; official page-overlap relevance: True.

> The Constitution upon its adoption obviously took from the States all power by any subsequent legislation to introduce as a citizen into the political family of the United States any one, no matter where he was born, or what might be his character or condition; and it gave to Congress the power to confer this character upon those only who were born outside of the dominions of the United States. And no law of a State, therefore, passed since the Constitution was adopted, can give any right of citizenship outside of its own territory. A clause similar to the one in the Constitution, in relation to the rights and immunities of citizens of one State in the other States, was contained in the Articles of Confederation. But there is a difference of language, which is worthy of note. The provision in the Articles of Confederation was, "that the f

Taney reasons from founding-era state citizenship, the Confederation’s racial exclusions, and limits on states creating national citizenship. This is the controlling opinion’s exclusion rationale. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp11–12, chunk 13: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.608797; official page-overlap relevance: True.

> The question.is simply this: Can a negro, whose ancestors were imported into this country, and sold as slaves, become a member of the political community formed and brought into existence by the Constitution of the United States, andfas such become entitled to all the rights, and privileges, and immuni- ties, guarantied by that instrument to the citizen? One of which rights is the privilege of sui in a court of the United States in the cases specified in the ConststutionIt will be observed, that the plea applies to that-class of per- sons only whose ancestors were negroes of the African race, and imported into this couintry, and sold and held as slaves. The only matter in issue before the court, therefore, is, whether the descendants of such ilaves, when they shall be emancipa' ted, or who are born of parents who had become free before th

Frames the citizenship issue, scope of the pleadings, and jurisdictional review. Merely posing the question is not the substantive historical/constitutional reasoning supporting the conclusion, despite the official page-overlap hit.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp24–25, chunk 26: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.602242; official page-overlap relevance: True.

> The legislation of the States therefore shows, in a manner not to be mistaken, the inferior and subject condition of that race at the time the Constitution was adopted, and long after- wards, throughout the thirteen States by Which that instru- ment was framed; and it is hardly consistent with the respect due to these States, to suppose that they regarded at that time, as fellow-citizens and members of the sovereignty, a class of beings whom they had thus stigmatized; whom, as we are bound, out of respect to the State sovereignties, to assume they had deemed it just and necessary thus to stigmatize, and upon whom they had impressed such deep and enduring marks of inferiority and degradation; or, that when they met in conven- tion to form the Constitution, they looked upon them as a portion of their constituents, or designed to include the

Taney uses discriminatory state laws and asserted founding-era status to infer that the framers did not include this population as constitutional citizens. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp184–185, chunk 186: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.600490; official page-overlap relevance: False.

> my opinion is, that, under the Constitution of the United States, every free person born on the -soil of a State, who is a citizen of that State by force of its Constitution or laws, is also a citizen of the United States. I will proceed to state' the grounds of that opinion. The first -section of the second article of the Constitution -uses the-language, "a naturalborn citizen." lit thus assumes that citizenship may be acquired by birth. Undoubtedly, this language of the Constitution" was used in reference to that principle of public law, well understood in this country at the time of the adoption of the Constitution, which referred citi- zenship to the place of birth. At the Declaration of Independ- .ence, anl ever since, the received general doctrine has been, in confrmity"-With the commcin law, that free persons born ,within either of

Curtis argues that founding-era Black state citizens remained national citizens and gives his own contrary citizenship rule. It does not independently state the Court’s exclusion rationale.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp183–184, chunk 185: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.596139; official page-overlap relevance: False.

> free colored persons, before and at the time of the formation of the Constitutionj were citizens of those States. The fourth of the fundamental articles of the Confederation was as follows: "The free inhabitants of each of these States,' aupers, vagabonds, and fugitives from justice, excepted, shall e entitled to all the privileges and immunities of free citizens in the several States." The fact that free persons of color were citizens .of some of the sever.] States, and the consequence, that this fourth article of the Confederation would have the effect to confer on such' persons the privileges and immunities of general citizenship, were not only known to those who framed and adopte'd those articles, but the evidence is decisive, that the fourth article was intended to have that effect, and that more restricted lan- guage, which would ha

Curtis uses state citizenship and the rejected attempt to insert “white” in the Confederation to argue the opposite of the Court’s conclusion.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp182–184, chunk 140: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.657202; official page-overlap relevance: False.

> free colored persons, before and at the time of the formation of the Constitutionj were citizens of those States. The fourth of the fundamental articles of the Confederation was as follows: "The free inhabitants of each of these States,' aupers, vagabonds, and fugitives from justice, excepted, shall e entitled to all the privileges and immunities of free citizens in the several States." The fact that free persons of color were citizens .of some of the sever.] States, and the consequence, that this fourth article of the Confederation would have the effect to confer on such' persons the privileges and immunities of general citizenship, were not only known to those who framed and adopte'd those articles, but the evidence is decisive, that the fourth article was intended to have that effect, and that more restricted lan- guage, which would ha

Curtis’s contrary founding-era citizenship and Confederation argument is a dissenting rebuttal, not the Court’s supporting reasoning.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp26–28, chunk 20: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.651369; official page-overlap relevance: True.

> The word citizen excluded, and no doubt intended to exclude, foreigners who had not become citizens of some one of the States when the Constitution was adopted; and also every description of persons who were not fully recognised as citizens in the several States. This, upon any fair construc- tion of the instruments to which we have -referred, was evidently the object and purpose of this change of words. To all this mass of proof we have still to add, that Congress has repeatedly legislated upon the same construction of the Constitution that we have given. Three laws, two of which were passed Ahmost immediately after the Government went into operatioA, will be abundantly sufficient to show this. The two first are particularly worthy of notice, because many of.the men who assisted in framing the Constitution, and took an active part in pro

Taney infers exclusion from the change from inhabitants to citizens and early congressional naturalization laws limited to white persons. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp195–197, chunk 149: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.650536; official page-overlap relevance: False.

> I dissent, therefore, from that part of the opinion of the ma- jority of the court, in which it is held that a person of Africandescent cannot be a citizen of the United States; and I regret I must go further,and dissent. both from what I deem their assumption of authority to examine the constitutionality of the act of Congress commonly called the Missouri compro4 DECEMBER TERM, 1856. 589 Dred Scott v. Sandford. [MR. JUSTICE CURTIS. nise aect, and the grounds and conclusions announced in their opinion.

Curtis explicitly concludes that free Black state citizens are national citizens and dissents from the majority’s exclusion. Semantic overlap does not answer what reasoning the Court used.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp10–11, chunk 8: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.644295; official page-overlap relevance: True.

> The question.is simply this: Can a negro, whose ancestors were imported into this country, and sold as slaves, become a member of the political community formed and brought into existence by the Constitution of the United States, andfas such become entitled to all the rights, and privileges, and immuni- ties, guarantied by that instrument to the citizen? One of which rights is the privilege of sui in a court of the United States in the cases specified in the ConststutionIt will be observed, that the plea applies to that-class of per- sons only whose ancestors were negroes of the African race, and imported into this couintry, and sold and held as slaves. The only matter in issue before the court, therefore, is, whether the descendants of such ilaves, when they shall be emancipa' ted, or who are born of parents who had become free before th

The Court explains why the citizenship plea is before it and frames the issue; it does not yet give the substantive reasoning for the citizenship conclusion.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp33–34, chunk 25: RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: majority; author: Taney; similarity (navigation only): 0.638672; official page-overlap relevance: False.

> The only two provisions which point to them and include them, treat them as property, and make it the duty of the Government to protect it;. no ofher power, in relation to this race, is to be found in the Cohstitution; and as it is a Govern- 426 SUPREME COURT. OPRON OF T CoURT.] Dred Scott v. Sandford. ment of special, delegated, powers, no authority beyond these two provisions can be constitutionally exercised. The Govern- ment of the United States had no right to interfere for any other purpose but that of protecting the rights of the owner, leaving it altogether with~the several States to deal with this race, whether emancipated or not, as each State may think justice, humanity, and the interests and safety of society, require. The States evidently intended to reserve this power exclusively to themselves. No one, we presume, supposes t

Taney describes constitutional treatment as property, asserted consequences of state-created citizenship, and fixed founding-era meaning; he synthesizes the historical and governmental evidence for exclusion.

Proposed addition: [[33, 34]]. Canonical source match: verified.

### OBE-04 — Obergefell v. Hodges

How did the Court connect the Due Process Clause and Equal Protection Clause in its analysis of same-sex marriage?

Type: `constitutional_principle`. Current ranges: [[4, 4], [28, 32]]. Proposed additions: [[64, 64]].

Confirmed incomplete on page 64: Roberts reproduces the majority’s actual explanation, verified on majority page 29. This is relevant quoted majority reasoning, although Roberts’s own criticism is not controlling reasoning. The preceding page-63 summary is ambiguous.

**fixed_900_150, rank 1, PDF pp29–30, chunk 28: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.675200; official page-overlap relevance: True.

> The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the ri

Kennedy expressly explains the independent but mutually instructive liberty/equality principles and their convergence in defining the marriage right. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp64–65, chunk 62: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.670443; official page-overlap relevance: False.

> “Rights implicit in liberty and rights secured by equal protection may rest on different precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to cap- ture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may con- verge in the identifcation and defnition of the right.” Ante, at 672. The majority goes on to assert in conclusory fashion that the Equal Protection Clause provides an alternative basis for its holding. Ante, at 675. Yet the majority fails to pro- vide even a single sentence explaining how the Equal Protec- tion Clause supplies independent weight for its position, nor does it attempt to justify its gratuitous violation of the canon against unnecessarily resolving c

Roberts quotes and explicitly attributes the majority’s mutually instructive and converging principles. Verified against Kennedy on source page 29. The quoted reasoning answers the question; Roberts’s disagreement does not convert the quote into his own contrary rule.

Proposed addition: [[64, 64]]. Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp63–64, chunk 61: AMBIGUOUS**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.669387; official page-overlap relevance: False.

> The central point seems to be that there is a “synergy between” the Equal Protection Clause and the Due Process Clause, and that some prece- dents relying on one Clause have also relied on the other. Ante, at 673. Absent from this portion of the opinion, how-

Roberts summarizes the majority’s “synergy” and shared precedents but calls the discussion difficult to follow; the full attributed majority quote is on page 64 and absent from this marker-ending chunk. Whether this terse critical summary alone suffices needs judgment.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp51–52, chunk 49: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.663713; official page-overlap relevance: False.

> Due Process Clause. The majority purports to identify four “principles and tra- ditions” in this Court's due process precedents that support a fundamental right for same-sex couples to marry. Ante, at 665. In reality, however, the majority's approach has no basis in principle or tradition, except for the unprincipled tradition of judicial policymaking that characterized discred- ited decisions such as Lochner v. New York, 198 U. S. 45. Stripped of its shiny rhetorical gloss, the majority's argu- ment is that the Due Process Clause gives same-sex couples a fundamental right to marry because it will be good for them and for society. If I were a legislator, I would cer- tainly consider that view as a matter of social policy. But as a judge, I fnd the majority's position indefensible as a matter of constitutional law. A Petitioners' “fundamen

Roberts disputes due-process reasoning and describes substantive due process, without explaining the majority’s connection to equal protection.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp4–5, chunk 3: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: syllabus; author: not established; similarity (navigation only): 0.657196; official page-overlap relevance: True.

> The Due Process Clause and the Equal Protection Clause are connected in a pro- found way. Rights implicit in liberty and rights secured by equal pro- tection may rest on different precepts and are not always co-extensive, yet each may be instructive as to the meaning and reach of the other. This dynamic is refected in Loving, where the Court invoked both the Equal Protection Clause and the Due Process Clause; and in Zablocki v. Redhail, 434 U. S. 374, where the Court invalidated a law barring fathers delinquent on child-support payments from marrying. Indeed, recognizing that new insights and societal understandings can reveal unjustifed inequality within fundamental institutions that once passed unnoticed and unchallenged, this Court has invoked equal protection principles to invalidate laws imposing sex-based inequality on marriage, see

The syllabus substantively explains mutually instructive principles, their interlocking application, and the combined liberty/equality injury in same-sex marriage. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp63–65, chunk 41: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.763555; official page-overlap relevance: False.

> “Rights implicit in liberty and rights secured by equal protection may rest on different precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to cap- ture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may con- verge in the identifcation and defnition of the right.” Ante, at 672. The majority goes on to assert in conclusory fashion that the Equal Protection Clause provides an alternative basis for its holding. Ante, at 675. Yet the majority fails to pro- vide even a single sentence explaining how the Equal Protec- tion Clause supplies independent weight for its position, nor does it attempt to justify its gratuitous violation of the canon against unnecessarily resolving c

The dissent independently contains a clearly attributed verbatim majority explanation of mutually instructive, converging liberty/equality principles, confirmed on source page 29. Accept that evidence, not Roberts’s subsequent critique.

Proposed addition: [[64, 64]]. Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp29–31, chunk 20: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.749449; official page-overlap relevance: True.

> The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the ri

Kennedy explains the interrelation and illustrates it with Loving and Zablocki. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp31–33, chunk 21: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.735614; official page-overlap relevance: True.

> This dynamic also applies to same-sex marriage. It is now clear that the challenged laws burden the liberty of same-sex couples, and it must be further acknowledged that they abridge central precepts of equality. Here the marriage laws enforced by the respondents are in essence unequal: Same-sex couples are denied all the benefts af- forded to opposite-sex couples and are barred from exercis- ing a fundamental right. Especially against a long history of disapproval of their relationships, this denial to same-sex couples of the right to marry works a grave and continuing harm. The imposition of this disability on gays and lesbians serves to disrespect and subordinate them. And the Equal Protection Clause, like the Due Process Clause, prohibits this unjustifed infringement of the fundamental right to marry. See, e. g., Zablocki, supra, at 3

Kennedy applies interlocking liberty and equality protections to same-sex couples and says both clauses prohibit the infringement. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp27–29, chunk 19: RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.684205; official page-overlap relevance: True.

> The right of same-sex couples to marry that is part of the liberty promised by the Fourteenth Amendment is derived, too, from that Amendment's guarantee of the equal protec- tion of the laws. The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles.

The closing passage explicitly derives the marriage right from both liberty and equal protection and connects the clauses. Earlier parts give exclusion/stigma context. Already covered.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp50–52, chunk 33: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.675876; official page-overlap relevance: False.

> Due Process Clause. The Solicitor Gen- 694 OBERGEFELL v. HODGES Roberts, C. J., dissenting eral of the United States, appearing in support of petitioners, expressly disowned that position before this Court. See Tr. of Oral Arg. on Question 1, at 38–39. The majority never- theless resolves these cases for petitioners based almost entirely on the Due Process Clause. The majority purports to identify four “principles and tra- ditions” in this Court's due process precedents that support a fundamental right for same-sex couples to marry. Ante, at 665. In reality, however, the majority's approach has no basis in principle or tradition, except for the unprincipled tradition of judicial policymaking that characterized discred- ited decisions such as Lochner v. New York, 198 U. S. 45. Stripped of its shiny rhetorical gloss, the majority's argu- me

Roberts’s account of the petitioners’ claims and attack on due-process reasoning does not explain the majority’s linkage of the two clauses.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### DRE-04 — Dred Scott v. Sandford

Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

Type: `legal_rule`. Current ranges: [[3, 4]]. Proposed additions: None.

No unambiguous addition from the saved Top-5. The question asks for the Court’s reason, and the accepted pages 3–4 summarize constitutional property/equal-access limits. Majority pages 58–60 confirm the property/due-process rationale as context only, not an addition proposed in this candidate-limited audit. Campbell and Daniel concurrences need human judgment; McLean, Curtis, Nelson, and Catron passages do not independently establish that controlling rationale. The Grier/Daniel attribution discrepancy is documented, not repaired.

**fixed_900_150, rank 1, PDF pp144–145, chunk 146: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.582107; official page-overlap relevance: False.

> State institution. In the ninth section of the first article of the Constitution, it is provided "that the migration or importation of such persons as any of the States now existing shall think proper to admit, shall not be prohibited by the- Congress prior to the year 1808, but a tax or duty may be impose on such importation, not exceed- in ten dollars for each person." In the Convention, it was proposed by a committee of eleven to limit the importation of slaves to the year 1800, when Mr. Pinckney moved to extend the time to the year 1808. This motion was carried-New Hampshire, Massachusetts, Connecti- cut, Maryland, North Carolina, South Carolina, and Georgia, voting in the affirmative; and New. Jersey, Pennsylvania, and Virginia, in the negative. [n opposition to the motion, Mr. 'Madison said: *"Twenty years will produce all the misch

McLean discusses slavery as a state institution and importation/state trade powers, not the Court’s constitutional restriction on Congress governing the federal territory.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp228–229, chunk 230: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.581026; official page-overlap relevance: False.

> while the third is, that the Constitution itself secures to every citizen who holds slaves, under the laws of any State, the indefeasible right to carry them into any Territory, and there hold them as property. No particular clause of the Constitution has been referred to at the bar in support of either of these views. The first seems to be rested upon general considerations concerning the social and moral evils of slavery, its relations to republican Govern- ments, its inconsistency with the Declaration of Independence and with natural right, The second i* drawn from considerations equally general, concerning the right of self-government, and the nature of the political institutions which have been established by the people of the United States. While the third is said to rest upon the equal right of all citizens to go with their propert

Curtis sets out several competing theories presented in argument and rejects inserting political exceptions into the Territory Clause. He does not attribute a supporting rationale to the controlling opinion.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp72–73, chunk 74: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: other; author: Nelson; similarity (navigation only): 0.578102; official page-overlap relevance: False.

> within the State of Missouri, that it can have any effect upon the question between the parties. Having no such effect di- rectly, it will be difficult, to maintain, upon any consistent reasoning, that it can be made to operate indirectly upon the subject. The argument, we think, in any aspect in which it may be viewed, is utterly destitute of support upon any principles of constitutional law, as, according to that, Congress has no pow- er whatever over the subject of slavery within the State; and is also subversive of the established doctrine of international jurisprudence, as, according to that, it is an axiom that the laws 6f one Government have no force within the limits of another, or extra-territorially, except from the consent of the latter. It is perhaps not unfit to 4otice, in this connection, that many of the most eminent states

Nelson’s discussion concerns Missouri status after return and extraterritorial operation of a law; that is a different ground from Congress’s inability to prohibit slavery within the federal territory.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp125–126, chunk 127: AMBIGUOUS**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: mixed_or_unassigned; author: not established; similarity (navigation only): 0.576227; official page-overlap relevance: False.

> in my opinion, that clause confers no power upon Con- gress to dissolve the relations of the master and slave on the omain of the United States, either within or without any of the States. The eighth section of the act of'Congress of the 6th of March, 1820, did not, in my opinion, operate to determine the domes- tic condition and status of the plaintiff and his family during their sojourn in Minnesota Territory, or after their return to -Missouri. The question occurs as to the judgment to be given in-this case. It appeared upon the trial that the. plaintiff, in 1834, was in a state of slavery in Missouri, and he had been in Mis- souri for near fifteen years in that condition when this suit was brought. N'or does it appear that he at apy time possessed another state or condition, de facto. His claim to freedom depends upon his temporary el

Campbell expressly denies territorial power to dissolve master/slave relations, but presents his own construction of the Territory Clause. It is not independently identified as Taney’s controlling property/due-process rationale. Human review is needed on whether this supporting concurrence satisfies “the Court.”

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 5, PDF pp235–236, chunk 237: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: Curtis; similarity (navigation only): 0.574086; official page-overlap relevance: False.

> due process of.law, what shall we say of the legislation of many of the slavehold- ing States.which hav6 enacted the same prohibition? As early as October, 1778, a law was passed.in Virginia,.that thereafter no slave should .be imported into that Commonwealth by pea or by land; -and that every slave who should be ihp orted should become free. A citizen of~irginiapurciasedinMary- land a slavewho belonged to'another citizen of .irgina, and removed with the slave to Virginia. The slave sued for her freedom, and recovered it; as maybe seen in "Wilson v. Isabel, (5 Call's R., 425.) See also Hunter v. Xulsher, (1 Leigh, 172;) and a -similar la6w has been recognised as vAlid in Maryland, in Stewart v. 0aks, (5 Ear. and John.; 107.) I am not aware that such laws, though'they exist in many States, were ever supp csed. to be in coflict with the Pri

Curtis attacks the property/due-process argument with state importation prohibitions and the slave-trade analogy. A contrary response is not the Court’s supporting reasoning.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp124–125, chunk 95: AMBIGUOUS**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: concurrence; author: Campbell; similarity (navigation only): 0.638517; official page-overlap relevance: False.

> Aiid, in my opinion, that clause confers no power upon Con- gress to dissolve the relations of the master and slave on the omain of the United States, either within or without any of the States. The eighth section of the act of'Congress of the 6th of March, 1820, did not, in my opinion, operate to determine the domes- tic condition and status of the plaintiff and his family during their sojourn in Minnesota Territory, or after their return to -Missouri. The question occurs as to the judgment to be given in-this case. It appeared upon the trial that the. plaintiff, in 1834, was in a state of slavery in Missouri, and he had been in Mis- souri for near fifteen years in that condition when this suit was brought. N'or does it appear that he at apy time possessed another state or condition, de facto. His claim to freedom depends upon his tempor

Campbell argues lack of municipal sovereignty in the territories and reports the Court’s limits on interstate migration controls. The territorial conclusion is his own construction; no clear attribution to the controlling rationale. Do not add automatically.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp97–99, chunk 74: AMBIGUOUS**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: concurrence; author: Daniel; similarity (navigation only): 0.636468; official page-overlap relevance: False.

> Nothing can be more conclusive to show the equality of this with every other right in all the citizens of the United States, and the iniquity and absurdity of the pretension to exclude or to disfranchise a portion of them because they are the owners of slaves, than the fact that the same instrument, which imparts to Congress its very existence and its every function, guaranties to the slaveholder the title to his property, and gives him the right to its reclamation throughout the entire extent of the nation; and, farther, that the only private roperty which the Constitution has s'pecifically recognised, and as imposed it as a direct obligation both on the States and the Federal Government to protect and enforce, is the property of the master in his slave; no other right of property is placed by the Constitution upon the same high ground, 

The source is Daniel, although saved parser metadata says Grier. His concurrence’s equal-access and constitutionally protected slave-property argument overlaps the majority’s reasoning on pages 3 and 59–60, but this is a separately stated argument rather than an identified quotation of that reasoning. Whether the wording permits it needs human judgment.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Source pp77–79 show Daniel begins after Grier on p77; running headings confirm Daniel. Saved parser attribution remains untouched.

**structure_aware_v1, rank 3, PDF pp143–145, chunk 111: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: dissent; author: McLean; similarity (navigation only): 0.620205; official page-overlap relevance: False.

> State institution. In the ninth section of the first article of the Constitution, it is provided "that the migration or importation of such persons as any of the States now existing shall think proper to admit, shall not be prohibited by the- Congress prior to the year 1808, but a tax or duty may be impose on such importation, not exceed- in ten dollars for each person." In the Convention, it was proposed by a committee of eleven to limit the importation of slaves to the year 1800, when Mr. Pinckney moved to extend the time to the year 1808. This motion was carried-New Hampshire, Massachusetts, Connecti- cut, Maryland, North Carolina, South Carolina, and Georgia, voting in the affirmative; and New. Jersey, Pennsylvania, and Virginia, in the negative. [n opposition to the motion, Mr. 'Madison said: *"Twenty years will produce all the misch

McLean’s state-institution and historical importation discussion is not the Court’s reasoning about prohibiting slaveholding in the federal territory.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp131–132, chunk 101: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: other; author: Catron; similarity (navigation only): 0.618463; official page-overlap relevance: False.

> My opinion is, that Congress had no power, in face of the 'compact between Virginia and the twelve other States, to force slavery into the Northwest Territory, because there, it was bound to that "engagement," and could not break it. SUPREME COURT. Ms. JUSTIc E CATRO..] Dqrd SoU v. Sandford. In 1790, North Carolina ceded her western territory, now the State of Tennessee, and stipulated that the inhabitants thereof should enioy all the privileges and advantages of the ordinance for governing the territory north of the Ohio river, and that Congress should assume the government, and accept the cession, under the express conditions contained in the or- dinance-: -Provided, "That no regulation made, or to be made, by Congress, shall tend to emancipate slaves." In 1802, Georgia ceded her western territory to the United States, -with the provisi

Catron analyzes limits arising from cession compacts and treaty protections. This is a distinct separate-opinion theory, not the controlling territorial property/due-process explanation asked for.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp116–117, chunk 89: NOT_RELEVANT**

Source: `data/processed/dred_scott_v_sandford.txt`; opinion: concurrence; author: Campbell; similarity (navigation only): 0.617719; official page-overlap relevance: False.

> Can Congress determine the condition and status of persons who inhabit the Territories? The Constitution permits Congress to dispose of and to make all needful rules and regulations respecting the teiritory or other property belonong to the United States.

Campbell discusses municipal sovereignty, Missouri’s state admission, and asks the territorial-power question without independently supplying the controlling answer.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

### OBE-01 — Obergefell v. Hodges

What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

Type: `facts`. Current ranges: [[12, 13]]. Proposed additions: None.

No unambiguous addition. Page 13 explicitly enumerates the two limited granted questions: Fourteenth Amendment licensing and recognition of lawful out-of-state same-sex marriages. A holding/syllabus reconstruction is ambiguous under this procedural wording. Retain the current ranges pending human judgment.

**fixed_900_150, rank 1, PDF pp37–39, chunk 36: AMBIGUOUS**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.630623; official page-overlap relevance: False.

> These cases also present the question whether the Consti- tution requires States to recognize same-sex marriages val- idly performed out of State. As made clear by the case of Obergefell and Arthur, and by that of DeKoe and Kostura, the recognition bans infict substantial and continuing harm on same-sex couples. Being married in one State but having that valid marriage denied in another is one of “the most perplexing and dis- tressing complications” in the law of domestic relations. Williams v. North Carolina, 317 U. S. 287, 299 (1942) (inter- nal quotation marks omitted). Leaving the current state of affairs in place would maintain and promote instability and uncertainty. For some couples, even an ordinary drive into a neighboring State to visit family or friends risks causing severe hardship in the event of a spouse's hospitalization wh

Kennedy states the licensing holding and discusses the recognition question in section V, but does not independently identify BOTH as the two questions limited in the grant of review. Accepting a holding-based reconstruction rather than the procedural fact needs judgment.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 2, PDF pp50–51, chunk 48: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.625040; official page-overlap relevance: False.

> Petitioners brought lawsuits contending that the Due Process and Equal Protection Clauses of the Fourteenth Amendment compel their States to license and recognize marriages between same-sex couples. In a carefully rea- soned decision, the Court of Appeals acknowledged the dem- ocratic “momentum” in favor of “expand[ing] the defnition of marriage to include gay couples,” but concluded that peti- tioners had not made “the case for constitutionalizing the defnition of marriage and for removing the issue from the place it has been since the founding: in the hands of state voters.” 772 F. 3d, at 396, 403. That decision interpreted the Constitution correctly, and I would affrm. II Petitioners frst contend that the marriage laws of their States violate the Due Process Clause. The Solicitor Gen-

Roberts describes petitioners’ claims to licensing/recognition and his preferred affirmance; this is not the Court’s specification of the two constitutional questions it agreed to decide.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 3, PDF pp33–34, chunk 32: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.619915; official page-overlap relevance: False.

> Constitution contemplates that democracy is the appropriate process for change, so long as that process does not abridge fundamental rights. Last Term, a plural- ity of this Court reaffrmed the importance of the democratic

Kennedy discusses debate, caution, and constitutional adjudication without identifying the two questions.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**fixed_900_150, rank 4, PDF pp97–98, chunk 94: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Alito; similarity (navigation only): 0.616240; official page-overlap relevance: False.

> Constitution. Thus, if the Constitution contained a provision guaran- teeing the right to marry a person of the same sex, it would be our duty to enforce that right. But the Con- 741 Cite as: 576 U. S. 644 (2015) Alito, J., dissenting stitution simply does not speak to the issue of same-sex marriage. In our system of government, ultimate sov- ereignty rests with the people, and the people have the right to control their own destiny. Any change on a question so fundamental should be made by the people through their elected offcials.” 570 U. S., at 809–810 (dissenting opinion) (citations and footnotes omitted). III Today's decision usurps the constitutional right of the peo- ple to decide whether to keep or alter the traditional un- derstanding of marriage. The decision will also have other important consequences. It will be used to vilify 

Alito discusses consequences and judicial power, not the two questions granted review.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**fixed_900_150, rank 5, PDF pp1–2, chunk 0: AMBIGUOUS**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: mixed_or_unassigned; author: not established; similarity (navigation only): 0.610681; official page-overlap relevance: False.

> Held: The Fourteenth Amendment requires a State to license a marriage between two people of the same sex and to recognize a marriage be- tween two people of the same sex when their marriage was lawfully licensed and performed out of State. Pp. 656–681. (a) Before turning to the governing principles and precedents, it is appropriate to note the history of the subject now before the Court. Pp. 656–663. (1) The history of marriage as a union between two persons of the opposite sex marks the beginning of these cases. To the respondents, it would demean a timeless institution if marriage were extended to same-sex couples. But the petitioners, far from seeking to devalue marriage, seek it for themselves because of their respect—and need— for its privileges and responsibilities, as illustrated by the petitioners' own experiences. Pp. 656–659. (2

The syllabus reports licensing/recognition claims and a holding addressing both, but does not specify the two questions in the limited grant of review. The existing standard for this procedural question requires both granted questions, not just the disposition.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

Extraction caveat: the final page marker has no following page text in this retrieved chunk.

**structure_aware_v1, rank 1, PDF pp19–20, chunk 14: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.677298; official page-overlap relevance: False.

> Defense of Marriage Act (DOMA), 110 Stat. 2419, defning marriage for all federal-law purposes as “only a legal union between one man and one woman as husband and wife.” 1 U. S. C. § 7. The new and widespread discussion of the subject led other States to a different conclusion. In 2003, the Supreme Judicial Court of Massachusetts held the State's Constitution guaranteed same-sex couples the right to marry. See Good- ridge v. Department of Public Health, 440 Mass. 309, 798 N. E. 2d 941. After that ruling, some additional States granted marriage rights to same-sex couples, either through judicial or legislative processes. These decisions and stat- utes are cited in Appendix B, infra. Two Terms ago, in United States v. Windsor, 570 U. S. 744 (2013), this Court invalidated DOMA to the extent it barred the Federal Gov- ernment from treating sam

Kennedy’s legal/history narrative covers Baehr, DOMA, and later developments, not both questions in the grant of review.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 2, PDF pp36–39, chunk 24: AMBIGUOUS**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.669059; official page-overlap relevance: False.

> These cases also present the question whether the Consti- tution requires States to recognize same-sex marriages val- idly performed out of State. As made clear by the case of Obergefell and Arthur, and by that of DeKoe and Kostura, the recognition bans infict substantial and continuing harm on same-sex couples. Being married in one State but having that valid marriage denied in another is one of “the most perplexing and dis- tressing complications” in the law of domestic relations. Williams v. North Carolina, 317 U. S. 287, 299 (1942) (inter- nal quotation marks omitted). Leaving the current state of affairs in place would maintain and promote instability and uncertainty. For some couples, even an ordinary drive into a neighboring State to visit family or friends risks causing severe hardship in the event of a spouse's hospitalization wh

Kennedy combines the licensing holding with the section-V recognition question and disposition. This is a plausible substantive reconstruction, but it does not explicitly report BOTH granted questions as on source page 13.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 3, PDF pp34–36, chunk 23: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: majority; author: Kennedy; similarity (navigation only): 0.665197; official page-overlap relevance: False.

> Court granted review to determine whether same-sex couples may 679 Cite as: 576 U. S. 644 (2015) Opinion of the Court exercise the right to marry. Were the Court to uphold the challenged laws as constitutional, it would teach the Nation that these laws are in accord with our society's most basic compact. Were the Court to stay its hand to allow slower, case-by-case determination of the required availability of specifc public benefts to same-sex couples, it still would deny gays and lesbians many rights and responsibilities in- tertwined with marriage. The respondents also argue allowing same-sex couples to wed will harm marriage as an institution by leading to fewer opposite-sex marriages. This may occur, the respondents contend, because licensing same-sex marriage severs the connection between natural procreation and marriage. That argum

Explicitly says review was granted on the right-to-marry issue and discusses petitioners’ injuries, but does not independently identify the second granted recognition question.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 4, PDF pp1–2, chunk 1: AMBIGUOUS**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: syllabus; author: not established; similarity (navigation only): 0.658190; official page-overlap relevance: False.

> Held: The Fourteenth Amendment requires a State to license a marriage between two people of the same sex and to recognize a marriage be- tween two people of the same sex when their marriage was lawfully licensed and performed out of State. Pp. 656–681. (a) Before turning to the governing principles and precedents, it is appropriate to note the history of the subject now before the Court. Pp. 656–663. (1) The history of marriage as a union between two persons of the opposite sex marks the beginning of these cases. To the respondents, it would demean a timeless institution if marriage were extended to same-sex couples. But the petitioners, far from seeking to devalue marriage, seek it for themselves because of their respect—and need— for its privileges and responsibilities, as illustrated by the petitioners' own experiences. Pp. 656–659. (2

The syllabus describes both claims and their disposition, not explicitly the two limited questions the Court granted review to decide. No range addition without resolving this procedural-versus-holding standard.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

**structure_aware_v1, rank 5, PDF pp43–45, chunk 29: NOT_RELEVANT**

Source: `data/processed/obergefell_v_hodges.txt`; opinion: dissent; author: Roberts; similarity (navigation only): 0.646645; official page-overlap relevance: False.

> license and recognize same-sex marriage. Many people will rejoice at this decision, and I begrudge none their celebration. But for those who believe in a government of laws, not of men, the majority's approach is deeply disheartening. Supporters of same-sex marriage have achieved considerable success persuading their fellow citizens—through the democratic process—to adopt their view. That ends today. Five lawyers have closed the de- bate and enacted their own vision of marriage as a matter of constitutional law. Stealing this issue from the people will for many cast a cloud over same-sex marriage, making a dra- matic social change that much more diffcult to accept. The majority's decision is an act of will, not legal judg- ment. The right it announces has no basis in the Consti- tution or this Court's precedent. The majority expressly dis

Roberts criticizes the majority’s licensing/recognition result; that criticism does not identify both questions in the Court’s grant of review.

Proposed addition: None (already covered, not relevant, or unresolved). Canonical source match: verified.

## SIMULATED — PROPOSED LABELS NOT APPLIED

Re-score all 40 SAVED Top-5 rankings using unchanged case/source/page-overlap and Hit@K/MRR rules, with only the eight frozen audit proposals added in memory. No reranking, embeddings, retrieval, or passage-decision substitution.

Page-overlap scoring remains coarse. A trailing empty page marker can obtain credit, and a partly irrelevant chunk on a newly labeled page can obtain credit. These metrics are not passage-level ground truth and do not resolve ambiguity.

| Strategy | Labels | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| fixed_900_150 | Official, reproduced locally | 0.725 | 0.900 | 0.900 | 0.808333 |
| fixed_900_150 | SIMULATED — proposed only | 0.750 | 0.900 | 0.900 | 0.825000 |
| structure_aware_v1 | Official, reproduced locally | 0.725 | 0.875 | 0.900 | 0.802083 |
| structure_aware_v1 | SIMULATED — proposed only | 0.825 | 0.925 | 0.950 | 0.877083 |

| Question | Fixed official → simulated rank | Structure official → simulated rank |
|---|---|---|
| DRE-01 | 3 → 1 | miss → 1 |
| MIR-04 | 1 → 1 | miss → 1 |
| MAR-01 | 1 → 1 | 2 → 1 |
| MAR-04 | 1 → 1 | 4 → 4 |
| DRE-03 | 1 → 1 | 2 → 2 |
| OBE-04 | 1 → 1 | 2 → 1 |
| DRE-04 | miss → miss | miss → miss |
| OBE-01 | miss → miss | miss → miss |

## Protected artifact verification

All 88 protected files are byte-identical by SHA-256 before/after audit processing and simulation. No network/API/embedding call, retrieval, chunk regeneration, vector-store write, commit, or push occurred.

Frozen decisions SHA-256: `47ca0884126688f4ce2d514624d587942e2fb80acef6866c3b2a622befa7ac59`.

| Protected file | SHA-256 before = after |
|---|---|
| `data/analysis/long_sentence_analysis.json` | `3fc7987789e3eac714f3ffc1a4badac762a6a89455b943298fede200c7a80418` |
| `data/analysis/long_sentence_analysis.md` | `2ce3d588d1b2e13eb91d66c2c450dc2ecc9612d7dc746f35fbc486fe79c95ca2` |
| `data/analysis/structure_aware_chunking.json` | `90fda71f43c598a1cc24815c1201e776b48220750e42712d5a83c9dc1bc90bbd` |
| `data/analysis/structure_aware_chunking.md` | `a84560f5ecf32faa71afdaf5bb8af6ce50343daafbd4838eb1b48c5ac2740b29` |
| `data/analysis/structure_aware_preview.json` | `0ade8e9853a10b8a57b0962ceeb839ed7493892caab903dd3b1b8dbfa9fa8442` |
| `data/analysis/structure_aware_preview.md` | `5d913b2f88147fd9152890cf4402269f47a42c16d20494d9472f4e183bdca48c` |
| `data/analysis/structure_aware_retrieval_evaluation.json` | `ea9c6c01903f668595671f6dde19f86823284cc8e26dd4a13c85693a0c03cee6` |
| `data/analysis/structure_aware_retrieval_evaluation.md` | `133760f9d075f161875ce18ebd1b4faed847d1d1a021a75490c6fb58d29437ad` |
| `data/chunks/dred_scott_v_sandford.jsonl` | `6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34` |
| `data/chunks/gideon_v_wainwright.jsonl` | `c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15` |
| `data/chunks/marbury_v_madison.jsonl` | `3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a` |
| `data/chunks/miranda_v_arizona.jsonl` | `8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b` |
| `data/chunks/new_york_times_co_v_united_states.jsonl` | `bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1` |
| `data/chunks/obergefell_v_hodges.jsonl` | `d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8` |
| `data/chunks/plessy_v_ferguson.jsonl` | `5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647` |
| `data/chunks/tinker_v_des_moines_school_dist.jsonl` | `15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768` |
| `data/evaluation/chunking_benchmark.json` | `00fc21f465043a09a209e8509f0513378cd6e385d62ca6dbfc7e09940a7eda3d` |
| `data/evaluation/chunking_benchmark_review.json` | `0cf60ecefd0e39df07d2eb76d8f8e629f499d92a190b293ffa70013795869370` |
| `data/evaluation/chunking_benchmark_review.md` | `13637d6f8dcd2f46a568085f4c22d9898301ddd45a2438da0ed6610c5ea09a15` |
| `data/evaluation/chunking_benchmark_reviewed.json` | `7cbfa42bf480717df7b7982297f8ea648a30a8d100d86ccdcaa5371b410b7595` |
| `data/experiments/chunking/1200_200/chunks/dred_scott_v_sandford.jsonl` | `6bced3d03076b6dfd93ff9f984dd88107ff582ca07be6b96d2e8dcd946173c34` |
| `data/experiments/chunking/1200_200/chunks/gideon_v_wainwright.jsonl` | `c52fe1269924b08ae97ff4dc999fc2b4129820c86d7524460749078e98b29b15` |
| `data/experiments/chunking/1200_200/chunks/marbury_v_madison.jsonl` | `3e8e7dde3b4b6ea2d7eabeba9e62c89b0175531b177181c4243497a5339c8e6a` |
| `data/experiments/chunking/1200_200/chunks/miranda_v_arizona.jsonl` | `8435d0deabb7e19135f3222be954e1219df33b4f239f98b581e2307736a3e77b` |
| `data/experiments/chunking/1200_200/chunks/new_york_times_co_v_united_states.jsonl` | `bdbac99d04f7fa7dae40f9c945cd4cb1a0b28163bc852101f49234be55fb91f1` |
| `data/experiments/chunking/1200_200/chunks/obergefell_v_hodges.jsonl` | `d9cfb053a24154723f815c833c07aeb4d839f080cd1a959d97e7d2381958ebd8` |
| `data/experiments/chunking/1200_200/chunks/plessy_v_ferguson.jsonl` | `5bea13c8765e84a03322d43b9849665d209c3e33a06899bab31ea0ce7cad0647` |
| `data/experiments/chunking/1200_200/chunks/tinker_v_des_moines_school_dist.jsonl` | `15aa8fe098ed56209a70c8f191d4bc9b7e01431a247682d91cff822689d49768` |
| `data/experiments/chunking/1200_200/vector_store/index.faiss` | `b8b7eb8795c385630cde542a8ec080cfd3db45eace57fcb741390d73f1214398` |
| `data/experiments/chunking/1200_200/vector_store/manifest.json` | `5c7c2d0550c78829d9d1b462bf97e19a31a96665f5dd99e993158c88de1f75b8` |
| `data/experiments/chunking/1200_200/vector_store/records.jsonl` | `0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648` |
| `data/experiments/chunking/1500_200/chunks/dred_scott_v_sandford.jsonl` | `10fae0685c82e38a761c0a4ea1d0071cd786e235a1dfc7a9c28f8de37c8e2742` |
| `data/experiments/chunking/1500_200/chunks/gideon_v_wainwright.jsonl` | `e8bd0ecadc3796c4db4985c10908008c139099c5b62cd6bfea2194ea7e645b28` |
| `data/experiments/chunking/1500_200/chunks/marbury_v_madison.jsonl` | `80e45c23b528fb783921f120237b5e27bf3063b8e2d0bfa0e2b9bc948971ef67` |
| `data/experiments/chunking/1500_200/chunks/miranda_v_arizona.jsonl` | `83d06f72d784b34fb414533653b1b80b17c213c82b99d00d0d3f5731999e92ef` |
| `data/experiments/chunking/1500_200/chunks/new_york_times_co_v_united_states.jsonl` | `87664a9f120da592273464784219306c2fe365438a54909a215d5938a0e89153` |
| `data/experiments/chunking/1500_200/chunks/obergefell_v_hodges.jsonl` | `3de38ca2d4fb4583ef212b45c71d0a51d69c7f4a241281fa3616eaf54effa11e` |
| `data/experiments/chunking/1500_200/chunks/plessy_v_ferguson.jsonl` | `f1dcc04ad0f49021e96df4781dedd9afcdcbe71d91d4a76f4de70eac4a3a56d6` |
| `data/experiments/chunking/1500_200/chunks/tinker_v_des_moines_school_dist.jsonl` | `81f365dd0aeea97e9faf0e4e7ebe9db7650b05f8a200945e86df39180e4c97dd` |
| `data/experiments/chunking/1500_200/vector_store/index.faiss` | `2e2a48e74ca9838482e4e091c20143b5c2d86282efd4588952329e13528184b2` |
| `data/experiments/chunking/1500_200/vector_store/manifest.json` | `6ab26c41d30b64583060470fde6704689f0053566b6947bbc7d83ddb1f01ef65` |
| `data/experiments/chunking/1500_200/vector_store/records.jsonl` | `42ffe0a0695d22b097bf8a2697f79d7ba549b4660d92f6e791e3f21b3afdc3b3` |
| `data/experiments/chunking/600_100/chunks/dred_scott_v_sandford.jsonl` | `c1609a75f1a36e53a097220f6c2dcb453f1216a768450c5b6071701e1ca71080` |
| `data/experiments/chunking/600_100/chunks/gideon_v_wainwright.jsonl` | `71459a6ad063507872da02249c2cdd4ecdafee1c6704b10d7a3ebe5c9265e410` |
| `data/experiments/chunking/600_100/chunks/marbury_v_madison.jsonl` | `a0cac67fddac8a95120c9d8c71dd372251c289a4cf79c03ae34e767ba4df593c` |
| `data/experiments/chunking/600_100/chunks/miranda_v_arizona.jsonl` | `fb5f22856d7410cac34b0ab71ec7defb82d19be231504036ab2f56bb8c0cb0e9` |
| `data/experiments/chunking/600_100/chunks/new_york_times_co_v_united_states.jsonl` | `a5f350297a6c5d3332149c38dfcea9a041b78e85e29fb55a011278055d5e94f2` |
| `data/experiments/chunking/600_100/chunks/obergefell_v_hodges.jsonl` | `2b0b30dfc0b05ae2e7d70111f0443740db5512b6192014c7c386211e1cbf9916` |
| `data/experiments/chunking/600_100/chunks/plessy_v_ferguson.jsonl` | `805a90d67ec45dc7ae6100cede7e3f745fa9d8fd5cf9fbeef1fcf7500a7e4108` |
| `data/experiments/chunking/600_100/chunks/tinker_v_des_moines_school_dist.jsonl` | `8066cc3b9ad15af0e214662003ca4c26c495b92d2ddd1bd184f79f388fb14ee3` |
| `data/experiments/chunking/600_100/vector_store/index.faiss` | `8e3ff55615273bc2c6e2b8f6831f276f9d6c38380c99acd09f744b897528e721` |
| `data/experiments/chunking/600_100/vector_store/manifest.json` | `6aff4f97e7314fb5e32369ee843f1b9debbbee303d132a11129905dac5b889d5` |
| `data/experiments/chunking/600_100/vector_store/records.jsonl` | `ef7c320e39ff67ebc5671a1f0e4473840cb314a88774a389ac580011c727e98d` |
| `data/experiments/chunking/900_150/chunks/dred_scott_v_sandford.jsonl` | `adaf3e4ebcc1f39a4de19548a4757ea57ad248a49eebaeef8ad55a3123432c40` |
| `data/experiments/chunking/900_150/chunks/gideon_v_wainwright.jsonl` | `2254a634b4c027e8049ee0488dfed74454388d805fa5e6a06f3baa0a001c8713` |
| `data/experiments/chunking/900_150/chunks/marbury_v_madison.jsonl` | `eb15fe41780d6e0451f637bbb1a62ee2a5f2f57e3f6cdd857df12e31cdf2edd4` |
| `data/experiments/chunking/900_150/chunks/miranda_v_arizona.jsonl` | `e62baecf9c2b45c05fc41ded6420f9951b87b816a0de8b2738d04308a7f8ada0` |
| `data/experiments/chunking/900_150/chunks/new_york_times_co_v_united_states.jsonl` | `a13bd800e9efe0fa3bc16127e0f7574a7f802b11719533aa19d6f9c762190ce0` |
| `data/experiments/chunking/900_150/chunks/obergefell_v_hodges.jsonl` | `2ab41ed081307b758da2ce031174e0815eef6622a2659b4b7871e1148c54368d` |
| `data/experiments/chunking/900_150/chunks/plessy_v_ferguson.jsonl` | `fd71d62c3f41f0cba8eeb960dc950a77a17b0d50a69c7fa83402ebed283e4203` |
| `data/experiments/chunking/900_150/chunks/tinker_v_des_moines_school_dist.jsonl` | `a68cd3727081d496f32e22828fdf7b4eab5882d5e541f2b7273d24ce624341eb` |
| `data/experiments/chunking/900_150/vector_store/index.faiss` | `e12f8a02f9b35fa9326fb830b917bdfdf41e5ba4aceccb0c2b806329770cc2a8` |
| `data/experiments/chunking/900_150/vector_store/manifest.json` | `846e19759df7714867d5353a60401e326439bb4fb92d9454986b9ce2124a4c99` |
| `data/experiments/chunking/900_150/vector_store/records.jsonl` | `f56cbda97ec73461c0c35f97cbc7575ce9ecf55c77beb5873377285c9d595f69` |
| `data/experiments/chunking/results.json` | `95ca699ef2be19f511d1a98508deeb6fb7c458228ee770e79f7afe83d7e6a123` |
| `data/experiments/chunking/reviewed_results.json` | `2e0d3d287b3e880dff3227939dbc796a75296986b9bbef9e86907e1d5c6e32ee` |
| `data/experiments/chunking/structure_aware_v1/chunks.jsonl` | `0feb95376bd2a3031d7df8ff87693c18ab5df757da002a2ff042040713a73fd4` |
| `data/experiments/chunking/structure_aware_v1/embedding_usage.json` | `dfeb22685a9b3eec3929d038ed94e72a3e81c5ac88e68a7d7b7a23e907a74bed` |
| `data/experiments/chunking/structure_aware_v1/evaluation_progress.json` | `ccd2e3d4c7cac3af4f89105bced86c7b4240dbe228a92228b87356c95ed22465` |
| `data/experiments/chunking/structure_aware_v1/manifest.json` | `d72c5703be6121228a107611ed47d0926424fa86a983ac83e747fe305f7d9e5d` |
| `data/experiments/chunking/structure_aware_v1/results.json` | `8928b1e1ec80881acdd7a4664c57661e1aa9df847691996db6229057acc081aa` |
| `data/experiments/chunking/structure_aware_v1/vector_store/index.faiss` | `8390441da91b421d6025327e7f8b6ca53030ec5b6e2d0516900330e614fbad81` |
| `data/experiments/chunking/structure_aware_v1/vector_store/manifest.json` | `55750e4b1b8086ee2596e83affdaa285cbe404f9e6cdeec180bc2100784e54af` |
| `data/experiments/chunking/structure_aware_v1/vector_store/records.jsonl` | `b736787bd3a2eae7ee8c8f029e18cf94a38332913ffe40ee44300c32002c4bce` |
| `data/processed/dred_scott_v_sandford.txt` | `1eb4617eebf3647626d7d3d4e142615c99d3cfbfdb7de80ce9c39b97b05b80ed` |
| `data/processed/gideon_v_wainwright.txt` | `10e0e4b6a2a7382d913a3cf3c1a8a3fa99aecdbbb14cfcee19011a4adce5db35` |
| `data/processed/marbury_v_madison.txt` | `85f4f933f9614718ca426da9545ae101778d39f88ee3fecd9bbb02081da74da1` |
| `data/processed/miranda_v_arizona.txt` | `872ba83c615f9d35e3f7ac841bc441d21dbc9e6ca22756314b42d12bb8cf9e6d` |
| `data/processed/new_york_times_co_v_united_states.txt` | `59a716ac534351d0ca21b10620ae31a2f27f9de4609feafbe1be9e8719496d49` |
| `data/processed/obergefell_v_hodges.txt` | `50267b559e1daf5e1c7859f8d3a167db54d128df11fc8ed9bfedbf33f5062b0b` |
| `data/processed/plessy_v_ferguson.txt` | `c15341b4e08e7060b6f089b1d2ee43ce0fc760020d53e0e943e88931a0fd191f` |
| `data/processed/tinker_v_des_moines_school_dist.txt` | `0d534a5e970cd117e9a397b6859ea4cb33c8f47a880d3c31e39a767e93df9dd7` |
| `data/vector_store/index.faiss` | `b81997170c48a649b84613ba4376c982c231acd27e610bda6e460c66a5d58a1c` |
| `data/vector_store/manifest.json` | `a97cecfdf385a49513c82b5fff1909053a77c74e833beffd773d3e54bffd5933` |
| `data/vector_store/records.jsonl` | `0a031b44b0556f217449a08e1f5bec8e04a58aeb9d8868da0c30a59a7d290648` |
| `generate_structure_aware_chunks.py` | `00d5e378f93dad3edee8e90a7219b5f47aebf4cdb02a2460df304f530fd6bcb9` |
| `parse_legal_structure.py` | `78d83a625d3316598c68bb92fd5c32d8e327c1f86698b48021bb38d5940e8ff3` |
| `run_structure_aware_experiment.py` | `f557892836178090f645fc68cbefa988c78d10f0189d152d0b388c377bef435f` |
