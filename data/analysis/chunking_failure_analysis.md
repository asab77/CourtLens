# Fixed-Chunking Failure Analysis

This report uses only the saved Experiment 1 rankings and local vector-store records. It does not rerun retrieval or infer explanations for the observed rank differences.

## Summary

| Comparison | Questions |
|---|---:|
| 1500/200 beats 1200/200 | 13 |
| 1200/200 beats 1500/200 | 9 |
| Tie | 18 |
| All four miss Top-5 | 4 |

A miss is ordered immediately after rank 5 for pairwise comparison. The manual-review set includes up to two strong miss-to-hit transitions per win category, then fills the category quota with the largest remaining rank improvements. All universal misses are included.

## First Relevant Rank Distribution

| Configuration | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Miss |
|---|---:|---:|---:|---:|---:|---:|
| 600/100 | 14 | 7 | 4 | 3 | 1 | 11 |
| 900/150 | 19 | 3 | 3 | 1 | 0 | 14 |
| 1200/200 | 17 | 5 | 2 | 1 | 3 | 12 |
| 1500/200 | 20 | 2 | 3 | 2 | 4 | 9 |

## Selected Questions

| Category | ID | Case | Relevant pages | 600/100 | 900/150 | 1200/200 | 1500/200 |
|---|---|---|---|---:|---:|---:|---:|
| 1500/200 wins | MAR-03 | Marbury v. Madison | 35-37 | 2 | 1 | Miss | 1 |
| 1500/200 wins | MAR-04 | Marbury v. Madison | 37-40 | 3 | 1 | Miss | 1 |
| 1500/200 wins | OBE-02 | Obergefell v. Hodges | 1 | Miss | Miss | 5 | 1 |
| 1500/200 wins | TIN-02 | Tinker v. Des Moines School Dist. | 1 | Miss | Miss | Miss | 3 |
| 1200/200 wins | PLE-04 | Plessy v. Ferguson | 4-5 | 2 | 2 | 1 | Miss |
| 1200/200 wins | GID-05 | Gideon v. Wainwright | 10-11 | Miss | Miss | 5 | Miss |
| 1200/200 wins | GID-04 | Gideon v. Wainwright | 10-11 | 1 | 2 | 1 | 4 |
| All configurations struggle | DRE-04 | Dred Scott v. Sandford | 3-4 | Miss | Miss | Miss | Miss |
| All configurations struggle | NYT-02 | New York Times Co. v. United States | 1-2 | Miss | Miss | Miss | Miss |
| All configurations struggle | NYT-03 | New York Times Co. v. United States | 2 | Miss | Miss | Miss | Miss |
| All configurations struggle | OBE-01 | Obergefell v. Hodges | 12-13 | Miss | Miss | Miss | Miss |

## 1500/200 wins

### MAR-03 — Marbury v. Madison

**Question:** Why did the Court consider mandamus an appropriate remedy for Marbury's withheld commission?

**Expected pages:** 35-37

**First relevant ranks:** 600/100 2; 900/150 1; 1200/200 Miss; 1500/200 1.

**Selection evidence:** 1500/200 found the first relevant result at rank 1; 1200/200 missed the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.627225 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 31-33; vector `271`; chunk `23`.

> ===== PAGE 31 ===== FEBRUARY, 1803. 167 The power of nominating to the fenate, and the pow- MA PBU RY er of appointing the perfon nominated, are political pow- V. ers, to be exerifed by the Prefident according to his own MAD;so N. difcretion. When, he has made an appointment, he has '-v'-- exercifed his whole power, and his difcretion has been completely applied to the cafe. If, by law, the officer be removable at the will of the Prefident, then a new ap- pointment may be immediately made, and the rights of the officer are terminated. But as a fa& which has ex- ifted cannot be made never to have exifted, the appoint- ment cannot be annihilated ; and confequently if the of- ficer is by law …

**Rank 2 — similarity 0.626971 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 16-18; vector `262`; chunk `14`.

> ===== PAGE 16 ===== SUPREME COURT U. S. MARBupY This caufe may feem trivial at firft view, but it is im '. portant in principle. It is for this reafon that this court MADOSON. is now troubled with it. The emoluments or thc dignity ' ' of the office, are no objeds with the applicants. They conceive themfelves to be duly appointed juftices of the peace, and they believe it to be their duty to maintain the rights of their office, and not to fuffer them to be violated by the hand of power. The citizens of this difirit have caeir fears excited by every firetch of power by a pcrfon fo high in office as the fecretary of ftate. It only remains now to confider whether a mandamus to compel the …

**Rank 3 — similarity 0.578883 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 33-34; vector `272`; chunk `24`.

> ===== PAGE 33 ===== FEBRUARY, 1803. 169 V has no other fpecific legal remedy, this court ought MAkBUIL-, "9 to affift by mandamus, upon reafons of juftice, as the IV. "9 writ expreffes, and upon reafons of public policy, to MADISON. "9 preferve peace, order and good, government." In the fame cafe he fays, "this writ ought to be ufed upon all "4 occafions where the law has eftablifhed no fpecific "c remedy, and where in juftice and good government "9 there ought to be one." In addition to the authorities now particularly cited, many others were relied on at the bar, which fhow how far the praalice has conformed to the general dotrines that have been juft quoted. This writ, if awarded, would …

**Rank 4 — similarity 0.578593 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 6-7; vector `253`; chunk `5`.

> ===== PAGE 6 ===== SUPREME COURT U. S. MA1t 1rit they Cnnot be bound to anfwer. Such are thelaCts con- q'. cerning foreign correfpondencies, and confidential com- MAalsoa. munications betweeh the head of the department and the Prefident. This, however, can be no obje&ion to their being fworn, but may he a ground of obje&ion to any particular queftion. Suppofe I claim title to land under a patent from the United States., I demand a copy of it from the fecretary of ifate. He refufes. Surely he may be compelled by mandamus to give it. But in order to obtain a mandamus, I muft fliew that the patent is re- corded in his office. My cafe would be hard indeed if -I could not' call upon the clerks …

**Rank 5 — similarity 0.572439 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 12-13; vector `258`; chunk `10`.

> ===== PAGE 12 ===== SUPREME COURT U. S. MAtitisvr ceedings of another, either as tb law or fa&, or both. ,v. The writ of mandamus is in the nature of an appeal as -MA D I s. to fa& as well as law. It is competent for congrefs td ' * prefcribe the forms of procefs by which the fupreme court fllall exercife its appelhite jurisdi&ion,. and they may well declare a mandamus to be one. But the power does not depend upon implication alone. It has been recognifed by legiflative provifion as well as in judicial decifions in this court. Congrefs, by a law paffed at the very firft feffion after the adoption of the confitution, vol. i. p. 58, fec. 13, have cxprefsly given the fupreme court the power …


#### 1500/200 Top-5

**Rank 1 — similarity 0.630929 — relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 36-38; vector `147`; chunk `18`.

> ===== PAGE 36 ===== SUPREME COURT U. S. MAl1URY States on the validity of any fuch rights, claimed under v. the a& aforefaid. MADISON. ~v~'After the paffage of this a&, a mandamus was movea for, to be direc&ed to the fecretary at war, commanding him to place on the penfion lift, a perfon ftating himfelf to be on the report of the judges. There is, therefore, much reafon to believe, that this mode of trying the legal right of the complainant, was deemed by the head of a department, and by the higheft law officer of the United States, the moft proper which could be felected-for the purpofe. When the fubjeHl was brought before the court the de- cifion was, not that a mandamus would not lie to …

**Rank 2 — similarity 0.626971 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 16-18; vector `137`; chunk `8`.

> ===== PAGE 16 ===== SUPREME COURT U. S. MARBupY This caufe may feem trivial at firft view, but it is im '. portant in principle. It is for this reafon that this court MADOSON. is now troubled with it. The emoluments or thc dignity ' ' of the office, are no objeds with the applicants. They conceive themfelves to be duly appointed juftices of the peace, and they believe it to be their duty to maintain the rights of their office, and not to fuffer them to be violated by the hand of power. The citizens of this difirit have caeir fears excited by every firetch of power by a pcrfon fo high in office as the fecretary of ftate. It only remains now to confider whether a mandamus to compel the …

**Rank 3 — similarity 0.607112 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 32-34; vector `145`; chunk `16`.

> ===== PAGE 32 ===== SUPREME COURT U. S. MARDURY of peace, for the county of Wafhington in the diftri& .V. of Columbia ; and that the feal of the United States, af- MAD ToN. fixed thereto by the fecretary of ftate, is conclufive tef- 'timony of the verity of the fignature, and of the com- pletion of the appointment ; and that the appointment conferred on him a legal right to the office for the fpace of five years. 2dly. That, having this legal title to the office, he has a confequent right, to the commiffion ; a re fufal to deliver which, is a plain violation of that right, for which the laws of his country afford him a remedy. It remains to be enquired whether, 3dly. He is entitled to the …

**Rank 4 — similarity 0.536974 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 30-32; vector `144`; chunk `15`.

> ===== PAGE 30 ===== SUPREME COURT U. 5. MARBUxY exercife of which he is to ufe his own difcretion, and is 'V. accountable only to his country in his political chara&er, MADISON. and to his own confcience. To aid him in the perform- ahce of thefe duties, he is authorized to appoint certain officers, who ad by his authority and in conformity with his orders. In fuch cafes, their ads are his ads ; and whatever opinion may be entertained of the manner in which exe- cutive difcretion may be ufed, fiill there exifts, and can exift, no power to control that difcretion. The fubjeds are political. They refped the nation, not individual rights, and being entrufted to the executive, the decifion of …

**Rank 5 — similarity 0.533682 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 12-14; vector `135`; chunk `6`.

> ===== PAGE 12 ===== SUPREME COURT U. S. MAtitisvr ceedings of another, either as tb law or fa&, or both. ,v. The writ of mandamus is in the nature of an appeal as -MA D I s. to fa& as well as law. It is competent for congrefs td ' * prefcribe the forms of procefs by which the fupreme court fllall exercife its appelhite jurisdi&ion,. and they may well declare a mandamus to be one. But the power does not depend upon implication alone. It has been recognifed by legiflative provifion as well as in judicial decifions in this court. Congrefs, by a law paffed at the very firft feffion after the adoption of the confitution, vol. i. p. 58, fec. 13, have cxprefsly given the fupreme court the power …


### MAR-04 — Marbury v. Madison

