# Citation-support candidate review

**PROPOSED — not human-adjudicated; not frozen.**

32 claim examples and 6 answer-level examples.

Claim label counts: SUPPORTED: 10, PARTIALLY_SUPPORTED: 8, UNSUPPORTED: 8, CONTRADICTED: 6.

All sources are exact corpus chunks. Synthetic design changes claims or pairings, never source wording. Labels evaluate the specified passage, not legal truth across the corpus.

## Coverage

| Category | Requirement | Examples |
|---|---|---|
| A | Direct factual support | CS-001, CS-002, CS-003, CS-004, CS-005, CS-009, AR-005 |
| B | Correct legal holding attribution | CS-001, CS-003, CS-004, CS-005, CS-006 |
| C | Partial support | CS-011, CS-012, CS-013, CS-014, CS-015, CS-016, CS-017, CS-018 |
| D | Unsupported conclusion | CS-013, CS-021, CS-022, AR-002 |
| E | Contradiction | CS-023, CS-026, CS-027, CS-028, CS-029, CS-030 |
| F | Majority versus dissent confusion | CS-008, CS-023, CS-031, AR-002 |
| G | Concurrence cited for majority reasoning | CS-017, CS-024, CS-032 |
| H | Correct majority quotation reproduced inside dissent | CS-008, CS-031 |
| I | Misleading topically related citation | CS-019, CS-020, CS-021, CS-022, AR-003, AR-006 |
| J | Missing legal qualification | CS-010, CS-011, CS-012, CS-018, CS-028, AR-001 |
| K | Multi-part claim with incomplete support | CS-011, CS-014, CS-016, CS-018, AR-001 |
| L | Accurate quotation versus inaccurate paraphrase | CS-007, CS-008, CS-010, CS-026, CS-030 |
| M | Uncertainty in OCR-derived attribution | CS-003, CS-015, CS-025, CS-032 |
| N | Correct insufficient-evidence response | AR-003, AR-004 |
| O | Unsupported out-of-corpus answer | CS-019, CS-020, CS-021, AR-006 |

## Human adjudication

Every example needs approval. Prioritize partial/contradicted boundaries, dissent quotations, concurrence/majority attribution, missing qualifications, and OCR uncertainty. Review may change labels; no approval is inferred from these proposals.

For each item record reviewer, decision (approve/relabel/reject), final proposed label or response assessment, reason, and date in a separate reviewed artifact. Do not overwrite frozen source material or mark this dataset frozen automatically.

## Claim examples

| ID | Label (proposed) | Kind | Case / PDF pages | Priority |
|---|---|---|---|---|
| CS-001 | SUPPORTED | synthetic | Miranda v. Arizona / 9–10 | NORMAL |
| CS-002 | SUPPORTED | synthetic | Miranda v. Arizona / 9–10 | NORMAL |
| CS-003 | SUPPORTED | synthetic | Miranda v. Arizona / 1–2 | HIGH |
| CS-004 | SUPPORTED | synthetic | Miranda v. Arizona / 9–10 | NORMAL |
| CS-005 | SUPPORTED | synthetic | Miranda v. Arizona / 56–58 | NORMAL |
| CS-006 | SUPPORTED | authentic | Obergefell v. Hodges / 29–31 | NORMAL |
| CS-007 | SUPPORTED | synthetic | Obergefell v. Hodges / 29–31 | HIGH |
| CS-008 | SUPPORTED | synthetic | Obergefell v. Hodges / 63–65 | HIGH |
| CS-009 | SUPPORTED | synthetic | Gideon v. Wainwright / 15–17 | NORMAL |
| CS-010 | SUPPORTED | synthetic | New York Times Co. v. United States / 18–20 | NORMAL |
| CS-011 | PARTIALLY_SUPPORTED | synthetic | Miranda v. Arizona / 9–10 | NORMAL |
| CS-012 | PARTIALLY_SUPPORTED | synthetic | Miranda v. Arizona / 9–10 | HIGH |
| CS-013 | PARTIALLY_SUPPORTED | authentic | Obergefell v. Hodges / 29–31 | HIGH |
| CS-014 | PARTIALLY_SUPPORTED | synthetic | Miranda v. Arizona / 56–58 | NORMAL |
| CS-015 | PARTIALLY_SUPPORTED | synthetic | Miranda v. Arizona / 1–2 | HIGH |
| CS-016 | PARTIALLY_SUPPORTED | synthetic | Obergefell v. Hodges / 29–31 | NORMAL |
| CS-017 | PARTIALLY_SUPPORTED | synthetic | Gideon v. Wainwright / 15–17 | HIGH |
| CS-018 | PARTIALLY_SUPPORTED | synthetic | New York Times Co. v. United States / 18–20 | HIGH |
| CS-019 | UNSUPPORTED | synthetic | Obergefell v. Hodges / 39–40 | NORMAL |
| CS-020 | UNSUPPORTED | synthetic | Obergefell v. Hodges / 12–13 | NORMAL |
| CS-021 | UNSUPPORTED | synthetic | Obergefell v. Hodges / 17–19 | NORMAL |
| CS-022 | UNSUPPORTED | synthetic | Miranda v. Arizona / 56–58 | NORMAL |
| CS-023 | CONTRADICTED | synthetic | Obergefell v. Hodges / 63–65 | NORMAL |
| CS-024 | UNSUPPORTED | synthetic | Gideon v. Wainwright / 15–17 | HIGH |
| CS-025 | UNSUPPORTED | synthetic | Tinker v. Des Moines School Dist. / 12–13 | HIGH |
| CS-026 | CONTRADICTED | synthetic | Obergefell v. Hodges / 29–31 | NORMAL |
| CS-027 | CONTRADICTED | synthetic | Miranda v. Arizona / 9–10 | NORMAL |
| CS-028 | CONTRADICTED | synthetic | Miranda v. Arizona / 55–56 | NORMAL |
| CS-029 | CONTRADICTED | synthetic | Gideon v. Wainwright / 15–17 | NORMAL |
| CS-030 | CONTRADICTED | synthetic | New York Times Co. v. United States / 18–20 | NORMAL |
| CS-031 | UNSUPPORTED | synthetic | Obergefell v. Hodges / 63–65 | HIGH |
| CS-032 | UNSUPPORTED | synthetic | Tinker v. Des Moines School Dist. / 12–13 | HIGH |

### CS-001 — SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** The person must be warned prior to questioning that they have the right to remain silent.

**Rationale:** S1 explicitly requires a warning of the right to remain silent before questioning, subject to the passage’s alternative-safeguards framework. This isolated warning description does not assert that alternatives are forbidden.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim verbatim_smoke_answer; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-002 — SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** The person must be informed that any statement they do make can be used as evidence against them.

**Rationale:** S1 explicitly describes the warning that any statement may be used as evidence.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim verbatim_smoke_answer; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-003 — SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** If the person is indigent, a lawyer will be appointed to represent them.

**Rationale:** The extracted Syllabus text explicitly states the indigence/appointed-lawyer warning. The claim describes its substance; it does not invent an author for the unknown-labeled source.

**Source:** [S2], Miranda v. Arizona, PDF pages [1, 2]; raw opinion unknown, raw author Unknown. Chunk `miranda_v_arizona:structure_aware_v1:00000`; original index 0; vector row 232.

**Origin:** synthetic; claim verbatim_smoke_answer; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
OCTOBER TERM, 1965. Syllabus. 384 U. S. MIRANDA v. ARIZONA. CERTIORARI TO THE SUPREME COURT OF ARIZONA. No. 759. Argued February 28-March 1, 1966.- Decided June 13, 1966.*" In each of these cases the defendant while in police custody was questioned by police officers, detectives, or'a prosecuting attorney in a room in which he was cut off from* the outside world. None of the defendants was given a'full and effective warning ot his rights at the outset of the interrogation process. In all four cases the. questioning elicited oral admissions, and in three of them signed statements as 'well, which were admitted at their trials. All defendants were convicted and all convictions, except in No. 584, were affirmed on appeal. Held: 1. The prosecution may not use statements, whether exculpatory or inculpatory, stemming from questioning initiated by law en-forcement officers after' a person has been taken into custody orotherwise deprived of his freedom of action in any ignificant way, unless it demonstrates the use of procedural safeguards effective tosecure the Fifth Amendment's jrivilege against, self-incrimination. Pp. 444-491. (a) The atmosphere and environment of incommunicadointerrogation as it exists today -is inherently intimidating and works to undermine the privilege against self-incrimination. Un- less adequate preventive measures are taken to dispel the compul- sion inherent in custodial surroundings,, no statement obtained from the defendant can truly' be the product of his free choice. Pp.445-458. (b) The privilege against self-incrimination, which has had a long and expansive historical development, is the essential main-stay of our adversary system and guarantees to the individual the 'right fo remain silent unless he chooses to speak in the unfet- tered exercise of his own will,"' during a period of custodial inter- *Together with No. 760, Vignera v. New York, on' certiorari to the Court of Appeals of New York and No. 761, Westover v. United States, on certiorari to the United States Court of Appeals for theNinth Circuit, both argued February 28-March 1, 1966; and No. 584, California v. Stewart, on certiorari to the Supreme Court of California, argued February 28-March , 1966. 436 • MIRANDA v. ARIZONA. 436 Syllabus. rogation 'as well as in the courts .or during the course of other official investigations. Pp. 458-465. (c) The decision in Escobedo v.' Illinois, 378 U. S. 478, stressed the need for protective devices to make the process of police interrogation conform to the dictates of the privilege. Pp. 465-466. (d) In the absence of other effective measures the following procedures to safeguard the Fifth Amendment privilege must be observed: The person in custody must, prior to interrogation, be clearly informed that he has the right to remain silent, and that anything he says will be used against him in court; he must be clearly informed that he has the right to consult with a lawyer and to have the lawyer with him during interrogation, and that, if he is indigent, a lawyer will be appointed to represent him. Pp. 467-473. (e) If the individual indicates, prior to or during questioning, that he wishes to remain silent, the interrogation must cease; if he states that he wants an attorney, the questioning must cease until an attorney is present. Pp. 473-474. (f) Where an interrogation is conducted without the presence of an ahtorney and a statement is taken, a heavy burden'rests on the Government to demonstrate that the defendant knowingly and intelligently waived his right to counsel. P. 475. (g) Where the hidividual answers some questions during in- custody interrogation he has not waived his privilege and may invoke his right to remain silent thereafter.
```

### CS-004 — SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** The waiver of these rights must be made voluntarily, knowingly, and intelligently.

**Rationale:** S1 states that a waiver must be voluntary, knowing and intelligent.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim verbatim_smoke_answer; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-005 — SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** The Court reversed Miranda’s conviction after finding his confession inadmissible without effective protection of his rights.

**Rationale:** The passage says “We reverse” and explains the missing warnings and lack of otherwise effective protection. The qualification is preserved.

**Source:** [S3], Miranda v. Arizona, PDF pages [56, 58]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00034`; original index 34; vector row 266.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
V. Because of the nature of the problem and because of its recurrent significance in numerous cases, we have to this point discussed the relationship of the Fifth Amend- ment privilege to police interrogation without specific concentration on the facts of the cases before us. We turn now to these facts to consider the application to these cases of the constitutional principles discussed above. In each instance, we have concluded that state- ments were obtained from the defendant under circum- stances that did not meet constitutional standards for protection of the privilege. No. 759. Miranda v. Arizona. On March 13, 1963, petitioner, Ernesto Miranda, was arrested at his home and taken in custody to a Phoenix police station. He was there identified by the complain- ing witness. The police then took him to "Interrogation Room No. 2" of the detective bureau. There he was questioned by two police officers. The officers admitted at trial that Miranda was not advised that he had a right to have an attorney present."0 Two hours later, the 6 Miranda was also convicted in a separate trial on an unrelated robbery charge not presented here for review. A statement intro- duced at that trial was obtained from Miranda during the same interrogation which resulted in the confession involved herp. At the robbery trial, one officer testified that during the interrogation he did not tell Miranda that anything he said would be held against him or that he could consult with an attorney. The other officer stated that they had both told Miranda that anything he said would be used against him and that he was not required by law to tell them anything. 4 OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. officersemerged from the interrogation room with a writ- ten confession signed by Miranda. At the top of the statement was a typed paragraph stating that th6 con- fession was made voluntarily, without threats or promises of immunity and "with full knowledge Of my legal rights, understanding any statement I make may be used against me." 11 At his trial before a jury, the written confession was adniitted into evidence over the objection of defense counsel, and the officers testified to the prior oral con- fession made by Miranda during the interrogation. Miranda was found guilty of kidnapping and rape. He was sentenced to 20 to 30 years' imprisonment on each count, the sentences to run concurrently. On appeal, the Supreme Court of Arizona held that Miranda's con- stitutional rights were not violated in obtaining the confession and affirmed-the conviction. 98 Ariz. 18, 401 P. 2d 721. In reaching its decision, the court empha- sized heavily the fact. that Miranda did not specifically request counsel. We reverse. From the -testimony of the officers and by the admission of respondent, it is clear that Miranda was not in any way apprised of his right to consult with an attorney and to have one present during the interro- gation, nor was his right not to be compelled to incrimi- nate himself effectively protected in any other, manner. Without these warnings the-statementi were- inadmis- sible. The mere fact that he signed- a statemenf which contained a typed-in clause stating that he had "full knowledge" of his "legal rights" does not approach the knowing and intelligent waiver required to' relinquish con stitutional rights. Cf. H-aynes-v. Washington, 373 U. S. 67 One of the officers testified that he read this paragraph to ,Miranda. ' Apparently, however, he did'not do so until after Miranda- had confessed orally. 492 " MIRANDA v. ARIZONA. 436 Opinion of the Court. .503, 512-513 (1963); Haley v. Ohio, 332 U. S. 596, 601 (1948) (opinion of MR. JUSTICE DOUGLAS). No. 760. Vignera v. New York. Petitioner, Michael Vignea, was picked up by New York police on October 14, 1960, in connection with the robbery three days earlier of a Brooklyn dress shop. They took him to the 17th Detective Squad headquarters in Manhattan. Sometime thereafter he, was taken to the 66th Detective Squad.
```

### CS-006 — SUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** The majority in Obergefell v. Hodges explained that the Due Process Clause and the Equal Protection Clause of the Fourteenth Amendment are connected in a profound way, though they articulate independent principles.

**Rationale:** Kennedy majority S2 explicitly says the two clauses are profoundly connected but independent.

**Source:** [S2], Obergefell v. Hodges, PDF pages [29, 31]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00020`; original index 20; vector row 351.

