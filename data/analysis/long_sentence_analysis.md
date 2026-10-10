# CourtLens Phase 4A.1: Long Sentence Analysis

This report reviews every sentence segment above 200 tokens in the Phase 4A structural preview. No source text was rewritten.

## Cause summary

| Likely cause | Count |
|---|---:|
| citation or statutory enumeration | 6 |
| extraction layout or footnote interleaving | 5 |
| genuinely long historical sentence | 7 |
| ocr punctuation loss | 8 |
| page boundary artifact | 2 |

## Decision

No parser-level sentence change: the failures are heterogeneous, and repairing OCR punctuation or page layout would require speculative text rewriting.

Preserve normal sentence packing, but when one sentence exceeds the future hard token maximum, apply a secondary token-aware split contained within the same opinion and retain the original page provenance.

## All oversized segments

### 1. Dred Scott v. Sandford — pp. 6–7 — 204 tokens

Unit: 1 (unknown, author raw: unknown).

Likely cause: **page boundary artifact**. The sentence continues across pages 6–7 and absorbs the running header because the page break has no sentence-ending punctuation.

Phase 4B fallback: yes — preserve provenance, then use a maximum-size fallback if the reconstructed sentence remains oversized

Beginning: “Louis myunty; that there was a verdict and judgment in his favor; that on a w rit of error to the Supreme Court, the judgment below was reversed, and thesame remanded to the Circuit Court, where it hasveen con- tinued to await the decision of this case.In May, 1854, the cause went before a jury, who found thefollowing verdict, viz: "As the first is”

Ending: “d, we of the jury find that be-fore and at the tune when, &c., in e rs count mentioned, the said Dred Scott was a negro slave, the lawful property ofthe defendant; and as to the issue thirdly above joined, we,the jury, find that before and at the time when, &c., in thesecond and third counts mentioned, the said Harriet, wife of DECEMBER TERM, 1856.”

### 2. Dred Scott v. Sandford — pp. 22–22 — 242 tokens

Unit: 2 (majority, author raw: Tane).

Likely cause: **ocr punctuation loss**. OCR joins sentence-ending punctuation to the next capitalized word (`State.And`), preventing a normal split.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “It is in these words:S"Whereas sound policy requires that the abolition of slavery should be effected as soon as may be consistent with the rightsof individuals, and the public safety and welfare "-showingthat the right of property in the master was to be protected,and that the measure was one of policy, and to prevent the in- jury and inconvenienc”

Ending: “seized by any one, and taken before the next au-thorit to be examined and delivered up to his master-whowas required to pay the charge which had accrued thereby.And a subsequent section of the same law provides, that ifany free negro shall travel without such pass, and shall be stopped, seized, or taken up, he shall pay all charges arising thereby.”

### 3. Dred Scott v. Sandford — pp. 24–24 — 201 tokens

Unit: 2 (majority, author raw: Tane).

Likely cause: **genuinely long historical sentence**. A single semicolon-heavy historical sentence remains grammatically continuous.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “The legislation of the States therefore shows, in a manner not to be mistaken, the inferior and subject condition of that race at the time the Constitution was adopted, and long after- wards, throughout the thirteen States by Which that instru- ment was framed; and it is hardly consistent with the respect due to these States, to suppose that they r”

Ending: “hey had impressed such deep and enduring marks of inferiority and degradation; or, that when they met in conven- tion to form the Constitution, they looked upon them as a portion of their constituents, or designed to include them in the provisions so carefully inserted for the security and protec- tion of the liberties and rights of their citizens.”

### 4. Dred Scott v. Sandford — pp. 43–43 — 214 tokens

Unit: 2 (majority, author raw: Tane).

Likely cause: **genuinely long historical sentence**. A single long constitutional-history sentence uses coordinated clauses and semicolons.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “They were about to dissolve this federative Union, and to surrender a portion of their independent sovereignty to a new Govern- ment, which, for certain purposes, would make the people of the several States one people; and which was to be supreme and controlling within its sphere of action throughout the United States; but this Government was to be”

Ending: “y had agreed upon be incapable of execution, and a mere nullity, -it was obvious that some provision was necessary to give the new Government sufficient power to enable it to carry into effect the objects for which it was ceded, and the compacts and agreements which the States had made with each other in'the exercise of their powers of sovereignty.”

### 5. Dred Scott v. Sandford — pp. 81–81 — 201 tokens

