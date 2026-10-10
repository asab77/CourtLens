# CourtLens Phase 4B.1 — structure-aware chunk inspection

Local descriptive validation only. Retrieval quality has not been evaluated.

## Algorithm and schema

Documents are sorted by source filename; units, sections and sentences retain source order. Foreign units are excluded. Every other unit is packed separately. Target 900; hard maximum 1100; soft minimum 300; tokenizer cl100k_base.

A section ending flushes a chunk at 300 or more tokens. Smaller sections may continue inside the same unit. Adding a sentence beyond 900 flushes a coherent chunk at or above 300; otherwise packing may approach the strict 1100 maximum. A complete trailing sentence is repeated only on an internal context break and only when it fits with the next source piece. Explicit sections and opinions never receive cross-boundary overlap.

Existing approximate sentences can contain a section marker internally. We align the validated marker by relative line offset in unit text and divide that sentence into exact character-range fragments at the marker. This does not change the parser or invent labels. Such fragments are ineligible for sentence overlap. Pages for every fragment conservatively retain the entire original sentence page range.

Oversized fragments prefer semicolons, colons, commas, then whitespace in a 700–900 token window; otherwise a measured character boundary gives a token-aware split near 900 without breaking Unicode characters. Original source character ranges concatenate exactly; no fallback fragment overlap is introduced.

The tokenizer is loaded only from a locally installed vocabulary whose reconstructed standard data matches the official SHA-256. Missing vocabulary fails without downloading.

Records follow the existing {text, metadata} schema. Metadata includes stable document-local IDs/indexes, one major-unit ID/type, opinion, raw parser author, known section IDs/markers/titles, original sentence IDs/range, overlap IDs/token count, and character-range provenance for each source piece. Whitespace joining follows Phase 4A canonical normalization.

Coverage validation checks exact sentence reconstruction from character ranges, all primary fragments in source order, every emitted text against its source pieces, pages, unit identity, and overlap eligibility before writing any output.

## Local quality measurements

```json
{
  "total_chunks": 433,
  "total_chunk_tokens": 348772,
  "mean": 805.48,
  "median": 873,
  "min": 9,
  "max": 900,
  "p10": 617.0,
  "p25": 829.0,
  "p75": 890.0,
  "p90": 896.0,
  "buckets": {
    "<300": 17,
    "300–599": 26,
    "600–900": 390,
    "901–1100": 0,
    ">1100": 0
  },
  "below_300_count": 17,
  "below_300_percentage": 3.93,
  "above_900_count": 0,
  "above_900_percentage": 0.0,
  "total_unique_cases": 8,
  "chunks_by_case": {
    "Dred Scott v. Sandford": 186,
    "Gideon v. Wainwright": 13,
    "Marbury v. Madison": 33,
    "Miranda v. Arizona": 67,
    "New York Times Co. v. United States": 32,
    "Obergefell v. Hodges": 64,
    "Plessy v. Ferguson": 20,
    "Tinker v. Des Moines School Dist.": 18
  },
  "chunks_by_major_unit_type": {
    "major_legal_component": 433
  },
  "chunks_by_opinion_type": {
    "concurrence": 68,
    "dissent": 164,
    "majority": 141,
    "other": 21,
    "syllabus": 11,
    "unknown": 28
  },
  "chunks_with_author": 375,
  "chunks_without_author": 58,
  "chunks_spanning_multiple_sections": 7,
  "chunks_using_overlap": 356,
  "average_overlap_tokens": 41.62,
  "maximum_overlap_tokens": 220,
  "total_overlap_tokens": 14817,
  "chunks_using_oversized_sentence_fallback": 0,
  "oversized_sentence_fallback_count": 0,
  "fallback_pieces_generated": 0,
  "fallback_examples": [],
  "section_boundary_sentence_fragments": 16,
  "excluded_foreign_units": 1,
  "excluded_foreign_tokens": 200,
  "excluded_foreign_details": [
    {
      "case_name": "Dred Scott v. Sandford",
      "unit_index": 0,
      "token_count": 200
    }
  ],
  "validation": {
    "MIXED_MAJOR_UNIT_CHUNKS": 0,
    "MIXED_OPINION_CHUNKS": 0,
    "eligible_source_sentences": 9704,
    "covered_source_sentences": 9704,
    "missing_source_sentences": 0,
    "coverage_percentage": 100.0,
    "eligible_source_fragments": 9712,
    "covered_source_fragments": 9712,
    "source_order_recoverable": true,
    "fallback_text_preserved": true,
    "foreign_material_in_chunks": 0
  }
}
```

## Fixed 900/150 descriptive comparison