**Origin:** authentic; claim verbatim_smoke_answer; pairing original_smoke_citation; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the right to marry refect this dynamic. In Loving, the Court invalidated a prohibi- tion on interracial marriage under both the Equal Protection Clause and the Due Process Clause. The Court frst de- clared the prohibition invalid because of its unequal treat- 673 Cite as: 576 U. S. 644 (2015) Opinion of the Court ment of interracial couples. It stated: “There can be no doubt that restricting the freedom to marry solely because of racial classifcations violates the central meaning of the Equal Protection Clause.” 388 U. S., at 12. With this link to equal protection the Court proceeded to hold the prohibi- tion offended central precepts of liberty: “To deny this fun- damental freedom on so unsupportable a basis as the racial classifcations embodied in these statutes, classifcations so directly subversive of the principle of equality at the heart of the Fourteenth Amendment, is surely to deprive all the State's citizens of liberty without due process of law.” Ibid. The reasons why marriage is a fundamental right became more clear and compelling from a full awareness and under- standing of the hurt that resulted from laws barring interra- cial unions. The synergy between the two protections is illustrated further in Zablocki. There the Court invoked the Equal Protection Clause as its basis for invalidating the challenged law, which, as already noted, barred fathers who were behind on child-support payments from marrying without judicial approval. The equal protection analysis depended in cen- tral part on the Court's holding that the law burdened a right “of fundamental importance.” 434 U. S., at 383. It was the essential nature of the marriage right, discussed at length in Zablocki, see id., at 383–387, that made apparent the law's incompatibility with requirements of equality. Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other. Indeed, in interpreting the Equal Protection Clause, the Court has recognized that new insights and societal under- standings can reveal unjustifed inequality within our most fundamental institutions that once passed unnoticed and un- challenged. To take but one period, this occurred with re- spect to marriage in the 1970's and 1980's. Notwithstanding the gradual erosion of the doctrine of coverture, see supra, at 660, invidious sex-based classifcations in marriage remained 674 OBERGEFELL v. HODGES Opinion of the Court common through the mid-20th century. See App. to Brief for Appellant in Reed v. Reed, O. T. 1971, No. 70–4, pp. 69– 88 (an extensive reference to laws extant as of 1971 treating women as unequal to men in marriage). These classifca- tions denied the equal dignity of men and women. One State's law, for example, provided in 1971 that “the husband is the head of the family and the wife is subject to him; her legal civil existence is merged in the husband, except so far as the law recognizes her separately, either for her own pro- tection, or for her beneft.” Ga. Code Ann. § 53–501 (1935).
```

### CS-007 — SUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other.

**Rationale:** This quotation exactly matches the original extracted majority text, including its em dash.

**Source:** [S2], Obergefell v. Hodges, PDF pages [29, 31]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00020`; original index 20; vector row 351.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the right to marry refect this dynamic. In Loving, the Court invalidated a prohibi- tion on interracial marriage under both the Equal Protection Clause and the Due Process Clause. The Court frst de- clared the prohibition invalid because of its unequal treat- 673 Cite as: 576 U. S. 644 (2015) Opinion of the Court ment of interracial couples. It stated: “There can be no doubt that restricting the freedom to marry solely because of racial classifcations violates the central meaning of the Equal Protection Clause.” 388 U. S., at 12. With this link to equal protection the Court proceeded to hold the prohibi- tion offended central precepts of liberty: “To deny this fun- damental freedom on so unsupportable a basis as the racial classifcations embodied in these statutes, classifcations so directly subversive of the principle of equality at the heart of the Fourteenth Amendment, is surely to deprive all the State's citizens of liberty without due process of law.” Ibid. The reasons why marriage is a fundamental right became more clear and compelling from a full awareness and under- standing of the hurt that resulted from laws barring interra- cial unions. The synergy between the two protections is illustrated further in Zablocki. There the Court invoked the Equal Protection Clause as its basis for invalidating the challenged law, which, as already noted, barred fathers who were behind on child-support payments from marrying without judicial approval. The equal protection analysis depended in cen- tral part on the Court's holding that the law burdened a right “of fundamental importance.” 434 U. S., at 383. It was the essential nature of the marriage right, discussed at length in Zablocki, see id., at 383–387, that made apparent the law's incompatibility with requirements of equality. Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other. Indeed, in interpreting the Equal Protection Clause, the Court has recognized that new insights and societal under- standings can reveal unjustifed inequality within our most fundamental institutions that once passed unnoticed and un- challenged. To take but one period, this occurred with re- spect to marriage in the 1970's and 1980's. Notwithstanding the gradual erosion of the doctrine of coverture, see supra, at 660, invidious sex-based classifcations in marriage remained 674 OBERGEFELL v. HODGES Opinion of the Court common through the mid-20th century. See App. to Brief for Appellant in Reed v. Reed, O. T. 1971, No. 70–4, pp. 69– 88 (an extensive reference to laws extant as of 1971 treating women as unequal to men in marriage). These classifca- tions denied the equal dignity of men and women. One State's law, for example, provided in 1971 that “the husband is the head of the family and the wife is subject to him; her legal civil existence is merged in the husband, except so far as the law recognizes her separately, either for her own pro- tection, or for her beneft.” Ga. Code Ann. § 53–501 (1935).
```

### CS-008 — SUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** Roberts reproduced the majority’s statement that liberty and equal protection may rest on different precepts and are not always co-extensive.

**Rationale:** The dissent explicitly introduces the quoted language as “The majority’s approach today” (with straight extracted apostrophe). Reproducing an opponent’s reasoning is not endorsing it.

**Source:** [S1], Obergefell v. Hodges, PDF pages [63, 65]; raw opinion dissent, raw author Roberts. Chunk `obergefell_v_hodges:structure_aware_v1:00041`; original index 41; vector row 372.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
III In addition to their due process argument, petitioners con- tend that the Equal Protection Clause requires their States to license and recognize same-sex marriages. The majority does not seriously engage with this claim. Its discussion is, quite frankly, diffcult to follow. The central point seems to be that there is a “synergy between” the Equal Protection Clause and the Due Process Clause, and that some prece- dents relying on one Clause have also relied on the other. Ante, at 673. Absent from this portion of the opinion, how- 707 Cite as: 576 U. S. 644 (2015) Roberts, C. J., dissenting ever, is anything resembling our usual framework for decid- ing equal protection cases. It is casebook doctrine that the “modern Supreme Court's treatment of equal protection claims has used a means-ends methodology in which judges ask whether the classifcation the government is using is suffciently related to the goals it is pursuing.” G. Stone, L. Seidman, C. Sunstein, M. Tushnet, & P. Karlan, Consti- tutional Law 453 (7th ed. 2013). The majority's approach today is different: “Rights implicit in liberty and rights secured by equal protection may rest on different precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to cap- ture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may con- verge in the identifcation and defnition of the right.” Ante, at 672. The majority goes on to assert in conclusory fashion that the Equal Protection Clause provides an alternative basis for its holding. Ante, at 675. Yet the majority fails to pro- vide even a single sentence explaining how the Equal Protec- tion Clause supplies independent weight for its position, nor does it attempt to justify its gratuitous violation of the canon against unnecessarily resolving constitutional questions. See Northwest Austin Municipal Util. Dist. No. One v. Holder, 557 U. S. 193, 197 (2009). In any event, the mar- riage laws at issue here do not violate the Equal Protection Clause, because distinguishing between opposite-sex and same-sex couples is rationally related to the States' “legiti- mate state interest” in “preserving the traditional institution of marriage.” Lawrence, 539 U. S., at 585 (O'Connor, J., con- curring in judgment). It is important to note with precision which laws petition- ers have challenged. Although they discuss some of the an- 708 OBERGEFELL v. HODGES Roberts, C. J., dissenting cillary legal benefts that accompany marriage, such as hospi- tal visitation rights and recognition of spousal status on offcial documents, petitioners' lawsuits target the laws de- fning marriage generally rather than those allocating bene- fts specifcally. The equal protection analysis might be dif- ferent, in my view, if we were confronted with a more focused challenge to the denial of certain tangible benefts. Of course, those more selective claims will not arise now that the Court has taken the drastic step of requiring every State to license and recognize marriages between same-sex couples.
```

### CS-009 — SUPPORTED (PROPOSED)

**Question:** How did Harlan describe Betts v. Brady in his Gideon concurrence?

**Claim:** Harlan agreed that Betts v. Brady should be overruled.

**Rationale:** The concurrence opens with his express agreement; the claim is about Harlan, not the majority.