Unit: 5 (concurrence, author raw: Grier).

Likely cause: **citation or statutory enumeration**. One sentence enumerates a long series of case citations before stating their common rule.

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “Beginning with the earliest Aecisions of this court, we have the cases of Bingham, v. Cabot et al., (3 Dallas, 882;) Turner v. Eurille, (4 Dallas, 7;) Abercrombie v. Dupuis et al., (1 Cranch, 343;) Wood v. Wagnon, '(2 Cranch, 9;) The United States v. The brig Union et al., (4 Cranch, 216;) Sullivan v. The Fulton Steamboat Company, (6 Wheaton, 450;)”

Ending: “oat Company, (6 Wheaton, 450;) Mollan et al. v. Torrence, (9 Wheaton, 537;) Brown v. Keene, (8 Peters, 112,) and Jackson v. Ashton, (8 Peters, 148;) ruling, in uniform and unbroken current, the doctrine that it is essential to the jurisdiction of the courts of the United States, that the facts upon which it is founded should appear upon the record.”

### 6. Dred Scott v. Sandford — pp. 100–100 — 341 tokens

Unit: 5 (concurrence, author raw: Grier).

Likely cause: **ocr punctuation loss**. Several apparent sentence endings are fused to following words (`pretended.In`, `jurisdiction; that`) and a footnote line is inserted.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “If, then, with the attendant formaliies of assent or compact, the restrictive power claimed was void as to the immediate subject of the ordinance, how much more unfounded must be the pretension to such a power as derived from that source, (viz: the ordinance of 1787,) with respect toterritory acquired by purchase or conquest under the supremeauthor”

Ending: “ot been adverted to; for although it has been ruled by this court, that in instanes of concurrent jurisdiction, the court first obtaining possession or cognizance of the contro- versy should retain and decide it, yet, as in this case there bad jLetwer f hom ames Madison to Robert Welsh, November 2th 1819, on the u- ject of Ithe Missouri Compromise.”

### 7. Dred Scott v. Sandford — pp. 107–107 — 220 tokens

Unit: 6 (concurrence, author raw: Campbell).

Likely cause: **genuinely long historical sentence**. A lengthy statutory quotation forms one sentence with repeated clauses.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “28,) "many colliers, coal-heavers, and salters, are in a state of slavery or bondage, bound to the collieries and salt works, where they work or life, transferable with the collieries and salt works when their ori-inal masters have no use for them; and whereas the eman- cipating or setting free the colliers, coal-heavers, and salters, in Scotland, ”

Ending: “njury to the present masters, and would remove the reproach of allowing such a state of servitude to exist in a free country," &c.; and again, in 1799, "they declare that many colliers and coal-heavers still continue in a state of bondage." fo statute, from the Con- quest till the 15 George II,. had been passed upon the subject of personal slavery.”

### 8. Dred Scott v. Sandford — pp. 118–118 — 201 tokens

Unit: 6 (concurrence, author raw: Campbell).

Likely cause: **extraction layout or footnote interleaving**. A footnote or parallel text block is inserted mid-sentence, mixing the territorial-power discussion with the Farmer's Letters quotation.

Phase 4B fallback: yes — retain source order and use a bounded fallback; automatic text repair would be speculative

Beginning: “But the power to"make rules and regulations respectinig the territory" is not restrained by State lines, nor are there any constitutional prohibitions- upon its exerbise in the domain of the United sates within the States; and whatever rules and regula- tions respecting territory Congress may constitutionally make are supreme, and are not dependent”

Ending: “ia- ment. to legislate ii all cases whatever over the colonies:' "It has been urged with great vehemence .against us," he says, and it seems to be thought their FORT by our adversaries, that a power of regulation is a power of legislation; and a power of legislation, if constitutional, must be universal and supreme, in the utmost sense of the word.”

### 9. Dred Scott v. Sandford — pp. 122–122 — 203 tokens

Unit: 6 (concurrence, author raw: Campbell).

Likely cause: **genuinely long historical sentence**. A long enumerative sentence lists many forms of territorial administration.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “The system of land surveys; the reservations for schools, internal improvements, military sites, and public buildings; the pre- emption claims of settlers; the establishment of land offices, and boards of inquiry, to determine the validity of land titles; the modes of entry, and sale, and of conferring titles; the pro- tection of the lands from tre”