| Measurement | Fixed 900/150 | Structure-aware v1 |
|---|---:|---:|
| total_chunks | 598 | 433 |
| mean | 602.51 | 805.48 |
| median | 614.5 | 873 |
| min | 5 | 9 |
| max | 897 | 900 |
| below_300_count | 4 | 17 |
| below_300_percentage | 0.67 | 3.93 |
| above_900_count | 0 | 0 |
| above_900_percentage | 0.0 | 0.0 |

Configured 150-token recursive splitter overlap; actual shared sentence/token overlap was not stored and is not inferred.

Structure-aware overlap: 356 chunks; mean 41.62 tokens; maximum 220 tokens. Distribution does not establish retrieval superiority.

## Boundary inspection

### Dred Scott v. Sandford

**Unit 0: foreign / unassigned — excluded foreign material; no retrieval chunk.**

**Unit 1: unknown / unassigned — 6 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00000`; pp. 1–2; 794 tokens; overlap 0; sections ['I']
  - Beginning: DRED SCOTT, PLAINTIFF IN ERROR, v. JomT F. A. SANDFORD. I. 1. Upon a writ of error to a Circuit Court of the United States, the transcript of the record of all the proceedings in t
  - Ending: entitled to sue in that character in the Circuit Court. 11. This being the case, the judgment of the court below, in favor of the plaintiff on the plea in abatement, was erroneous,

- `dred_scott_v_sandford:structure_aware_v1:00005`; pp. 6–7; 622 tokens; overlap 1; sections ['V']
  - Beginning: It is agreed that Dred Scott brought suit for his freedom in the Circuit Court of St. Louis myunty; that there was a verdict and judgment in his favor; that on a w rit of error to 
  - Ending: he subject is thoroughly examined in the opinion of the court, the opinions of the concurring judges, and the opin- ions of the judges who dissented from the judgment of the court.

**Unit 2: majority / Tane — 41 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00006`; pp. 7–9; 886 tokens; overlap 0; sections []
  - Beginning: Mr. Chief Justice TANE delivered the opinion of the court. . t This case has been twice argued. After the argument at the last term, differences of opinion were found to exist amon
  - Ending: Court of the United States; in other words, where they are what the law terms courts of general jurisdiction; they are presumed to have ju- risdiction, unless the contrary appears.

- `dred_scott_v_sandford:structure_aware_v1:00046`; pp. 61–62; 654 tokens; overlap 1; sections []
  - Beginning: The case was carried before the Supreme Court of the State; was fully argued there; and that court decided that neither the plaintiff nor his family were entitled to freedom; and w
  - Ending: d could give no judgment in it. Its judgment for the de- fendant must, consequently, be reversed, anc a mandate issued, directing the suit to be dismissed for want of jurisdiction.

**Unit 3: concurrence / Wayne — 2 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00047`; pp. 62–63; 858 tokens; overlap 0; sections []
  - Beginning: Mr. Justice WAYNE. Concurring as I do entirely in the opinion of the court, as it has been written and read by the Chief Justice-without any qualification of its reasoning or its c
  - Ending: adjudged cases; and. it has been.shown that writs of error to a State court and to the Circuit Courts of the Ufnitd States are. tQ be deterriiined by different laws and principles.

- `dred_scott_v_sandford:structure_aware_v1:00048`; pp. 63–65; 813 tokens; overlap 1; sections []
  - Beginning: The differences between the rules concerning pleas to the jurisdiction in the couits of the United States and common- law courts have been stated and sustained by reasoniig and adj
  - Ending: the argument of the Chief Justice. I have already said that the opinion of the court has my unqualified assent. DECEMBER TERM, 1856. 457 Dred coft v. Sandford. [iR. JUSTICE NELSON.

**Unit 4: other / Lnelson — 9 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00049`; pp. 65–66; 891 tokens; overlap 0; sections []
  - Beginning: Mr. Justice lNELSON. I shall proceed to state the grouinds upon which I have arrived at the conclusion, that the judgment of the court below should be affirmed. The suit was brough
  - Ending: in his favor; but that, on a writ of error from the Supreme Court of the State, the judgment of the court below was reversed, and the cause remanded to the circuit for a new trial.