**Source:** [S1], Gideon v. Wainwright, PDF pages [15, 17]; raw opinion concurrence, raw author Harlan. Chunk `gideon_v_wainwright:structure_aware_v1:00011`; original index 11; vector row 197.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE HARLAN, concurring. I agree that Betts v. Brady should be overruled, but consider it entitled to a more respectful burial than has been accorded, at least on the part of those of us who were not on the Court when that case was decided. I cannot subscribe to the view that Betts v. Brady represented "an abrupt break with its own well-consid- ered precedents." Ante, p. 344. In 1932, in Powell v. Alabama, 287 U. S. 45, a capital case, this Court declared that under the particular facts there presented-"the ignorance and illiteracy of the defendants, their youth, the circumstances of public hostility ... and above all that they stood in deadly peril of their lives" (287 U. S., at 71)-the state court had a duty to assign counsel for 3 See, e. g., Barzun, In Favor of Capital Punishment; 31 American Scholar 181, 188-189 (1962). 350 OCTOBER TERM, 1962. HARLAN, J., concurring. 372 U. S. the trial as a necessary requisite of due process of law. It is evident that these limiting facts were not added to the opinion as an afterthought; they were repeatedly empha- sized, see 287 U. S., at 52, 57-58, 71, and were clearly regarded as important to the result. Thus when this Court, a decade later, decided Betts v. Brady, it did no more than to admit of the possible- exist- ence of special circumstances in noncapital as well as capital trials, while at the same time insisting that such circumstances be shown in order to establish a denial of due process. The right to appointed counsel had been recognized as being considerably broader in federal prose- cutions, see Johnson v. Zerbst, 304 U. S. 458, but to have imposed these requirements on the States would indeed have been "an abrupt break" with the almost immediate past. The declaration that the right to appointed counsel in state prosecutions, as established in Powell v. Ala- bama, was not limited to capital cases was in truth not a departure from, but an extension of, existing precedent. The principles declared in Powell and in Betts, however, have had a troubled journey throughout the years that have followed first the one case and then the other. Even by the time of the Betts decision, dictum in at least one of the Court's opinions had indicated that there was an abso- lute right to the services of counsel in the trial of state capital cases.1 Such dicta continued to appear in subse- quent decisions,' and any lingering doubts were finally eliminated by the holding of Hamilton v. Alabama, 368 U. S. 52. In noncapital cases, the "special circumstances" rule has continued to exist in form while its substance has been substantially and steadily eroded. In the first decade after Betts, there were cases in which the Court 'Avery v. Alabama, 308 U. S. 444, 445. 2 E. g., Bute v. Illinois, 333 U. S. 640, 674; Uveges v. Pennsylvania, 335 U. S. 437, 441. GIDEON v. WAINWRIGHT. 335 HARLAN, J., concurring. found special circumstances to be lacking, but usually by a sharply divided vote.3 However, no such decision has been cited to us, and I have found none, after Quicksall v. Michigan, 339 U. S. 660, decided in 1950. At the same tij.,p, there have been not a few cases in which special cir- cumstances were found in little or nothing more than the "complexity". of the legal questions presented, although those questions were often of only routine difficulty.4 The Court has come to recognize, in other words, that the mere existence of a serious criminal charge constituted in itself special circumstances requiring the servicesL of counsel at trial. In truth the Betts v. Brady rule is no longer a reality.
```

### CS-010 — SUPPORTED (PROPOSED)

**Question:** What position did White take on prior restraints in New York Times Co. v. United States?

**Claim:** White declined to say that the First Amendment would forbid injunctions in every circumstance.

**Rationale:** He expressly writes “I do not say that in no circumstances” an injunction would be permitted. Attribution and conditional scope are preserved.

**Source:** [S1], New York Times Co. v. United States, PDF pages [18, 20]; raw opinion concurrence, raw author White. Chunk `new_york_times_co_v_united_states:structure_aware_v1:00013`; original index 13; vector row 312.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. I concur in today's judgments, but only because of the concededly extraordinary protection against prior re- NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an injunction against publication in these cases, at least in the absence of express and appropriately limited con- gressional authorization for prior restraints in circum- stances such as these. 1 The Congress has authorized a strain of prior restraints against private parties in certain instances. The National Labor Relations Board routinely issues cease-and-desist orders against employers who it finds have threatened or coerced employees in the exercise of protected rights. See 29 U. S. C. § 160 (c). Similarly, the Federal Trade Commission is empowered to impose cease-and-desist orders against unfair methods of competition. 15 U. S. C. § 45 (b). Such orders can, and quite often do, restrict what may be spoken or written under certain circumstances. See, e. g., NLRB v. Gissel Packing Co., 395 U. S. 575, 616-620 (1969). Article I, § 8, of the Constitution authorizes Congress to secure the "exclusive right" of authors to their writings, and no one denies that a newspaper can properly be enjoined from publishing the copyrighted works of another. See Westermann Co. v. Dispatch Co., 249 U. S. 100 (1919). Newspapers do themselves rely from time to time on the copyright as a means of protecting their accounts of important events. However, those enjoined under the statutes relating to the National Labor Relations Board and the Federal Trade Com- mission are private parties, not the press; and when the press is enjoined under the copyright laws the complainant is a private copyright holder enforcing a private right. These situations are quite distinct from the Government's request for an injunction against publishing information about the affairs of government, a request admittedly not based on any statute. OCTOBER TERM, 1970 WHrTE, J., concurring 403 U. S. The Government's position is simply stated: The re- sponsibility of the Executive for the conduct of the foreign affairs and for the security of the Nation is so basic that the President is entitled to an injunction against publi- cation of a newspaper story whenever he can convince a court that the information to be revealed threatens "grave and irreparable" injury to the public interest; 2 and the injunction should issue whether or not the material to be published is classified, whether or not publication would be lawful under relevant criminal statutes enacted by Congress, and regardless of the circumstances by which the newspaper came into possession of the information. At least in the absence of legislation by Congress, based on its own investigations and findings, I am quite unable to agree that the inherent powers of the Executive and the courts reach so far as to authorize remedies having such sweeping potential for inhibiting publications by the press. Much of the difficulty inheres in the "grave and irreparable danger" standard suggested by the United States. If the United States were to have judgment under such a standard in these cases, our decision would be of little guidance to other courts in other cases, for the material at issue here would not be available from the Court's opinion or from public records, nor would it be published by the press. Indeed, even today where we hold that the United States has not met its burden, the material remains sealed in court records and it is 2 The "grave and irreparable danger" standard is that asserted by the Government in this Court.
```

### CS-011 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** Miranda required the right-to-silence warning and a signed written waiver in every interrogation.

**Rationale:** The silence warning is supported; a signed written waiver in every interrogation is not established. The compound probe has two declared components.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-012 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** Miranda’s specified warnings are the only lawful safeguards for all custodial questioning.

**Rationale:** The warning framework is supported, but the claim omits the express allowance for other fully effective means and overstates exclusivity. Review whether the absolute “only” instead warrants CONTRADICTED.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-013 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** This connection helped the Court conclude that state laws banning same-sex marriage violate both liberty and equality principles enshrined in the Fourteenth Amendment [S2].

**Rationale:** The clause interrelation is directly supported, but this selected majority chunk does not state the operative same-sex-marriage holding. The next majority chunk was not generation evidence. Review scope relative to implication versus explicit holding.

**Source:** [S2], Obergefell v. Hodges, PDF pages [29, 31]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00020`; original index 20; vector row 351.

**Origin:** authentic; claim verbatim_smoke_answer; pairing original_smoke_citation; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the right to marry refect this dynamic. In Loving, the Court invalidated a prohibi- tion on interracial marriage under both the Equal Protection Clause and the Due Process Clause. The Court frst de- clared the prohibition invalid because of its unequal treat- 673 Cite as: 576 U. S. 644 (2015) Opinion of the Court ment of interracial couples. It stated: “There can be no doubt that restricting the freedom to marry solely because of racial classifcations violates the central meaning of the Equal Protection Clause.” 388 U. S., at 12. With this link to equal protection the Court proceeded to hold the prohibi- tion offended central precepts of liberty: “To deny this fun- damental freedom on so unsupportable a basis as the racial classifcations embodied in these statutes, classifcations so directly subversive of the principle of equality at the heart of the Fourteenth Amendment, is surely to deprive all the State's citizens of liberty without due process of law.” Ibid. The reasons why marriage is a fundamental right became more clear and compelling from a full awareness and under- standing of the hurt that resulted from laws barring interra- cial unions. The synergy between the two protections is illustrated further in Zablocki. There the Court invoked the Equal Protection Clause as its basis for invalidating the challenged law, which, as already noted, barred fathers who were behind on child-support payments from marrying without judicial approval. The equal protection analysis depended in cen- tral part on the Court's holding that the law burdened a right “of fundamental importance.” 434 U. S., at 383. It was the essential nature of the marriage right, discussed at length in Zablocki, see id., at 383–387, that made apparent the law's incompatibility with requirements of equality. Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other. Indeed, in interpreting the Equal Protection Clause, the Court has recognized that new insights and societal under- standings can reveal unjustifed inequality within our most fundamental institutions that once passed unnoticed and un- challenged. To take but one period, this occurred with re- spect to marriage in the 1970's and 1980's. Notwithstanding the gradual erosion of the doctrine of coverture, see supra, at 660, invidious sex-based classifcations in marriage remained 674 OBERGEFELL v. HODGES Opinion of the Court common through the mid-20th century. See App. to Brief for Appellant in Reed v. Reed, O. T. 1971, No. 70–4, pp. 69– 88 (an extensive reference to laws extant as of 1971 treating women as unequal to men in marriage). These classifca- tions denied the equal dignity of men and women. One State's law, for example, provided in 1971 that “the husband is the head of the family and the wife is subject to him; her legal civil existence is merged in the husband, except so far as the law recognizes her separately, either for her own pro- tection, or for her beneft.” Ga. Code Ann. § 53–501 (1935).
```

### CS-014 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** Miranda’s confession was inadmissible, and every spontaneous statement to police is inadmissible.

**Rationale:** The specific confession finding is supported; the universal spontaneous-statement rule is not. These two components intentionally form one compound diagnostic probe.

**Source:** [S3], Miranda v. Arizona, PDF pages [56, 58]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00034`; original index 34; vector row 266.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
V. Because of the nature of the problem and because of its recurrent significance in numerous cases, we have to this point discussed the relationship of the Fifth Amend- ment privilege to police interrogation without specific concentration on the facts of the cases before us. We turn now to these facts to consider the application to these cases of the constitutional principles discussed above. In each instance, we have concluded that state- ments were obtained from the defendant under circum- stances that did not meet constitutional standards for protection of the privilege. No. 759. Miranda v. Arizona. On March 13, 1963, petitioner, Ernesto Miranda, was arrested at his home and taken in custody to a Phoenix police station. He was there identified by the complain- ing witness. The police then took him to "Interrogation Room No. 2" of the detective bureau. There he was questioned by two police officers. The officers admitted at trial that Miranda was not advised that he had a right to have an attorney present."0 Two hours later, the 6 Miranda was also convicted in a separate trial on an unrelated robbery charge not presented here for review. A statement intro- duced at that trial was obtained from Miranda during the same interrogation which resulted in the confession involved herp. At the robbery trial, one officer testified that during the interrogation he did not tell Miranda that anything he said would be held against him or that he could consult with an attorney. The other officer stated that they had both told Miranda that anything he said would be used against him and that he was not required by law to tell them anything. 4 OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. officersemerged from the interrogation room with a writ- ten confession signed by Miranda. At the top of the statement was a typed paragraph stating that th6 con- fession was made voluntarily, without threats or promises of immunity and "with full knowledge Of my legal rights, understanding any statement I make may be used against me." 11 At his trial before a jury, the written confession was adniitted into evidence over the objection of defense counsel, and the officers testified to the prior oral con- fession made by Miranda during the interrogation. Miranda was found guilty of kidnapping and rape. He was sentenced to 20 to 30 years' imprisonment on each count, the sentences to run concurrently. On appeal, the Supreme Court of Arizona held that Miranda's con- stitutional rights were not violated in obtaining the confession and affirmed-the conviction. 98 Ariz. 18, 401 P. 2d 721. In reaching its decision, the court empha- sized heavily the fact. that Miranda did not specifically request counsel. We reverse. From the -testimony of the officers and by the admission of respondent, it is clear that Miranda was not in any way apprised of his right to consult with an attorney and to have one present during the interro- gation, nor was his right not to be compelled to incrimi- nate himself effectively protected in any other, manner. Without these warnings the-statementi were- inadmis- sible. The mere fact that he signed- a statemenf which contained a typed-in clause stating that he had "full knowledge" of his "legal rights" does not approach the knowing and intelligent waiver required to' relinquish con stitutional rights. Cf. H-aynes-v. Washington, 373 U. S. 67 One of the officers testified that he read this paragraph to ,Miranda. ' Apparently, however, he did'not do so until after Miranda- had confessed orally. 492 " MIRANDA v. ARIZONA. 436 Opinion of the Court. .503, 512-513 (1963); Haley v. Ohio, 332 U. S. 596, 601 (1948) (opinion of MR. JUSTICE DOUGLAS). No. 760. Vignera v. New York. Petitioner, Michael Vignea, was picked up by New York police on October 14, 1960, in connection with the robbery three days earlier of a Brooklyn dress shop. They took him to the 17th Detective Squad headquarters in Manhattan. Sometime thereafter he, was taken to the 66th Detective Squad.
```

### CS-015 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** This is a syllabus passage authored by Warren.

**Rationale:** The source text identifies Syllabus, but its author metadata is null/unknown and the passage does not establish Warren as the syllabus author.

