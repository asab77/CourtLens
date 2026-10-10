# CourtLens Phase 4A: Structure-Aware Parsing Preview

This is a deterministic local parsing preview for human review. It does not contain final chunks and makes no retrieval-performance claim.

## Parser rules

- **Hard major-component boundaries:** the first standalone `Syllabus` label, standalone `PER CURIAM`, an explicit delivery of the opinion of the Court, explicit authored concurrence/dissent headings, and medium-confidence standalone justice attributions.
- **Case identity:** when a confidently detected opinion occurs before a later caption containing every expected party-name anchor, the pre-caption text is preserved as `foreign` and cannot inherit the metadata case's opinion type.
- **Ignored as hard boundaries:** repeated reporter headers, citations, and ordinary prose mentioning concurrences or dissents.
- **Sections:** standalone Roman numerals or Roman numerals followed by a short predominantly uppercase title. Sections are preferred boundaries for a future phase, not opinion boundaries.
- **Sentences:** terminal punctuation after protecting common legal abbreviations and `U. S.` reporter citations. Long segments are reported because OCR and citations still defeat the heuristic.
- **Text preservation:** metadata and artificial page-marker lines are excluded. All page text is retained in order; coverage is checked after whitespace-only canonicalization.

## Corpus summary

| Case | Pages | Tokens | Major units | Opinion boundaries | Sections | Unknown units | Ambiguous candidates |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dred Scott v. Sandford | 241 | 150,161 | 10 | 10 | 3 | 1 | 23 |
| Gideon v. Wainwright | 18 | 8,542 | 6 | 5 | 2 | 1 | 3 |
| Marbury v. Madison | 44 | 25,701 | 2 | 1 | 0 | 1 | 5 |
| Miranda v. Arizona | 110 | 52,588 | 5 | 4 | 12 | 1 | 24 |
| New York Times Co. v. United States | 51 | 22,034 | 12 | 11 | 2 | 1 | 11 |
| Obergefell v. Hodges | 99 | 50,421 | 7 | 6 | 18 | 1 | 35 |
| Plessy v. Ferguson | 28 | 13,846 | 4 | 3 | 0 | 1 | 13 |
| Tinker v. Des Moines School Dist. | 24 | 10,852 | 7 | 6 | 2 | 1 | 2 |

## Per-case structural preview

### Dred Scott v. Sandford

Pages: **241** · Tokens: **150,161** · Major units: **10** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | foreign | — | 1–1 | 200 | low | — | 0 |
| 1 | unknown | — | 1–7 | 4,851 | high | DRED SCOTT, PLAINTIFF IN ERROR, v. JomT F. A. SANDFORD. | 3 |
| 2 | majority | Tane | 7–62 | 34,863 | high | Mr. Chief Justice TANE delivered the opinion of the court. . t | 0 |
| 3 | concurrence | Wayne | 62–65 | 1,683 | medium | Mr. Justice WAYNE. | 0 |
| 4 | other | Lnelson | 65–77 | 8,020 | medium | Mr. Justice lNELSON. | 0 |
| 5 | concurrence | Grier | 77–101 | 15,695 | medium | Mr. Justice GRIER. | 0 |
| 6 | concurrence | Campbell | 101–126 | 16,816 | medium | Mr. Justice CAMPBELL. | 0 |
| 7 | other | Oatron | 126–137 | 7,019 | medium | Mr. Justice OATRON. | 0 |
| 8 | dissent | Mclean | 137–172 | 23,244 | high | Mr. Justice McLEAN dissenting. | 0 |
| 9 | dissent | Curtis | 172–241 | 46,128 | high | Mr. Justice CURTIS dissenting. | 0 |

Detected types: concurrence, dissent, foreign, majority, other, unknown. Detected authors: Tane, Wayne, Lnelson, Grier, Campbell, Oatron, Mclean, Curtis. Sentences over 200 tokens: 18. Repeated reporter headers ignored: 4.

#### Priority review note

A caption-identity conflict rule now preserves the opening Sturgis/Honold material as foreign source text and begins Dred Scott front matter at the `DRED SCOTT ... v. ... SANDFORD` caption. The Taney boundary and both express dissents are strong; the intervening standalone justice attributions are intentionally medium confidence, and several raw author names remain visibly OCR-corrupted.

#### Boundary inspection details

**Unit 0 — foreign / author unknown / pp. 1–1**

Trigger: `leading unassigned text` (low; source text before the matching case caption; preserved but not attributed to the metadata case).

Sections: none.

Beginning: “DECEMBER TERM, 1856. 393 Dred ScoU v. Sandford. LATHROP L. STURGIS, PLAINTIFF IN ERROR, V. CHRISTIAN R1ONOLD. The decision in the preceding case again affirmed. Tnis, like the preceding case, of which it constituted a branch, was brought up, by writ of error, from the Circuit Court of the United States for the eastern district of Louisiana. It was ”

Ending: “ixteenths of the ship from Sturgis, and four-sixteenths from Bulkley. The two cases proceeded through the courts pari yassu, and were argued together in this court. Mr. Justice CURTIS delivered the opinion of the court. This case depends on the same facts and principles as the preceding case, and the judgment of the Circuit Court therein is aErmed.”