**Question:** Why could the Supreme Court not exercise original jurisdiction to issue the writ of mandamus requested by Marbury?

**Expected pages:** 37-40

**First relevant ranks:** 600/100 3; 900/150 1; 1200/200 Miss; 1500/200 1.

**Selection evidence:** 1500/200 found the first relevant result at rank 1; 1200/200 missed the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.592545 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 16-18; vector `262`; chunk `14`.

> ===== PAGE 16 ===== SUPREME COURT U. S. MARBupY This caufe may feem trivial at firft view, but it is im '. portant in principle. It is for this reafon that this court MADOSON. is now troubled with it. The emoluments or thc dignity ' ' of the office, are no objeds with the applicants. They conceive themfelves to be duly appointed juftices of the peace, and they believe it to be their duty to maintain the rights of their office, and not to fuffer them to be violated by the hand of power. The citizens of this difirit have caeir fears excited by every firetch of power by a pcrfon fo high in office as the fecretary of ftate. It only remains now to confider whether a mandamus to compel the …

**Rank 2 — similarity 0.579093 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 31-33; vector `271`; chunk `23`.

> ===== PAGE 31 ===== FEBRUARY, 1803. 167 The power of nominating to the fenate, and the pow- MA PBU RY er of appointing the perfon nominated, are political pow- V. ers, to be exerifed by the Prefident according to his own MAD;so N. difcretion. When, he has made an appointment, he has '-v'-- exercifed his whole power, and his difcretion has been completely applied to the cafe. If, by law, the officer be removable at the will of the Prefident, then a new ap- pointment may be immediately made, and the rights of the officer are terminated. But as a fa& which has ex- ifted cannot be made never to have exifted, the appoint- ment cannot be annihilated ; and confequently if the of- ficer is by law …

**Rank 3 — similarity 0.570523 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 12-13; vector `258`; chunk `10`.

> ===== PAGE 12 ===== SUPREME COURT U. S. MAtitisvr ceedings of another, either as tb law or fa&, or both. ,v. The writ of mandamus is in the nature of an appeal as -MA D I s. to fa& as well as law. It is competent for congrefs td ' * prefcribe the forms of procefs by which the fupreme court fllall exercife its appelhite jurisdi&ion,. and they may well declare a mandamus to be one. But the power does not depend upon implication alone. It has been recognifed by legiflative provifion as well as in judicial decifions in this court. Congrefs, by a law paffed at the very firft feffion after the adoption of the confitution, vol. i. p. 58, fec. 13, have cxprefsly given the fupreme court the power …

**Rank 4 — similarity 0.561546 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 6-7; vector `253`; chunk `5`.

> ===== PAGE 6 ===== SUPREME COURT U. S. MA1t 1rit they Cnnot be bound to anfwer. Such are thelaCts con- q'. cerning foreign correfpondencies, and confidential com- MAalsoa. munications betweeh the head of the department and the Prefident. This, however, can be no obje&ion to their being fworn, but may he a ground of obje&ion to any particular queftion. Suppofe I claim title to land under a patent from the United States., I demand a copy of it from the fecretary of ifate. He refufes. Surely he may be compelled by mandamus to give it. But in order to obtain a mandamus, I muft fliew that the patent is re- corded in his office. My cafe would be hard indeed if -I could not' call upon the clerks …

**Rank 5 — similarity 0.556737 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 9-11; vector `256`; chunk `8`.

> ===== PAGE 9 ===== FEBRUARY, 1803. 145 is a fiCt which all the world have a right to know. If MABUlZr he thought any of the queftions improper, he might ftate M. V. his objedions. Mr. Lincoln then prayed time till the next day to con- fider of his anfwers under this opinion of the court. The court granted it and pofiponed further confideratioa of the caufe till the next day. At the opening of the court on the next morning, Mr. Lincoln faid he had no objelion to anfwering the quef- tions propofed, excepting the laft which he did not think himfelf obliged to anfwer fully. The queftion was, what had been done with the commillions. He had no heft- tation in faying that he did not know that …


#### 1500/200 Top-5

**Rank 1 — similarity 0.596719 — relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 36-38; vector `147`; chunk `18`.

> ===== PAGE 36 ===== SUPREME COURT U. S. MAl1URY States on the validity of any fuch rights, claimed under v. the a& aforefaid. MADISON. ~v~'After the paffage of this a&, a mandamus was movea for, to be direc&ed to the fecretary at war, commanding him to place on the penfion lift, a perfon ftating himfelf to be on the report of the judges. There is, therefore, much reafon to believe, that this mode of trying the legal right of the complainant, was deemed by the head of a department, and by the higheft law officer of the United States, the moft proper which could be felected-for the purpofe. When the fubjeHl was brought before the court the de- cifion was, not that a mandamus would not lie to …

**Rank 2 — similarity 0.592545 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 16-18; vector `137`; chunk `8`.

> ===== PAGE 16 ===== SUPREME COURT U. S. MARBupY This caufe may feem trivial at firft view, but it is im '. portant in principle. It is for this reafon that this court MADOSON. is now troubled with it. The emoluments or thc dignity ' ' of the office, are no objeds with the applicants. They conceive themfelves to be duly appointed juftices of the peace, and they believe it to be their duty to maintain the rights of their office, and not to fuffer them to be violated by the hand of power. The citizens of this difirit have caeir fears excited by every firetch of power by a pcrfon fo high in office as the fecretary of ftate. It only remains now to confider whether a mandamus to compel the …

**Rank 3 — similarity 0.557220 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 32-34; vector `145`; chunk `16`.

> ===== PAGE 32 ===== SUPREME COURT U. S. MARDURY of peace, for the county of Wafhington in the diftri& .V. of Columbia ; and that the feal of the United States, af- MAD ToN. fixed thereto by the fecretary of ftate, is conclufive tef- 'timony of the verity of the fignature, and of the com- pletion of the appointment ; and that the appointment conferred on him a legal right to the office for the fpace of five years. 2dly. That, having this legal title to the office, he has a confequent right, to the commiffion ; a re fufal to deliver which, is a plain violation of that right, for which the laws of his country afford him a remedy. It remains to be enquired whether, 3dly. He is entitled to the …

**Rank 4 — similarity 0.527913 — not relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 12-14; vector `135`; chunk `6`.

> ===== PAGE 12 ===== SUPREME COURT U. S. MAtitisvr ceedings of another, either as tb law or fa&, or both. ,v. The writ of mandamus is in the nature of an appeal as -MA D I s. to fa& as well as law. It is competent for congrefs td ' * prefcribe the forms of procefs by which the fupreme court fllall exercife its appelhite jurisdi&ion,. and they may well declare a mandamus to be one. But the power does not depend upon implication alone. It has been recognifed by legiflative provifion as well as in judicial decifions in this court. Congrefs, by a law paffed at the very firft feffion after the adoption of the confitution, vol. i. p. 58, fec. 13, have cxprefsly given the fupreme court the power …

**Rank 5 — similarity 0.521435 — relevant**

Source: `Marbury v. Madison` / `marbury_v_madison.pdf`; pages 38-40; vector `148`; chunk `19`.