**Source:** [S2], Miranda v. Arizona, PDF pages [1, 2]; raw opinion unknown, raw author Unknown. Chunk `miranda_v_arizona:structure_aware_v1:00000`; original index 0; vector row 232.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
OCTOBER TERM, 1965. Syllabus. 384 U. S. MIRANDA v. ARIZONA. CERTIORARI TO THE SUPREME COURT OF ARIZONA. No. 759. Argued February 28-March 1, 1966.- Decided June 13, 1966.*" In each of these cases the defendant while in police custody was questioned by police officers, detectives, or'a prosecuting attorney in a room in which he was cut off from* the outside world. None of the defendants was given a'full and effective warning ot his rights at the outset of the interrogation process. In all four cases the. questioning elicited oral admissions, and in three of them signed statements as 'well, which were admitted at their trials. All defendants were convicted and all convictions, except in No. 584, were affirmed on appeal. Held: 1. The prosecution may not use statements, whether exculpatory or inculpatory, stemming from questioning initiated by law en-forcement officers after' a person has been taken into custody orotherwise deprived of his freedom of action in any ignificant way, unless it demonstrates the use of procedural safeguards effective tosecure the Fifth Amendment's jrivilege against, self-incrimination. Pp. 444-491. (a) The atmosphere and environment of incommunicadointerrogation as it exists today -is inherently intimidating and works to undermine the privilege against self-incrimination. Un- less adequate preventive measures are taken to dispel the compul- sion inherent in custodial surroundings,, no statement obtained from the defendant can truly' be the product of his free choice. Pp.445-458. (b) The privilege against self-incrimination, which has had a long and expansive historical development, is the essential main-stay of our adversary system and guarantees to the individual the 'right fo remain silent unless he chooses to speak in the unfet- tered exercise of his own will,"' during a period of custodial inter- *Together with No. 760, Vignera v. New York, on' certiorari to the Court of Appeals of New York and No. 761, Westover v. United States, on certiorari to the United States Court of Appeals for theNinth Circuit, both argued February 28-March 1, 1966; and No. 584, California v. Stewart, on certiorari to the Supreme Court of California, argued February 28-March , 1966. 436 • MIRANDA v. ARIZONA. 436 Syllabus. rogation 'as well as in the courts .or during the course of other official investigations. Pp. 458-465. (c) The decision in Escobedo v.' Illinois, 378 U. S. 478, stressed the need for protective devices to make the process of police interrogation conform to the dictates of the privilege. Pp. 465-466. (d) In the absence of other effective measures the following procedures to safeguard the Fifth Amendment privilege must be observed: The person in custody must, prior to interrogation, be clearly informed that he has the right to remain silent, and that anything he says will be used against him in court; he must be clearly informed that he has the right to consult with a lawyer and to have the lawyer with him during interrogation, and that, if he is indigent, a lawyer will be appointed to represent him. Pp. 467-473. (e) If the individual indicates, prior to or during questioning, that he wishes to remain silent, the interrogation must cease; if he states that he wants an attorney, the questioning must cease until an attorney is present. Pp. 473-474. (f) Where an interrogation is conducted without the presence of an ahtorney and a statement is taken, a heavy burden'rests on the Government to demonstrate that the defendant knowingly and intelligently waived his right to counsel. P. 475. (g) Where the hidividual answers some questions during in- custody interrogation he has not waived his privilege and may invoke his right to remain silent thereafter.
```

### CS-016 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** Loving invalidated racial marriage restrictions under both clauses, and imposed damages on each state official.

**Rationale:** The first proposition is explicitly described; the passage supplies no damages disposition.

**Source:** [S2], Obergefell v. Hodges, PDF pages [29, 31]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00020`; original index 20; vector row 351.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the right to marry refect this dynamic. In Loving, the Court invalidated a prohibi- tion on interracial marriage under both the Equal Protection Clause and the Due Process Clause. The Court frst de- clared the prohibition invalid because of its unequal treat- 673 Cite as: 576 U. S. 644 (2015) Opinion of the Court ment of interracial couples. It stated: “There can be no doubt that restricting the freedom to marry solely because of racial classifcations violates the central meaning of the Equal Protection Clause.” 388 U. S., at 12. With this link to equal protection the Court proceeded to hold the prohibi- tion offended central precepts of liberty: “To deny this fun- damental freedom on so unsupportable a basis as the racial classifcations embodied in these statutes, classifcations so directly subversive of the principle of equality at the heart of the Fourteenth Amendment, is surely to deprive all the State's citizens of liberty without due process of law.” Ibid. The reasons why marriage is a fundamental right became more clear and compelling from a full awareness and under- standing of the hurt that resulted from laws barring interra- cial unions. The synergy between the two protections is illustrated further in Zablocki. There the Court invoked the Equal Protection Clause as its basis for invalidating the challenged law, which, as already noted, barred fathers who were behind on child-support payments from marrying without judicial approval. The equal protection analysis depended in cen- tral part on the Court's holding that the law burdened a right “of fundamental importance.” 434 U. S., at 383. It was the essential nature of the marriage right, discussed at length in Zablocki, see id., at 383–387, that made apparent the law's incompatibility with requirements of equality. Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other. Indeed, in interpreting the Equal Protection Clause, the Court has recognized that new insights and societal under- standings can reveal unjustifed inequality within our most fundamental institutions that once passed unnoticed and un- challenged. To take but one period, this occurred with re- spect to marriage in the 1970's and 1980's. Notwithstanding the gradual erosion of the doctrine of coverture, see supra, at 660, invidious sex-based classifcations in marriage remained 674 OBERGEFELL v. HODGES Opinion of the Court common through the mid-20th century. See App. to Brief for Appellant in Reed v. Reed, O. T. 1971, No. 70–4, pp. 69– 88 (an extensive reference to laws extant as of 1971 treating women as unequal to men in marriage). These classifca- tions denied the equal dignity of men and women. One State's law, for example, provided in 1971 that “the husband is the head of the family and the wife is subject to him; her legal civil existence is merged in the husband, except so far as the law recognizes her separately, either for her own pro- tection, or for her beneft.” Ga. Code Ann. § 53–501 (1935).
```

### CS-017 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** How did Harlan describe Betts v. Brady in his Gideon concurrence?

**Claim:** Harlan agreed with overruling Betts and adopted every part of the majority’s historical account.

**Rationale:** Overruling agreement is explicit, but Harlan criticizes the majority’s description of precedent. Human review should consider CONTRADICTED for the second component.

**Source:** [S1], Gideon v. Wainwright, PDF pages [15, 17]; raw opinion concurrence, raw author Harlan. Chunk `gideon_v_wainwright:structure_aware_v1:00011`; original index 11; vector row 197.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE HARLAN, concurring. I agree that Betts v. Brady should be overruled, but consider it entitled to a more respectful burial than has been accorded, at least on the part of those of us who were not on the Court when that case was decided. I cannot subscribe to the view that Betts v. Brady represented "an abrupt break with its own well-consid- ered precedents." Ante, p. 344. In 1932, in Powell v. Alabama, 287 U. S. 45, a capital case, this Court declared that under the particular facts there presented-"the ignorance and illiteracy of the defendants, their youth, the circumstances of public hostility ... and above all that they stood in deadly peril of their lives" (287 U. S., at 71)-the state court had a duty to assign counsel for 3 See, e. g., Barzun, In Favor of Capital Punishment; 31 American Scholar 181, 188-189 (1962). 350 OCTOBER TERM, 1962. HARLAN, J., concurring. 372 U. S. the trial as a necessary requisite of due process of law. It is evident that these limiting facts were not added to the opinion as an afterthought; they were repeatedly empha- sized, see 287 U. S., at 52, 57-58, 71, and were clearly regarded as important to the result. Thus when this Court, a decade later, decided Betts v. Brady, it did no more than to admit of the possible- exist- ence of special circumstances in noncapital as well as capital trials, while at the same time insisting that such circumstances be shown in order to establish a denial of due process. The right to appointed counsel had been recognized as being considerably broader in federal prose- cutions, see Johnson v. Zerbst, 304 U. S. 458, but to have imposed these requirements on the States would indeed have been "an abrupt break" with the almost immediate past. The declaration that the right to appointed counsel in state prosecutions, as established in Powell v. Ala- bama, was not limited to capital cases was in truth not a departure from, but an extension of, existing precedent. The principles declared in Powell and in Betts, however, have had a troubled journey throughout the years that have followed first the one case and then the other. Even by the time of the Betts decision, dictum in at least one of the Court's opinions had indicated that there was an abso- lute right to the services of counsel in the trial of state capital cases.1 Such dicta continued to appear in subse- quent decisions,' and any lingering doubts were finally eliminated by the holding of Hamilton v. Alabama, 368 U. S. 52. In noncapital cases, the "special circumstances" rule has continued to exist in form while its substance has been substantially and steadily eroded. In the first decade after Betts, there were cases in which the Court 'Avery v. Alabama, 308 U. S. 444, 445. 2 E. g., Bute v. Illinois, 333 U. S. 640, 674; Uveges v. Pennsylvania, 335 U. S. 437, 441. GIDEON v. WAINWRIGHT. 335 HARLAN, J., concurring. found special circumstances to be lacking, but usually by a sharply divided vote.3 However, no such decision has been cited to us, and I have found none, after Quicksall v. Michigan, 339 U. S. 660, decided in 1950. At the same tij.,p, there have been not a few cases in which special cir- cumstances were found in little or nothing more than the "complexity". of the legal questions presented, although those questions were often of only routine difficulty.4 The Court has come to recognize, in other words, that the mere existence of a serious criminal charge constituted in itself special circumstances requiring the servicesL of counsel at trial. In truth the Betts v. Brady rule is no longer a reality.
```

### CS-018 — PARTIALLY_SUPPORTED (PROPOSED)

**Question:** What position did White take on prior restraints in New York Times Co. v. United States?

**Claim:** White agreed with denying the injunction and said publication could cause no public-interest damage.

**Rationale:** Agreement with the judgment is explicit; the no-damage clause conflicts with his expressed confidence in substantial damage. Review compound-label convention versus CONTRADICTED.