**Unit 1 — unknown / author unknown / pp. 1–7**

Trigger: `DRED SCOTT, PLAINTIFF IN ERROR, v. JomT F. A. SANDFORD.` (high; caption contains all expected case-party anchors after foreign opinion material).

Sections: I (p. 1), II (p. 2), V (p. 4).

Beginning: “DRED SCOTT, PLAINTIFF IN ERROR, v. JomT F. A. SANDFORD. I. 1. Upon a writ of error to a Circuit Court of the United States, the transcript of the record of all the proceedings in the case is brought before this court, and is open to its inspection and revision. 2. When a plea to the jurisdiction, in abatement, is overruled by the court upon demurre”

Ending: “. Joihnson for the defendant in error. The reporter regrets that want of room will not allow him to give the'arguments of counsel; but he regrets it the less, be- cause the subject is thoroughly examined in the opinion of the court, the opinions of the concurring judges, and the opin- ions of the judges who dissented from the judgment of the court.”

**Unit 2 — majority / Tane / pp. 7–62**

Trigger: `Mr. Chief Justice TANE delivered the opinion of the court. . t` (high; explicit delivery of the opinion of the Court).

Sections: none.

Beginning: “Mr. Chief Justice TANE delivered the opinion of the court. . t This case has been twice argued. After the argument at the last term, differences of opinion were found to exist among. the members of the court; and as the questions in controversy are of the highest importance, .and the court -was at that time much pressed by the ordinaiy business of ”

Ending: “ssouri, in the sense in which that word is used in the Constitution; and that the Circuit Court of the United States, for that reason, had no jurisdiction in the case, and could give no judgment in it. Its judgment for the de- fendant must, consequently, be reversed, anc a mandate issued, directing the suit to be dismissed for want of jurisdiction.”

**Unit 3 — concurrence / Wayne / pp. 62–65**

Trigger: `Mr. Justice WAYNE.` (medium; standalone justice attribution followed by an express statement joining the Court).

Sections: none.

Beginning: “Mr. Justice WAYNE. Concurring as I do entirely in the opinion of the court, as it has been written and read by the Chief Justice-without any qualification of its reasoning or its conclusions-I shall neither read nor file an opinion of my own in this case, which I prepared when I supposed it might be necessary and proper for me to do so. The opinion”