Ending: “o form a self-sustaining municipal Govern- ment-these important ruls and regulations will sufficiently illustrate the scope and operation of the 3d section of the 4th article of the Constitution. - But this clause in the Constitution ,does not exhaust the powers of Congress within the territorial .subdivisions, or over the persons who inhabit them.”

### 10. Dred Scott v. Sandford — pp. 123–123 — 240 tokens

Unit: 6 (concurrence, author raw: Campbell).

Likely cause: **ocr punctuation loss**. OCR punctuation and dash-prefixed continuations (`. -But`, `.Whatever`) obscure multiple likely sentence boundaries.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “The Consti: tution allows Congress to coin money, and'regulate its value; to regulate foreign and Federal commerce; to secure, for a limited period, to authors and inventors, -a property in their writings and discoveries: and to make rules concernin cap- tures in war; and, within the limits of these powers, it has exercised, rightly, 'to a greater ”

Ending: “e by which it is held. .Whatever these Constitutions and laws validly determine to be property, it is the duty of the Federal Government, through the domain of jurisdiction merely Federal, to recognise to be property.I And this principle follows from the structure of the respect- ive Governments, State and Federal, and their reciprocal rela- tions.”

### 11. Dred Scott v. Sandford — pp. 173–173 — 221 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **ocr punctuation loss**. Multiple sentences are fused without spaces after periods (`jurisdiction.It`, `State.To`).

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “And that when arecord comes here upon a writ of error or appeal, and, on its inspection, it appea rs to this court that the Circuit Court hadnot jurisdiction, its judgment mulst be reversed, and the cause remanded, to be dismissed for want of jurisdiction.It is alleged by the defendant in error, in this case, that thenlea td the jurisdiction was a ”

Ending: “onstitution, because it was not a suit by a citizen of one State against a citizen of another State.To this it is answered, first that the defendant, bycleadingoven after the plea .to the jurisdiction. was adjudge insuf-cient, finally waived all benefit of that plea.plhen that plea was adjud ed insuffcient, the defendant was obliged to answer over.”

### 12. Dred Scott v. Sandford — pp. 176–176 — 255 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **ocr punctuation loss**. A long quoted plea is followed by OCR dash-and-period sequences that hide the next sentence boundary.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “Sand- ford,. in his own proper person, comep and says that this court ought not to have or take further cognizance of the iaction aforesaid, because he says that said cause of action,- and each and every of them, (if any such have accrued to the said Dred scott),acarued to the said Dred Scott out of the jurisdicion of this court, and exclusively wi”

Ending: “s the said Sandford is ready to verify. -Wherefore, he prays judgment whether this cburt can or will take, further cogni- zahee of the action aforesaid." - .The plaintiff demurred, and the judgment of the Circuit Court was that the plea was insufficient. * I cannot treat-this plea as a general traverse of the citizeniship -alleged'by the plaintiff.”

### 13. Dred Scott v. Sandford — pp. 210–210 — 248 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **extraction layout or footnote interleaving**. Two quoted passages and a footnote marker are merged into one extracted segment.

Phase 4B fallback: yes — retain source order and use a bounded fallback; automatic text repair would be speculative

Beginning: “Mr. Chief Justice Gamble,. in his dissenting opinion in that case, said: "I regard the question as conclusively settled by repeated adjudications of this court; and- if I doubted or denied the pro- priety of those decisions, I would not feel myself any more at liberty to overturn them, than I would any other series of de- cisions by which the law u”

Ending: “hen there was no feeling to disturb the view of the legal questions upon which the rightg of parties depend." t "In this State, it has been recognised from the biginning of the Government as a correct position in law, that the master who takes his slave to reside in a State or Territory where sla- very is prohibited, thereby emancipates his slave."”

### 14. Dred Scott v. Sandford — pp. 222–222 — 214 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **ocr punctuation loss**. Question marks and periods are followed by OCR dash-prefixed text, which the conservative splitter does not treat as a new sentence.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “But it may be mentioned, in passing, that under this power to regulate commerce, Congress has .enacted a great system of municipal laws, and extended it over the vessels and crews of the United States on the hi-h seas and in foreign ports, and even over citizens of the nited States resident in China; 'and has established judicatures, with power to ”

Ending: “ Congress, it finds limits in the express prohibitions .on Congress not to do certain things; 'that, in the exercise of the le is ative power, Conress cann ot pass an ex post facto law-or bill -of attainder; and so in respect to each. of the other prohibitions contained in the Constitutioh.I Besides -this, the rules and regulations must be needful.”