**Source:** [S1], New York Times Co. v. United States, PDF pages [18, 20]; raw opinion concurrence, raw author White. Chunk `new_york_times_co_v_united_states:structure_aware_v1:00013`; original index 13; vector row 312.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. I concur in today's judgments, but only because of the concededly extraordinary protection against prior re- NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an injunction against publication in these cases, at least in the absence of express and appropriately limited con- gressional authorization for prior restraints in circum- stances such as these. 1 The Congress has authorized a strain of prior restraints against private parties in certain instances. The National Labor Relations Board routinely issues cease-and-desist orders against employers who it finds have threatened or coerced employees in the exercise of protected rights. See 29 U. S. C. § 160 (c). Similarly, the Federal Trade Commission is empowered to impose cease-and-desist orders against unfair methods of competition. 15 U. S. C. § 45 (b). Such orders can, and quite often do, restrict what may be spoken or written under certain circumstances. See, e. g., NLRB v. Gissel Packing Co., 395 U. S. 575, 616-620 (1969). Article I, § 8, of the Constitution authorizes Congress to secure the "exclusive right" of authors to their writings, and no one denies that a newspaper can properly be enjoined from publishing the copyrighted works of another. See Westermann Co. v. Dispatch Co., 249 U. S. 100 (1919). Newspapers do themselves rely from time to time on the copyright as a means of protecting their accounts of important events. However, those enjoined under the statutes relating to the National Labor Relations Board and the Federal Trade Com- mission are private parties, not the press; and when the press is enjoined under the copyright laws the complainant is a private copyright holder enforcing a private right. These situations are quite distinct from the Government's request for an injunction against publishing information about the affairs of government, a request admittedly not based on any statute. OCTOBER TERM, 1970 WHrTE, J., concurring 403 U. S. The Government's position is simply stated: The re- sponsibility of the Executive for the conduct of the foreign affairs and for the security of the Nation is so basic that the President is entitled to an injunction against publi- cation of a newspaper story whenever he can convince a court that the information to be revealed threatens "grave and irreparable" injury to the public interest; 2 and the injunction should issue whether or not the material to be published is classified, whether or not publication would be lawful under relevant criminal statutes enacted by Congress, and regardless of the circumstances by which the newspaper came into possession of the information. At least in the absence of legislation by Congress, based on its own investigations and findings, I am quite unable to agree that the inherent powers of the Executive and the courts reach so far as to authorize remedies having such sweeping potential for inhibiting publications by the press. Much of the difficulty inheres in the "grave and irreparable danger" standard suggested by the United States. If the United States were to have judgment under such a standard in these cases, our decision would be of little guidance to other courts in other cases, for the material at issue here would not be available from the Court's opinion or from public records, nor would it be published by the press. Indeed, even today where we hold that the United States has not met its burden, the material remains sealed in court records and it is 2 The "grave and irreparable danger" standard is that asserted by the Government in this Court.
```

### CS-019 — UNSUPPORTED (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Claim:** Dobbs held that the Constitution protects a right to abortion.

**Rationale:** The cited passage lists lower-court marriage decisions and supplies no Dobbs holding. Do not use outside knowledge to turn absence into contradiction.

**Source:** [S1], Obergefell v. Hodges, PDF pages [39, 40]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00025`; original index 25; vector row 356.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
3d 859 (CA8 2006) Windsor v. United States, 699 F. 3d 169 (CA2 2012) Massachusetts v. Department of Health and Human Serv- ices, 682 F. 3d 1 (CA1 2012) Perry v. Brown, 671 F. 3d 1052 (CA9 2012) Latta v. Otter, 771 F. 3d 456 (CA9 2014) Baskin v. Bogan, 766 F. 3d 648 (CA7 2014) Bishop v. Smith, 760 F. 3d 1070 (CA10 2014) Bostic v. Schaefer, 760 F. 3d 352 (CA4 2014) Kitchen v. Herbert, 755 F. 3d 1193 (CA10 2014) DeBoer v. Snyder, 772 F. 3d 388 (CA6 2014) Latta v. Otter, 779 F. 3d 902 (CA9 2015) (O'Scannlain, J., dissenting from the denial of rehearing en banc) United States District Court Decisions Adams v. Howerton, 486 F. Supp. 1119 (CD Cal. 1980) Citizens for Equal Protection, Inc. v. Bruning, 290 F. Supp. 2d 1004 (Neb. 2003) Citizens for Equal Protection, Inc. v. Bruning, 368 F. Supp. 2d 980 (Neb. 2005) Wilson v. Ake, 354 F. Supp. 2d 1298 (MD Fla. 2005) Smelt v. County of Orange , 374 F. Supp. 2d 861 (CD Cal. 2005) Bishop v. Oklahoma ex rel. Edmondson, 447 F. Supp. 2d 1239 (ND Okla. 2006) Massachusetts v. Department of Health and Human Serv- ices, 698 F. Supp. 2d 234 (Mass. 2010) Gill v. Offce of Personnel Management, 699 F. Supp. 2d 374 (Mass. 2010) Perry v. Schwarzenegger, 704 F. Supp. 2d 921 (ND Cal. 2010) Dragovich v. Department of Treasury , 764 F. Supp. 2d 1178 (ND Cal. 2011) Golinski v. Offce of Personnel Management, 824 F. Supp. 2d 968 (ND Cal. 2012) 683 Cite as: 576 U. S. 644 (2015) Appendix A to opinion of the Court Dragovich v. Department of Treasury , 872 F. Supp. 2d 944 (ND Cal. 2012) Windsor v. United States, 833 F. Supp. 2d 394 (SDNY 2012) Pedersen v. Offce of Personnel Management, 881 F. Supp. 2d 294 (Conn. 2012) Jackson v. Abercrombie , 884 F. Supp. 2d 1065 (Haw. 2012) Sevcik v. Sandoval, 911 F. Supp. 2d 996 (Nev. 2012) Merritt v. Attorney General, 2013 WL 6044329 (MD La., Nov. 14, 2013) Gray v. Orr, 4 F. Supp. 3d 984 (ND Ill. 2013) Lee v. Orr, 2013 WL 6490577 (ND Ill., Dec. 10, 2013) Kitchen v. Herbert, 961 F. Supp. 2d 1181 (Utah 2013) Obergefell v. Wymyslo, 962 F.
```

### CS-020 — UNSUPPORTED (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Claim:** Dobbs overruled Roe v. Wade.

**Rationale:** This passage concerns Obergefell’s questions presented and amicus listings, not Dobbs. A proposition’s possible external truth does not make this citation support it.

**Source:** [S2], Obergefell v. Hodges, PDF pages [12, 13]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00010`; original index 10; vector row 341.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Anderson by Michael F. Smith; for Heather Barwick et al. by David Boyle; for Robert J. Bentley, Governor of Alabama, by Algert S. Agricola, Jr., and David B. Byrne, Jr.; for David Boyle, by Mr. Boyle, pro se; for Theodore Coates by Mr. Coates, pro se; for Jason Feliciano et al. by Sandra F. Gilbert; for Lary S. Larson by Sean J. Coletti; for Richard A. Lawrence by Mr. Lawrence, pro se; for Algirdas M. Liepas, by Mr. Liepas, pro se; for Robert Oscar Lopez et al. by Mr. Boyle; for Earl M. Maltz et al. by Herbert G. Grey; for C. L. “Butch” Otter, Governor of Idaho, by Gene C. Schaerr and Thomas C. Perry; for Judith Reisman et al. by Mathew D. Stave, Anita L. Stave, Horatio G. Mihet, and Mary E. McAlister; for David A. Robinson by Mr. Robinson, pro se; for Jon Simmons by Kevin E. Green; for Dawn Stefanowicz et al. by Mr. Boyle; for 47 Scholars by Robert P . George; for 54 International and Comparative Law Experts from 27 Countries et al. by Lynn D. Wardle, W. Cole Durham, Jr., and Robert T. Smith; for 57 Members of U. S. Con- gress by D. John Sauer; and for 100 Scholars of Marriage by Gene C. Schaerr. Briefs of amici curiae urging affrmance in No. 14–571 were fled for American Family Association-Michigan by Stephen M. Crampton, Thomas L. Brejcha, and Mr. Gillen; and for the Michigan Catholic Conference by James Walsh and Thomas J. Rheaume, Jr. Ronald D. Ray and Richard L. Masters fled a brief for 106 Members of the Kentucky General Assembly as amici curiae urging affrmance in No. 14–574. Briefs of amici curiae were fled in all cases for Citizens United for the Individual Freedom to Defne Marriage by D'Arcy Winston Straub; for the Eagle Forum Education & Legal Defense Fund by Lawrence J. Joseph; for the General Conference of Seventh-day Adventists et al. by Eric C. Rassbach, Hannah C. Smith, Asma T. Uddin, Todd McFarland, and An- drew G. Schultz; for the Leadership Conference on Civil and Human Rights et al. by Matthew M. Hoffman, Abigail Hemani, Wade J. Hender- 656 OBERGEFELL v. HODGES Opinion of the Court The petitioners fled these suits in United States District Courts in their home States. Each District Court ruled in their favor. Citations to those cases are in Appendix A, infra . The respondents appealed the decisions against them to the United States Court of Appeals for the Sixth Circuit. It consolidated the cases and reversed the judg- ments of the District Courts. DeBoer v. Snyder, 772 F. 3d 388 (2014). The Court of Appeals held that a State has no constitutional obligation to license same-sex marriages or to recognize same-sex marriages performed out of State. The petitioners sought certiorari. This Court granted re- view, limited to two questions. 574 U. S. 1118 (2015). The frst, presented by the cases from Michigan and Kentucky, is whether the Fourteenth Amendment requires a State to li- cense a marriage between two people of the same sex. The second, presented by the cases from Ohio, Tennessee, and, again, Kentucky, is whether the Fourteenth Amendment re- quires a State to recognize a same-sex marriage licensed and performed in a State which does grant that right.
```

### CS-021 — UNSUPPORTED (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Claim:** The Court in Dobbs applied strict scrutiny to every abortion restriction.

**Rationale:** The passage recounts marriage/social history and other cases; no Dobbs standard appears.

**Source:** [S3], Obergefell v. Hodges, PDF pages [17, 19]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00013`; original index 13; vector row 344.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
As women gained legal, political, and property rights, and as society began to under- stand that women have their own equal dignity, the law of coverture was abandoned. See Brief for Historians of Marriage et al. as Amici Curiae 16–19. These and other developments in the institution of marriage over the past centuries were not mere superfcial changes. Rather, they worked deep transformations in its structure, affecting as- pects of marriage long viewed by many as essential. See generally Cott, supra; Coontz, supra; H. Hartog, Man and Wife in America: A History (2000). These new insights have strengthened, not weakened, the institution of marriage. Indeed, changed understandings of marriage are characteristic of a Nation where new dimen- sions of freedom become apparent to new generations, often through perspectives that begin in pleas or protests and then are considered in the political sphere and the judicial process. This dynamic can be seen in the Nation's experiences with the rights of gays and lesbians. Until the mid-20th century, same-sex intimacy long had been condemned as immoral by the state itself in most Western nations, a belief often em- bodied in the criminal law. For this reason, among others, many persons did not deem homosexuals to have dignity in their own distinct identity. A truthful declaration by same- sex couples of what was in their hearts had to remain unspo- ken. Even when a greater awareness of the humanity and integrity of homosexual persons came in the period after World War II, the argument that gays and lesbians had a just claim to dignity was in confict with both law and wide- 661 Cite as: 576 U. S. 644 (2015) Opinion of the Court spread social conventions. Same-sex intimacy remained a crime in many States. Gays and lesbians were prohibited from most government employment, barred from military service, excluded under immigration laws, targeted by po- lice, and burdened in their rights to associate. See Brief for Organization of American Historians as Amicus Curiae 5–28. For much of the 20th century, moreover, homosexuality was treated as an illness. When the American Psychiatric Association published the frst Diagnostic and Statistical Manual of Mental Disorders in 1952, homosexuality was clas- sifed as a mental disorder, a position adhered to until 1973. See Position Statement on Homosexuality and Civil Rights, 1973, in 131 Am. J. Psychiatry 497 (1974). Only in more re- cent years have psychiatrists and others recognized that sexual orientation is both a normal expression of human sex- uality and immutable. See Brief for American Psychologi- cal Association et al. as Amici Curiae 7–17. In the late-20th century, following substantial cultural and political developments, same-sex couples began to lead more open and public lives and to establish families. This devel- opment was followed by a quite extensive discussion of the issue in both governmental and private sectors and by a shift in public attitudes toward greater tolerance. As a result, questions about the rights of gays and lesbians soon reached the courts, where the issue could be discussed in the formal discourse of the law. This Court frst gave detailed consideration to the legal status of homosexuals in Bowers v. Hardwick, 478 U. S. 186 (1986). There it upheld the constitutionality of a Georgia law deemed to criminalize certain homosexual acts. Ten years later, in Romer v. Evans, 517 U. S. 620 (1996), the Court invalidated an amendment to Colorado's Constitution that sought to foreclose any branch or political subdivision of the State from protecting persons against discrimination based on sexual orientation. Then, in 2003, the Court over- 662 OBERGEFELL v. HODGES Opinion of the Court ruled Bowers, holding that laws making same-sex intimacy a crime “demea[n] the lives of homosexual persons.” Law- rence v. Texas, 539 U. S. 558, 575. Against this background, the legal question of same-sex marriage arose. In 1993, the Hawaii Supreme Court held Hawaii's law restricting marriage to opposite-sex couples constituted a classifcation on the basis of sex and was there- fore subject to strict scrutiny under the Hawaii Constitution.
```

### CS-022 — UNSUPPORTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** Miranda requires all custodial interrogations to be videotaped.

**Rationale:** The passage about Miranda’s interrogation and reversal does not establish a videotaping rule.

**Source:** [S3], Miranda v. Arizona, PDF pages [56, 58]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00034`; original index 34; vector row 266.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
V. Because of the nature of the problem and because of its recurrent significance in numerous cases, we have to this point discussed the relationship of the Fifth Amend- ment privilege to police interrogation without specific concentration on the facts of the cases before us. We turn now to these facts to consider the application to these cases of the constitutional principles discussed above. In each instance, we have concluded that state- ments were obtained from the defendant under circum- stances that did not meet constitutional standards for protection of the privilege. No. 759. Miranda v. Arizona. On March 13, 1963, petitioner, Ernesto Miranda, was arrested at his home and taken in custody to a Phoenix police station. He was there identified by the complain- ing witness. The police then took him to "Interrogation Room No. 2" of the detective bureau. There he was questioned by two police officers. The officers admitted at trial that Miranda was not advised that he had a right to have an attorney present."0 Two hours later, the 6 Miranda was also convicted in a separate trial on an unrelated robbery charge not presented here for review. A statement intro- duced at that trial was obtained from Miranda during the same interrogation which resulted in the confession involved herp. At the robbery trial, one officer testified that during the interrogation he did not tell Miranda that anything he said would be held against him or that he could consult with an attorney. The other officer stated that they had both told Miranda that anything he said would be used against him and that he was not required by law to tell them anything. 4 OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. officersemerged from the interrogation room with a writ- ten confession signed by Miranda. At the top of the statement was a typed paragraph stating that th6 con- fession was made voluntarily, without threats or promises of immunity and "with full knowledge Of my legal rights, understanding any statement I make may be used against me." 11 At his trial before a jury, the written confession was adniitted into evidence over the objection of defense counsel, and the officers testified to the prior oral con- fession made by Miranda during the interrogation. Miranda was found guilty of kidnapping and rape. He was sentenced to 20 to 30 years' imprisonment on each count, the sentences to run concurrently. On appeal, the Supreme Court of Arizona held that Miranda's con- stitutional rights were not violated in obtaining the confession and affirmed-the conviction. 98 Ariz. 18, 401 P. 2d 721. In reaching its decision, the court empha- sized heavily the fact. that Miranda did not specifically request counsel. We reverse. From the -testimony of the officers and by the admission of respondent, it is clear that Miranda was not in any way apprised of his right to consult with an attorney and to have one present during the interro- gation, nor was his right not to be compelled to incrimi- nate himself effectively protected in any other, manner. Without these warnings the-statementi were- inadmis- sible. The mere fact that he signed- a statemenf which contained a typed-in clause stating that he had "full knowledge" of his "legal rights" does not approach the knowing and intelligent waiver required to' relinquish con stitutional rights. Cf. H-aynes-v. Washington, 373 U. S. 67 One of the officers testified that he read this paragraph to ,Miranda. ' Apparently, however, he did'not do so until after Miranda- had confessed orally. 492 " MIRANDA v. ARIZONA. 436 Opinion of the Court. .503, 512-513 (1963); Haley v. Ohio, 332 U. S. 596, 601 (1948) (opinion of MR. JUSTICE DOUGLAS). No. 760. Vignera v. New York. Petitioner, Michael Vignea, was picked up by New York police on October 14, 1960, in connection with the robbery three days earlier of a Brooklyn dress shop. They took him to the 17th Detective Squad headquarters in Manhattan. Sometime thereafter he, was taken to the 66th Detective Squad.
```

### CS-023 — CONTRADICTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** Roberts endorsed the majority’s due-process/equal-protection synergy.

**Rationale:** The dissent calls the discussion difficult to follow and criticizes the purported independent equal-protection basis; endorsement reverses his position.

**Source:** [S1], Obergefell v. Hodges, PDF pages [63, 65]; raw opinion dissent, raw author Roberts. Chunk `obergefell_v_hodges:structure_aware_v1:00041`; original index 41; vector row 372.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
III In addition to their due process argument, petitioners con- tend that the Equal Protection Clause requires their States to license and recognize same-sex marriages. The majority does not seriously engage with this claim. Its discussion is, quite frankly, diffcult to follow. The central point seems to be that there is a “synergy between” the Equal Protection Clause and the Due Process Clause, and that some prece- dents relying on one Clause have also relied on the other. Ante, at 673. Absent from this portion of the opinion, how- 707 Cite as: 576 U. S. 644 (2015) Roberts, C. J., dissenting ever, is anything resembling our usual framework for decid- ing equal protection cases. It is casebook doctrine that the “modern Supreme Court's treatment of equal protection claims has used a means-ends methodology in which judges ask whether the classifcation the government is using is suffciently related to the goals it is pursuing.” G. Stone, L. Seidman, C. Sunstein, M. Tushnet, & P. Karlan, Consti- tutional Law 453 (7th ed. 2013). The majority's approach today is different: “Rights implicit in liberty and rights secured by equal protection may rest on different precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to cap- ture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may con- verge in the identifcation and defnition of the right.” Ante, at 672. The majority goes on to assert in conclusory fashion that the Equal Protection Clause provides an alternative basis for its holding. Ante, at 675. Yet the majority fails to pro- vide even a single sentence explaining how the Equal Protec- tion Clause supplies independent weight for its position, nor does it attempt to justify its gratuitous violation of the canon against unnecessarily resolving constitutional questions. See Northwest Austin Municipal Util. Dist. No. One v. Holder, 557 U. S. 193, 197 (2009). In any event, the mar- riage laws at issue here do not violate the Equal Protection Clause, because distinguishing between opposite-sex and same-sex couples is rationally related to the States' “legiti- mate state interest” in “preserving the traditional institution of marriage.” Lawrence, 539 U. S., at 585 (O'Connor, J., con- curring in judgment). It is important to note with precision which laws petition- ers have challenged. Although they discuss some of the an- 708 OBERGEFELL v. HODGES Roberts, C. J., dissenting cillary legal benefts that accompany marriage, such as hospi- tal visitation rights and recognition of spousal status on offcial documents, petitioners' lawsuits target the laws de- fning marriage generally rather than those allocating bene- fts specifcally. The equal protection analysis might be dif- ferent, in my view, if we were confronted with a more focused challenge to the denial of certain tangible benefts. Of course, those more selective claims will not arise now that the Court has taken the drastic step of requiring every State to license and recognize marriages between same-sex couples.
```

### CS-024 — UNSUPPORTED (PROPOSED)

**Question:** How did Harlan describe Betts v. Brady in his Gideon concurrence?

**Claim:** The Gideon majority said that Betts deserved a more respectful burial.

**Rationale:** The words appear as Harlan’s separate concurring criticism, not an attributed majority rationale. A concurrence cannot establish this asserted majority attribution.

**Source:** [S1], Gideon v. Wainwright, PDF pages [15, 17]; raw opinion concurrence, raw author Harlan. Chunk `gideon_v_wainwright:structure_aware_v1:00011`; original index 11; vector row 197.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE HARLAN, concurring. I agree that Betts v. Brady should be overruled, but consider it entitled to a more respectful burial than has been accorded, at least on the part of those of us who were not on the Court when that case was decided. I cannot subscribe to the view that Betts v. Brady represented "an abrupt break with its own well-consid- ered precedents." Ante, p. 344. In 1932, in Powell v. Alabama, 287 U. S. 45, a capital case, this Court declared that under the particular facts there presented-"the ignorance and illiteracy of the defendants, their youth, the circumstances of public hostility ... and above all that they stood in deadly peril of their lives" (287 U. S., at 71)-the state court had a duty to assign counsel for 3 See, e. g., Barzun, In Favor of Capital Punishment; 31 American Scholar 181, 188-189 (1962). 350 OCTOBER TERM, 1962. HARLAN, J., concurring. 372 U. S. the trial as a necessary requisite of due process of law. It is evident that these limiting facts were not added to the opinion as an afterthought; they were repeatedly empha- sized, see 287 U. S., at 52, 57-58, 71, and were clearly regarded as important to the result. Thus when this Court, a decade later, decided Betts v. Brady, it did no more than to admit of the possible- exist- ence of special circumstances in noncapital as well as capital trials, while at the same time insisting that such circumstances be shown in order to establish a denial of due process. The right to appointed counsel had been recognized as being considerably broader in federal prose- cutions, see Johnson v. Zerbst, 304 U. S. 458, but to have imposed these requirements on the States would indeed have been "an abrupt break" with the almost immediate past. The declaration that the right to appointed counsel in state prosecutions, as established in Powell v. Ala- bama, was not limited to capital cases was in truth not a departure from, but an extension of, existing precedent. The principles declared in Powell and in Betts, however, have had a troubled journey throughout the years that have followed first the one case and then the other. Even by the time of the Betts decision, dictum in at least one of the Court's opinions had indicated that there was an abso- lute right to the services of counsel in the trial of state capital cases.1 Such dicta continued to appear in subse- quent decisions,' and any lingering doubts were finally eliminated by the holding of Hamilton v. Alabama, 368 U. S. 52. In noncapital cases, the "special circumstances" rule has continued to exist in form while its substance has been substantially and steadily eroded. In the first decade after Betts, there were cases in which the Court 'Avery v. Alabama, 308 U. S. 444, 445. 2 E. g., Bute v. Illinois, 333 U. S. 640, 674; Uveges v. Pennsylvania, 335 U. S. 437, 441. GIDEON v. WAINWRIGHT. 335 HARLAN, J., concurring. found special circumstances to be lacking, but usually by a sharply divided vote.3 However, no such decision has been cited to us, and I have found none, after Quicksall v. Michigan, 339 U. S. 660, decided in 1950. At the same tij.,p, there have been not a few cases in which special cir- cumstances were found in little or nothing more than the "complexity". of the legal questions presented, although those questions were often of only routine difficulty.4 The Court has come to recognize, in other words, that the mere existence of a serious criminal charge constituted in itself special circumstances requiring the servicesL of counsel at trial. In truth the Betts v. Brady rule is no longer a reality.
```

### CS-025 — UNSUPPORTED (PROPOSED)

**Question:** What did Stewart say about children’s First Amendment rights in Tinker?

**Claim:** Every line of this passage is reliably verified to have been written by Stewart.

**Rationale:** The corpus labels concurrence/Stewart, but the extracted text contains a Black dissent header amid Stewart prose. Raw labels do not independently verify every line’s author.

**Source:** [S1], Tinker v. Des Moines School Dist., PDF pages [12, 13]; raw opinion concurrence, raw author Stewart. Chunk `tinker_v_des_moines_school_dist:structure_aware_v1:00009`; original index 9; vector row 424.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE STEWART, concurring. Although I agree with much of what is said in the Court's opinion, and with its judgment in this case, I 514 TINKER v. DES MOINES SCHOOL DIST. 515 503 BLACK, J., dissenting. cannot share the Court's uncritical assumption that, school discipline aside, the First Amendment rights of children are co-extensive with those of adults. Indeed, I had thought the Court decided otherwise just last Term in Ginsberg v. New York, 390 U. S. 629. I con- tinue to hold the view I expressed in that case: "[A] State may permissibly determine that, at least in some precisely delineated areas, a child-like someone in a captive audience-is not possessed of that full capacity for individual choice which is the presupposition of First Amendment guarantees." Id., at 649-650 (con- curring in result). Cf. Prince v. Massachusetts, 321 U. S. 158.
```

### CS-026 — CONTRADICTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** The two Fourteenth Amendment clauses always have identical reach.

**Rationale:** The majority says they set forth independent principles and are not always co-extensive; this paraphrase reverses that limitation.

**Source:** [S2], Obergefell v. Hodges, PDF pages [29, 31]; raw opinion majority, raw author Kennedy. Chunk `obergefell_v_hodges:structure_aware_v1:00020`; original index 20; vector row 351.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
The Due Process Clause and the Equal Protection Clause are connected in a profound way, though they set forth independent principles. Rights implicit in lib- erty and rights secured by equal protection may rest on dif- ferent precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to capture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may converge in the identifcation and defnition of the right. See M. L. B., 519 U. S., at 120–121; id., at 128–129 (Kennedy, J., concurring in judgment); Bearden v. Georgia, 461 U. S. 660, 665 (1983). This interrelation of the two principles furthers our understanding of what freedom is and must become. The Court's cases touching upon the right to marry refect this dynamic. In Loving, the Court invalidated a prohibi- tion on interracial marriage under both the Equal Protection Clause and the Due Process Clause. The Court frst de- clared the prohibition invalid because of its unequal treat- 673 Cite as: 576 U. S. 644 (2015) Opinion of the Court ment of interracial couples. It stated: “There can be no doubt that restricting the freedom to marry solely because of racial classifcations violates the central meaning of the Equal Protection Clause.” 388 U. S., at 12. With this link to equal protection the Court proceeded to hold the prohibi- tion offended central precepts of liberty: “To deny this fun- damental freedom on so unsupportable a basis as the racial classifcations embodied in these statutes, classifcations so directly subversive of the principle of equality at the heart of the Fourteenth Amendment, is surely to deprive all the State's citizens of liberty without due process of law.” Ibid. The reasons why marriage is a fundamental right became more clear and compelling from a full awareness and under- standing of the hurt that resulted from laws barring interra- cial unions. The synergy between the two protections is illustrated further in Zablocki. There the Court invoked the Equal Protection Clause as its basis for invalidating the challenged law, which, as already noted, barred fathers who were behind on child-support payments from marrying without judicial approval. The equal protection analysis depended in cen- tral part on the Court's holding that the law burdened a right “of fundamental importance.” 434 U. S., at 383. It was the essential nature of the marriage right, discussed at length in Zablocki, see id., at 383–387, that made apparent the law's incompatibility with requirements of equality. Each con- cept—liberty and equal protection—leads to a stronger un- derstanding of the other. Indeed, in interpreting the Equal Protection Clause, the Court has recognized that new insights and societal under- standings can reveal unjustifed inequality within our most fundamental institutions that once passed unnoticed and un- challenged. To take but one period, this occurred with re- spect to marriage in the 1970's and 1980's. Notwithstanding the gradual erosion of the doctrine of coverture, see supra, at 660, invidious sex-based classifcations in marriage remained 674 OBERGEFELL v. HODGES Opinion of the Court common through the mid-20th century. See App. to Brief for Appellant in Reed v. Reed, O. T. 1971, No. 70–4, pp. 69– 88 (an extensive reference to laws extant as of 1971 treating women as unequal to men in marriage). These classifca- tions denied the equal dignity of men and women. One State's law, for example, provided in 1971 that “the husband is the head of the family and the wife is subject to him; her legal civil existence is merged in the husband, except so far as the law recognizes her separately, either for her own pro- tection, or for her beneft.” Ga. Code Ann. § 53–501 (1935).
```

### CS-027 — CONTRADICTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** A defendant may waive Miranda rights involuntarily.

**Rationale:** The source expressly requires a voluntary, knowing and intelligent waiver.

**Source:** [S1], Miranda v. Arizona, PDF pages [9, 10]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00006`; original index 6; vector row 238.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Our holding will be spelled out with some specificity in the pages which follow but briefly stated it is this: the prosecution may not use statements, whether excul- patory .or inculpatory, stemming from custodial interro- gation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination. By custodial interrogation; we mean questioning initiatedby law enforcement officers after a person has been taken into custody or otherwise deprived of his freedom of action in any significant way.4 As for' the procedural safeguards to be employedi unless other fully effective means are devised to inform accused persons of their right of silence and to assure a contin- uous opportunity to exercise it, the following measures are required. Prior to any questioning, the person must be warned that he has a right to remain silent, that any statement he-does make may be used as evidence against him, and'that he has a right to the presence of an attor- ney, either retained or appointed. The defendant may -waive effectuation of these rights,,provided the waiver is made voluntarily, knowingly and intelligently. If, how- ever, he indicates in any manner and at any stage of the 4 This is what *e~meant in Escobedo when we spoke -of ap investi- gation which had focused on an accused. 444 MIRANDA v. ARIZONA. 436 Opinion of the Court. process thit he wishes to consult with an'attorney before speaking there'can be no. questioning. likewise, if the individual, is alone and indicates in any manner that he does not wish to be interrogated, the police may not question him. The mere fact that he may have answered some questions or volunteered some statements on his own does not deprive -him of the' right -to refrain from answering any further inquiries until he has consulted with an attorney and thereafter consents to be questioned.
```

### CS-028 — CONTRADICTED (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Claim:** States are forbidden to develop equally effective alternative safeguards.

**Rationale:** The source expressly says Congress and States are free to develop safeguards fully as effective as those described.

**Source:** [S4], Miranda v. Arizona, PDF pages [55, 56]; raw opinion majority, raw author Warren. Chunk `miranda_v_arizona:structure_aware_v1:00033`; original index 33; vector row 265.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
Opinion of the Court. 384 U. S. whereas other jurisdictions arrived, at their conclusions on the basis of principles of justice not so specifically defined.64 It is also urged upon us that we withhold decision on this issue until state legislative bodies and advisory groups have had an opportunity to deal with these prob- lems by rule making.6 5 We- have already pointed out that the Constitution does not require any specific code of procedures for protecting the privilege against self- incrimination during custodial interrogation. Congress and the States are free to develop their own safeguards for the privilege, so long as they are fully as effective as those described above'in informing accused persons of their right of silence and in affording a continuous oppor- tunity to exercise it. In any event, however, the issues presented are of constitutional dimensions and must be determined by the courts. The admissibility of a state- ment in the face of a claim that it was obtained in viola- tion of the defendant's constitutional rights is an issue the resolution of which has long since been undertaken by this Court. See Hopt v. Utah, 110 U. S. 574 (1884). Judicial solutions to problems of constitutional dimen- sion have evolved decade by decade. As courts have been presented with the need to enforce constitutional rights, they have found means of doing so. That was our responsibility 'when Escobedo was before us and it is our 6 4 Although' no constitution existed at the time confessions were excluded by rule of evidence in 1872, India now has a written con- stitution which includes the provision that "No person accused of any offence'shall be compelled to be a witness against himself." Constitution of India, Article 20 (3). See Tope: The Constitution' of India 63-67 (1960). clBrief for United States in No. 761, Westover v. United States, pp. 44-47; Brief for the State of New York as amicus curiae, pp. 35-39. See also Brief for the National District Attorneys Associa- -tion as amicus curiae, pp. 23-26. MIRANDA v. ARIZONA. 436 Opinion of the -Court. responsibility today. Where rights secured by the Con- stitution are involved, there can be no rule-making or legislation which would abrogate them.
```

### CS-029 — CONTRADICTED (PROPOSED)

**Question:** How did Harlan describe Betts v. Brady in his Gideon concurrence?

**Claim:** Harlan opposed overruling Betts v. Brady.

**Rationale:** The concurrence opens “I agree that Betts v. Brady should be overruled”.

**Source:** [S1], Gideon v. Wainwright, PDF pages [15, 17]; raw opinion concurrence, raw author Harlan. Chunk `gideon_v_wainwright:structure_aware_v1:00011`; original index 11; vector row 197.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE HARLAN, concurring. I agree that Betts v. Brady should be overruled, but consider it entitled to a more respectful burial than has been accorded, at least on the part of those of us who were not on the Court when that case was decided. I cannot subscribe to the view that Betts v. Brady represented "an abrupt break with its own well-consid- ered precedents." Ante, p. 344. In 1932, in Powell v. Alabama, 287 U. S. 45, a capital case, this Court declared that under the particular facts there presented-"the ignorance and illiteracy of the defendants, their youth, the circumstances of public hostility ... and above all that they stood in deadly peril of their lives" (287 U. S., at 71)-the state court had a duty to assign counsel for 3 See, e. g., Barzun, In Favor of Capital Punishment; 31 American Scholar 181, 188-189 (1962). 350 OCTOBER TERM, 1962. HARLAN, J., concurring. 372 U. S. the trial as a necessary requisite of due process of law. It is evident that these limiting facts were not added to the opinion as an afterthought; they were repeatedly empha- sized, see 287 U. S., at 52, 57-58, 71, and were clearly regarded as important to the result. Thus when this Court, a decade later, decided Betts v. Brady, it did no more than to admit of the possible- exist- ence of special circumstances in noncapital as well as capital trials, while at the same time insisting that such circumstances be shown in order to establish a denial of due process. The right to appointed counsel had been recognized as being considerably broader in federal prose- cutions, see Johnson v. Zerbst, 304 U. S. 458, but to have imposed these requirements on the States would indeed have been "an abrupt break" with the almost immediate past. The declaration that the right to appointed counsel in state prosecutions, as established in Powell v. Ala- bama, was not limited to capital cases was in truth not a departure from, but an extension of, existing precedent. The principles declared in Powell and in Betts, however, have had a troubled journey throughout the years that have followed first the one case and then the other. Even by the time of the Betts decision, dictum in at least one of the Court's opinions had indicated that there was an abso- lute right to the services of counsel in the trial of state capital cases.1 Such dicta continued to appear in subse- quent decisions,' and any lingering doubts were finally eliminated by the holding of Hamilton v. Alabama, 368 U. S. 52. In noncapital cases, the "special circumstances" rule has continued to exist in form while its substance has been substantially and steadily eroded. In the first decade after Betts, there were cases in which the Court 'Avery v. Alabama, 308 U. S. 444, 445. 2 E. g., Bute v. Illinois, 333 U. S. 640, 674; Uveges v. Pennsylvania, 335 U. S. 437, 441. GIDEON v. WAINWRIGHT. 335 HARLAN, J., concurring. found special circumstances to be lacking, but usually by a sharply divided vote.3 However, no such decision has been cited to us, and I have found none, after Quicksall v. Michigan, 339 U. S. 660, decided in 1950. At the same tij.,p, there have been not a few cases in which special cir- cumstances were found in little or nothing more than the "complexity". of the legal questions presented, although those questions were often of only routine difficulty.4 The Court has come to recognize, in other words, that the mere existence of a serious criminal charge constituted in itself special circumstances requiring the servicesL of counsel at trial. In truth the Betts v. Brady rule is no longer a reality.
```

### CS-030 — CONTRADICTED (PROPOSED)

**Question:** What position did White take on prior restraints in New York Times Co. v. United States?

**Claim:** White believed disclosing the documents would cause no substantial damage to public interests.

**Rationale:** White expressly says he is confident disclosure will cause substantial damage.

**Source:** [S1], New York Times Co. v. United States, PDF pages [18, 20]; raw opinion concurrence, raw author White. Chunk `new_york_times_co_v_united_states:structure_aware_v1:00013`; original index 13; vector row 312.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. I concur in today's judgments, but only because of the concededly extraordinary protection against prior re- NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an injunction against publication in these cases, at least in the absence of express and appropriately limited con- gressional authorization for prior restraints in circum- stances such as these. 1 The Congress has authorized a strain of prior restraints against private parties in certain instances. The National Labor Relations Board routinely issues cease-and-desist orders against employers who it finds have threatened or coerced employees in the exercise of protected rights. See 29 U. S. C. § 160 (c). Similarly, the Federal Trade Commission is empowered to impose cease-and-desist orders against unfair methods of competition. 15 U. S. C. § 45 (b). Such orders can, and quite often do, restrict what may be spoken or written under certain circumstances. See, e. g., NLRB v. Gissel Packing Co., 395 U. S. 575, 616-620 (1969). Article I, § 8, of the Constitution authorizes Congress to secure the "exclusive right" of authors to their writings, and no one denies that a newspaper can properly be enjoined from publishing the copyrighted works of another. See Westermann Co. v. Dispatch Co., 249 U. S. 100 (1919). Newspapers do themselves rely from time to time on the copyright as a means of protecting their accounts of important events. However, those enjoined under the statutes relating to the National Labor Relations Board and the Federal Trade Com- mission are private parties, not the press; and when the press is enjoined under the copyright laws the complainant is a private copyright holder enforcing a private right. These situations are quite distinct from the Government's request for an injunction against publishing information about the affairs of government, a request admittedly not based on any statute. OCTOBER TERM, 1970 WHrTE, J., concurring 403 U. S. The Government's position is simply stated: The re- sponsibility of the Executive for the conduct of the foreign affairs and for the security of the Nation is so basic that the President is entitled to an injunction against publi- cation of a newspaper story whenever he can convince a court that the information to be revealed threatens "grave and irreparable" injury to the public interest; 2 and the injunction should issue whether or not the material to be published is classified, whether or not publication would be lawful under relevant criminal statutes enacted by Congress, and regardless of the circumstances by which the newspaper came into possession of the information. At least in the absence of legislation by Congress, based on its own investigations and findings, I am quite unable to agree that the inherent powers of the Executive and the courts reach so far as to authorize remedies having such sweeping potential for inhibiting publications by the press. Much of the difficulty inheres in the "grave and irreparable danger" standard suggested by the United States. If the United States were to have judgment under such a standard in these cases, our decision would be of little guidance to other courts in other cases, for the material at issue here would not be available from the Court's opinion or from public records, nor would it be published by the press. Indeed, even today where we hold that the United States has not met its burden, the material remains sealed in court records and it is 2 The "grave and irreparable danger" standard is that asserted by the Government in this Court.
```

### CS-031 — UNSUPPORTED (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Claim:** Roberts’s own controlling-majority opinion established the synergy of the two clauses.

**Rationale:** The metadata/text identify Roberts dissenting. His reproduction of majority words does not make this his controlling-majority opinion.

**Source:** [S1], Obergefell v. Hodges, PDF pages [63, 65]; raw opinion dissent, raw author Roberts. Chunk `obergefell_v_hodges:structure_aware_v1:00041`; original index 41; vector row 372.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence smoke_generation_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
III In addition to their due process argument, petitioners con- tend that the Equal Protection Clause requires their States to license and recognize same-sex marriages. The majority does not seriously engage with this claim. Its discussion is, quite frankly, diffcult to follow. The central point seems to be that there is a “synergy between” the Equal Protection Clause and the Due Process Clause, and that some prece- dents relying on one Clause have also relied on the other. Ante, at 673. Absent from this portion of the opinion, how- 707 Cite as: 576 U. S. 644 (2015) Roberts, C. J., dissenting ever, is anything resembling our usual framework for decid- ing equal protection cases. It is casebook doctrine that the “modern Supreme Court's treatment of equal protection claims has used a means-ends methodology in which judges ask whether the classifcation the government is using is suffciently related to the goals it is pursuing.” G. Stone, L. Seidman, C. Sunstein, M. Tushnet, & P. Karlan, Consti- tutional Law 453 (7th ed. 2013). The majority's approach today is different: “Rights implicit in liberty and rights secured by equal protection may rest on different precepts and are not always co-extensive, yet in some instances each may be instructive as to the meaning and reach of the other. In any particular case one Clause may be thought to cap- ture the essence of the right in a more accurate and comprehensive way, even as the two Clauses may con- verge in the identifcation and defnition of the right.” Ante, at 672. The majority goes on to assert in conclusory fashion that the Equal Protection Clause provides an alternative basis for its holding. Ante, at 675. Yet the majority fails to pro- vide even a single sentence explaining how the Equal Protec- tion Clause supplies independent weight for its position, nor does it attempt to justify its gratuitous violation of the canon against unnecessarily resolving constitutional questions. See Northwest Austin Municipal Util. Dist. No. One v. Holder, 557 U. S. 193, 197 (2009). In any event, the mar- riage laws at issue here do not violate the Equal Protection Clause, because distinguishing between opposite-sex and same-sex couples is rationally related to the States' “legiti- mate state interest” in “preserving the traditional institution of marriage.” Lawrence, 539 U. S., at 585 (O'Connor, J., con- curring in judgment). It is important to note with precision which laws petition- ers have challenged. Although they discuss some of the an- 708 OBERGEFELL v. HODGES Roberts, C. J., dissenting cillary legal benefts that accompany marriage, such as hospi- tal visitation rights and recognition of spousal status on offcial documents, petitioners' lawsuits target the laws de- fning marriage generally rather than those allocating bene- fts specifcally. The equal protection analysis might be dif- ferent, in my view, if we were confronted with a more focused challenge to the denial of certain tangible benefts. Of course, those more selective claims will not arise now that the Court has taken the drastic step of requiring every State to license and recognize marriages between same-sex couples.
```

### CS-032 — UNSUPPORTED (PROPOSED)

**Question:** What did Stewart say about children’s First Amendment rights in Tinker?

**Claim:** The Tinker majority adopted Stewart’s separate objection to co-extensive child/adult speech rights.

**Rationale:** This concurrence expressly disputes the Court’s assumption, and a mixed extracted header adds attribution uncertainty. It does not establish majority adoption.

**Source:** [S1], Tinker v. Des Moines School Dist., PDF pages [12, 13]; raw opinion concurrence, raw author Stewart. Chunk `tinker_v_des_moines_school_dist:structure_aware_v1:00009`; original index 9; vector row 424.

**Origin:** synthetic; claim constructed_claim; pairing constructed_evidence_pairing; evidence constructed_local_context.

**Exact cited passage (complete chunk; OCR unchanged):**

```text
MR. JUSTICE STEWART, concurring. Although I agree with much of what is said in the Court's opinion, and with its judgment in this case, I 514 TINKER v. DES MOINES SCHOOL DIST. 515 503 BLACK, J., dissenting. cannot share the Court's uncritical assumption that, school discipline aside, the First Amendment rights of children are co-extensive with those of adults. Indeed, I had thought the Court decided otherwise just last Term in Ginsberg v. New York, 390 U. S. 629. I con- tinue to hold the view I expressed in that case: "[A] State may permissibly determine that, at least in some precisely delineated areas, a child-like someone in a captive audience-is not possessed of that full capacity for individual choice which is the presupposition of First Amendment guarantees." Id., at 649-650 (con- curring in result). Cf. Prince v. Massachusetts, 321 U. S. 158.
```

## Answer-level examples — separate assessment axes

### AR-001 (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Answer:** The Supreme Court in Miranda v. Arizona required the following safeguards before custodial interrogation may be lawfully conducted:

1. The person must be warned prior to questioning that they have the right to remain silent.
2. The person must be informed that any statement they do make can be used as evidence against them.
3. The person must be told they have the right to consult with an attorney and to have an attorney present during interrogation.
4. If the person is indigent, a lawyer will be appointed to represent them.
5. If the individual indicates at any time that they wish to remain silent, interrogation must cease.
6. If the individual requests an attorney, questioning must stop until an attorney is present.
7. The waiver of these rights must be made voluntarily, knowingly, and intelligently.

The Court emphasized that these procedural safeguards are necessary to secure the Fifth Amendment privilege against self-incrimination and that absent these warnings and protections, any statements obtained during custodial interrogation are inadmissible in prosecution [S1][S2][S3].

**Assessment:** {"completeness": "INCOMPLETE", "abstention": "NOT_APPLICABLE", "certainty": "OVERSTATED", "citation_coverage": "INCOMPLETE"}

**Rationale:** Safeguards are covered, but the evidence also allows equally effective alternatives; grouping citations at the end weakens claim-level attribution. Completeness is judged against the supplied context, not all law.

**Context:** [S1] miranda_v_arizona:structure_aware_v1:00006 (PDF 9–10), [S2] miranda_v_arizona:structure_aware_v1:00000 (PDF 1–2), [S3] miranda_v_arizona:structure_aware_v1:00034 (PDF 56–58), [S4] miranda_v_arizona:structure_aware_v1:00033 (PDF 55–56)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

### AR-002 (PROPOSED)

**Question:** How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?

**Answer:** The majority in Obergefell v. Hodges explained that the Due Process Clause and the Equal Protection Clause of the Fourteenth Amendment are connected in a profound way, though they articulate independent principles. The Court stated that rights implicit in liberty (Due Process) and rights secured by equal protection may rest on different legal foundations and are not always co-extensive, but in some cases each can shed light on the meaning and scope of the other. One Clause may capture the essence of a right more accurately or comprehensively in a particular case, yet both Clauses can converge in defining and identifying that right [S2].

The majority illustrated this synergy by referencing prior decisions such as Loving v. Virginia, where the prohibition on interracial marriage was invalidated on Equal Protection grounds because it imposed unequal treatment based on race, and simultaneously on Due Process grounds because it burdened the fundamental liberty to marry. Similarly, in Zablocki v. Redhail, the Court relied on Equal Protection in conjunction with Due Process to invalidate a law restricting the right to marry, highlighting how the fundamental nature of the marriage right provided a basis for equal protection analysis [S2].

Thus, the majority viewed the interplay between Due Process and Equal Protection Clauses as mutually reinforcing in understanding the fundamental right to marry, with each Clause offering insight that informs and strengthens the other. This connection helped the Court conclude that state laws banning same-sex marriage violate both liberty and equality principles enshrined in the Fourteenth Amendment [S2].

**Assessment:** {"completeness": "COMPLETE", "abstention": "NOT_APPLICABLE", "certainty": "OVERSTATED", "citation_coverage": "INCOMPLETE"}

**Rationale:** It addresses the requested clause relationship. The final holding extension is not directly established by the cited majority chunk. Completeness and support are separate dimensions.

**Context:** [S1] obergefell_v_hodges:structure_aware_v1:00041 (PDF 63–65), [S2] obergefell_v_hodges:structure_aware_v1:00020 (PDF 29–31), [S3] obergefell_v_hodges:structure_aware_v1:00033 (PDF 50–52)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

### AR-003 (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Answer:** The available Supreme Court documents do not provide enough evidence to answer this question about the decision in Dobbs v. Jackson Women's Health Organization [S1]-[S3].

**Assessment:** {"completeness": "NOT_APPLICABLE", "abstention": "APPROPRIATE", "certainty": "JUSTIFIED", "citation_coverage": "MISLEADING"}

**Rationale:** It refuses to invent a Dobbs holding, but appends references to unrelated Obergefell text. Appropriate abstention can coexist with misleading citations.

**Context:** [S1] obergefell_v_hodges:structure_aware_v1:00025 (PDF 39–40), [S2] obergefell_v_hodges:structure_aware_v1:00010 (PDF 12–13), [S3] obergefell_v_hodges:structure_aware_v1:00013 (PDF 17–19)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

### AR-004 (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Answer:** The available Supreme Court documents do not provide enough evidence to answer this question.

**Assessment:** {"completeness": "NOT_APPLICABLE", "abstention": "APPROPRIATE", "certainty": "JUSTIFIED", "citation_coverage": "NOT_APPLICABLE"}

**Rationale:** The supplied passages contain no Dobbs holding. This is a deliberately constructed canonical refusal, not a new model run. No supporting citation is needed.

**Context:** [S1] obergefell_v_hodges:structure_aware_v1:00025 (PDF 39–40), [S2] obergefell_v_hodges:structure_aware_v1:00010 (PDF 12–13), [S3] obergefell_v_hodges:structure_aware_v1:00013 (PDF 17–19)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

### AR-005 (PROPOSED)

**Question:** What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?

**Answer:** The available Supreme Court documents do not provide enough evidence to answer this question.

**Assessment:** {"completeness": "NOT_APPLICABLE", "abstention": "UNWARRANTED", "certainty": "OVERSTATED", "citation_coverage": "NOT_APPLICABLE"}

**Rationale:** The selected Miranda majority and syllabus excerpts directly supply the requested safeguards. The same refusal is not justified for this evidence context.

**Context:** [S1] miranda_v_arizona:structure_aware_v1:00006 (PDF 9–10), [S2] miranda_v_arizona:structure_aware_v1:00000 (PDF 1–2), [S3] miranda_v_arizona:structure_aware_v1:00034 (PDF 56–58), [S4] miranda_v_arizona:structure_aware_v1:00033 (PDF 55–56)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

### AR-006 (PROPOSED)

**Question:** What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?

**Answer:** Dobbs held that every abortion regulation is unconstitutional [S1].

**Assessment:** {"completeness": "INCOMPLETE", "abstention": "NOT_APPLICABLE", "certainty": "OVERSTATED", "citation_coverage": "MISLEADING"}

**Rationale:** Obergefell excerpts do not establish this Dobbs holding; this synthetic out-of-corpus answer asserts certainty without support. No outside legal truth judgment is needed.

**Context:** [S1] obergefell_v_hodges:structure_aware_v1:00025 (PDF 39–40), [S2] obergefell_v_hodges:structure_aware_v1:00010 (PDF 12–13), [S3] obergefell_v_hodges:structure_aware_v1:00013 (PDF 17–19)

Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.

## Limitations

- Small curated challenge set, not population-representative or a frozen benchmark.
- Most passages are Miranda/Obergefell; supplemental concurrence cases broaden attribution coverage only.
- Original smoke citations are sometimes paragraph/grouped; newly assigned claim-passage pairings are marked synthetic.
- Five compound diagnostic probes intentionally relax atomicity for coverage K; primary units otherwise target one proposition.
- Some OCR/opinion boundaries are uncertain; raw metadata is preserved and not verified authorship.
- Proposed labels, especially partial versus contradicted and implicit majority support, require independent human review.
- No verifier, judge, model requests, metric computation, or training/test split is implemented.