> ===== PAGE 38 ===== SUPREME COURT U. S. MALuRT cafe ; becaufe the right claimed is given by a law of the 'V. United States. MADISON. ~v'In the diftribution 9f this power it is declared that (( the " fupreme court fhall have original jurifdi&ion in all " cafes affeding ambaffadors, other public minifters and " confuls, and thofe in which a ftate fhall be a party. "In all other cafes, the fupreme court fhall have appellate 4c jurifdi&ion." It has been infifted, at the bar, that as the original grant of jurifdiition, to the fupreme and inferior c urts&, is general, and the claufe, affigning original jurifdi&ion to the fupreme court, contains no negative or rctlri&ive words ; the power remains …


### OBE-02 — Obergefell v. Hodges

**Question:** What did the Court hold the Fourteenth Amendment requires States to do regarding same-sex marriages?

**Expected pages:** 1

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 5; 1500/200 1.

**Selection evidence:** 1500/200 found the first relevant result at rank 1, compared with rank 5 for 1200/200.

#### 1200/200 Top-5

**Rank 1 — similarity 0.608932 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 2-3; vector `364`; chunk `1`.

> ===== PAGE 2 ===== 645 Cite as: 576 U. S. 644 (2015) Syllabus a Nation where new dimensions of freedom become apparent to new generations. This dynamic can be seen in the Nation's experience with gay and lesbian rights. Well into the 20th century, many States condemned same-sex intimacy as immoral, and homosexuality was treated as an illness. Later in the century, cultural and political developments al- lowed same-sex couples to lead more open and public lives. Extensive public and private dialogue followed, along with shifts in public atti- tudes. Questions about the legal treatment of gays and lesbians soon reached the courts, where they could be discussed in the formal dis- course of …

**Rank 2 — similarity 0.602201 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 37-39; vector `387`; chunk `24`.

> ===== PAGE 37 ===== 680 OBERGEFELL v. HODGES Opinion of the Court ples that are so fulflling and so central to their lives and faiths, and to their own deep aspirations to continue the fam- ily structure they have long revered. The same is true of those who oppose same-sex marriage for other reasons. In turn, those who believe allowing same-sex marriage is proper or indeed essential, whether as a matter of religious conviction or secular belief, may engage those who disagree with their view in an open and searching debate. The Con- stitution, however, does not permit the State to bar same- sex couples from marriage on the same terms as accorded to couples of the opposite sex. V These cases …

**Rank 3 — similarity 0.598956 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 4-5; vector `366`; chunk `3`.

> ===== PAGE 4 ===== 647 Cite as: 576 U. S. 644 (2015) Syllabus marriage and are consigned to an instability many opposite-sex couples would fnd intolerable. It is demeaning to lock same-sex couples out of a central institution of the Nation's society, for they too may aspire to the transcendent purposes of marriage. The limitation of marriage to opposite-sex couples may long have seemed natural and just, but its inconsistency with the central meaning of the fundamental right to marry is now manifest. Pp. 665–671. (3) The right of same-sex couples to marry is also derived from the Fourteenth Amendment's guarantee of equal protection. The Due Process Clause and the Equal Protection Clause are …

**Rank 4 — similarity 0.594911 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 50-52; vector `395`; chunk `32`.

> ===== PAGE 50 ===== 693 Cite as: 576 U. S. 644 (2015) Roberts, C. J., dissenting State Constitution to require recognition of same-sex mar- riage, many States—including the four at issue here— enacted constitutional amendments formally adopting the longstanding defnition of marriage. Over the last few years, public opinion on marriage has shifted rapidly. In 2009, the legislatures of Vermont, New Hampshire, and the District of Columbia became the frst in the Nation to enact laws that revised the defnition of mar- riage to include same-sex couples, while also providing ac- commodations for religious believers. In 2011, the New York Legislature enacted a similar law. In 2012, voters in Maine …

**Rank 5 — similarity 0.593005 — relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 1-2; vector `363`; chunk `0`.

> ===== PAGE 1 ===== 644 OCTOBER TERM, 2014 Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men whose same-sex partners are deceased, fled suits in Fed- eral District Courts in their home States, claiming that respondent state offcials violate the Fourteenth Amendment by denying them the right to marry or to have marriages lawfully performed in another State given full recognition. Each District …


#### 1500/200 Top-5

**Rank 1 — similarity 0.611545 — relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 1-3; vector `217`; chunk `0`.

> ===== PAGE 1 ===== 644 OCTOBER TERM, 2014 Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men whose same-sex partners are deceased, fled suits in Fed- eral District Courts in their home States, claiming that respondent state offcials violate the Fourteenth Amendment by denying them the right to marry or to have marriages lawfully performed in another State given full recognition. Each District …

**Rank 2 — similarity 0.591079 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 35-38; vector `235`; chunk `18`.

> ===== PAGE 35 ===== 678 OBERGEFELL v. HODGES Opinion of the Court nalizing same-sex intimacy. See 478 U. S., at 190–195. That approach might have been viewed as a cautious en- dorsement of the democratic process, which had only just begun to consider the rights of gays and lesbians. Yet, in effect, Bowers upheld state action that denied gays and lesbi- ans a fundamental right and caused them pain and humilia- tion. As evidenced by the dissents in that case, the facts and principles necessary to a correct holding were known to the Bowers Court. See id., at 199 (Blackmun, J., joined by Brennan, Marshall, and Stevens, JJ., dissenting); id., at 214 (Stevens, J., joined by Brennan and Marshall, …

**Rank 3 — similarity 0.584795 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 3-5; vector `218`; chunk `1`.

> ===== PAGE 3 ===== 646 OBERGEFELL v. HODGES Syllabus protected. See, e. g., Eisenstadt, supra, at 453–454. This analysis compels the conclusion that same-sex couples may exercise the right to marry. Pp. 663–665. (2) Four principles and traditions demonstrate that the reasons marriage is fundamental under the Constitution apply with equal force to same-sex couples. The frst premise of this Court's relevant prece- dents is that the right to personal choice regarding marriage is inherent in the concept of individual autonomy. This abiding connection be- tween marriage and liberty is why Loving invalidated interracial mar- riage bans under the Due Process Clause. See 388 U. S., at 12. Deci- …

**Rank 4 — similarity 0.579421 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 42-44; vector `239`; chunk `22`.

> ===== PAGE 42 ===== 685 Cite as: 576 U. S. 644 (2015) Appendix B to opinion of the Court Li v. State, 338 Ore. 376, 110 P. 3d 91 (2005) Cote-Whitacre v. Department of Public Health, 446 Mass. 350, 844 N. E. 2d 623 (2006) Lewis v. Harris, 188 N. J. 415, 908 A. 2d 196 (2006) Andersen v. King County, 158 Wash. 2d 1, 138 P. 3d 963 (2006) Hernandez v. Robles, 7 N. Y . 3d 338, 855 N. E. 2d 1 (2006) Conaway v. Deane, 401 Md. 219, 932 A. 2d 571 (2007) In re Marriage Cases, 43 Cal. 4th 757, 183 P. 3d 384 (2008) Kerrigan v. Commissioner of Public Health, 289 Conn. 135, 957 A. 2d 407 (2008) Strauss v. Horton, 46 Cal. 4th 364, 207 P. 3d 48 (2009) Varnum v. Brien, 763 N. W. 2d 862 (Iowa 2009) Griego v. …

**Rank 5 — similarity 0.577897 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 28-30; vector `232`; chunk `15`.

> ===== PAGE 28 ===== 671 Cite as: 576 U. S. 644 (2015) Opinion of the Court now manifest. With that knowledge must come the recogni- tion that laws excluding same-sex couples from the marriage right impose stigma and injury of the kind prohibited by our basic charter. Objecting that this does not refect an appropriate framing of the issue, the respondents refer to Washington v. Glucks- berg, 521 U. S. 702, 721 (1997), which called for a “ `careful description' ” of fundamental rights. They assert the peti- tioners do not seek to exercise the right to marry but rather a new and nonexistent “right to same-sex marriage.” Brief for Respondent in No. 14–556, p. 8. Glucksberg did insist that …


### TIN-02 — Tinker v. Des Moines School Dist.

**Question:** Why did the Court hold that the students' wearing of black armbands was constitutionally protected?

**Expected pages:** 1

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 Miss; 1500/200 3.

**Selection evidence:** 1500/200 found the first relevant result at rank 3; 1200/200 missed the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.677054 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 7-9; vector `438`; chunk `3`.

> ===== PAGE 7 ===== TINKER v. DES MOINES SCHOOL DIST. 509 503 Opinion of the Court. the basis of our national strength and of the independence and vigor of Americans who grow up and live in this relatively permissive, often disputatious, society. In order for the State in the person of school officials to justify prohibition of a particular expression of opinion, it must be able to show that its action was caused by something more than a mere desire to avoid the dis- comfort and unpleasantness that always accompany an unpopular viewpoint. Certainly where there is no find- ing and no showing that engaging in the forbidden con- duct would "materially and substantially interfere with the …

**Rank 2 — similarity 0.641008 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 3-5; vector `436`; chunk `1`.

> ===== PAGE 3 ===== TINKER v. DES MOINES SCHOOL DIST. 505 503 Opinion of the Court. held the constitutionality of the school authorities' action on the ground that it was reasonable in order to prevent disturbance of school discipline. 258 F. Supp. 971 (1966). The court referred to but expressly declined to follow the Fifth Circuit's holding in a similar case that the wearing of symbols like the armbands cannot be prohibited unless it "materially and substantially interfere[s] with the requirements of appropriate dis- cipline in the operation of the school." Burnside v. Byars, 363 F. 2d 744, 749 (1966). 1 On appeal, the Court of Appeals for the Eighth Circuit considered the case en banc. …

**Rank 3 — similarity 0.600969 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 5-7; vector `437`; chunk `2`.

> ===== PAGE 5 ===== TINKER v. DES MOINES SCHOOL DIST. 507 503 Opinion of the Court. U. S. 510 (1925); West Virginia v. Barnette, 319 U. S. 624 (1943); McCollum v. Board of Education, 333 U. S. 203 (1948); Wieman v. Updegrafl, 344 U. S. 183, 195 (1952) (concurring opinion); Sweezy v. New Hampshire, 354 U. S. 234 (1957); Shelton v. Tucker, 364 U. S. 479, 487 (1960); Engel v. Vitale, 370 U. S. 421 (1962); Keyishian v. Board of Regents, 385 U. S. 589, 603 (1967); Epperson v. Arkansas, ante, p. 97 (1968). In West Virginia v. Barnette, supra, this Court held that under the First Amendment, the student in public school may not be compelled to salute the flag. Speak- ing through Mr. Justice …

**Rank 4 — similarity 0.596371 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 13-15; vector `441`; chunk `6`.

> ===== PAGE 13 ===== TINKER v. DES MOINES SCHOOL DIST. 515 503 BLACK, J., dissenting. cannot share the Court's uncritical assumption that, school discipline aside, the First Amendment rights of children are co-extensive with those of adults. Indeed, I had thought the Court decided otherwise just last Term in Ginsberg v. New York, 390 U. S. 629. I con- tinue to hold the view I expressed in that case: "[A] State may permissibly determine that, at least in some precisely delineated areas, a child-like someone in a captive audience-is not possessed of that full capacity for individual choice which is the presupposition of First Amendment guarantees." Id., at 649-650 (con- curring in result). …

**Rank 5 — similarity 0.576445 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 11-13; vector `440`; chunk `5`.

> ===== PAGE 11 ===== TINKER v. DES MOINES SCHOOL DIST. 513 503 Opinion of the Court. the campus during the authorized hours, he may express his opinions, even on controversial subjects like the con- flict in Vietnam, if he does so without "materially and substantially interfer[ing] with the requirements of ap- propriate discipline in the operation of the school" and without colliding with the rights of others. Burnside v. Byars, supra, at 749. But conduct by the student, in class or out of it, which for any reason-whether it stems from time, place, or type of behavior-materially disrupts classwork or involves substantial disorder or invasion of the rights of others is, of course, not …


#### 1500/200 Top-5

**Rank 1 — similarity 0.664810 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 6-9; vector `280`; chunk `2`.

> ===== PAGE 6 ===== OCTOBER TERM, 1968. Opinion of the Court. 393 U. S. ing, to hair style, or deportment. Cf. Ferrell v. Dallas Independent School District, 392 F. 2d 697 (1968); Pugsley v. Sellmeyer, 158 Ark. 247, 250 S. W. 538 (1923). It does not concern aggressive, disruptive action or even group demonstrations. Our problem involves direct, primary First Amendment rights akin to "pure speech." The school officials banned and sought to punish peti- tioners for a silent, passive expression of opinion, unac- companied by any disorder or disturbance on the part of petitioners. There is here no evidence whatever of peti- tioners' interference, actual or nascent, with the schools' work or of …

**Rank 2 — similarity 0.593179 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 12-15; vector `282`; chunk `4`.

> ===== PAGE 12 ===== OCTOBER TERM, 1968. STEWART, J., concurring. 393 U. S. mond v. South Carolina State College, 272 F. Supp. 947 (D. C. S. C. 1967) (orderly protest meeting on state college campus); Dickey v. Alabama State Board of Edu- cation, 273 F. Supp. 613 (D. C. M. D. Ala. 1967) (expul- sion of student editor of college newspaper). In the circumstances of the present case, the prohibition of the silent, passive "witness of the armbands," as one of the children called it, is no less offensive to the Constitution's guarantees. As we have discussed, the record does not demonstrate any facts which might reasonably have led school authori- ties to forecast substantial disruption of or …

**Rank 3 — similarity 0.593043 — relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 1-4; vector `278`; chunk `0`.

> ===== PAGE 1 ===== TINKER v. DES MOINES SCHOOL DIST. 503 Syllabus. TINKER ET AL. v. DES MOINES INDEPENDENT COMMUNITY SCHOOL DISTRICT ET AL. CERTIORARI TO THE UNITED STATES COURT OF APPEALS FOR THE EIGHTH CIRCUIT. No. 21. Argued November 12, 1968.-Decided February 24, 1969. Petitioners, three public school pupils in Des Moines, Iowa, were suspended from school for wearing black armbands to protest the Government's policy in Vietnam. They sought nominal dam- ages and an injunction against a regulation that the respondents had promulgated banning the wearing of armbands. The District Court dismissed the complaint on the ground that the regulation was within the Board's power, despite the …

**Rank 4 — similarity 0.571843 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 23-24; vector `286`; chunk `8`.

> ===== PAGE 23 ===== TINKER v. DES MOINES SCHOOL DIST. 525 503 BLACK, J., dissenting. marily refused to obey a school order designed to give pupils who want to learn the opportunity to do so. One does not need to be a prophet or the son of a prophet to know that after the Court's holding today some stu- dents in Iowa schools and indeed in all schools will be ready, able, and willing to defy their teachers on prac- tically all orders. This is the more unfortunate for the schools since groups of students all over the land are already running loose, conducting break-ins, sit-ins, lie- ins, and smash-ins. Many of these student groups, as is all too familiar to all who read the newspapers and …

**Rank 5 — similarity 0.545261 — not relevant**

Source: `Tinker v. Des Moines School Dist.` / `tinker_v_des_moines_school_dist.pdf`; pages 20-23; vector `285`; chunk `7`.

> ===== PAGE 20 ===== OCTOBER TERM, 1968. BLACK, J., dissenting. 393 U. S. speech and religion into a Catholic church or Jewish synagogue. Nor does a person carry with him into the United States Senate or House, or into the Supreme Court, or any other court, a complete constitutional right to go into those places contrary to their rules and speak his mind on any subject he pleases. It is a myth to say that any person has a constitutional right to say what he pleases, where he pleases, and when he pleases. Our Court has decided precisely the opposite. See, e. g., Cox v. Louisiana, 379 U. S. 536, 555; Adderley v. Florida, 385 U. S. 39. In my view, teachers in state-controlled public schools …


## 1200/200 wins

### PLE-04 — Plessy v. Ferguson

**Question:** What penalties and enforcement powers did Louisiana's Separate Car Act impose on passengers who refused their assigned racial coach?

**Expected pages:** 4-5

**First relevant ranks:** 600/100 2; 900/150 2; 1200/200 1; 1500/200 Miss.

**Selection evidence:** 1200/200 found the first relevant result at rank 1; 1500/200 missed the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.579315 — relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 5-7; vector `423`; chunk `2`.

> ===== PAGE 5 ===== PLESSY v. FERGUSON. Opinion of the Court. to assign each passenger to the coach or compartment used for the race to which such passenger belongs; any passenger insisting on going into a coach or compartment to which by race he does not belong, shall be liable to a fine of twenty-five dollars, or in lieu thereof to imprisonment for a period of not more than twenty days in the parish prison, and any officer of any railroad insisting on assigning a passenger to a coach or compartment other than the one set aside for the race to which said passenger belongs, shall be liable to a fine of twenty-five dollars, or in lieu thereof to imprisonment for a period of not more than …

**Rank 2 — similarity 0.556635 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 13-15; vector `427`; chunk `6`.

> ===== PAGE 13 ===== PLESSY v. FERGUSON. Opinion of the Court. tion in damages for a refusal to receive him into the coach in which he properly belongs, is a valid exercise of the legisla- tive power. Indeed, we understand it to be conceded by the State's attorney, that such part of the act as exempts from liability the railway company and its officers is unconstitu- tional. The power to assign to a particular coach obviously implies the power to determine to which race the passenger belongs, as well as the power to determine who, under the laws of the particular State, is to be deemed a white, and who a colored person. This question, though indicated in the brief of the plaintiff in error, …

**Rank 3 — similarity 0.545082 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 15-17; vector `428`; chunk `7`.

> ===== PAGE 15 ===== PLESSY v. FERGUSOK. Opinion of the Court. is unreasonable, or more obnoxious to the Fourteenth Amend- ment than the acts of Congress requiring separate schools for colored children in the District of Columbia, the constitution- ality of which does not seem to have been questioned, or the corresponding acts of state legislatures. We consider the underlying fallacy of the plaintiff's argu- ment to consist in the assumption that the enforced separation of the two races stamps the colored race with a badge of in- feriority. If this be so, it is not by reason of anything found in the act, but solely because the colored race chooses to put that construction upon it. The …

**Rank 4 — similarity 0.539800 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 11-13; vector `426`; chunk `5`.

> ===== PAGE 11 ===== PLESSY v. FERGUSON. Opinion of the Court. domain of state legislation; but to provide modes of relief against state legislation, or state action, of the kind referred to. It does not authorize Congress to create a code of munici- pal law for the regulation of private rights; but to provide modes of redress against the operation of state laws, and the action of state officers, executive or judicial, when these are subversive of the fundamental rights specified in the amend- ment. Positive rights and privileges are undoubtedly secured by the Fourteenth Amendment; but they are secured by way of prohibition against state laws and state proceedings affect- ing those rights …

**Rank 5 — similarity 0.536668 — relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 3-5; vector `422`; chunk `1`.

> ===== PAGE 3 ===== PLESSY v. FERGUSOIN. Statement of the Case. :New Orleans, and there held to answer a charge made by such officer to the effect that he was guilty of having crim- inally violated an act of the General Assembly of the State, approved July 10, 1890, in such case made and provided. That petitioner was subsequently brought before the re- corder of the city for preliminary examination and committed for trial to the criminal District Court for the parish of Orleans, where an information was filed against him in the matter above set forth, for a violation of the above act, which act the petitioner affirmed to be null and void, because in conflict with the Constitution of the …


#### 1500/200 Top-5

**Rank 1 — similarity 0.569591 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 12-14; vector `270`; chunk `5`.

> ===== PAGE 12 ===== OCTOBER TERM, 1895. Opinion of the Court. sengers, or affect, in any manner, the privileges and rights of such passengers. All that we can consider is, whether the State has the power to require that railroad trains within her limits shall have separate accommodations for the two races; that affecting only commerce within the State is no invasion of the power given to Congress by the commerce clause." A like course of reasoning applies to the case under con- sideration, since the Supreme Court of Louisiana in the case of the State ex rel. Abbott v. flicks, Judge, et al., 44 La. Ann. 770, held that the statute in question did not apply to interstate passengers, but was …

**Rank 2 — similarity 0.551793 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 16-18; vector `272`; chunk `7`.

> ===== PAGE 16 ===== OCTOBER TERAf, 1895. Dissenting Opinion: Harlan, . or politically. If one race be inferior to the other socially, the Constitution of the United States cannot put them upon the same plane. It is true that the question of the proportion of colored blood necessary to constitute a colored person, as distinguished from a white person, is one upon which there is a difference of opinion in the different States, some holding that any visi- ble admixture of black blood stamps the person as belonging to the colored race, (State v. Clavers, 5 Jones, [:N. 0.] ], p. 11); others that it depends upon the preponderance of blood, (Gray v. State, 4 Ohio, 354; .Afonroe v. Collins, 17 …

**Rank 3 — similarity 0.536784 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 10-12; vector `269`; chunk `4`.

> ===== PAGE 10 ===== 546 OCTOBER TERM, 1895. Opinion of the Court. color, we have held that this meant that persons of color should travel in the same car as white ones, and that the enactment was not satisfied by the company's providing cars assigned exclusively to people of color, though they were as good as those which they assigned exclusively to white per- sons. Railroad Company v. Brown, 17 Wall. 445. Upon the other hand, where a statute of Louisiana required those engaged in the transportation of passengers among the States to give to all persons travelling within that State, upon vessels employed in that business, equal rights and privileges in all parts of the vessel, without …

**Rank 4 — similarity 0.515998 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 24-26; vector `276`; chunk `11`.

> ===== PAGE 24 ===== OCTOBER TERM. 1895. Dissenting Opinion: Harlan, J. race, and, whether emancipated or not, yet remained subject to their authority, and had no rights or 1rivileges but such as those who held the power and the government might choose to grant them." 19 How. 393, 404. The recent amendments of the Constitution, it was supposed, had eradicated these principles from our institutions. But it seems that we have yet, in some of the States, a dominant race-a superior class of citizens, which assumes to regulate the enjoyment of civil rights, common to all citizens, upon the basis of race. The present decision, it may well be apprehended, will not only stimulate aggressions, more …

**Rank 5 — similarity 0.509107 — not relevant**

Source: `Plessy v. Ferguson` / `plessy_v_ferguson.pdf`; pages 1-3; vector `265`; chunk `0`.

> ===== PAGE 1 ===== PLESSY v. FERGUSON. Syllabus. boundary line as described in said report and as delineated on said map, and now marked by cedar posts, be permanently marked as recommended in said report, with all convenient speed, and that said commission be continued for that purpose, and make report thereon to this court, and that this cause be retained until such report is made. It is further ordered, adjudged, and decreed that the com- pensation and expenses of the commissioners and the expenses attendant on the discharge of their duties, up to this time, be, and they are hereby, allowed at the sum of two thousand two hundred and thirty-six dollars and sixty cents in accord- ance …


### GID-05 — Gideon v. Wainwright

**Question:** What difficulties did the Court identify that even an intelligent and educated person may face when defending himself without a lawyer?

**Expected pages:** 10-11

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 5; 1500/200 Miss.

**Selection evidence:** 1200/200 found the first relevant result at rank 5; 1500/200 missed the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.493473 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 36-38; vector `300`; chunk `20`.

> ===== PAGE 36 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court. may be the person who most needs counsel. A; the California Supreme Court has aptly put it: "Finally, we must recognize that the imposition of the requirement for the request would discrimi- nate against the defendant who does not know his rights. The defendant who does not ask for counsel is the very defendant who most needs counsel. We cannot penalize a defendant who, not understanding his constitutional rights, does not make the formal request and by such failure demonstrates his help- lessness. To require the request would be to favor the defendant whose sophistication or status had fortuitously prompted him to make it." …

**Rank 2 — similarity 0.461243 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 38-40; vector `301`; chunk `21`.

> ===== PAGE 38 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court. of counsel to the indigent at the time of interrogation while allowing an attorney to those who can afford one would be no more supportable by reason or logic than the similar situation at trial and on appeal struck down in Gideon v. Wainwright, 372 U. S. 335 (1963), and Douglas v. California, 372 U. S. 353 (1963). In order fully to apprise a person interrogated of the extent of his rights under this system then, it is neces- sary to warn him not only that he has the right to con- sult with an attorney, but also that if he is indigent a lawyer will be appointed to represent him. Without this additional warning, the …

**Rank 3 — similarity 0.458949 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 34-36; vector `299`; chunk `19`.

> ===== PAGE 34 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court.. mation as to his age, education, intelligence, or prior contact with authorities, can never be more than specu- lation; 38 a warning is a clearcut fact. More important, whatever the background of the person interrogated, a warning at the time of the interrogation is indispensable to overcome its pressures and- to insure that the indi- vidual knows he is free to exercise the privilege at that. point in time. The warning of the right to remain silent must be accompanied by the explanation that anything said can and will be used against the individual in court. This warning is needed in order'to make him aware not only of the …

**Rank 4 — similarity 0.454538 — not relevant**

Source: `Gideon v. Wainwright` / `gideon_v_wainwright.pdf`; pages 3-5; vector `240`; chunk `1`.

> ===== PAGE 3 ===== GIDEON v. WAINWRIGHT. 335 Opinion of the Court. Florida law. Appearing in court without funds and with- out a lawyer, petitioner asked the court to appoint counsel for him, whereupon the following colloquy took place: "The CoURT: Mr. Gideon, I am sorry, but I can- not appoint Counsel to represent you in this case. Under the laws of the State of Florida, the only time the Court can appoint Counsel to represent a Defend- ant is when that person is charged with a capital offense. I am sorry, but I will have to deny your request to appoint Counsel to defend you in this case. "The DEFENDANT: The United States Supreme Court says I am entitled to be represented by Counsel." Put …

**Rank 5 — similarity 0.453716 — relevant**

Source: `Gideon v. Wainwright` / `gideon_v_wainwright.pdf`; pages 9-11; vector `243`; chunk `4`.

> ===== PAGE 9 ===== GIDEON v. WAINWRIGHT. 335 Opinion of the Court. counsel is of this fundamental character." Powell v. Ala- bama, 287 U. S. 45, 68 (1932). While the Court at the close of its Powell opinion did by its language, as this Court frequently does, limit its holding to the particular facts and circumstances of that case, its conclusions about the fundamental nature of the right to counsel are unmis- takable. Several years later, in 1936, the Court reem- phasized what it had said about the fundamental nature of the right to counsel in this language: "We concluded that certain fundamental rights, safeguarded by the first eight amendments against federal action, were also …


#### 1500/200 Top-5

**Rank 1 — similarity 0.483659 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 35-38; vector `167`; chunk `15`.

> ===== PAGE 35 ===== OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. warning given by the interrogators is not alone sufficient to accomplish that end. Prosecutors themselves claim that the admonishment of the right to remain silent with- out more "will benefit only the recidivist and the pro- fessional." Brief for the National District Attorndys Association as amicus curiae, p. 14. Even preliminary advice given to the accused by his own attorney can be swiftly overcome by the secret interrogation process., Cf. Escobedo v. Illinois, 378 U. S. 478, 485, n. 5. Thus, the need for counsel to protect the Fifth Amendment priv- ilege comprehends not merely a right to consult with counsel prior …

**Rank 2 — similarity 0.447819 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 38-41; vector `168`; chunk `16`.

> ===== PAGE 38 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court. of counsel to the indigent at the time of interrogation while allowing an attorney to those who can afford one would be no more supportable by reason or logic than the similar situation at trial and on appeal struck down in Gideon v. Wainwright, 372 U. S. 335 (1963), and Douglas v. California, 372 U. S. 353 (1963). In order fully to apprise a person interrogated of the extent of his rights under this system then, it is neces- sary to warn him not only that he has the right to con- sult with an attorney, but also that if he is indigent a lawyer will be appointed to represent him. Without this additional warning, the …

**Rank 3 — similarity 0.434768 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 84-86; vector `187`; chunk `35`.

> ===== PAGE 84 ===== MIR.NDA v. ARIZONA. 436 HARLAN, J., dissenting. tained during brief, daytime'questioning conducted by two officers and unmarked by any of the traditional in- dicia of coercion. They assured a conviction for a brutal and unsettling crime, for which the police had and quite possibly could obtain little evidence other than the vic- tim's identificatilns, evidence which is frequently un- reliable. There was, in sum, a legitimate purpose, no perceptible unfairness, and certainly littlerisk of injus- tice in the interrogation. Yet the resulting confessions, and the responsible course of police practice they repre- sent, are to be' sacrificed to the Court's own finespun …

**Rank 4 — similarity 0.428803 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 65-67; vector `178`; chunk `26`.

> ===== PAGE 65 ===== OCTOBER TERM, 1965. Opinion of Cr,.uu. .T. 384 U.S. that appear every year in the law reports. The police agencies-all the way from municipal and state forces to the federal bureaus-are responsible for law enforcement and public safety in this country. I am proud of their efforts, which in my view are not fairly characterized by the Court's opinion. The ipse dixit of the majority has no" support in our cases. Indeed, the Court admits that "we might not find the defendants' statements [here] to have been involuntary in traditional terms." Ante, p. 457. In short, the Court has added more to the requirements that the accused is entitled to consult with his lawyer and that …

**Rank 5 — similarity 0.427650 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 17-20; vector `159`; chunk `7`.

> ===== PAGE 17 ===== OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. cation that he was about to pull a gun on you, and that's when you had to act to save your own life. That's about it, isn't it, Joe?" Having then obtained the admission of shooting, the interrogator is advised to refer to circumstantial evidence which negates the self-defense explanation. This should enable him to secure the entire story. One text notes that "Even if he fails to do so, the inconsistency between the subject's original denial of the shooting and his pres- ent admission of at least doing the shooting will serve to deprive him of a self-defense 'out' at the time of trial." 16 When the techniques described …


### GID-04 — Gideon v. Wainwright

**Question:** Why did the Court consider lawyers necessities rather than luxuries in criminal trials?

**Expected pages:** 10-11

**First relevant ranks:** 600/100 1; 900/150 2; 1200/200 1; 1500/200 4.

**Selection evidence:** 1200/200 found the first relevant result at rank 1, compared with rank 4 for 1500/200.

#### 1200/200 Top-5

**Rank 1 — similarity 0.544790 — relevant**

Source: `Gideon v. Wainwright` / `gideon_v_wainwright.pdf`; pages 9-11; vector `243`; chunk `4`.

> ===== PAGE 9 ===== GIDEON v. WAINWRIGHT. 335 Opinion of the Court. counsel is of this fundamental character." Powell v. Ala- bama, 287 U. S. 45, 68 (1932). While the Court at the close of its Powell opinion did by its language, as this Court frequently does, limit its holding to the particular facts and circumstances of that case, its conclusions about the fundamental nature of the right to counsel are unmis- takable. Several years later, in 1936, the Court reem- phasized what it had said about the fundamental nature of the right to counsel in this language: "We concluded that certain fundamental rights, safeguarded by the first eight amendments against federal action, were also …

**Rank 2 — similarity 0.515600 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 36-38; vector `300`; chunk `20`.

> ===== PAGE 36 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court. may be the person who most needs counsel. A; the California Supreme Court has aptly put it: "Finally, we must recognize that the imposition of the requirement for the request would discrimi- nate against the defendant who does not know his rights. The defendant who does not ask for counsel is the very defendant who most needs counsel. We cannot penalize a defendant who, not understanding his constitutional rights, does not make the formal request and by such failure demonstrates his help- lessness. To require the request would be to favor the defendant whose sophistication or status had fortuitously prompted him to make it." …

**Rank 3 — similarity 0.467466 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 78-80; vector `321`; chunk `41`.

> ===== PAGE 78 ===== MIRANDA v. ARIZONA.- 436 HARLAN, J., disenting. Griffin v. California, 380 U. S. 609. However, the Court's unspoken assumption that any pressure violates the privilege is not supported by the.precedents aid it. has failed to show why the Fifth Amendment prohibits that- relatively mild pressure the Due- Process Clause permits. The Court appears similarly wrong in thinking that precise knowledge of one's rights is a settled prerequisite under the Fifth Amendment to the loss of its protections. A number of lower federal court cases have held that grand jury witnesses need not always be warned of their privilege, e. g., United States v. Scully, 225 F. 2d 113, 116, and …

**Rank 4 — similarity 0.455477 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 85-87; vector `325`; chunk `45`.

> ===== PAGE 85 ===== OCTOBER TERM, 1965. HARLAN, J., dissenting. 384 U. S. the courts that have accepted the invitation, it is hard to know how many have felt compelled by their best guess as to this Court's likely construction.; but none of the state decisions saw fit to rely on the state privilege against self-incrimination, and no decision at all has gone as far as this Court goes today." It is also instructive to compare the attitude in this case of those responsible for law enforcement with the official views that existed when the Court undertook three majdr revisions of prosecutorial practice prior to this case, Johnson v. Zerbst, 304 U. S. 458, Mapp v. Ohio, 367 U. S. 643, and Gideon …

**Rank 5 — similarity 0.454979 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 6-8; vector `283`; chunk `3`.

> ===== PAGE 6 ===== MIRANDA v. ARIZONA. 436 Opinion of the Court. cutor have speculated on its range and desirability.' We granted certiorari in these cases, 382 U. S. 924, 925, 937, in order further to explore some facets of the prob- lems, -thus exposed, of applying the privilege against self- incrimination to in-custody interrogation, and to give Beyond: The Need for a Fourteenth Amendment Code of Criminal Procedure, 56 J. Crim. L., C. & P. S. 143, 156 (1965). The complex problems also prompted discussions by jurists. Com- pare Bazelon, Law, Morality, and Civil Liberties, 12 U. C. L. A. L. Rev. 13 (1964), with Friendly, The Bill of Rights as a Code of Criminal Procedure, 53 Calif. L. …


#### 1500/200 Top-5

**Rank 1 — similarity 0.510632 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 35-38; vector `167`; chunk `15`.

> ===== PAGE 35 ===== OCTOBER TERM, 1965. Opinion of the Court. 384 U. S. warning given by the interrogators is not alone sufficient to accomplish that end. Prosecutors themselves claim that the admonishment of the right to remain silent with- out more "will benefit only the recidivist and the pro- fessional." Brief for the National District Attorndys Association as amicus curiae, p. 14. Even preliminary advice given to the accused by his own attorney can be swiftly overcome by the secret interrogation process., Cf. Escobedo v. Illinois, 378 U. S. 478, 485, n. 5. Thus, the need for counsel to protect the Fifth Amendment priv- ilege comprehends not merely a right to consult with counsel prior …

**Rank 2 — similarity 0.474991 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 84-86; vector `187`; chunk `35`.

> ===== PAGE 84 ===== MIR.NDA v. ARIZONA. 436 HARLAN, J., dissenting. tained during brief, daytime'questioning conducted by two officers and unmarked by any of the traditional in- dicia of coercion. They assured a conviction for a brutal and unsettling crime, for which the police had and quite possibly could obtain little evidence other than the vic- tim's identificatilns, evidence which is frequently un- reliable. There was, in sum, a legitimate purpose, no perceptible unfairness, and certainly littlerisk of injus- tice in the interrogation. Yet the resulting confessions, and the responsible course of police practice they repre- sent, are to be' sacrificed to the Court's own finespun …

**Rank 3 — similarity 0.467455 — not relevant**

Source: `Miranda v. Arizona` / `miranda_v_arizona.pdf`; pages 78-80; vector `184`; chunk `32`.

> ===== PAGE 78 ===== MIRANDA v. ARIZONA.- 436 HARLAN, J., disenting. Griffin v. California, 380 U. S. 609. However, the Court's unspoken assumption that any pressure violates the privilege is not supported by the.precedents aid it. has failed to show why the Fifth Amendment prohibits that- relatively mild pressure the Due- Process Clause permits. The Court appears similarly wrong in thinking that precise knowledge of one's rights is a settled prerequisite under the Fifth Amendment to the loss of its protections. A number of lower federal court cases have held that grand jury witnesses need not always be warned of their privilege, e. g., United States v. Scully, 225 F. 2d 113, 116, and …

**Rank 4 — similarity 0.464825 — relevant**

Source: `Gideon v. Wainwright` / `gideon_v_wainwright.pdf`; pages 9-12; vector `125`; chunk `3`.

> ===== PAGE 9 ===== GIDEON v. WAINWRIGHT. 335 Opinion of the Court. counsel is of this fundamental character." Powell v. Ala- bama, 287 U. S. 45, 68 (1932). While the Court at the close of its Powell opinion did by its language, as this Court frequently does, limit its holding to the particular facts and circumstances of that case, its conclusions about the fundamental nature of the right to counsel are unmis- takable. Several years later, in 1936, the Court reem- phasized what it had said about the fundamental nature of the right to counsel in this language: "We concluded that certain fundamental rights, safeguarded by the first eight amendments against federal action, were also …

**Rank 5 — similarity 0.460997 — not relevant**

Source: `Gideon v. Wainwright` / `gideon_v_wainwright.pdf`; pages 16-18; vector `128`; chunk `6`.

> ===== PAGE 16 ===== 350 OCTOBER TERM, 1962. HARLAN, J., concurring. 372 U. S. the trial as a necessary requisite of due process of law. It is evident that these limiting facts were not added to the opinion as an afterthought; they were repeatedly empha- sized, see 287 U. S., at 52, 57-58, 71, and were clearly regarded as important to the result. Thus when this Court, a decade later, decided Betts v. Brady, it did no more than to admit of the possible- exist- ence of special circumstances in noncapital as well as capital trials, while at the same time insisting that such circumstances be shown in order to establish a denial of due process. The right to appointed counsel had been recognized …


## All configurations struggle

### DRE-04 — Dred Scott v. Sandford

**Question:** Why did the Court conclude that Congress could not prohibit slaveholders from taking enslaved people into the federal territory at issue?

**Expected pages:** 3-4

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 Miss; 1500/200 Miss.

**Selection evidence:** No fixed-size configuration retrieved a relevant result within the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.582107 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 144-145; vector `142`; chunk `142`.

> ===== PAGE 144 ===== 5686 SUPREME COURT. M. JusTIOE MCLEAN.] Dred Scott v. Sandford. itors; they descend to heirs, are taxed, and in the South they are a subject of commerce. In the case. of Rankin v. Lydia, (2 A. K. Marshall's Rep.,) Judgl Mills, speaking for the Court of Appeals of Kentucky, says: "In deciding the question, (of slavery,) we disclaim the iiafluence of the general principles of liberty, which we all ad- mire, and conceive it ougbt to be decided by the law as it is, and not as it ought 'to be. Slavery is sanctioned by, the laws of this.State, and the right to hold slaves under our municipal regulations is unquestionable. But we view this as a right existing by positive law …

**Rank 2 — similarity 0.581041 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 228-229; vector `226`; chunk `226`.

> ===== PAGE 228 ===== 620 SUPREME COURT. MR. JUSTICE CURTIS.] . )red Ecoa vr. Sandfor& One is, that though Congress can make a regulation pro- hibiting slavery in a Territory, they cannot make a regulation allowing it; another is, that it can neither be established nor pro- hibited by Congress, but that the people of a Territory, when organized by Congress, can establish or prohibit slavery; while the third is, that the Constitution itself secures to every citizen who holds slaves, under the laws of any State, the indefeasible right to carry them into any Territory, and there hold them as property. No particular clause of the Constitution has been referred to at the bar in support of either …

**Rank 3 — similarity 0.578102 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 72-73; vector `70`; chunk `70`.

> ===== PAGE 72 ===== ki. Jusmcu NELSON.) Dred Scott v. Sandford. "The ordinance in question, he observes, if still in force, could have no more operation than the laws of Ohio in the State of Kentucky, and could not influence the decision upon the rights of the -master or the slaves in that State." This view, thus aiuthoritatively declared, furnishes a conclu- sive answer to the distinction attempted to be set up between the extra-territorial eflect of a State law and the act of Congress in question. It must be admitted. that Congress possesses no power to regulate or abolish slavery within the States; and that, if this act had attempted any such legislation, it would have been a nullity. …

**Rank 4 — similarity 0.576254 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 125-126; vector `123`; chunk `123`.

> ===== PAGE 125 ===== DECEMBER TERM, 1856. 517 Dred&otu v. Sandford. [31. JU8TICZ CAXP.t,. sional legislation or interference. The question then arises, whether Congress, which can exercise no jurisdiction over the relations of master and slave withiii the limits of the Union, and is bound to recogmise and respect the rights and relations that validly exist under the Constitutions and laws of the States, can deny the exercise of those rights, and prohibit the continuance-of.those relations, within the Territories. And the citation of State staftutes -prohibiting the immigra- tion of slaves, and of the decisions of State courts enforcing the-forfeiture of the master's title in accordance …

**Rank 5 — similarity 0.574369 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 235-236; vector `233`; chunk `233`.

> ===== PAGE 235 ===== DECEMBER TERM, 1856. Dred SoU v. Sandford. (lh. 3us'cr Cu. the great charter. It existed in every political community in America in 1787,, when- the ordinance prohibiting slavery north and west of the Ohio was passed. And if a prohibition of slavery in a Territory in 1820 violated this principle of Mfagna (JkarA the ordinance of 1787 also violated it;'and what power had, I do not say the Congress of the- Confederation alone, but ,the Legislature of Vir'na, or the Legislature of any or all the States of. the Confederacy,. to consent to such a violation?.-, The people of the States had conferred no such power. I think I may at least say, if the Congess did then violate …


#### 1500/200 Top-5

**Rank 1 — similarity 0.595997 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 234-236; vector `118`; chunk `118`.

> ===== PAGE 234 ===== SUPREME COURT. ML. JUSTICE GUETIL.] Dred Scot v. Sanford. slavery which existed in the particular State from which eabh slave last came, what an anomaly is this? Where -else can we find, -under the law of any civilized country; the power to introduce and permanently continue diverse systems of foreign municipal law, for holding persons in slavery? I say, not x erely to introduce, but permanently to continue, these anom- alies. For the offspring of the female must be governed by the foreign municipal laws to which the mother was subject; and when any slave is sold or passes by succession -on the death of the owner, there must pass with him, by a species of subrogation, …

**Rank 2 — similarity 0.579452 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 224-226; vector `113`; chunk `113`.

> ===== PAGE 224 ===== 616 SUPREME COURT. 'M. JUSTICE CURTIS.] Dred Scou v. Sandford. will respecting it, manifested in the Constitution, can be snbject to no restriction. The purposes and objects of the clause were the enactment of laws concerning the disposal of the public lands, and the temporary government of the settlers thereon until new States should be formed. It will not be questioned that, when the Constitution of the United States was framed and adopted, the allowance and the prohibition of negro slavery were recognised subjects of municipal legisla- tion; every State lad in some measure acted thereon; and the only legislative act concerning the territory-the ordinance of 1787, …

**Rank 3 — similarity 0.572917 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 124-126; vector `63`; chunk `63`.

> ===== PAGE 124 ===== 516 SUPREME COURT. H&. TUSTIOX CAMPBELL.) Dred ZcoU v. Sarford. Eaired. A proscription, therefore, of the Constitution and of one or more States, determining property, on the part of the Federal Government, by which the stability of its social s stem may be endangered, is plainly repugnant to the con- ditions on which the Federal Constitution was adopted, or which that Government was designed. to accomplish. Each of the States surrendered its powers of war and negotiation, to raise armies and to support a navy, and all of these powers are sometimes required to preserve a State from disaster and ruin. The Federal Government was 'constituted to exercise these powers for …

**Rank 4 — similarity 0.571091 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 228-230; vector `115`; chunk `115`.

> ===== PAGE 228 ===== 620 SUPREME COURT. MR. JUSTICE CURTIS.] . )red Ecoa vr. Sandfor& One is, that though Congress can make a regulation pro- hibiting slavery in a Territory, they cannot make a regulation allowing it; another is, that it can neither be established nor pro- hibited by Congress, but that the people of a Territory, when organized by Congress, can establish or prohibit slavery; while the third is, that the Constitution itself secures to every citizen who holds slaves, under the laws of any State, the indefeasible right to carry them into any Territory, and there hold them as property. No particular clause of the Constitution has been referred to at the bar in support of either …

**Rank 5 — similarity 0.570608 — not relevant**

Source: `Dred Scott v. Sandford` / `dred_scott_v_sandford.pdf`; pages 150-152; vector `76`; chunk `76`.

> ===== PAGE 150 ===== 642 SUPREME COURT. Mu. JUSTICE McLsAN.] Dred SoU v. Sandford. But, if it be admitted that the word territory as used means land, and nothing but land, the power of Congress to organize a temporary Government is clear. It has power to make all needful regulations -respecting the public lands, and the extent of those "needful regulations" depends upon the direction of Congress, where the means are appropriate to the end, and do not conflict with-any of the prohibitions of the Constitution. If atemporary Government be deemed needful, necessary, requisite, or is wanted, Congress has power to establish it. 3his court says, in M4cCulloch v. The State of Maryland, (4 Wheat., …


### NYT-02 — New York Times Co. v. United States

**Question:** Why did the Court refuse to sustain the government's attempt to stop publication?

**Expected pages:** 1-2

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 Miss; 1500/200 Miss.

**Selection evidence:** No fixed-size configuration retrieved a relevant result within the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.649284 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 19-21; vector `347`; chunk `9`.

> ===== PAGE 19 ===== NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an …

**Rank 2 — similarity 0.628355 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 37-39; vector `356`; chunk `18`.

> ===== PAGE 37 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BURGER, C. J., dissenting setting of these cases reflects our universal abhorrence of prior restraint. But prompt judicial action does not mean unjudicial haste. Here, moreover, the frenetic haste is due in large part to the manner in which the Times proceeded from the date it obtained the purloined documents. It seems reasonably clear now that the haste precluded reasonable and deliberate judicial treatment of these cases and was not warranted. The precipitate action of this Court aborting trials not yet completed is not the kind of judicial conduct that ought to attend the disposition of a great issue. The newspapers make a …

**Rank 3 — similarity 0.625998 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 13-15; vector `344`; chunk `6`.

> ===== PAGE 13 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BRENNAN, J., concurring orders to block the publication of material sought to be suppressed by the Government. So far as I can deter- mine, never before has the United States sought to enjoin a newspaper from publishing information in its posses- sion. The relative novelty of the questions presented, the necessary haste with which decisions were reached, the magnitude of the interests asserted, and the fact that all the parties have concentrated their arguments upon the question whether permanent restraints were proper may have justified at least some of the restraints hereto- fore imposed in these cases. Certainly it is difficult …

**Rank 4 — similarity 0.608656 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 47-49; vector `361`; chunk `23`.

> ===== PAGE 47 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BLACKMUN, J., dissenting restraints on publication. I cannot believe that the doc- trine prohibiting prior restraints reaches to the point of preventing courts from maintaining the status quo long enough to act responsibly in matters of such national importance as those involved here. MR. JUSTICE BLACKMUN, dissenting. I join MR. JUSTICE HARLAN in his dissent. I also am in substantial accord with much that MR. JUSTICE WHITE says, by way of admonition, in the latter part of his opinion. At this point the focus is on only the comparatively few documents specified by the Government as critical. So far as the other material-vast in …

**Rank 5 — similarity 0.596513 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 5-7; vector `340`; chunk `2`.

> ===== PAGE 5 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BLACK, J., concurring that they were, wrote in language they earnestly believed could never be misunderstood: "Congress shall make no law ... abridging the freedom ... of the press . .. ." Both the history and language of the First Amendment support the view that the press must be left free to publish news, whatever the source, without censorship, injunctions, or prior restraints. In the First Amendment the Founding Fathers gave the free press the protection it must have to fulfill its essential role in our democracy. The press was to serve the governed, not the governors. The Government's power to censor the press was abolished so …


#### 1500/200 Top-5

**Rank 1 — similarity 0.644623 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 19-22; vector `204`; chunk `6`.

> ===== PAGE 19 ===== NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an …

**Rank 2 — similarity 0.616361 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 36-39; vector `211`; chunk `13`.

> ===== PAGE 36 ===== OCTOBER TERM, 1970 BURGER, C. J., dissenting 403 U. S. be affirmed and the judgment of the United States Court of Appeals for the Second Circuit should be reversed in- sofar as it remands the case for further hearings. MR. CHIEF JUSTICE BURGER, dissenting. So clear are the constitutional limitations on prior restraint against expression, that from the time of Near v. Minnesota, 283 U. S. 697 (1931), until recently in Organization for a Better Austin v. Keefe, 402 U. S. 415 (1971), we have had little occasion to be concerned with cases involving prior restraints against news reporting on matters of public interest. There is, therefore, little variation among the members …

**Rank 3 — similarity 0.588763 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 7-10; vector `200`; chunk `2`.

> ===== PAGE 7 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BLACK, J., concurring post, at 721-722. To find that the President has "inher- ent power" to halt the publication of news by resort to the courts would wipe out the First Amendment and destroy the fundamental liberty and security of the very people the Government hopes to make "secure." No one can read the history of the adoption of the First Amendment without being convinced beyond any doubt that it was injunctions like those sought here that Madison and his collaborators intended to outlaw in this Nation for all time. The word "security" is a broad, vague generality whose contours should not be invoked to abrogate the funda- …

**Rank 4 — similarity 0.585939 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 13-16; vector `202`; chunk `4`.

> ===== PAGE 13 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BRENNAN, J., concurring orders to block the publication of material sought to be suppressed by the Government. So far as I can deter- mine, never before has the United States sought to enjoin a newspaper from publishing information in its posses- sion. The relative novelty of the questions presented, the necessary haste with which decisions were reached, the magnitude of the interests asserted, and the fact that all the parties have concentrated their arguments upon the question whether permanent restraints were proper may have justified at least some of the restraints hereto- fore imposed in these cases. Certainly it is difficult …

**Rank 5 — similarity 0.583773 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 33-36; vector `210`; chunk `12`.

> ===== PAGE 33 ===== NEW YORK TIMES CO. v. UNITED STATES 713 MARSHALL, J., concurring At least one of the many statutes in this area seems rel- evant to these cases. Congress has provided in 18 U. S. C. § 793 (e) that whoever "having unauthorized possession of, access to, or control over any document, writing, code book, signal book ... or note relating to the national defense, or information relating to the national defense which information the possessor has reason to believe could be used to the injury of the United States or to the advantage of any foreign nation, willfully communicates, delivers, transmits... the same to any person not entitled to receive it, or willfully retains the …


### NYT-03 — New York Times Co. v. United States

**Question:** What burden does the government face when seeking a prior restraint on publication?

**Expected pages:** 2

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 Miss; 1500/200 Miss.

**Selection evidence:** No fixed-size configuration retrieved a relevant result within the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.590951 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 13-15; vector `344`; chunk `6`.

> ===== PAGE 13 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BRENNAN, J., concurring orders to block the publication of material sought to be suppressed by the Government. So far as I can deter- mine, never before has the United States sought to enjoin a newspaper from publishing information in its posses- sion. The relative novelty of the questions presented, the necessary haste with which decisions were reached, the magnitude of the interests asserted, and the fact that all the parties have concentrated their arguments upon the question whether permanent restraints were proper may have justified at least some of the restraints hereto- fore imposed in these cases. Certainly it is difficult …

**Rank 2 — similarity 0.584956 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 19-21; vector `347`; chunk `9`.

> ===== PAGE 19 ===== NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an …

**Rank 3 — similarity 0.550333 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 21-23; vector `348`; chunk `10`.

> ===== PAGE 21 ===== NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring properly not discussed in today's opinions. Moreover, because the material poses substantial dangers to national interests and because of the hazards of criminal sanctions, a responsible press may choose never to publish the more sensitive materials. To sustain the Government in these cases would start the courts down a long and hazardous road that I am not willing to travel, at least without congressional guidance and direction. It is not easy to reject the proposition urged by the United States and to deny relief on its good-faith claims in these cases that publication will work serious damage to the …

**Rank 4 — similarity 0.535821 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 37-39; vector `356`; chunk `18`.

> ===== PAGE 37 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BURGER, C. J., dissenting setting of these cases reflects our universal abhorrence of prior restraint. But prompt judicial action does not mean unjudicial haste. Here, moreover, the frenetic haste is due in large part to the manner in which the Times proceeded from the date it obtained the purloined documents. It seems reasonably clear now that the haste precluded reasonable and deliberate judicial treatment of these cases and was not warranted. The precipitate action of this Court aborting trials not yet completed is not the kind of judicial conduct that ought to attend the disposition of a great issue. The newspapers make a …

**Rank 5 — similarity 0.529238 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 41-43; vector `358`; chunk `20`.

> ===== PAGE 41 ===== NEW YORK TIMES CO. v. UNITED STATES 713 HARLAN, J., dissenting real importance in shaping the law of the future, but because of some accident of immediate over- whelming interest which appeals to the feelings and distorts the judgment. These immediate interests exercise a kind of hydraulic pressure which makes what previously was clear seem doubtful, and before which even well settled principles of law will bend." With all respect, I consider that the Court has been almost irresponsibly feverish in dealing with these cases. Both the Court of Appeals for the Second Circuit and the Court of Appeals for the District of Columbia Circuit rendered judgment on June 23. The New …


#### 1500/200 Top-5

**Rank 1 — similarity 0.602738 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 19-22; vector `204`; chunk `6`.

> ===== PAGE 19 ===== NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the First Amendment permit an injunction against pub- lishing information about government plans or opera- tions.' Nor, after examining the materials the Govern- ment characterizes as the most sensitive and destructive, can I deny that revelation of these documents will do substantial damage to public interests. Indeed, I am confident that their disclosure will have that result. But I nevertheless agree that the United States has not satis- fied the very heavy burden that it must meet to warrant an …

**Rank 2 — similarity 0.549529 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 13-16; vector `202`; chunk `4`.

> ===== PAGE 13 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BRENNAN, J., concurring orders to block the publication of material sought to be suppressed by the Government. So far as I can deter- mine, never before has the United States sought to enjoin a newspaper from publishing information in its posses- sion. The relative novelty of the questions presented, the necessary haste with which decisions were reached, the magnitude of the interests asserted, and the fact that all the parties have concentrated their arguments upon the question whether permanent restraints were proper may have justified at least some of the restraints hereto- fore imposed in these cases. Certainly it is difficult …

**Rank 3 — similarity 0.547665 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 36-39; vector `211`; chunk `13`.

> ===== PAGE 36 ===== OCTOBER TERM, 1970 BURGER, C. J., dissenting 403 U. S. be affirmed and the judgment of the United States Court of Appeals for the Second Circuit should be reversed in- sofar as it remands the case for further hearings. MR. CHIEF JUSTICE BURGER, dissenting. So clear are the constitutional limitations on prior restraint against expression, that from the time of Near v. Minnesota, 283 U. S. 697 (1931), until recently in Organization for a Better Austin v. Keefe, 402 U. S. 415 (1971), we have had little occasion to be concerned with cases involving prior restraints against news reporting on matters of public interest. There is, therefore, little variation among the members …

**Rank 4 — similarity 0.510975 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 7-10; vector `200`; chunk `2`.

> ===== PAGE 7 ===== NEW YORK TIMES CO. v. UNITED STATES 713 BLACK, J., concurring post, at 721-722. To find that the President has "inher- ent power" to halt the publication of news by resort to the courts would wipe out the First Amendment and destroy the fundamental liberty and security of the very people the Government hopes to make "secure." No one can read the history of the adoption of the First Amendment without being convinced beyond any doubt that it was injunctions like those sought here that Madison and his collaborators intended to outlaw in this Nation for all time. The word "security" is a broad, vague generality whose contours should not be invoked to abrogate the funda- …

**Rank 5 — similarity 0.501815 — not relevant**

Source: `New York Times Co. v. United States` / `new_york_times_co_v_united_states.pdf`; pages 22-24; vector `205`; chunk `7`.

> ===== PAGE 22 ===== OCTOBER TERM, 1970 WHITE, J., concurring 403 U. S. 1917, Congress eliminated from the bill a provision that would have given the President broad powers in time of war to proscribe, under threat of criminal penalty, the publication of various categories of information related to the national defense.3 Congress at that time was un- willing to clothe the President with such far-reaching powers to monitor the press, and those opposed to this part of the legislation assumed that a necessary con- comitant of such power was the power to "filter out the news to the people through some man." 55 Cong. Rec. 2008 (remarks of Sen. Ashurst). However, these same members of Congress …


### OBE-01 — Obergefell v. Hodges

**Question:** What two constitutional questions concerning same-sex marriage did the Supreme Court agree to decide?

**Expected pages:** 12-13

**First relevant ranks:** 600/100 Miss; 900/150 Miss; 1200/200 Miss; 1500/200 Miss.

**Selection evidence:** No fixed-size configuration retrieved a relevant result within the Top-5.

#### 1200/200 Top-5

**Rank 1 — similarity 0.634330 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 35-37; vector `386`; chunk `23`.

> ===== PAGE 35 ===== 678 OBERGEFELL v. HODGES Opinion of the Court nalizing same-sex intimacy. See 478 U. S., at 190–195. That approach might have been viewed as a cautious en- dorsement of the democratic process, which had only just begun to consider the rights of gays and lesbians. Yet, in effect, Bowers upheld state action that denied gays and lesbi- ans a fundamental right and caused them pain and humilia- tion. As evidenced by the dissents in that case, the facts and principles necessary to a correct holding were known to the Bowers Court. See id., at 199 (Blackmun, J., joined by Brennan, Marshall, and Stevens, JJ., dissenting); id., at 214 (Stevens, J., joined by Brennan and Marshall, …

**Rank 2 — similarity 0.630623 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 37-39; vector `387`; chunk `24`.

> ===== PAGE 37 ===== 680 OBERGEFELL v. HODGES Opinion of the Court ples that are so fulflling and so central to their lives and faiths, and to their own deep aspirations to continue the fam- ily structure they have long revered. The same is true of those who oppose same-sex marriage for other reasons. In turn, those who believe allowing same-sex marriage is proper or indeed essential, whether as a matter of religious conviction or secular belief, may engage those who disagree with their view in an open and searching debate. The Con- stitution, however, does not permit the State to bar same- sex couples from marriage on the same terms as accorded to couples of the opposite sex. V These cases …

**Rank 3 — similarity 0.610639 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 1-2; vector `363`; chunk `0`.

> ===== PAGE 1 ===== 644 OCTOBER TERM, 2014 Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men whose same-sex partners are deceased, fled suits in Fed- eral District Courts in their home States, claiming that respondent state offcials violate the Fourteenth Amendment by denying them the right to marry or to have marriages lawfully performed in another State given full recognition. Each District …

**Rank 4 — similarity 0.609878 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 42-44; vector `391`; chunk `28`.

> ===== PAGE 42 ===== 685 Cite as: 576 U. S. 644 (2015) Appendix B to opinion of the Court Li v. State, 338 Ore. 376, 110 P. 3d 91 (2005) Cote-Whitacre v. Department of Public Health, 446 Mass. 350, 844 N. E. 2d 623 (2006) Lewis v. Harris, 188 N. J. 415, 908 A. 2d 196 (2006) Andersen v. King County, 158 Wash. 2d 1, 138 P. 3d 963 (2006) Hernandez v. Robles, 7 N. Y . 3d 338, 855 N. E. 2d 1 (2006) Conaway v. Deane, 401 Md. 219, 932 A. 2d 571 (2007) In re Marriage Cases, 43 Cal. 4th 757, 183 P. 3d 384 (2008) Kerrigan v. Commissioner of Public Health, 289 Conn. 135, 957 A. 2d 407 (2008) Strauss v. Horton, 46 Cal. 4th 364, 207 P. 3d 48 (2009) Varnum v. Brien, 763 N. W. 2d 862 (Iowa 2009) Griego v. …

**Rank 5 — similarity 0.600879 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 33-35; vector `385`; chunk `22`.

> ===== PAGE 33 ===== 676 OBERGEFELL v. HODGES Opinion of the Court same-sex couples from civil marriage on the same terms and conditions as opposite-sex couples. IV There may be an initial inclination in these cases to pro- ceed with caution—to await further legislation, litigation, and debate. The respondents warn there has been insuff- cient democratic discourse before deciding an issue so basic as the defnition of marriage. In its ruling on the cases now before this Court, the majority opinion for the Court of Ap- peals made a cogent argument that it would be appropriate for the respondents' States to await further public discussion and political measures before licensing same-sex …


#### 1500/200 Top-5

**Rank 1 — similarity 0.632290 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 35-38; vector `235`; chunk `18`.

> ===== PAGE 35 ===== 678 OBERGEFELL v. HODGES Opinion of the Court nalizing same-sex intimacy. See 478 U. S., at 190–195. That approach might have been viewed as a cautious en- dorsement of the democratic process, which had only just begun to consider the rights of gays and lesbians. Yet, in effect, Bowers upheld state action that denied gays and lesbi- ans a fundamental right and caused them pain and humilia- tion. As evidenced by the dissents in that case, the facts and principles necessary to a correct holding were known to the Bowers Court. See id., at 199 (Blackmun, J., joined by Brennan, Marshall, and Stevens, JJ., dissenting); id., at 214 (Stevens, J., joined by Brennan and Marshall, …

**Rank 2 — similarity 0.626666 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 1-3; vector `217`; chunk `0`.

> ===== PAGE 1 ===== 644 OCTOBER TERM, 2014 Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men whose same-sex partners are deceased, fled suits in Fed- eral District Courts in their home States, claiming that respondent state offcials violate the Fourteenth Amendment by denying them the right to marry or to have marriages lawfully performed in another State given full recognition. Each District …

**Rank 3 — similarity 0.609878 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 42-44; vector `239`; chunk `22`.

> ===== PAGE 42 ===== 685 Cite as: 576 U. S. 644 (2015) Appendix B to opinion of the Court Li v. State, 338 Ore. 376, 110 P. 3d 91 (2005) Cote-Whitacre v. Department of Public Health, 446 Mass. 350, 844 N. E. 2d 623 (2006) Lewis v. Harris, 188 N. J. 415, 908 A. 2d 196 (2006) Andersen v. King County, 158 Wash. 2d 1, 138 P. 3d 963 (2006) Hernandez v. Robles, 7 N. Y . 3d 338, 855 N. E. 2d 1 (2006) Conaway v. Deane, 401 Md. 219, 932 A. 2d 571 (2007) In re Marriage Cases, 43 Cal. 4th 757, 183 P. 3d 384 (2008) Kerrigan v. Commissioner of Public Health, 289 Conn. 135, 957 A. 2d 407 (2008) Strauss v. Horton, 46 Cal. 4th 364, 207 P. 3d 48 (2009) Varnum v. Brien, 763 N. W. 2d 862 (Iowa 2009) Griego v. …

**Rank 4 — similarity 0.603382 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 96-99; vector `263`; chunk `46`.

> ===== PAGE 96 ===== 739 Cite as: 576 U. S. 644 (2015) Alito, J., dissenting Adherents to different schools of philosophy use different terms to explain why society should formalize marriage and attach special benefts and obligations to persons who marry. Here, the States defending their adherence to the traditional understanding of marriage have explained their position using the pragmatic vocabulary that characterizes most American political discourse. Their basic argument is that States formalize and promote marriage, unlike other fulfll- ing human relationships, in order to encourage potentially procreative conduct to take place within a lasting unit that has long been thought to …

**Rank 5 — similarity 0.598917 — not relevant**

Source: `Obergefell v. Hodges` / `obergefell_v_hodges.pdf`; pages 38-40; vector `236`; chunk `19`.

> ===== PAGE 38 ===== 681 Cite as: 576 U. S. 644 (2015) Appendix A to opinion of the Court recognize those marriages performed elsewhere are under- mined. See Tr. of Oral Arg. on Question 2, p. 44. The Court, in this decision, holds same-sex couples may exercise the fundamental right to marry in all States. It follows that the Court also must hold—and it now does hold—that there is no lawful basis for a State to refuse to recognize a law- ful same-sex marriage performed in another State on the ground of its same-sex character. * * * No union is more profound than marriage, for it embodies the highest ideals of love, fdelity, devotion, sacrifce, and family. In forming a marital union, two …

## Limitations

- The report shows the stored Top-5 only. It cannot determine where a relevant chunk ranked below five.
- Similarity scores are comparable within a configuration's ranking, but chunk boundaries and candidate sets differ across configurations.
- Excerpts collapse extraction whitespace and are truncated for manual inspection; the structured source records remain unchanged.
- Selection reasons describe rank evidence only. Determining why a chunk succeeded or failed requires human review of the included excerpts.