### 15. Dred Scott v. Sandford — pp. 227–227 — 218 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **citation or statutory enumeration**. One sentence enumerates a series of territorial statutes and dates.

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “To these instances should be added the act of March 6th, 1820, (8 Stat. at Large, 548,) prohibiting slavery in the territory acquired from France, being northwest of Missouri, and north of thirty-six degrees thirty minutes north latitudei Of the second class, in which Congress refused to interfere with slavery already existing under the municipal l”

Ending: “at Large, 283,) for the government of Louisiana; the act of March 2d, 1805, (2 Stat. at Large, 322,) for the government of the Territory of-Orleans; the act of June 4th, 18112, (2 Stat. at Large, 743,) for the government of the Missouri Territory; the -aft of March 80th, 1822; (3 Stat. at Large, 654,) for the government of the Territory of Florida.”

### 16. Dred Scott v. Sandford — pp. 231–231 — 275 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **ocr punctuation loss**. OCR quote marks and punctuation around `While` obscure a likely boundary before a new sentence.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “The power once conceded,.it may operate on iiy and every subject of commerce to which the legislative discretion maiy aP .pgwer to regulate commerce extends td an indefinite pro- hibition of the use of all vessels belonging-to citizens of the several States, and may operate, without exception, upon-every subject of commerce to which the legislative”

Ending: “, in my opinion, violate every' sound rule of interpretation to force that exception into the Constitution upon the strength of abstract political reasoning, which we are bound to believe the people of the United States thought insufficient to induce them -to limit the power of Con- gress, because what they have said contains no such" limita- tion.”

### 17. Dred Scott v. Sandford — pp. 233–233 — 210 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **genuinely long historical sentence**. A single long rhetorical question remains syntactically continuous despite OCR noise.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “Is it'not 'm6re rational to conclude that they 'who ,fra ed! and adopted th6 Constitution wer6 ':ware that'persons he d to, service under .the "laws' if a State are property only to the extent nd under the conditions fixed by those laws; that. they- must cease to be available as pr6perty, when their owners- voluntarily place them• permanently withi”

Ending: “h or' displace them, or to -ompel Congress t6 legislate in any particular manner on the subject, and..having empowered Congress to nYake all needful rules and'regulations' respecting. the territory of the United States, it was their intention'to leave to the discfetion of Congress what regulations, if any, should be made concerning slavery therein?”

### 18. Dred Scott v. Sandford — pp. 236–236 — 206 tokens

Unit: 9 (dissent, author raw: Curtis).

Likely cause: **ocr punctuation loss**. Bullet-like OCR characters after periods prevent several otherwise plausible splits.

Phase 4B fallback: yes — token-aware fallback is safer than guessing missing punctuation during parsing

Beginning: “Such an objection rests upon a misapprehension ,of the proviiice and power of courts respect- ing the constitutiofi$lit of laws enacted by th'e Legislature.' f.t.'e Constitution prescripe one rule, and the law another and different rule, it is the djuty of "courts to declare. that the .Constitution,-. and not the -law, governs the case before them ”

Ending: “which the Legislature has the p'ower to gcvern, 'then the law can have- no operation. -If it includes cases. whicA the Legislature, has power to govern, and concerning which the Constitution -does not prescribe a different rule, the law gov- erns those- cases, though it. may, in its terms, attempt tQ in- clude others, ' oif which it cannot operate.”

### 19. Gideon v. Wainwright — pp. 7–7 — 230 tokens

Unit: 2 (majority, author raw: Black).

Likely cause: **extraction layout or footnote interleaving**. A long footnote citation list is inserted after the opening clause and ends mid-citation.

Phase 4B fallback: yes — retain source order and use a bounded fallback; automatic text repair would be speculative

Beginning: “For the same reason, though not always in precisely the same terminology, the Court hag made oblig- atory on the States the Fifth Amendment's command that 4E. g., Gitlow v. New York, 268 U. S. 652, 666 (1925) (speech and press); Lovell v. City of Griffin, 303 U. S. 444, 450 (1938) (speech and press); Staub v. City of Baxley, 355 U. S. 313, 321 (195”