- `dred_scott_v_sandford:structure_aware_v1:00057`; pp. 75–77; 856 tokens; overlap 1; sections []
  - Beginning: This was nearly thiy years before the decision in that case, which was in 1828. The Court of Appeals observed, in deciding the Maryland case, that "however the laws of Great Britai
  - Ending: es, we shall be prepared to decide it. DECEMBER TERM, 1856. 469 Dred &ott v. Sandford. [MV. JUSTC- GimR. Our conclusion is, that the judgment of the court below should be affirmed.

**Unit 5: concurrence / Grier — 19 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00058`; pp. 77–78; 771 tokens; overlap 0; sections []
  - Beginning: Mr. Justice GRIER. I concur in the opinion delivered by Mr. Justice Nelson on the questions discussed by him. I also concur with the opinion of the court as delivered by the Chief 
  - Ending: the Circuit Court could not take cognizance of the action- To this plea in abatement, a demurrer having been inter- posed on behalf of the plaintiff, it was sustained by the court.

- `dred_scott_v_sandford:structure_aware_v1:00076`; pp. 100–101; 548 tokens; overlap 1; sections []
  - Beginning: The effect of such a discrimination is suffi- ciently evident."* In support of the ordinance of 1787, there may be adduced the semblance at least of obligation deducible from compa
  - Ending: r of autre actionyendent, it wag thought that the fact of a prior decision, how- ever conclusive it might have been if regularly pleaded, could not be incidentally taken into view.

**Unit 6: concurrence / Campbell — 20 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00077`; pp. 101–102; 885 tokens; overlap 0; sections []
  - Beginning: Mr. Justice CAMPBELL. I concur in the judgment pronounced by the Chief Justice, but the importance of the cause, the expectation and interest it has awakened, and the responsibilit
  - Ending: eved the subject of much of its diffi- culty. (12 B. M. Ky. R., 545; Foster v. Foster, 10 Gratt. Va. R., 485; 4 Har. and McH. Md. R., 295; Scott v. Emerson, 15 Misso., 576; 4 Rich.

- `dred_scott_v_sandford:structure_aware_v1:00096`; pp. 125–126; 324 tokens; overlap 1; sections []
  - Beginning: The jury have returned that the plaintiff and his family are slaves. Upon this record, it is apparent that this is not a controversy between citizens of different States; and that 
  - Ending: hink the judgment should be affirmed, on the ground that the Circuit Court had no jurisdiction, or that the case should be reversed and. re- manded, that the suit may be dismissed.

**Unit 7: other / Oatron — 9 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00097`; pp. 126–127; 882 tokens; overlap 0; sections []
  - Beginning: Mr. Justice OATRON. The defendant pleaded to the jurisdiction of the Circuit Court, that the plaintiff was a negro of African blood; the descendant of Africans, -ho had een importe
  - Ending: rolibited. " From this prohibition, the territory now constituting the State of Missouri was excepted; which exception to the stipu- lation gave it the designation of a compromise.

- `dred_scott_v_sandford:structure_aware_v1:00105`; pp. 136–137; 326 tokens; overlap 1; sections []
  - Beginning: I concur with Judge Baldwin, that Federal power is exer- cised over all the territory within the United States, pursuant to the, Constitution; and, the conditions of the cession, w
  - Ending: s above stated, I concur with my brother Judges that the plaintiff, Scott, is a slave, and was so when this suit was brought. Mr. Justice McLEAN and Mir. Justice CURTIS. dissented.

**Unit 8: dissent / Mclean — 26 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00106`; pp. 137–138; 877 tokens; overlap 0; sections []
  - Beginning: Mr. Justice McLEAN dissenting. This case is before us on a writ of error from the Circuit Court for the digtrict of Missouri. An action of trespass was brought, which charges the c
  - Ending: of the 'State of Missouri, and upon the river Mississippi. Lizzie is -about seven years old, and was born in the State of Missouri, :at the military post called Jeffersoi Barracks.

- `dred_scott_v_sandford:structure_aware_v1:00131`; pp. 171–172; 834 tokens; overlap 1; sections []
  - Beginning: On this head, I consider myself fortu- nate in being able to turn- to the decision of this court, given by Mr. Justice Grier,.in Pease v. Peck, a case from the State of Michigan, (
  - Ending: ision being against such right, it may be brought for revilsion before this court,.from the Supreme Court of Missouri. - I think the judgment of the court below-should be reversed.

**Unit 9: dissent / Curtis — 54 chunk(s).**

- `dred_scott_v_sandford:structure_aware_v1:00132`; pp. 172–174; 899 tokens; overlap 0; sections []
  - Beginning: Mr. Justice CURTIS dissenting. "I dissent from the opinion pronounced- by the Chief Justice, ahd from te judgment which the majority of the court think it proper to render in this 
  - Ending: the Uited States have not provided any mode ofreviewing the decision of the Circuit Court on such a plea,when that decision is against the defendant. This is not the SUPREME COURT.

- `dred_scott_v_sandford:structure_aware_v1:00185`; pp. 240–241; 836 tokens; overlap 1; sections []
  - Beginning: Bat it is quite unnecessary, in my opinion, to pursue this inquiry further, because it clearly appears from the language of the article; and it. has been decided by this court that
  - Ending: er more or less, would have been inconsistent with my views of my duty. In my opinion, the judgment of the Circuit Court should be reversed, andtthe cause remanded for a new trial.

### New York Times Co. v. United States

**Unit 0: unknown / unassigned — 1 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00000`; pp. 1–1; 9 tokens; overlap 0; sections []
  - Beginning: NEW YORK TIMES CO. v. UNITED STATES
  - Ending: NEW YORK TIMES CO. v. UNITED STATES

**Unit 1: syllabus / unassigned — 1 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00001`; pp. 1–2; 419 tokens; overlap 0; sections []
  - Beginning: Syllabus NEW YORK TIMES CO. v. UNITED STATES CERTIORARI TO THE UNITED STATES COURT OF APPEALS FOR THE SECOND CIRCUIT No. 1873. Argued June 26, 1971-Decided June 30, 1971* The Unite
  - Ending: 1885, United States v. Washington Post Co. et al., on certiorari to the United States Court of Appeals for the District of Columbia Circuit. OCTOBER TERM, 1970 Per Curiam 403 U. S.

**Unit 2: majority / Per Curiam — 1 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00002`; pp. 2–2; 326 tokens; overlap 0; sections []
  - Beginning: PER CURIAM. We granted certiorari in these cases in which the United States seeks to enjoin the New York Times and the Wash- ington Post from publishing the contents of a classifie
  - Ending: he judgment of the District Court for the Southern District of New York. The stays entered June 25, 1971, by the Court are vacated. The judgments shall issue forthwith. So ordered.

**Unit 3: concurrence / Black — 3 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00003`; pp. 2–4; 859 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE BLACK, with whom MR. JUsTICE DOUGLAS joins, concurring. I adhere to the view that the Government's case against the Washington Post should have been dismissed and that 
  - Ending: t of religious belief or worship, nor shall any national religion be established, nor shall the full and equal rights of conscience be in any manner, or on any pretext, infringed."

- `new_york_times_co_v_united_states:structure_aware_v1:00005`; pp. 6–8; 558 tokens; overlap 1; sections []
  - Beginning: 76. 4 Brief for the United States 13-14. Compare the views of the Solicitor General with those of James Madison, the author of the First Amendment. When speaking of the Bill of Rig
  - Ending:  will of the people and that changes, if desired, may be obtained by peaceful means. Therein lies the security of the Republic, the very foundation of constitutional government." '

**Unit 4: concurrence / Douglas — 3 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00006`; pp. 8–10; 874 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE DOUGLAS, with whom MR. JUSTICE BLACK joins, concurring. While I join the opinion of the Court I believe it necessary to express my views more fully. It should be noted 
  - Ending: y cited and that provision was defeated. 55 Cong. Rec. 2167. Judge Gurfein's holding in the Times case that this Act does not apply to this case was therefore pre- eminently sound.

- `new_york_times_co_v_united_states:structure_aware_v1:00008`; pp. 12–12; 213 tokens; overlap 1; sections []
  - Beginning: The pres- ent cases will, I think, go down in history as the most dramatic illustration of that principle. A debate of large proportions goes on in the Nation over our posture in V
  - Ending: ct Court. The stays in these cases that have been in effect for more than a week constitute a flouting of the principles of the First Amendment as interpreted in Near v. Minnesota.

**Unit 5: concurrence / Brennan — 2 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00009`; pp. 12–13; 326 tokens; overlap 0; sections ['I']
  - Beginning: MR. JUSTICE BRENNAN, concurring. I I write separately in these cases only to emphasize what should be apparent: that our judgments in the pres- ent cases may not be taken to indica
  - Ending: traints in the future. More important, the First Amendment stands as an absolute bar to the imposition of judicial restraints in circumstances of the kind presented by these cases.

- `new_york_times_co_v_united_states:structure_aware_v1:00010`; pp. 13–15; 775 tokens; overlap 0; sections ['II']
  - Beginning: II The error that has pervaded these cases from the out- set was the granting of any injunctive relief whatsoever, interim or otherwise. The entire thrust of the Govern- ment's cla
  - Ending: ourts an opportunity to examine the claim more thoroughly. Unless and until the Government has clearly made out its case, the First Amendment commands that no injunction may issue.

**Unit 6: concurrence / Stewart — 2 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00011`; pp. 15–17; 877 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE STEWART, with whom Ma. JUSTICE WHITE joins, concurring. In the governmental structure created by our Consti- tution, the Executive is endowed with enormous power in the
  - Ending: uppose that moral, political, and practical con- siderations would dictate that a very first principle of that wisdom would be an insistence upon avoiding secrecy for its own sake.

- `new_york_times_co_v_united_states:structure_aware_v1:00012`; pp. 17–18; 704 tokens; overlap 1; sections []
  - Beginning: I should suppose that moral, political, and practical con- siderations would dictate that a very first principle of that wisdom would be an insistence upon avoiding secrecy for its
  - Ending: le damage to our Nation or its people. That being so, there can under the First Amendment be but one judicial resolution of the issues before us. I join the judgments of the Court.

**Unit 7: concurrence / White — 6 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00013`; pp. 18–20; 867 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE WHITE, with whom MR. JUSTICE STEWART joins, concurring. I concur in today's judgments, but only because of the concededly extraordinary protection against prior re- NEW
  - Ending: tates has not met its burden, the material remains sealed in court records and it is 2 The "grave and irreparable danger" standard is that asserted by the Government in this Court.

- `new_york_times_co_v_united_states:structure_aware_v1:00018`; pp. 27–28; 495 tokens; overlap 1; sections []
  - Beginning: But that case arose under other parts of the predecessor to § 793, see 312 U. S., at 21-22-parts that imposed different intent standards not repeated in § 793 (d) or § 793 (e). Cf.
  - Ending: that event, the issue of guilt or innocence would be determined by procedures and standards quite different from those that have purported to govern these injunc- tive proceedings.

**Unit 8: concurrence / Marshall — 4 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00019`; pp. 28–30; 884 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE MARSHALL, concurring. The Government contends that the only issue in these cases is whether in a suit by the United States, "the First Amendment bars a court from prohi
  - Ending: awyer, 343 U. S. 579 (1952). It did not provide for government by injunc- tion in which the courts and the Executive Branch can "make law" without regard to the action of Congress.

- `new_york_times_co_v_united_states:structure_aware_v1:00022`; pp. 34–36; 805 tokens; overlap 1; sections []
  - Beginning: On at least two occasions Congress has refused to enact legislation that would have made the conduct engaged in here unlawful and given the President the power that he seeks in thi
  - Ending: enting 403 U. S. be affirmed and the judgment of the United States Court of Appeals for the Second Circuit should be reversed in- sofar as it remands the case for further hearings.

**Unit 9: dissent / Burger — 3 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00023`; pp. 36–38; 862 tokens; overlap 0; sections []
  - Beginning: MR. CHIEF JUSTICE BURGER, dissenting. So clear are the constitutional limitations on prior restraint against expression, that from the time of Near v. Minnesota, 283 U. S. 697 (193
  - Ending: ssession of the documents for three to four months, during which it has had its expert analysts studying them, presumably digesting them and preparing the material for publication.

- `new_york_times_co_v_united_states:structure_aware_v1:00025`; pp. 40–40; 177 tokens; overlap 1; sections []
  - Beginning: This Court is in no better posture. I agree generally with MR. JUSTICE HARLAN and MR. JUSTICE BLACKMUN but I am not prepared to reach the merits.3 I would affirm the Court of Appea
  - Ending: ormation relating to the national defense. We all crave speedier judicial processes but when judges are pressured as in these cases the result is a parody of the judicial function.

**Unit 10: dissent / Harlan — 4 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00026`; pp. 40–42; 897 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE HARLAN, with whom THE CHIEF JUSTICE and MR. JUSTICE BLACKMUN join, dissenting. These cases forcefully call to mind the wise admoni- tion of Mr. Justice Holmes, dissenti
  - Ending: riously impair the national security. 5. What weight should be given to the opinion of high officers in the Executive Branch of the Government with respect to questions 3 and 4. 6.

- `new_york_times_co_v_united_states:structure_aware_v1:00029`; pp. 46–47; 125 tokens; overlap 1; sections []
  - Beginning: The ensuing review by the District Court should be in ac- cordance with the views expressed in this opinion. And for the reasons stated above I would affirm the judgment of the Cou
  - Ending: r restraints reaches to the point of preventing courts from maintaining the status quo long enough to act responsibly in matters of such national importance as those involved here.

**Unit 11: dissent / Blackmun — 2 chunk(s).**

- `new_york_times_co_v_united_states:structure_aware_v1:00030`; pp. 47–49; 874 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE BLACKMUN, dissenting. I join MR. JUSTICE HARLAN in his dissent. I also am in substantial accord with much that MR. JUSTICE WHITE says, by way of admonition, in the latt
  - Ending: ticle II of the great document vests in the Executive Branch primary power over the conduct of foreign affairs and places in that branch the responsibility for the Nation's safety.

- `new_york_times_co_v_united_states:structure_aware_v1:00031`; pp. 49–51; 894 tokens; overlap 1; sections []
  - Beginning: Article II of the great document vests in the Executive Branch primary power over the conduct of foreign affairs and places in that branch the responsibility for the Nation's safet
  - Ending: rolongation of the war and of further delay in the freeing of United States prisoners, then the Nation's people will know where the responsibility for these sad consequences rests.

### Obergefell v. Hodges

**Unit 0: unknown / unassigned — 1 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00000`; pp. 1–1; 9 tokens; overlap 0; sections []
  - Beginning: 644 OCTOBER TERM, 2014
  - Ending: 644 OCTOBER TERM, 2014

**Unit 1: syllabus / unassigned — 5 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00001`; pp. 1–2; 885 tokens; overlap 0; sections []
  - Beginning: Syllabus OBERGEFELL et al. v. HODGES, DIRECTOR, OHIO DEPARTMENT OF HEALTH certiorari to the united states court of appeals for the sixth circuit No. 14–556. Argued April 28, 2015—D
  - Ending: th Amend- ment's Due Process Clause extend to certain personal choices central to individual dignity and autonomy, including intimate choices defning personal identity and beliefs.

- `obergefell_v_hodges:structure_aware_v1:00005`; pp. 6–8; 821 tokens; overlap 1; sections []
  - Beginning: Davidson, Paul D. Castillo, Camilla B. Taylor, and Ellen Essig fled briefs for petitioners in No. 14– 556 on Question 2. Joseph F. Whalen, Associate Solicitor General of Tennes- se
  - Ending: ation et al. by Elizabeth L. Hileman, David A. Niose, and Edward Tabash; for the American Psychological Association et al. by 651 Cite as: 576 U. S. 644 (2015) Opinion of the Court

**Unit 2: majority / Kennedy — 23 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00006`; pp. 8–9; 899 tokens; overlap 0; sections []
  - Beginning: Justice Kennedy delivered the opinion of the Court. The Constitution promises liberty to all within its reach, a liberty that includes certain specifc rights that allow per- Paul M
  - Ending: l; for Indiana University by Jon Laramore, D. Lucetta Pope, Jane Dall Wilson, and Daniel E. Pulliam; for the Institute for Justice by Wil- liam H. Mellor, Dana Berliner, Jeffrey T.

- `obergefell_v_hodges:structure_aware_v1:00028`; pp. 42–43; 397 tokens; overlap 1; sections ['V']
  - Beginning: Alabama Policy Inst., 200 So. 3d 495 (Ala. 2015) B State Legislation and Judicial Decisions Legalizing Same-Sex Marriage Legislation Del. Code Ann., Tit. 13, § 129 (Cum. Supp. 2014
  - Ending: 2d 407 (2008) Varnum v. Brien, 763 N. W. 2d 862 (Iowa 2009) Griego v. Oliver , 2014–NMSC–003, 316 P. 3d 865 (2013) Garden State Equality v. Dow, 216 N. J. 314, 79 A. 3d 1036 (2013)

**Unit 3: dissent / Roberts — 16 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00029`; pp. 43–45; 877 tokens; overlap 0; sections []
  - Beginning: Chief Justice Roberts, with whom Justice Scalia and Justice Thomas join, dissenting. Petitioners make strong arguments rooted in social policy and considerations of fairness. They 
  - Ending: question based not on neutral principles of con- stitutional law, but on its own “understanding of what free- dom is and must become.” Ante, at 672 I have no choice but to dissent.

- `obergefell_v_hodges:structure_aware_v1:00044`; pp. 69–70; 631 tokens; overlap 1; sections ['IV']
  - Beginning: Perhaps the most discouraging aspect of today's decision is the extent to which the majority feels compelled to sully those on the other side of the debate. The majority offers a c
  - Ending: new expression of commitment to a partner. Celebrate the availability of new benefts. But do not celebrate the Con- stitution. It had nothing to do with it. I respectfully dissent.

**Unit 4: dissent / Scalia — 5 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00045`; pp. 70–71; 330 tokens; overlap 0; sections []
  - Beginning: Justice Scalia, with whom Justice Thomas joins, dissenting. I join The Chief Justice's opinion in full. I write sepa- rately to call attention to this Court's threat to American de
  - Ending: se of liberty, robs the People of the most important liberty they asserted in the Declaration of Independence and won in the Revolution of 1776: the free- dom to govern themselves.

- `obergefell_v_hodges:structure_aware_v1:00049`; pp. 76–78; 616 tokens; overlap 1; sections ['II']
  - Beginning: 22 If, even as the price to be paid for a ffth vote, I ever joined an opinion for the Court that began: “The Constitution promises liberty to all within its reach, a liberty that i
  - Ending: being reminded of our impotence. 25 Ante, at 672. 26 The Federalist No. 78, pp. 522, 523 (J. Cooke ed. 1961) (A. Hamilton). 721 Cite as: 576 U. S. 644 (2015) Thomas, J., dissenting

**Unit 5: dissent / Thomas — 10 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00050`; pp. 78–79; 738 tokens; overlap 0; sections ['I']
  - Beginning: Justice Thomas, with whom Justice Scalia joins, dissenting. The Court's decision today is at odds not only with the Constitution, but with the principles upon which our Nation was 
  - Ending: he results of the political process in over 30 States, based on a provision that guarantees only “due process” is but further evidence of the danger of sub- stantive due process. 1

- `obergefell_v_hodges:structure_aware_v1:00059`; pp. 91–93; 692 tokens; overlap 0; sections ['IV']
  - Beginning: IV Perhaps recognizing that these cases do not actually in- volve liberty as it has been understood, the majority goes to great lengths to assert that its decision will advance the
  - Ending: use, and dis- torts the principles on which this Nation was founded. Its decision will have inestimable consequences for our Constitu- tion and our society. I respectfully dissent.

**Unit 6: dissent / Alito — 4 chunk(s).**

- `obergefell_v_hodges:structure_aware_v1:00060`; pp. 93–95; 694 tokens; overlap 0; sections ['I']
  - Beginning: Justice Alito, with whom Justice Scalia and Justice Thomas join, dissenting. Until the federal courts intervened, the American people were engaged in a debate about whether their S
  - Ending: established tradition. The Justices in the ma- jority claim the authority to confer constitutional protec - tion upon that right simply because they believe that it is fundamental.

- `obergefell_v_hodges:structure_aware_v1:00063`; pp. 98–99; 700 tokens; overlap 0; sections ['III']
  - Beginning: III Today's decision usurps the constitutional right of the peo- ple to decide whether to keep or alter the traditional un- derstanding of marriage. The decision will also have oth
  - Ending: because of their views on the issue of same- sex marriage. But all Americans, whatever their thinking on that issue, should worry about what the majority's claim of power portends.

### Marbury v. Madison

**Unit 0: unknown / unassigned — 14 chunk(s).**

- `marbury_v_madison:structure_aware_v1:00000`; pp. 1–2; 585 tokens; overlap 0; sections []
  - Beginning: DECEMBER, i8ox. it iball have been paid to the creditor. The flieriff may TuRNIM certainly make fuch payment out of court, if no circum- I. ftance occuirs which legally obitructs o
  - Ending: commanding him.to Scaufe to be delivered to them refpedively their feveral Th fupreme commiffions as juftices of the~peace in the diftri& of Co. court of the U States has n lumbia.

- `marbury_v_madison:structure_aware_v1:00013`; pp. 16–17; 433 tokens; overlap 1; sections []
  - Beginning: 3 '. A mandamus will fometimes lie in a FEBRUARY, 1803. doubtful cafe, z Leviiz 123, tobe further confidered on MARBUSY thereturn, 2 Levinz, 14. 1 Siderfin, x69. IV.MA P1SONq. It l
  - Ending: r the county of Wafhington ; and Robert r. Hooe a juftice of the peace for the county of Alexandria, in the diftri&l of Columbia. Afterwards, on the 24 th of February the following

**Unit 1: majority / unassigned — 19 chunk(s).**

- `marbury_v_madison:structure_aware_v1:00014`; pp. 17–19; 845 tokens; overlap 0; sections []
  - Beginning: opinion of the court was delivered by the chief juftice. Opinion of the court. At the laft term on tle affidavits then read and filed with the clerk, a rule was granted in this caf
  - Ending: cers of the United States, whofe ap- " pointments are not otherwife ptovided for." The third fe&ion declares, that ", he fhall commiffion ,, all the officers of the United States."

- `marbury_v_madison:structure_aware_v1:00032`; pp. 44–44; 182 tokens; overlap 1; sections []
  - Beginning: To prefcribe, or to take this oath, be- comes equally a crime. It is alfo not entirely unworthy of obfervation, that in declaring what fhall be the fupreme law of the land, the eon
  - Ending: itten conftitutions, that a law repugnant to. the conftitution is void ; and that rourts, as well as other departments, are bound by that inftrument. 'The rule mufto be difcharged.

### Tinker v. Des Moines School Dist.

**Unit 0: unknown / unassigned — 1 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00000`; pp. 1–1; 13 tokens; overlap 0; sections []
  - Beginning: TINKER v. DES MOINES SCHOOL DIST. 503
  - Ending: TINKER v. DES MOINES SCHOOL DIST. 503

**Unit 1: syllabus / unassigned — 1 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00001`; pp. 1–2; 465 tokens; overlap 0; sections []
  - Beginning: Syllabus. TINKER ET AL. v. DES MOINES INDEPENDENT COMMUNITY SCHOOL DISTRICT ET AL. CERTIORARI TO THE UNITED STATES COURT OF APPEALS FOR THE EIGHTH CIRCUIT. No. 21. Argued November 
  - Ending: Belin. Charles Morgan, Jr., filed a brief for the United States National Student Association, as amicus curiae, urging reversal. OCTOBER TERM, 1968. Opinion of the Court. 393 U. S.

**Unit 2: majority / Fortas — 7 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00002`; pp. 2–3; 621 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE FORTAS delivered the opinion of the Court. Petitioner John F. Tinker, 15 years old, and petitioner Christopher Eckhardt, 16 years old, attended high schools in Des Moin
  - Ending: nc. The court was equally divided, and the District Court's decision was accord- ingly affirmed, without opinion. 383 F. 2d 988 (1967). We granted certiorari. 390 U. S. 942 (1968).

- `tinker_v_des_moines_school_dist:structure_aware_v1:00008`; pp. 11–12; 547 tokens; overlap 1; sections ['II']
  - Beginning: This provision means what it says. We prop- erly read it to permit reasonable regulation of speech- connected activities in carefully restricted circumstances. But we do not confin
  - Ending: which should be granted, this being a matter for the lower courts to determine. We reverse and remand for further pro- ceedings consistent with this opinion. Reversed and remanded.

**Unit 3: concurrence / Stewart — 1 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00009`; pp. 12–13; 211 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE STEWART, concurring. Although I agree with much of what is said in the Court's opinion, and with its judgment in this case, I 514 TINKER v. DES MOINES SCHOOL DIST. 515 
  - Ending: ull capacity for individual choice which is the presupposition of First Amendment guarantees." Id., at 649-650 (con- curring in result). Cf. Prince v. Massachusetts, 321 U. S. 158.

**Unit 4: concurrence / White — 1 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00010`; pp. 13–13; 131 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE WHITE, concurring. While I join the Court's opinion, I deem it appropriate to note, first, that the Court continues to recognize a dis- tinction between communicating b
  - Ending:  Court of Appeals said about free speech in its opinion in Burnside v. Byars, 363 F. 2d 744, 748 (C. A. 5th Cir. 1966), a case relied upon by the Court in the matter now before us.

**Unit 5: dissent / Black — 6 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00011`; pp. 13–15; 882 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE BLACK, dissenting. The Court's holding in this case ushers in what I deem to be an entirely new era in which the power to control pupils by the elected "officials of st
  - Ending:  clearly stated that the rights of free speech and assembly "do not mean that everyone with opinions or beliefs to express may address a group at any public place and at any time."

- `tinker_v_des_moines_school_dist:structure_aware_v1:00016`; pp. 22–24; 550 tokens; overlap 1; sections []
  - Beginning: School discipline, like parental dis- cipline, is an integral and important part of training our children to be good citizens-to be better citizens. Here a very small number of stu
  - Ending: e Federal Constitution compels the teachers, parents, and elected school officials to surrender control of the American pub- lic school system to public school students. I dissent.

**Unit 6: dissent / Harlan — 1 chunk(s).**

- `tinker_v_des_moines_school_dist:structure_aware_v1:00017`; pp. 24–24; 216 tokens; overlap 0; sections []
  - Beginning: MR. JUSTICE HARLAN, dissenting. I certainly agree that state public school authorities in the discharge of their responsibilities are not wholly exempt from the requirements of the
  - Ending:  the good faith of respondents in promulgating the armband regulation, I would affirm the judgment below. 4 Statistical Abstract of the United States (1968), Table No. 578, p. 406.

## Edge cases and readiness

Short legitimate units and final residual chunks remain below 300; the minimum never overrides opinion structure. Front matter and syllabus remain eligible. Raw OCR names and running headers remain as in Phase 4A. Section-marker sentence fragments retain conservative pages and may be smaller than normal sentences. No actual sentence in this corpus exceeds 1100; fallback is exercised by synthetic tests.

The actual fixed baseline averages 602.51 tokens versus 805.48 for this packing policy. Matching the configured target does not match realized granularity; later evaluation should acknowledge this size-distribution difference when interpreting structural effects. No parameter was adjusted using benchmark questions, labels or results.

READY for Phase 4B.2 once separately authorized. This phase creates no embeddings or vector store and makes no retrieval-quality claim.