Ending: “on of the court upon the point of jurisdiction, and do not allow my- self to doubt that the error of a contrary bonclusion will be fully understood by all who shall read the argument of the Chief Justice. I have already said that the opinion of the court has my unqualified assent. DECEMBER TERM, 1856. 457 Dred coft v. Sandford. [iR. JUSTICE NELSON.”

**Unit 4 — other / Lnelson / pp. 65–77**

Trigger: `Mr. Justice lNELSON.` (medium; standalone justice attribution between opinion text).

Sections: none.

Beginning: “Mr. Justice lNELSON. I shall proceed to state the grouinds upon which I have arrived at the conclusion, that the judgment of the court below should be affirmed. The suit was brought in the court below by the plaintiff for the purpose of asserting his freedom, and that of Harriet, his wife, and two children. The defendant plead, in abatement to the ”

Ending: “the one in hand, and turns upon the rights and privileges secured to a common-citizen of the republic under the Constitution of the United States. When that question arises, we shall be prepared to decide it. DECEMBER TERM, 1856. 469 Dred &ott v. Sandford. [MV. JUSTC- GimR. Our conclusion is, that the judgment of the court below should be affirmed.”

**Unit 5 — concurrence / Grier / pp. 77–101**

Trigger: `Mr. Justice GRIER.` (medium; standalone justice attribution followed by an express statement joining the Court).

Sections: none.

Beginning: “Mr. Justice GRIER. I concur in the opinion delivered by Mr. Justice Nelson on the questions discussed by him. I also concur with the opinion of the court as delivered by the Chief Justice, that th6 act of Congress of 6th March, 1820, is unconstitutional and void; and that, assuming the facts as stated in the opinion, the plaintiff cannot sue as a c”

Ending: “ 2th 1819, on the u- ject of Ithe Missouri Compromise. DECEMBER TERM, 1856. 498 Dred Scott v. Sandford. [MR. JusTIcE CAMPBELL. been no plea, either of a former judgment or of autre actionyendent, it wag thought that the fact of a prior decision, how- ever conclusive it might have been if regularly pleaded, could not be incidentally taken into view.”

**Unit 6 — concurrence / Campbell / pp. 101–126**

Trigger: `Mr. Justice CAMPBELL.` (medium; standalone justice attribution followed by an express statement joining the Court).

Sections: none.

Beginning: “Mr. Justice CAMPBELL. I concur in the judgment pronounced by the Chief Justice, but the importance of the cause, the expectation and interest it has awakened, and the responsibility involved in its deter- mination, induce me to file a separate opinion. The case shows that the plaintiff, in the year 1834, was a negro slave in Missouri, the property ”

Ending: “think it a safe conclusion to enforce the lesser disabil- ity imposed by the Constitution of the United States, and leave to the plaintiff all his rights in Missouri. I think the judgment should be affirmed, on the ground that the Circuit Court had no jurisdiction, or that the case should be reversed and. re- manded, that the suit may be dismissed.”

**Unit 7 — other / Oatron / pp. 126–137**

Trigger: `Mr. Justice OATRON.` (medium; standalone justice attribution between opinion text).

Sections: none.

Beginning: “Mr. Justice OATRON. The defendant pleaded to the jurisdiction of the Circuit Court, that the plaintiff was a negro of African blood; the descendant of Africans, -ho had een imported and sold in this country. as slavesi and thus had no capacity as a citizen of Missouri to iniintain a suit in the Circuit Court. The court sustained a demurer to this p”

Ending: “and immunities. On these grounds, I hold the compromise act to have been void; and, consequently, that the plaintiff, Scott, can claim no benefit under it. For the reasons above stated, I concur with my brother Judges that the plaintiff, Scott, is a slave, and was so when this suit was brought. Mr. Justice McLEAN and Mir. Justice CURTIS. dissented.”

**Unit 8 — dissent / Mclean / pp. 137–172**

Trigger: `Mr. Justice McLEAN dissenting.` (high; explicit authored dissent heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “Mr. Justice McLEAN dissenting. This case is before us on a writ of error from the Circuit Court for the digtrict of Missouri. An action of trespass was brought, which charges the cie- fendant with an assault and imprisonment of the plaintiff, and also of Harriet Scott, his .wife, Eliza and Lizzie, -his two chil- dren, on the ground that they were h”

Ending: “, it is a question, as it would seem, within the twenty-fifth section of the judiciary act, where a right to freedom being set up under the -act of .Congress, and the decision being against such right, it may be brought for revilsion before this court,.from the Supreme Court of Missouri. - I think the judgment of the court below-should be reversed.”

**Unit 9 — dissent / Curtis / pp. 172–241**

Trigger: `Mr. Justice CURTIS dissenting.` (high; explicit authored dissent heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “Mr. Justice CURTIS dissenting. "I dissent from the opinion pronounced- by the Chief Justice, ahd from te judgment which the majority of the court think it proper to render in this case. The plaintiff alleged, in his - declaration, that he was a citizen of the State of Missouri, and. that the defendant was a citizen of the State'of.New York. It "is ”

Ending: “ain whether thb judgment otht Circuit Court should stand or be reverspd. I have avoiddd Ao'qtiestion on which the validity of that judg- ment depends. t To-have done either more or less, would have been inconsistent with my views of my duty. In my opinion, the judgment of the Circuit Court should be reversed, andtthe cause remanded for a new trial.”

Ambiguous candidate examples:

- p. 7: `the court, the opinions of the concurring judges, and the opin-`
- p. 15: `In the opinion of the court, the legislation and histories of`
- p. 34: `Department, all concurring together, and leading to the same`
- p. 60: `with the duty of guarding and protecting the owner, in hisrihts.upon these considerations, it is the opinion of the court that`
- p. 62: `Concurring as I do entirely in the opinion of the court, as`
- p. 62: `The opinion of the court meets fully and decides every point`
- p. 63: `from the opinion of the court. A third, Mr. Justice Nelson,`
- p. 64: `I have already said that the opinion of the court has my`

Size diagnostics: units under 200 tokens: none; units over 25,000 tokens: [2, 9].

Boundary risks:

- Possible false positive: Standalone justice attributions without an express opinion type are treated as boundaries at medium confidence.
- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Gideon v. Wainwright

Pages: **18** · Tokens: **8,542** · Major units: **6** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–1 | 10 | low | — | 0 |
| 1 | syllabus | — | 1–2 | 877 | high | Syllabus. | 0 |
| 2 | majority | Black | 2–11 | 4,391 | high | MR. JUSTICE BLACK delivered the oninion of the Court. | 2 |
| 3 | concurrence | Douglas | 11–13 | 835 | medium | MR. JUSTICE DOUGLAS. | 0 |
| 4 | concurrence | Clark | 13–15 | 1,267 | high | MR. JUSTICE CLARK, concurring in the result. | 0 |
| 5 | concurrence | Harlan | 15–18 | 1,618 | high | MR. JUSTICE HARLAN, concurring. | 0 |

Detected types: concurrence, majority, syllabus, unknown. Detected authors: Black, Douglas, Clark, Harlan. Sentences over 200 tokens: 1. Repeated reporter headers ignored: 15.

Ambiguous candidate examples:

- p. 11: `While I join the opinion of the Court, a brief historical`
- p. 12: `U. S. 497, 515-522 (dissenting opinion). That view`
- p. 12: `Justice Brewer, in joining the opinion of the Court, abandoned the`

Size diagnostics: units under 200 tokens: [0]; units over 25,000 tokens: none.

Boundary risks:

- Possible false positive: Standalone justice attributions without an express opinion type are treated as boundaries at medium confidence.
- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Marbury v. Madison

Pages: **44** · Tokens: **25,701** · Major units: **2** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–17 | 11,160 | low | — | 0 |
| 1 | majority | — | 17–44 | 15,604 | high | opinion of the court was delivered by the chief juftice. | 0 |

Detected types: majority, unknown. Detected authors: none. Sentences over 200 tokens: 2. Repeated reporter headers ignored: 2.

Ambiguous candidate examples:

- p. 9: `fider of his anfwers under this opinion of the court.`
- p. 9: `of it. He prayed the. opinion of the court whether he`
- p. 21: `fenate concurring with his nomination, has been made,`
- p. 26: `It is therefore decidedly the opinion of the court, that`
- p. 31: `It is then the opinion of the court,`

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Miranda v. Arizona

Pages: **110** · Tokens: **52,588** · Major units: **5** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–4 | 1,978 | low | — | 0 |
| 1 | majority | Warren | 4–64 | 29,939 | high | MR. CHIEF JUSTICE WARREN delivered the opinion of the Court. | 5 |
| 2 | other | Clark | 64–69 | 2,456 | medium | MR. JbsTM " CLARK, dissenting in Nos. 759, 760, and' 761, and concurring in the result in No. 584. | 2 |
| 3 | dissent | Harlan | 69–91 | 11,493 | high | MR. JUSTICE HARLAN, whom MR. JUSTICE STEWART and MR. JusTIcE WHITE join, dissenting. | 3 |
| 4 | dissent | White | 91–110 | 9,642 | high | MR. JUSTICE WHITE, with whom MR. JUSTICE HARLAN and MR. JusTICE STEWART join, dissenting. | 2 |

Detected types: dissent, majority, other, unknown. Detected authors: Warren, Clark, Harlan, White. Sentences over 200 tokens: 1. Repeated reporter headers ignored: 79.

Ambiguous candidate examples:

- p. 24: `(DOuGLAS, J., dissenting).`
- p. 25: `556, 579, 581-582 (Frank, J., dissenting), rev'd, 353 U. S.`
- p. 31: `(HARLAN, J., dissenting). Cf. Pointer v. Texas, 380`
- p. 35: `448 (1958) (DOUGLAS, J., dissenting).`
- p. 45: `(dissenting opinion)."`
- p. 45: `4 9 In quoting the above, from the dissenting opinion of Mr. Justjse`
- p. 60: `436' Opinion of the Court.`
- p. 64: `dissenting brethren do not go quite far enough. Nor can`

Size diagnostics: units under 200 tokens: none; units over 25,000 tokens: [1].

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### New York Times Co. v. United States

Pages: **51** · Tokens: **22,034** · Major units: **12** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–1 | 9 | low | — | 0 |
| 1 | syllabus | — | 1–2 | 442 | high | Syllabus | 0 |
| 2 | majority | Per Curiam | 2–2 | 343 | high | PER CURIAM. | 0 |
| 3 | concurrence | Black | 2–8 | 2,401 | high | MR. JUSTICE BLACK, with whom MR. JUsTICE DOUGLAS joins, concurring. | 0 |
| 4 | concurrence | Douglas | 8–12 | 2,045 | high | MR. JUSTICE DOUGLAS, with whom MR. JUSTICE BLACK joins, concurring. | 0 |
| 5 | concurrence | Brennan | 12–15 | 1,178 | high | MR. JUSTICE BRENNAN, concurring. | 2 |
| 6 | concurrence | Stewart | 15–18 | 1,636 | high | MR. JUSTICE STEWART, with whom Ma. JUSTICE WHITE joins, concurring. | 0 |
| 7 | concurrence | White | 18–28 | 5,060 | high | MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. | 0 |
| 8 | concurrence | Marshall | 28–36 | 3,575 | high | MR. JUSTICE MARSHALL, concurring. | 0 |
| 9 | dissent | Burger | 36–40 | 1,982 | high | MR. CHIEF JUSTICE BURGER, dissenting. | 0 |
| 10 | dissent | Harlan | 40–47 | 2,928 | high | MR. JUSTICE HARLAN, with whom THE CHIEF JUSTICE and MR. JUSTICE BLACKMUN join, dissenting. | 0 |
| 11 | dissent | Blackmun | 47–51 | 1,858 | high | MR. JUSTICE BLACKMUN, dissenting. | 0 |

Detected types: concurrence, dissent, majority, syllabus, unknown. Detected authors: Per Curiam, Black, Douglas, Brennan, Stewart, White, Marshall, Burger, Harlan, Blackmun. Sentences over 200 tokens: 2. Repeated reporter headers ignored: 49.

#### Priority review note

The parser finds the short per curiam disposition, six separately authored concurrences, and three dissents. All authored splits use explicit headings; 49 repeated reporter headers were ignored rather than treated as new opinions.

#### Boundary inspection details

**Unit 0 — unknown / author unknown / pp. 1–1**

Trigger: `leading unassigned text` (low; text before the first confidently detected major component).

Sections: none.

Beginning: “NEW YORK TIMES CO. v. UNITED STATES”

Ending: “NEW YORK TIMES CO. v. UNITED STATES”

**Unit 1 — syllabus / author unknown / pp. 1–2**

Trigger: `Syllabus` (high; first standalone Syllabus label).

Sections: none.

Beginning: “Syllabus NEW YORK TIMES CO. v. UNITED STATES CERTIORARI TO THE UNITED STATES COURT OF APPEALS FOR THE SECOND CIRCUIT No. 1873. Argued June 26, 1971-Decided June 30, 1971* The United States, which brought these actions to enjoin publication in the New York Times and in the Washington Post of certain classified material, has not met the "heavy burden”

Ending: “aenkel, and Marvin M. Karpatkin for the American Civil Liberties Union; and by Victor Rabinowitz for the National Emergency Civil Liberties Committee. *Together with No. 1885, United States v. Washington Post Co. et al., on certiorari to the United States Court of Appeals for the District of Columbia Circuit. OCTOBER TERM, 1970 Per Curiam 403 U. S.”

**Unit 2 — majority / Per Curiam / pp. 2–2**

Trigger: `PER CURIAM.` (high; standalone PER CURIAM attribution).

Sections: none.

Beginning: “PER CURIAM. We granted certiorari in these cases in which the United States seeks to enjoin the New York Times and the Wash- ington Post from publishing the contents of a classified study entitled "History of U. S. Decision-Making Process on Viet Nam Policy." Post, pp. 942, 943. "Any system of prior restraints of expression comes to this Court bear”

Ending: “uit is therefore affirmed. The order of the Court of Appeals for the Second Circuit is reversed and the case is remanded with directions to enter a judg- ment affirming the judgment of the District Court for the Southern District of New York. The stays entered June 25, 1971, by the Court are vacated. The judgments shall issue forthwith. So ordered.”

**Unit 3 — concurrence / Black / pp. 2–8**

Trigger: `MR. JUSTICE BLACK, with whom MR. JUsTICE DOUGLAS joins, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE BLACK, with whom MR. JUsTICE DOUGLAS joins, concurring. I adhere to the view that the Government's case against the Washington Post should have been dismissed and that the injunction against the New York Times should have been vacated without oral argument when the cases were first presented to this Court. I believe NEW YORK TIMES CO. v”

Ending: “M, 1970 DOUGLAS, J., concurring 403 U. S. assembly in order to maintain the opportunity for free political discussion, to the end that government may be responsive to the will of the people and that changes, if desired, may be obtained by peaceful means. Therein lies the security of the Republic, the very foundation of constitutional government." '”

**Unit 4 — concurrence / Douglas / pp. 8–12**

Trigger: `MR. JUSTICE DOUGLAS, with whom MR. JUSTICE BLACK joins, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE DOUGLAS, with whom MR. JUSTICE BLACK joins, concurring. While I join the opinion of the Court I believe it necessary to express my views more fully. It should be noted at the outset that the First Amend- ment provides that "Congress shall make no law ... abridging the freedom of speech, or of the press." That leaves, in my view, no room”

Ending: “-270. I would affirm the judgment of the Court of Appeals in the Post case, vacate the stay of the Court of Appeals in the Times case and direct that it affirm the District Court. The stays in these cases that have been in effect for more than a week constitute a flouting of the principles of the First Amendment as interpreted in Near v. Minnesota.”

**Unit 5 — concurrence / Brennan / pp. 12–15**

Trigger: `MR. JUSTICE BRENNAN, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: I (p. 12), II (p. 13).

Beginning: “MR. JUSTICE BRENNAN, concurring. I I write separately in these cases only to emphasize what should be apparent: that our judgments in the pres- ent cases may not be taken to indicate the propriety, in the future, of issuing temporary stays and restraining NEW YORK TIMES CO. v. UNITED STATES 713 BRENNAN, J., concurring orders to block the publicatio”

Ending: “y restraint issued in this case, whatever its form, has violated the First Amend- ment-and not less so because that restraint was jus- tified as necessary to afford the courts an opportunity to examine the claim more thoroughly. Unless and until the Government has clearly made out its case, the First Amendment commands that no injunction may issue.”

**Unit 6 — concurrence / Stewart / pp. 15–18**

Trigger: `MR. JUSTICE STEWART, with whom Ma. JUSTICE WHITE joins, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE STEWART, with whom Ma. JUSTICE WHITE joins, concurring. In the governmental structure created by our Consti- tution, the Executive is endowed with enormous power in the two related areas of national defense and inter- national, relations. This power, largely unchecked by the Legislative 1 and Judicial' branches, has been pressed to the ”

Ending: “tive is correct with re- spect to some of the documents involved. But I can- not say that disclosure of any of them will surely result in direct, immediate, and irreparable damage to our Nation or its people. That being so, there can under the First Amendment be but one judicial resolution of the issues before us. I join the judgments of the Court.”

**Unit 7 — concurrence / White / pp. 18–28**

Trigger: `MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. I concur in today's judgments, but only because of the concededly extraordinary protection against prior re- NEW YORK TIMES CO. v. UNITED STATES 713 WHITE, J., concurring straints enjoyed by the press under our constitutional system. I do not say that in no circumstances would the ”

Ending: “blished all the material now in its possession. That matter must await resolution in the context of a criminal pro- ceeding if one is instituted by the United States. In that event, the issue of guilt or innocence would be determined by procedures and standards quite different from those that have purported to govern these injunc- tive proceedings.”

**Unit 8 — concurrence / Marshall / pp. 28–36**

Trigger: `MR. JUSTICE MARSHALL, concurring.` (high; explicit authored concurrence heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE MARSHALL, concurring. The Government contends that the only issue in these cases is whether in a suit by the United States, "the First Amendment bars a court from prohibiting a news- 10 Also relevant is 18 U. S. C. § 794. Subsection (b) thereof forbids in time of war the collection or publication, with intent that it shall be communicat”

Ending: “ has refused to pass. I believe that the judgment of the United States Court of Appeals for the District of Columbia Circuit should OCTOBER TERM, 1970 BURGER, C. J., dissenting 403 U. S. be affirmed and the judgment of the United States Court of Appeals for the Second Circuit should be reversed in- sofar as it remands the case for further hearings.”

**Unit 9 — dissent / Burger / pp. 36–40**

Trigger: `MR. CHIEF JUSTICE BURGER, dissenting.` (high; explicit authored dissent heading).

Sections: none.

Beginning: “MR. CHIEF JUSTICE BURGER, dissenting. So clear are the constitutional limitations on prior restraint against expression, that from the time of Near v. Minnesota, 283 U. S. 697 (1931), until recently in Organization for a Better Austin v. Keefe, 402 U. S. 415 (1971), we have had little occasion to be concerned with cases involving prior restraints a”

Ending: “that I am in general agreement with much of what MR. JUSTICE WHITE has expressed with respect to penal sanctions concerning communication or retention of documents or information relating to the national defense. We all crave speedier judicial processes but when judges are pressured as in these cases the result is a parody of the judicial function.”

**Unit 10 — dissent / Harlan / pp. 40–47**

Trigger: `MR. JUSTICE HARLAN, with whom THE CHIEF JUSTICE and MR. JUSTICE BLACKMUN join, dissenting.` (high; explicit authored dissent heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE HARLAN, with whom THE CHIEF JUSTICE and MR. JUSTICE BLACKMUN join, dissenting. These cases forcefully call to mind the wise admoni- tion of Mr. Justice Holmes, dissenting in Northern Securities Co. v. United States, 193 U. S. 197, 400-401 (1904): "Great cases like hard cases make bad law. For great cases are called great, not by reason ”

Ending: “es, I would continue the NEW YORK TIMES CO. v. UNITED STATES 713 BLACKMUN, J., dissenting restraints on publication. I cannot believe that the doc- trine prohibiting prior restraints reaches to the point of preventing courts from maintaining the status quo long enough to act responsibly in matters of such national importance as those involved here.”

**Unit 11 — dissent / Blackmun / pp. 47–51**

Trigger: `MR. JUSTICE BLACKMUN, dissenting.` (high; explicit authored dissent heading with OCR-tolerant judicial-title match).

Sections: none.

Beginning: “MR. JUSTICE BLACKMUN, dissenting. I join MR. JUSTICE HARLAN in his dissent. I also am in substantial accord with much that MR. JUSTICE WHITE says, by way of admonition, in the latter part of his opinion. At this point the focus is on only the comparatively few documents specified by the Government as critical. So far as the other material-vast in a”

Ending: “n of alliances, the greatly increased difficulty of negotiation with our enemies, the inability of our diplomats to negotiate," to which list I might add the factors of prolongation of the war and of further delay in the freeing of United States prisoners, then the Nation's people will know where the responsibility for these sad consequences rests.”

Ambiguous candidate examples:

- p. 6: `a law.5 See concurring opinion of MR. JUSTICE DOUGLAS,`
- p. 8: `While I join the opinion of the Court I believe it`
- p. 8: `See Beauharnais v. Illinois, 343 U. S. 250, 267 (dissenting opinion`
- p. 8: `of MR. JUSTICE BLACK), 284 (my dissenting opinion); Roth v. United`
- p. 8: `States, 354 U. S. 476, 508 (my dissenting opinion which MR. JUSTICE`
- p. 8: `v. Sullivan, 376 U. S. 254, 293 (concurring opinion of MR. JUSTICE`
- p. 8: `concurring opinion which MR. JUSTICE BLACK joined).`
- p. 33: `Brother WHITE'S concurring opinion.`

Size diagnostics: units under 200 tokens: [0]; units over 25,000 tokens: none.

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Obergefell v. Hodges

Pages: **99** · Tokens: **50,421** · Major units: **7** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–1 | 11 | low | — | 0 |
| 1 | syllabus | — | 1–8 | 4,567 | high | Syllabus | 0 |
| 2 | majority | Kennedy | 8–43 | 20,276 | high | Justice Kennedy delivered the opinion of the Court. | 5 |
| 3 | dissent | Roberts | 43–70 | 13,934 | high | Chief Justice Roberts, with whom Justice Scalia and Justice Thomas join, dissenting. | 4 |
| 4 | dissent | Scalia | 70–78 | 3,679 | high | Justice Scalia, with whom Justice Thomas joins, dissenting. | 2 |
| 5 | dissent | Thomas | 78–93 | 8,488 | high | Justice Thomas, with whom Justice Scalia joins, dissenting. | 4 |
| 6 | dissent | Alito | 93–99 | 2,909 | high | Justice Alito, with whom Justice Scalia and Justice Thomas join, dissenting. | 3 |

Detected types: dissent, majority, syllabus, unknown. Detected authors: Kennedy, Roberts, Scalia, Thomas, Alito. Sentences over 200 tokens: 1. Repeated reporter headers ignored: 88.

#### Priority review note

The parser finds the syllabus, Kennedy majority, and four separately authored dissents by Roberts, Scalia, Thomas, and Alito. These boundaries are explicit and high confidence; the many reporter headers and syllabus filing summaries are retained without becoming splits.

#### Boundary inspection details

**Unit 0 — unknown / author unknown / pp. 1–1**

Trigger: `leading unassigned text` (low; text before the first confidently detected major component).

Sections: none.

Beginning: “644 OCTOBER TERM, 2014”

Ending: “644 OCTOBER TERM, 2014”

**Unit 1 — syllabus / author unknown / pp. 1–8**

Trigger: `Syllabus` (high; first standalone Syllabus label).

Sections: none.

Beginning: “Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—Decided June 26, 2015* Michigan, Kentucky, Ohio, and Tennessee defne marriage as a union be- tween one man and one woman. The petitioners, 14 same-sex couples and two men ”

Ending: “ns et al. by Alice O'Brien, Jason Walta, Lynn K. Rhinehart, H. Craig Becker, Judith A. Scott, Nicole G. Berner, and Patrick J. Szymanski; for the American Humanist Association et al. by Elizabeth L. Hileman, David A. Niose, and Edward Tabash; for the American Psychological Association et al. by 651 Cite as: 576 U. S. 644 (2015) Opinion of the Court”

**Unit 2 — majority / Kennedy / pp. 8–43**

Trigger: `Justice Kennedy delivered the opinion of the Court.` (high; explicit delivery of the opinion of the Court).

Sections: I (p. 10), II (p. 13), III (p. 20), IV (p. 33), V (p. 37).

Beginning: “Justice Kennedy delivered the opinion of the Court. The Constitution promises liberty to all within its reach, a liberty that includes certain specifc rights that allow per- Paul M. Smith, Nathalie F. P . Gilfoyle, and Aaron M. Panner; for the American Public Health Association et al. by Boris Bershteyn, Sheree R. Kanner, Kenneth Y . Choe, and Dani”

Ending: “ting Judicial Decisions Goodridge v. Department of Public Health, 440 Mass. 309, 798 N. E. 2d 941 (2003) Kerrigan v. Commissioner of Public Health, 289 Conn. 135, 957 A. 2d 407 (2008) Varnum v. Brien, 763 N. W. 2d 862 (Iowa 2009) Griego v. Oliver , 2014–NMSC–003, 316 P. 3d 865 (2013) Garden State Equality v. Dow, 216 N. J. 314, 79 A. 3d 1036 (2013)”

**Unit 3 — dissent / Roberts / pp. 43–70**

Trigger: `Chief Justice Roberts, with whom Justice Scalia and Justice Thomas join, dissenting.` (high; explicit authored dissent heading).

Sections: I (p. 45), II (p. 50), III (p. 63), IV (p. 65).

Beginning: “Chief Justice Roberts, with whom Justice Scalia and Justice Thomas join, dissenting. Petitioners make strong arguments rooted in social policy and considerations of fairness. They contend that same-sex couples should be allowed to affrm their love and commit- ment through marriage, just like opposite-sex couples. That position has undeniable appeal”

Ending: “rientation—who favor expanding same-sex marriage, by all means celebrate today's decision. Celebrate the achieve- ment of a desired goal. Celebrate the opportunity for a new expression of commitment to a partner. Celebrate the availability of new benefts. But do not celebrate the Con- stitution. It had nothing to do with it. I respectfully dissent.”

**Unit 4 — dissent / Scalia / pp. 70–78**

Trigger: `Justice Scalia, with whom Justice Thomas joins, dissenting.` (high; explicit authored dissent heading).

Sections: I (p. 71), II (p. 75).

Beginning: “Justice Scalia, with whom Justice Thomas joins, dissenting. I join The Chief Justice's opinion in full. I write sepa- rately to call attention to this Court's threat to American democracy. The substance of today's decree is not of immense personal importance to me. The law can recognize as marriage what- ever sexual attachments and living arrangeme”

Ending: “op- erly left to them—with each decision that is unabashedly based not on law, but on the “reasoned judgment” of a bare majority of this Court—we move one step closer to being reminded of our impotence. 25 Ante, at 672. 26 The Federalist No. 78, pp. 522, 523 (J. Cooke ed. 1961) (A. Hamilton). 721 Cite as: 576 U. S. 644 (2015) Thomas, J., dissenting”

**Unit 5 — dissent / Thomas / pp. 78–93**

Trigger: `Justice Thomas, with whom Justice Scalia joins, dissenting.` (high; explicit authored dissent heading).

Sections: I (p. 78), II (p. 79), III (p. 89), IV (p. 92).

Beginning: “Justice Thomas, with whom Justice Scalia joins, dissenting. The Court's decision today is at odds not only with the Constitution, but with the principles upon which our Nation was built. Since well before 1787, liberty has been under- stood as freedom from government action, not entitlement to government benefts. The Framers created our Constitu- t”

Ending: “majority misapplies a clause focused on “due process” to af- ford substantive rights, disregards the most plausible under- standing of the “liberty” protected by that clause, and dis- torts the principles on which this Nation was founded. Its decision will have inestimable consequences for our Constitu- tion and our society. I respectfully dissent.”

**Unit 6 — dissent / Alito / pp. 93–99**

Trigger: `Justice Alito, with whom Justice Scalia and Justice Thomas join, dissenting.` (high; explicit authored dissent heading).

Sections: I (p. 94), II (p. 95), III (p. 98).

Beginning: “Justice Alito, with whom Justice Scalia and Justice Thomas join, dissenting. Until the federal courts intervened, the American people were engaged in a debate about whether their States should recognize same-sex marriage. 1 The question in these cases, however, is not what States should do about same-sex mar- riage but whether the Constitution answ”

Ending: “d perhaps irremediable corruption of our legal culture's conception of constitutional interpretation. Most Americans—understandably—will cheer or lament today's decision because of their views on the issue of same- sex marriage. But all Americans, whatever their thinking on that issue, should worry about what the majority's claim of power portends.”

Ambiguous candidate examples:

- p. 5: `Kennedy, J., delivered the opinion of the Court, in which Ginsburg,`
- p. 5: `Scalia, J., fled a dissenting opinion, in which Thomas, J., joined, post,`
- p. 5: `p. 713. Thomas, J., fled a dissenting opinion, in which Scalia, J., joined,`
- p. 5: `post, p. 721. Alito, J., fled a dissenting opinion, in which Scalia and`
- p. 21: `(Harlan, J., dissenting). Rather, it requires courts to exer-`
- p. 22: `dissenting).`
- p. 28: `concurring in judgment); id., at 789–792 (Breyer, J., concur-`
- p. 29: `J., concurring in judgment); Bearden v. Georgia, 461 U. S.`

Size diagnostics: units under 200 tokens: [0]; units over 25,000 tokens: none.

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Plessy v. Ferguson

Pages: **28** · Tokens: **13,846** · Major units: **4** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–1 | 11 | low | — | 0 |
| 1 | syllabus | — | 1–4 | 1,737 | high | Syllabus. | 0 |
| 2 | majority | Brown | 4–16 | 6,516 | medium | YR. JusTIoE BRowN, after stating the case, delivered the opinion of the court. | 0 |
| 3 | dissent | Uamla | 16–28 | 6,421 | high | MR. JUSTICE UAMLA dissenting. | 0 |

Detected types: dissent, majority, syllabus, unknown. Detected authors: Brown, Uamla. Sentences over 200 tokens: 3. Repeated reporter headers ignored: 13.

Ambiguous candidate examples:

- p. 10: `delivering the opinion of the court Mr. Justice Bradley ob-`
- p. 16: `Dissenting Opinion: Harlan, .`
- p. 17: `Dissenting Opinion: Harlan, J.`
- p. 18: `Dissenting Opinion: Harlan, J.`
- p. 19: `Dissenting Opinion: Harlan, J.`
- p. 20: `Dissenting Opinion: Harlan, J.`
- p. 21: `Dissenting Opinion: Harlan, J.`
- p. 22: `Dissenting Opinion: Harlan, J.`

Size diagnostics: units under 200 tokens: [0]; units over 25,000 tokens: none.

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

### Tinker v. Des Moines School Dist.

Pages: **24** · Tokens: **10,852** · Major units: **7** · Coverage: **pass**

| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |
|---:|---|---|---:|---:|---|---|---:|
| 0 | unknown | — | 1–1 | 13 | low | — | 0 |
| 1 | syllabus | — | 1–2 | 486 | high | Syllabus. | 0 |
| 2 | majority | Fortas | 2–12 | 5,404 | high | MR. JUSTICE FORTAS delivered the opinion of the Court. | 2 |
| 3 | concurrence | Stewart | 12–13 | 220 | high | MR. JUSTICE STEWART, concurring. | 0 |
| 4 | concurrence | White | 13–13 | 136 | high | MR. JUSTICE WHITE, concurring. | 0 |
| 5 | dissent | Black | 13–24 | 5,023 | high | MR. JUSTICE BLACK, dissenting. | 0 |
| 6 | dissent | Harlan | 24–24 | 233 | high | MR. JUSTICE HARLAN, dissenting. | 0 |

Detected types: concurrence, dissent, majority, syllabus, unknown. Detected authors: Fortas, Stewart, White, Black, Harlan. Sentences over 200 tokens: 0. Repeated reporter headers ignored: 22.

Ambiguous candidate examples:

- p. 5: `(1952) (concurring opinion); Sweezy v. New Hampshire,`
- p. 18: `BLACK, .J., dissenting. 393 U. S.`

Size diagnostics: units under 200 tokens: [0, 4]; units over 25,000 tokens: none.

Boundary risks:

- Possible false negative: OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.
- Possible false negative: Repeated reporter running headers are intentionally ignored even when they name an opinion type.

## Uncertainty and human-review priorities

- OCR corruption can hide a true heading or distort an author name. The parser keeps such text even when it cannot classify it.
- Medium-confidence standalone justice attributions are useful for older reports, but they deserve manual review because the line may introduce commentary rather than a new opinion.
- Repeated running headers are excluded from boundary detection. This prevents many false splits but can miss a boundary when the true heading was lost in extraction.
- Sentence segmentation is an approximation. Long reported segments identify places where abbreviations, citations, OCR, or unusual punctuation prevented a clean split.
- An `unknown` leading unit means the parser could not confidently assign front matter, argument, an earlier case fragment, or a syllabus-like component to an opinion.

The three priority cases should be reviewed unit by unit before Phase 4B. Questionable boundaries are intentionally surfaced here rather than silently corrected.