Ending: “speech and press); Staub v. City of Baxley, 355 U. S. 313, 321 (1958) (speech); Groejean v. American Press Co., 297 U. S. 233, 244 (193a) (press); Cantwell v. Connecticut, 310 U. S. 296, 303 (1940) (religion); De Jonge v. Oregon, 299 U. S. 353, 364 (1937) (assembly); Shelton v. Tucker, 364 U. S. 479, 486, 488 (1960) (association); Louisiana ex rel.”

### 20. Marbury v. Madison — pp. 2–2 — 544 tokens

Unit: 0 (unknown, author raw: unknown).

Likely cause: **extraction layout or footnote interleaving**. Marginal headnotes and main text are interleaved by column-order extraction, creating a 544-token pseudo-sentence.

Phase 4B fallback: yes — retain source order and use a bounded fallback; automatic text repair would be speculative

Beginning: “This motion was fupportcdby affidavits of the power to iffue following fa&s; that notice of this motion had beem a mandimus to given to Mr. Madifon; that Mr. Adams,- the late prefi-" fecretary of o..afate of the U of the Unted States,. nominated the applicants to the States, it being fenate for their advice and confent to be appointed juf- an excrc”

Ending: “the advice and confent of the fenate, theconftituticon. who has declined giving fuch a certificate; whereupon a A commifflonl is not neceffary rule was laid to fhewcaufe on the 4th day of this term. to the appoint- This rule having been duly ferved, ment of an of- ficer by the ex- Mr. Lee, in fupport of the rule, obferved that it was ecetive-Senab.”

### 21. Marbury v. Madison — pp. 3–4 — 286 tokens

Unit: 0 (unknown, author raw: unknown).

Likely cause: **page boundary artifact**. A statutory quotation crosses pages 3–4 and absorbs the page header into the continuing sentence.

Phase 4B fallback: yes — preserve provenance, then use a maximum-size fallback if the reconstructed sentence remains oversized

Beginning: “It is in thefe words, -Be it " enaded, &c. that there fhall be' an executive depart- f ment, to be denominated the department of foreign af- c fairs, and that there (hall be a principal officer therein, " to be called the fecretary of the department of foreign c affairs, who flall perform. and execute fucji duties as " fhall from time to time be en”

Ending: “ther applications from foreign public mi- " nifters, or other foreigners, or to fuch other nhatters " refpeding foreign affairs as the Prefident of the United ", States fhall aflign to the faid department; and further- " more, that the faid principal officer fhall'condud the cc bufinefs of the faid department in fuch manner as the Prefident of the.”

### 22. Miranda v. Arizona — pp. 26–26 — 251 tokens

Unit: 1 (majority, author raw: Warren).

Likely cause: **extraction layout or footnote interleaving**. Footnote 30 is inserted inside a quotation and interrupts the main sentence sequence.

Phase 4B fallback: yes — retain source order and use a bounded fallback; automatic text repair would be speculative

Beginning: “As a practical matter, the compulsion to speak in the isolated setting of the police station may well be greater than in courts or other official investiga- tions, where .there are often impartial observers to guard against intimidation or trickery30 This question, in fact, could have been taken as settled in federal courts almost 70 years ago, whe”

Ending: “ In Bram, the Court reviewed the British and American history and case law and set down the Fifth Amendment standard for compulsion which we implement today: "Much of the confusion which has resulted from the effort to deduce from the adjudged cases what 30 Compare Brown v. Walker, 161 U. S. 591 (1896); Quinn v. United State3, 349 U. S. 155 (1955).”

### 23. New York Times Co. v. United States — pp. 23–23 — 228 tokens

Unit: 7 (concurrence, author raw: White).

Likely cause: **citation or statutory enumeration**. The segment is a long quoted statutory subsection with four enumerated clauses.

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “6 In relevant part 18 U. S. C. § 798 provides: "(a) Whoever knowingly and willfully communicates, furnishes, transmits, or otherwise makes available to an unauthorized person, or publishes, or uses in any manner prejudicial to the safety or inter- est of the United States or for the benefit of any foreign government to the detriment of the United S”

Ending: “ng the communication intelligence activities of the United States or any foreign government; or "(4) obtained by the process of communication intelligence from the communications of any foreign government, knowing the same to have been obtained by such processes- "Shall be fined not more than $10,000 or imprisoned not more than ten years, or both."”

### 24. New York Times Co. v. United States — pp. 25–25 — 220 tokens

Unit: 7 (concurrence, author raw: White).

Likely cause: **citation or statutory enumeration**. The segment quotes the long enumerative text of 18 U.S.C. § 793(e).

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “The subsection was added in 1950 because pre-existing law provided no 8 Section 793 (e) of 18 U. S. C. provides that: "(e) Whoever having unauthorized possession of, access to, or control over any document, writing, code book, signal book, sketch, photograph, photographic negative, blueprint, plan, map, model, instrument, appliance, or note relatin”

Ending: “o communicate, deliver, trans- mit or cause to be communicated, delivered, or transmitted the same to any person not entitled to receive it, or willfully retains the same and fails to deliver it to the officer or employee of the United States entitled to receive it;" is guilty of an offense punishable by 10 years in prison, a $10,000 fine, or both.”

### 25. Obergefell v. Hodges — pp. 55–55 — 257 tokens

Unit: 3 (dissent, author raw: Roberts).

Likely cause: **citation or statutory enumeration**. A single citation-dense sentence contains multiple parentheticals and nested quotations.

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “See, e. g., District Attor- ney's Offce for Third Judicial Dist. v. Osborne, 557 U. S. 52, 72 (2009); Flores, 507 U. S., at 303; United States v. Salerno, 481 U. S. 739, 751 (1987); Moore v. East Cleveland, 431 U. S. 494, 503 (1977) (plurality opinion); see also id., at 544 (White, J., dissenting) (“The Judiciary, including this Court, is the most ”

Ending: “ or even the design of the Constitution.”); Troxel v. Granville , 530 U. S. 57, 96–101 (2000) (Kennedy, J., dissenting) (consulting “ `[o]ur Nation's history, legal traditions, and practices' ” and concluding that “[w]e owe it to the Nation's domestic relations legal structure . . . to proceed with caution” (quoting Glucksberg, 521 U. S., at 721)).”

### 26. Plessy v. Ferguson — pp. 2–2 — 206 tokens

Unit: 1 (syllabus, author raw: unknown).

Likely cause: **genuinely long historical sentence**. A single fact-statement sentence uses repeated semicolon-separated clauses.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “Ferguson, judge of the criminal District Court for the parish of Orleans, and setting forth in substance the following facts: That petitioner was a citizen of the" United States and a resident of the State of Louisiana, of mixed descent, in the proportion of seven eighths Caucasian and one eighth African blood; that the mixture of colored blood was”

Ending: “ to Covington, in the same State, and thereupon entered a passenger train, and took possession of a vacant seat in a coach where passen- gers of the white race were accommodated; that such railroad company was incorporated by the laws of Louisiana as a common carrier, and was not authorized to distinguish be- tween citizens according to their race.”

### 27. Plessy v. Ferguson — pp. 3–3 — 267 tokens

Unit: 1 (syllabus, author raw: unknown).

Likely cause: **genuinely long historical sentence**. A single procedural-history sentence contains many coordinated clauses.

Phase 4B fallback: yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion

Beginning: “That petitioner was subsequently brought before the re- corder of the city for preliminary examination and committed for trial to the criminal District Court for the parish of Orleans, where an information was filed against him in the matter above set forth, for a violation of the above act, which act the petitioner affirmed to be null and void, be”

Ending: “to fine and sentence petitioner to imprisonment, and thus deprive him of his con- stitutional rights set forth in his said plea, notwithstanding the unconstitutionality of the act under which he was being prosecuted; that no appeal lay from such sentence, and peti- tioner was without relief or remedy except by writs of pro- hibition and certiorari.”

### 28. Plessy v. Ferguson — pp. 5–5 — 206 tokens

Unit: 2 (majority, author raw: Brown).

Likely cause: **citation or statutory enumeration**. A long statutory quotation enumerates penalties, officer powers, and liability rules.

Phase 4B fallback: yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum

Beginning: “Opinion of the Court. to assign each passenger to the coach or compartment used for the race to which such passenger belongs; any passenger insisting on going into a coach or compartment to which by race he does not belong, shall be liable to a fine of twenty-five dollars, or in lieu thereof to imprisonment for a period of not more than twenty days”

Ending: “ and should any passenger refuse to occupy the coach or compartment to which lie or she is assigned by the officer of such railway, said officer shall have power to refuse to carry such passenger on his train, and for such refusal neither he nor the railway company which he represents shall be liabl6 for damages in any of the courts of this State."”

