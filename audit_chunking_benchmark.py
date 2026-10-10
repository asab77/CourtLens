"""Phase 4C manual audit packaging, source checks, and saved-ranking simulation.

This is NOT a relevance classifier. DECISIONS below are manual judgments made
after reading the eight questions, all 80 retrieved passages, and their extracted
source pages. It never imports the experiment runners, SDK, tokenizer, or FAISS.
Only the two Phase 4C output files can be written by this program.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

from benchmark_relevance import page_range_overlaps, relevant_ranges_for_item


ROOT = Path(__file__).resolve().parent
AUDIT_PATH = Path('data/evaluation/chunking_benchmark_phase4c_audit.json')
REPORT_PATH = Path('data/analysis/chunking_benchmark_phase4c_audit.md')
BENCHMARK = Path('data/evaluation/chunking_benchmark_reviewed.json')
FIXED_RESULTS = Path('data/experiments/chunking/reviewed_results.json')
STRUCTURE_RESULTS = Path('data/experiments/chunking/structure_aware_v1/results.json')
PREVIEW = Path('data/analysis/structure_aware_preview.json')
QUESTION_IDS = ('DRE-01', 'MIR-04', 'MAR-01', 'MAR-04', 'DRE-03', 'OBE-04', 'DRE-04', 'OBE-01')
STRATEGIES = ('fixed_900_150', 'structure_aware_v1')
R, N, A = 'RELEVANT', 'NOT_RELEVANT', 'AMBIGUOUS'


def decision(label, reason, anchor='', additions=()):
    return {'decision': label, 'rationale': reason, 'excerpt_anchor': anchor,
            'proposed_range_additions': [list(pair) for pair in additions]}


# Each list contains fixed ranks 1–5 followed by structure-aware ranks 1–5.
# Rank and similarity are navigation metadata, never inputs to a judgment.
DECISIONS = {
    'DRE-01': [
        decision(R, 'McLean recounts this plaintiff moving from Missouri to Rock Island for two years, then Fort Snelling for two years where the Missouri Compromise prohibited slavery. These residence facts answer a factual question; his opposing legal conclusion does not invalidate the facts.', 'a slave is brought from Missouri', ((167, 167),)),
        decision(N, 'Discusses emancipation precedents and the return from Fort Snelling to Missouri; does not independently give Scott’s residence history in both Illinois and Fort Snelling.', 'When Dred Scott'),
        decision(R, 'The agreed statement of facts identifies Emerson’s removal of Scott to Rock Island in 1834, the 1836 move to Fort Snelling north of 36°30′, and residence there until 1838. Already covered.', 'In the year 1834'),
        decision(N, 'Continues the Fort Snelling/family facts and return to Missouri, but the Illinois residence facts are in the preceding source page, outside this retrieved text. Daniel’s source heading also contradicts the coarse Grier attribution.', 'Fort Snelling'),
        decision(N, 'The Illinois and Fort Snelling facts concern the analogous Rachel v. Walker litigation, not Scott’s own residence history.', 'Rachel'),
        decision(R, 'Independently contains McLean’s concrete account of Scott’s two Illinois years and two Fort Snelling years under a slavery prohibition. The factual wording permits evidence in a dissent.', 'a slave is brought from Missouri', ((167, 167),)),
        decision(R, 'Taney’s opinion repeats the agreed Rock Island/Fort Snelling residence facts and expressly links those stays to the two freedom questions. This is also a majority source, not just a separate-opinion gap.', 'The case, as he himself states it', ((39, 40),)),
        decision(N, 'Describes Rachel v. Walker and other emancipation precedents; these are not the plaintiff’s own Illinois and Fort Snelling residence facts.', 'Rachel'),
        decision(N, 'Gives the legal rejection of territorial freedom and the Illinois/Missouri choice-of-law issue, rather than the specific residence history asked for.', 'But there is another point'),
        decision(N, 'Discusses Illinois law and the Winny v. Whitesides analogy, not Scott’s own residence in both named places.', 'Winny'),
    ],
    'MIR-04': [
        decision(R, 'Warren states cessation on silence/counsel requests, provision of counsel for indigent suspects, and the prosecution’s burden to establish a knowing, intelligent waiver. Already covered.', 'If the individual states'),
        decision(A, 'Clark’s FBI comparison implies counsel-presence and appointment requirements, but the retrieved text largely contrasts FBI practice with the new rule. It ends at the page-67 marker before Clark’s explicit list; accepting the indirect comparison needs human judgment.', 'The offer of coun-'),
        decision(N, 'White criticizes the automatic-coercion premise and discusses the prior totality standard, without independently stating the required safeguards.', 'totality'),
        decision(R, 'Warren expressly requires warning that statements can be used in court and describes the right to counsel present during interrogation. This answers safeguards under the prior standard allowing substantive components, not necessarily the entire rule in every chunk. Already covered.', 'warning'),
        decision(N, 'General statements about voluntariness and procedural safeguards do not enumerate the safeguards. The chunk ends at the page-44 marker; the concrete warning list on source page 44 is absent.', 'Procedural safeguards'),
        decision(R, 'Warren independently lists silence, evidentiary-use, retained/appointed counsel, knowing and intelligent waiver, and cessation when counsel or silence is invoked.', 'Prior to any questioning', ((9, 10),)),
        decision(N, 'White disputes coercion and the old voluntariness standard; this does not independently state the new required safeguards.', 'coercion'),
        decision(R, 'Clark explicitly reports the majority’s new waiver, prosecution-burden, counsel-presence, withdrawal-of-waiver, and indigent-counsel requirements on source page 67. His criticism is separate from this accurate report of safeguards; the question asks what was required, not why the majority justified it.', 'an affirmative', ((67, 67),)),
        decision(N, 'White disputes the factual/constitutional premise for the new rules and contrasts spontaneous and interrogated confessions; it does not state the concrete safeguards.', 'confession'),
        decision(N, 'Warren describes lack of warnings in the four underlying cases and coercive interrogation history. It does not independently tell the reader which warnings and counsel procedures are required.', 'warnings'),
    ],
    'MAR-01': [
        decision(R, 'Marshall identifies Marbury’s withheld commission and mandamus to deliver the commission or its recorded copy. Already covered.', 'commifflon which has'),
        decision(R, 'The Court describes the motion directing delivery to Marbury of his justice-of-the-peace commission and the asserted violated right. Already covered.', 'deliver'),
        decision(R, 'Marshall states that Marbury has legal title to the office, a consequent right to the commission, and that refusal to deliver violates that right and warrants a remedy.', '2dly. That', ((32, 32),)),
        decision(A, 'Describes an applicant kept out of an office and the conditions for mandamus, but the excerpt does not itself specify Marbury’s withheld commission or Madison’s refusal. A broad partial-answer standard might accept it; no addition proposed.', 'Or, in the words'),
        decision(R, 'The Court expressly says the mandamus now sought is to deliver a commission to which the applicant has a vested legal right that the executive cannot take away.', 'It is true that the mandamus', ((36, 36),)),
        decision(R, 'Marshall explains the completed appointment, right to the commission, refusal to deliver, and availability of a legal remedy; substantively answers why he sought the writ.', '2dly. That', ((32, 32),)),
        decision(R, 'The matching Marbury case caption and motion seek an order compelling Madison to deliver the justice-of-the-peace commissions. The preceding Turner/Fendall material is not evidence for this answer. The Marbury portion on page 2 is already covered.', 'WILLIAM MARBURY'),
        decision(R, 'The Marbury-specific portion says the writ seeks delivery of the commission and a vested right prevents the executive from withholding it. The earlier pension-law analogy is not the answer.', 'It is true that the mandamus', ((36, 36),)),
        decision(A, 'An affidavit proves the commission was signed and a general account explains mandamus procedure, but it does not independently establish the withheld commission as the reason for Marbury’s request.', 'affidavit'),
        decision(R, 'The opinion opens with the delivery motion and states that the signed, sealed commission never reached Marbury. Already covered.', 'the commiffion has never'),
    ],
    'MAR-04': [
        decision(A, 'States that authority would fail if the statute is unconstitutional, but does not yet give the Article III allocation or explain why this request is original rather than appellate. Page 38 is only a trailing marker. The conditional preview is an incomplete answer, despite its official page-overlap hit.', 'unconflitutional'),
        decision(N, 'This is counsel’s argument that Congress can confer original jurisdiction and that mandamus is appellate, the position the Court rejects—not the Court’s holding.', 'Congrcfs is not'),
        decision(N, 'Witness examination and examples of access to government records do not explain the Court’s original-jurisdiction limit.', 'The court ordered'),
        decision(N, 'The right to a commission and generic mandamus definition do not answer the separate Article III jurisdiction problem.', 'power of this court'),
        decision(N, 'Introduces the three questions and Marbury’s asserted commission right; gives no reason the Court cannot exercise original jurisdiction.', 'following queflions'),
        decision(N, 'Addresses appointment, commission rights, and generic mandamus, not the constitutional allocation of original jurisdiction.', 'power of this court'),
        decision(N, 'General mandamus procedure and an affidavit that commissions were signed do not state the Court’s jurisdictional holding.', 'affidavit'),
        decision(N, 'Reports counsel’s assertion that Congress is not restrained from conferring original jurisdiction and mandamus can be appellate. This is the argument rejected on source pages 38–40.', 'Congrcfs is not'),
        decision(N, 'The pension-case analogy and proper-remedy discussion do not reach the original/appellate distinction or Article III’s exclusive allocation.', 'It is true that the mandamus'),
        decision(N, 'Sets out the motion, appointment, and delivery facts; no constitutional jurisdictional holding appears.', 'following queflions'),
    ],
    'DRE-03': [
        decision(R, 'Taney reasons from founding-era state citizenship, the Confederation’s racial exclusions, and limits on states creating national citizenship. This is the controlling opinion’s exclusion rationale. Already covered.', 'The Constitution upon'),
        decision(N, 'Frames the citizenship issue, scope of the pleadings, and jurisdictional review. Merely posing the question is not the substantive historical/constitutional reasoning supporting the conclusion, despite the official page-overlap hit.', 'The question.is simply'),
        decision(R, 'Taney uses discriminatory state laws and asserted founding-era status to infer that the framers did not include this population as constitutional citizens. Already covered.', 'The legislation of the States'),
        decision(N, 'Curtis argues that founding-era Black state citizens remained national citizens and gives his own contrary citizenship rule. It does not independently state the Court’s exclusion rationale.', 'my opinion is'),
        decision(N, 'Curtis uses state citizenship and the rejected attempt to insert “white” in the Confederation to argue the opposite of the Court’s conclusion.', 'free colored persons'),
        decision(N, 'Curtis’s contrary founding-era citizenship and Confederation argument is a dissenting rebuttal, not the Court’s supporting reasoning.', 'free colored persons'),
        decision(R, 'Taney infers exclusion from the change from inhabitants to citizens and early congressional naturalization laws limited to white persons. Already covered.', 'The word citizen excluded'),
        decision(N, 'Curtis explicitly concludes that free Black state citizens are national citizens and dissents from the majority’s exclusion. Semantic overlap does not answer what reasoning the Court used.', 'I dissent'),
        decision(N, 'The Court explains why the citizenship plea is before it and frames the issue; it does not yet give the substantive reasoning for the citizenship conclusion.', 'The question.is simply'),
        decision(R, 'Taney describes constitutional treatment as property, asserted consequences of state-created citizenship, and fixed founding-era meaning; he synthesizes the historical and governmental evidence for exclusion.', 'The only two provisions', ((33, 34),)),
    ],
    'OBE-04': [
        decision(R, 'Kennedy expressly explains the independent but mutually instructive liberty/equality principles and their convergence in defining the marriage right. Already covered.', 'The Due Process Clause'),
        decision(R, 'Roberts quotes and explicitly attributes the majority’s mutually instructive and converging principles. Verified against Kennedy on source page 29. The quoted reasoning answers the question; Roberts’s disagreement does not convert the quote into his own contrary rule.', '“Rights implicit', ((64, 64),)),
        decision(A, 'Roberts summarizes the majority’s “synergy” and shared precedents but calls the discussion difficult to follow; the full attributed majority quote is on page 64 and absent from this marker-ending chunk. Whether this terse critical summary alone suffices needs judgment.', 'The central point'),
        decision(N, 'Roberts disputes due-process reasoning and describes substantive due process, without explaining the majority’s connection to equal protection.', 'Due Process Clause'),
        decision(R, 'The syllabus substantively explains mutually instructive principles, their interlocking application, and the combined liberty/equality injury in same-sex marriage. Already covered.', 'The Due Process Clause'),
        decision(R, 'The dissent independently contains a clearly attributed verbatim majority explanation of mutually instructive, converging liberty/equality principles, confirmed on source page 29. Accept that evidence, not Roberts’s subsequent critique.', '“Rights implicit', ((64, 64),)),
        decision(R, 'Kennedy explains the interrelation and illustrates it with Loving and Zablocki. Already covered.', 'The Due Process Clause'),
        decision(R, 'Kennedy applies interlocking liberty and equality protections to same-sex couples and says both clauses prohibit the infringement. Already covered.', 'This dynamic also applies'),
        decision(R, 'The closing passage explicitly derives the marriage right from both liberty and equal protection and connects the clauses. Earlier parts give exclusion/stigma context. Already covered.', 'The right of same-sex couples to marry'),
        decision(N, 'Roberts’s account of the petitioners’ claims and attack on due-process reasoning does not explain the majority’s linkage of the two clauses.', 'Due Process Clause'),
    ],
    'DRE-04': [
        decision(N, 'McLean discusses slavery as a state institution and importation/state trade powers, not the Court’s constitutional restriction on Congress governing the federal territory.', 'State institution'),
        decision(N, 'Curtis sets out several competing theories presented in argument and rejects inserting political exceptions into the Territory Clause. He does not attribute a supporting rationale to the controlling opinion.', 'While the third'),
        decision(N, 'Nelson’s discussion concerns Missouri status after return and extraterritorial operation of a law; that is a different ground from Congress’s inability to prohibit slavery within the federal territory.', 'within the State of Missouri'),
        decision(A, 'Campbell expressly denies territorial power to dissolve master/slave relations, but presents his own construction of the Territory Clause. It is not independently identified as Taney’s controlling property/due-process rationale. Human review is needed on whether this supporting concurrence satisfies “the Court.”', 'in my opinion'),
        decision(N, 'Curtis attacks the property/due-process argument with state importation prohibitions and the slave-trade analogy. A contrary response is not the Court’s supporting reasoning.', 'due process'),
        decision(A, 'Campbell argues lack of municipal sovereignty in the territories and reports the Court’s limits on interstate migration controls. The territorial conclusion is his own construction; no clear attribution to the controlling rationale. Do not add automatically.', 'Aiid, in my opinion'),
        decision(A, 'The source is Daniel, although saved parser metadata says Grier. His concurrence’s equal-access and constitutionally protected slave-property argument overlaps the majority’s reasoning on pages 3 and 59–60, but this is a separately stated argument rather than an identified quotation of that reasoning. Whether the wording permits it needs human judgment.', 'Nothing can be more conclusive'),
        decision(N, 'McLean’s state-institution and historical importation discussion is not the Court’s reasoning about prohibiting slaveholding in the federal territory.', 'State institution'),
        decision(N, 'Catron analyzes limits arising from cession compacts and treaty protections. This is a distinct separate-opinion theory, not the controlling territorial property/due-process explanation asked for.', 'My opinion is'),
        decision(N, 'Campbell discusses municipal sovereignty, Missouri’s state admission, and asks the territorial-power question without independently supplying the controlling answer.', 'Can Congress determine'),
    ],
    'OBE-01': [
        decision(A, 'Kennedy states the licensing holding and discusses the recognition question in section V, but does not independently identify BOTH as the two questions limited in the grant of review. Accepting a holding-based reconstruction rather than the procedural fact needs judgment.', 'These cases also present'),
        decision(N, 'Roberts describes petitioners’ claims to licensing/recognition and his preferred affirmance; this is not the Court’s specification of the two constitutional questions it agreed to decide.', 'Petitioners brought'),
        decision(N, 'Kennedy discusses debate, caution, and constitutional adjudication without identifying the two questions.', 'Constitution'),
        decision(N, 'Alito discusses consequences and judicial power, not the two questions granted review.', 'Constitution'),
        decision(A, 'The syllabus reports licensing/recognition claims and a holding addressing both, but does not specify the two questions in the limited grant of review. The existing standard for this procedural question requires both granted questions, not just the disposition.', 'Held:'),
        decision(N, 'Kennedy’s legal/history narrative covers Baehr, DOMA, and later developments, not both questions in the grant of review.', 'Defense of Marriage'),
        decision(A, 'Kennedy combines the licensing holding with the section-V recognition question and disposition. This is a plausible substantive reconstruction, but it does not explicitly report BOTH granted questions as on source page 13.', 'These cases also present'),
        decision(N, 'Explicitly says review was granted on the right-to-marry issue and discusses petitioners’ injuries, but does not independently identify the second granted recognition question.', 'Court granted review'),
        decision(A, 'The syllabus describes both claims and their disposition, not explicitly the two limited questions the Court granted review to decide. No range addition without resolving this procedural-versus-holding standard.', 'Held:'),
        decision(N, 'Roberts criticizes the majority’s licensing/recognition result; that criticism does not identify both questions in the Court’s grant of review.', 'license'),
    ],
}

CONCLUSIONS = {
    'DRE-01': 'Confirmed incomplete: majority restatement on pages 39–40 and Scott-specific factual narrative in McLean’s dissent on page 167 independently answer the question. A blanket exclusion of separate opinions was too restrictive for residence facts.',
    'MIR-04': 'Confirmed incomplete: Warren’s pages 9–10 give the required safeguards independently. Clark’s page 67 also accurately lists several new requirements while criticizing them. The question asks what safeguards were required, so accurate reports are admissible evidence; it does not ask for Clark’s rationale.',
    'MAR-01': 'Confirmed incomplete: pages 32 and 36 expressly give the violated commission right and the delivery remedy. Topic-only mandamus discussions remain ambiguous or irrelevant.',
    'MAR-04': 'No confirmed addition from these candidates. The accepted source pages 38–40 explain Article III’s allocation and why this writ would be original. Fixed rank 1 only previews unconstitutionality on page 37 and carries an empty page-38 marker: an apparent page-level false positive/incomplete answer, not evidence that every accepted page range is wrong.',
    'DRE-03': 'Confirmed incomplete on pages 33–34. Curtis’s high-ranked dissent provides the contrary citizenship theory, not the Court’s exclusion rationale. The issue-framing chunks on pages 10–11/11–12 also illustrate overinclusive page-level credit.',
    'OBE-04': 'Confirmed incomplete on page 64: Roberts reproduces the majority’s actual explanation, verified on majority page 29. This is relevant quoted majority reasoning, although Roberts’s own criticism is not controlling reasoning. The preceding page-63 summary is ambiguous.',
    'DRE-04': 'No unambiguous addition from the saved Top-5. The question asks for the Court’s reason, and the accepted pages 3–4 summarize constitutional property/equal-access limits. Majority pages 58–60 confirm the property/due-process rationale as context only, not an addition proposed in this candidate-limited audit. Campbell and Daniel concurrences need human judgment; McLean, Curtis, Nelson, and Catron passages do not independently establish that controlling rationale. The Grier/Daniel attribution discrepancy is documented, not repaired.',
    'OBE-01': 'No unambiguous addition. Page 13 explicitly enumerates the two limited granted questions: Fourteenth Amendment licensing and recognition of lawful out-of-state same-sex marriages. A holding/syllabus reconstruction is ambiguous under this procedural wording. Retain the current ranges pending human judgment.',
}


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def digest(value):
    return hashlib.sha256(serialized(value).encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def protected_snapshot(root=ROOT):
    paths = set()
    for directory in ('data/processed', 'data/chunks', 'data/vector_store', 'data/experiments/chunking', 'data/evaluation'):
        paths.update(p for p in (root / directory).rglob('*') if p.is_file())
    for stem in ('long_sentence_analysis', 'structure_aware_chunking', 'structure_aware_preview', 'structure_aware_retrieval_evaluation'):
        paths.update(root / 'data/analysis' / (stem + suffix) for suffix in ('.json', '.md'))
    paths.update(root / name for name in ('parse_legal_structure.py', 'generate_structure_aware_chunks.py', 'run_structure_aware_experiment.py'))
    return {str(p.relative_to(root)): file_digest(p) for p in sorted(paths)
            if p.exists() and p != root / AUDIT_PATH}


def source_pages(text):
    pieces = re.split(r'^===== PAGE (\d+) =====\s*$', text, flags=re.M)
    pages = {int(pieces[i]): pieces[i + 1] for i in range(1, len(pieces), 2)}
    if not pages:
        raise ValueError('Canonical source has no extracted PDF page markers')
    return pages


def normalized(text):
    text = re.sub(r'^===== PAGE \d+ =====\s*$', '', text, flags=re.M)
    text = re.sub(r'^(CASE_NAME|SOURCE_FILE|ORIGINAL_SOURCE_FILE|DOCUMENT_PAGES):.*$', '', text, flags=re.M)
    return ' '.join(text.split())


def excerpt(text, anchor):
    text = normalized(text)
    start = text.casefold().find(normalized(anchor).casefold()) if anchor else 0
    if start < 0:
        raise ValueError(f'Manual excerpt anchor not found: {anchor!r}')
    return text[start:start + 850]


def configurations(root):
    fixed = next(c for c in read_json(root / FIXED_RESULTS)['configurations'] if c['id'] == '900_150')
    structure = next(c for c in read_json(root / STRUCTURE_RESULTS)['configurations'] if c['id'] == 'structure_aware_v1')
    return dict(zip(STRATEGIES, (fixed, structure)))


def load_candidates(root, configs, question_id):
    candidates = []
    for strategy in STRATEGIES:
        question = next(q for q in configs[strategy]['questions'] if q['id'] == question_id)
        saved = question['metrics']['retrieved'][:5]
        if [c['rank'] for c in saved] != [1, 2, 3, 4, 5]:
            raise ValueError(f'Expected five ordered saved candidates: {question_id} {strategy}')
        for candidate in saved:
            row = copy.deepcopy(candidate)
            if strategy == 'fixed_900_150':
                path = root / 'data/experiments/chunking/900_150/chunks' / (Path(row['source_file']).stem + '.jsonl')
                records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
                record = next(r for r in records if r['metadata']['chunk_index'] == row['chunk_index'])
                for key in ('case_name', 'source_file', 'page_start', 'page_end', 'chunk_index'):
                    if row[key] != record['metadata'][key]:
                        raise ValueError(f'Saved ranking/chunk mismatch: {question_id} {key}')
                row['text'] = record['text']
            row['retrieval_strategy'] = strategy
            candidates.append(row)
    return candidates


def opinion_context(candidate, preview):
    doc = next(d for d in preview['documents'] if d['source_file'] == candidate['source_file'])
    units = [u for u in doc['major_units'] if u['page_start'] <= candidate['page_end'] and u['page_end'] >= candidate['page_start']]
    raw = [{'opinion_type': u['opinion_type'], 'author': u['author'], 'pages': [u['page_start'], u['page_end']]} for u in units]
    # Source-confirmed corrections are audit annotations only, not parser changes.
    source = candidate['source_file']
    if source == 'dred_scott_v_sandford.pdf' and 78 <= candidate['page_start'] <= candidate['page_end'] <= 101:
        return 'concurrence', 'Daniel', raw, 'Source pp77–79 show Daniel begins after Grier on p77; running headings confirm Daniel. Saved parser attribution remains untouched.'
    if candidate.get('opinion_type'):
        author = {'Tane': 'Taney', 'Mclean': 'McLean', 'Oatron': 'Catron', 'Lnelson': 'Nelson'}.get(candidate.get('author'), candidate.get('author'))
        return candidate['opinion_type'], author, raw, 'Saved attribution checked against source context; OCR names normalized for display only. Null authors remain unknown.'
    if len(raw) == 1:
        u = raw[0]
        author = {'Tane': 'Taney', 'Mclean': 'McLean', 'Oatron': 'Catron', 'Lnelson': 'Nelson'}.get(u['author'], u['author'])
        return u['opinion_type'], author, raw, 'Source context plus existing parser page span; page-level attribution is approximate.'
    return 'mixed_or_unassigned', None, raw, 'Multiple/unassigned parser units overlap; source context controls the judgment, not coarse unit labels.'


def build_audit(root=ROOT):
    """Package predetermined manual decisions; do not compute proposed metrics."""
    configs = configurations(root)
    benchmark = read_json(root / BENCHMARK)
    by_id = {q['id']: q for q in benchmark['questions']}
    preview = read_json(root / PREVIEW)
    questions = []
    for qid in QUESTION_IDS:
        q = by_id[qid]
        candidates = load_candidates(root, configs, qid)
        if len(DECISIONS[qid]) != len(candidates):
            raise ValueError(f'Manual decisions/candidates disagree: {qid}')
        rows = []
        for c, judgment in zip(candidates, DECISIONS[qid]):
            source_path = Path('data/processed') / (Path(c['source_file']).stem + '.txt')
            raw_source = (root / source_path).read_text(encoding='utf-8')
            pages = source_pages(raw_source)
            corpus_span = ' '.join(pages[n] for n in range(c['page_start'], c['page_end'] + 1))
            if normalized(c['text']) not in normalized(corpus_span):
                raise ValueError(f'Candidate not found on declared source pages: {qid} {c["retrieval_strategy"]} {c["rank"]}')
            opinion, author, raw_units, attribution_note = opinion_context(c, preview)
            markers = re.findall(r'^===== PAGE (\d+) =====\s*$', c['text'], flags=re.M)
            empty_end = bool(markers and int(markers[-1]) == c['page_end'] and not c['text'].rsplit('=====', 1)[-1].strip())
            additions = judgment['proposed_range_additions']
            if additions and judgment['decision'] != R:
                raise ValueError('Only confirmed relevant evidence may propose a range')
            source_evidence = []
            for start, end in additions:
                if start < c['page_start'] or end > c['page_end']:
                    raise ValueError('Proposed evidence pages must be within this candidate')
                source_evidence.append({'pages': [start, end], 'canonical_text': '\n'.join(pages[n].strip() for n in range(start, end + 1))})
            row = {key: c.get(key) for key in ('rank', 'case_name', 'source_file', 'original_source_file', 'chunk_index', 'chunk_id', 'similarity', 'vector_id')}
            row.update({
                'candidate_id': f'{qid}:{c["retrieval_strategy"]}:{c["rank"]}',
                'retrieval_strategy': c['retrieval_strategy'], 'pages': [c['page_start'], c['page_end']],
                'candidate_source': str(source_path), 'source_sha256': file_digest(root / source_path),
                'opinion_type': opinion, 'author': author, 'saved_opinion_type': c.get('opinion_type'),
                'saved_author': c.get('author'), 'parser_page_context': raw_units, 'attribution_note': attribution_note,
                'source_verified': True, 'source_verification': 'Entire candidate matches the declared canonical page span after whitespace/metadata/page-marker removal only; OCR is not corrected.',
                'trailing_page_marker_without_text': empty_end,
                'official_page_overlap_relevant': c['relevant'],
                'evidence_excerpt': excerpt(c['text'], judgment['excerpt_anchor']),
                'full_candidate_text': c['text'], 'decision': judgment['decision'],
                'rationale': judgment['rationale'], 'proposed_range_additions': copy.deepcopy(additions),
                'canonical_proposed_page_evidence': source_evidence,
            })
            rows.append(row)
        additions = sorted({tuple(p) for c in rows for p in c['proposed_range_additions']})
        questions.append({'question_id': qid, 'question': q['question'], 'question_type': q['type'],
                          'case_name': q['expected_case'], 'expected_source_file': q['expected_source_file'],
                          'current_accepted_ranges': relevant_ranges_for_item(q), 'candidates': rows,
                          'proposed_range_additions': [list(p) for p in additions],
                          'benchmark_appears_incomplete': bool(additions),
                          'conclusion': CONCLUSIONS[qid]})
    audit = {'phase': '4C', 'status': 'PROPOSED AUDIT — LABELS NOT APPLIED',
             'scope': list(QUESTION_IDS), 'candidate_count': sum(len(q['candidates']) for q in questions),
             'method': 'Manual passage-level judgments, source-verified against extracted CourtLens texts. Rank/similarity are navigation only. No automatic relevance classifier.',
             'standard': 'Require independent substantive evidence for the question. Components of a multi-part safeguards answer may qualify, as in the previous review. For Court-reasoning questions, distinguish supporting controlling reasoning from opposing theories. Accurate attributed majority quotations can answer even when embedded in a dissent; factual residence narratives are not excluded by opinion type. Ambiguous procedural/holding and concurrence boundaries are not proposed as additions.',
             'input_sha256': {str(p): file_digest(root / p) for p in (BENCHMARK, FIXED_RESULTS, STRUCTURE_RESULTS, PREVIEW)},
             'questions': questions}
    audit['frozen_decisions_sha256'] = digest(questions)
    return audit


def validate_frozen(audit, root=ROOT):
    if audit['scope'] != list(QUESTION_IDS) or [q['question_id'] for q in audit['questions']] != list(QUESTION_IDS):
        raise ValueError('Audit must cover exactly the eight Phase 4C questions in order')
    if digest(audit['questions']) != audit['frozen_decisions_sha256']:
        raise ValueError('Frozen decisions changed; rebuild the audit before simulation')
    for path, expected in audit['input_sha256'].items():
        if file_digest(root / path) != expected:
            raise ValueError(f'Frozen audit input changed: {path}')


def first_rank(saved_question, benchmark_item):
    """Existing case + source + inclusive page-overlap rule, on saved Top-5."""
    for row in saved_question['metrics']['retrieved'][:5]:
        if row['case_name'] != benchmark_item['expected_case']:
            continue
        expected = benchmark_item.get('expected_source_file')
        if expected and expected not in {row.get('source_file'), row.get('original_source_file')}:
            continue
        if page_range_overlaps(row['page_start'], row['page_end'], relevant_ranges_for_item(benchmark_item)):
            return row['rank']
    return None


def rank_metrics(ranks):
    count = len(ranks)
    if not count:
        raise ValueError('No saved questions to score')
    return {'question_count': count,
            **{f'hit_at_{k}': sum(r is not None and r <= k for r in ranks) / count for k in (1, 3, 5)},
            'mrr': sum(1 / r if r else 0 for r in ranks) / count}


def simulate(audit, root=ROOT):
    """Called only after the decision artifact has been frozen and saved."""
    validate_frozen(audit, root)
    benchmark = read_json(root / BENCHMARK)
    proposed = copy.deepcopy(benchmark)
    original_map = {q['id']: q for q in benchmark['questions']}
    proposed_map = {q['id']: q for q in proposed['questions']}
    for q in audit['questions']:
        proposed_map[q['question_id']]['relevant_ranges'] = q['current_accepted_ranges'] + q['proposed_range_additions']
    output = {'status': 'SIMULATED — PROPOSED LABELS NOT APPLIED',
              'decision_sha256': audit['frozen_decisions_sha256'],
              'method': 'Re-score all 40 SAVED Top-5 rankings using unchanged case/source/page-overlap and Hit@K/MRR rules, with only the eight frozen audit proposals added in memory. No reranking, embeddings, retrieval, or passage-decision substitution.',
              'limitation': 'Page-overlap scoring remains coarse. A trailing empty page marker can obtain credit, and a partly irrelevant chunk on a newly labeled page can obtain credit. These metrics are not passage-level ground truth and do not resolve ambiguity.',
              'strategies': {}}
    for strategy, config in configurations(root).items():
        saved = config['questions']
        if len(saved) != 40 or len({q['id'] for q in saved}) != 40 or {q['id'] for q in saved} != set(original_map):
            raise ValueError('Simulation requires all 40 unique saved benchmark rankings')
        baseline = [first_rank(q, original_map[q['id']]) for q in saved]
        after = [first_rank(q, proposed_map[q['id']]) for q in saved]
        baseline_metrics = rank_metrics(baseline)
        for key, value in baseline_metrics.items():
            if abs(value - config['metrics'][key]) > 1e-12:
                raise ValueError(f'Saved baseline metrics do not reproduce: {strategy} {key}')
        output['strategies'][strategy] = {'official_reproduced': baseline_metrics, 'simulated': rank_metrics(after),
            'audited_ranks': [{'question_id': q['id'], 'official_first_relevant_rank': before,
                               'simulated_first_relevant_rank': new}
                              for q, before, new in zip(saved, baseline, after) if q['id'] in QUESTION_IDS]}
    return output


def report(audit):
    lines = ['# CourtLens Phase 4C — targeted benchmark audit', '',
             '**PROPOSED AUDIT — LABELS NOT APPLIED.** Exactly eight questions; 80 candidate appearances (five saved results from each strategy per question).', '',
             audit['method'], '', audit['standard'], '',
             'Decisions were made from the question and complete source-verified text before computing any proposed metric impact. The initial JSON was written without a simulation; its questions are frozen by SHA-256. The optional simulation reads that frozen artifact.', '',
             'PDF page numbers are extraction markers, not printed reporter pagination. Evidence excerpts normalize whitespace only; full retrieved text and canonical proposed-page text are in the JSON. OCR spellings and dates are not silently repaired. Similarity does not determine a decision.', '',
             '## Proposed additions — do not apply', '',
             '| Question | Current ranges | Proposed additions | Conclusion |', '|---|---|---|---|']
    for q in audit['questions']:
        lines.append(f'| {q["question_id"]} | {q["current_accepted_ranges"]} | {q["proposed_range_additions"] or "None"} | {q["conclusion"]} |')
    lines += ['', '## All candidate decisions', '', 'R = RELEVANT; N = NOT_RELEVANT; A = AMBIGUOUS. Columns list ranks 1–5 in order. See evidence and rationale below for each appearance.', '',
              '| Question | Fixed 900/150 ranks 1–5 | Structure-aware ranks 1–5 |', '|---|---|---|']
    labels = {R: 'R', N: 'N', A: 'A'}
    for q in audit['questions']:
        cells = [', '.join(labels[c['decision']] for c in q['candidates'] if c['retrieval_strategy'] == strategy) for strategy in STRATEGIES]
        lines.append(f'| {q["question_id"]} | {cells[0]} | {cells[1]} |')
    lines += ['', '## Limitations and human judgments', '',
              '- This audit only assesses the selected eight questions and their saved Top-5 candidates. “No confirmed addition” does not establish that every relevant passage in the entire opinion is labeled.',
              '- Page ranges are a coarse proxy. MAR-04 fixed rank 1 lacks the original/appellate rationale, DRE-03 issue-framing chunks lack the supporting citizenship rationale, and MIR-04 fixed rank 5 lacks the page-44 warning list. Official page-overlap credit is preserved in the simulation, not mistaken for manual relevance.',
              '- MIR-04 fixed rank 2 ends with a page-67 marker before the actual explicit list. Adding page 67 can credit that chunk mechanically even though its FBI comparison remains ambiguous. OBE-04 fixed rank 3 similarly ends with a page-64 marker before the majority quotation.',
              '- OBE-01 holding/syllabus passages identify licensing and recognition substantively but do not explicitly identify both limited granted questions. Four candidates remain ambiguous; source page 13 is the clear procedural answer.',
              '- DRE-04 Campbell and Daniel supporting concurrences remain ambiguous under “the Court”: shared themes/conclusions alone do not establish the controlling reason. Curtis/McLean rebuttals and Nelson/Catron alternative grounds are not added.',
              '- DRE-01 fixed rank 4 and DRE-04 structure rank 2 have Daniel source headings, although the existing parser page span labels the material Grier. This annotation corrects the audit attribution only; parser, chunks, and metadata remain untouched. Other OCR names are normalized only for audit display; uncertain authors remain null.',
              '- The original accepted ranges are not removed or narrowed. Previously credited passages can be incomplete answers; resolving that scoring limitation requires a separately approved benchmark decision.', '',
              '## Per-question evidence', '']
    for q in audit['questions']:
        lines += [f'### {q["question_id"]} — {q["case_name"]}', '', q['question'], '',
                  f'Type: `{q["question_type"]}`. Current ranges: {q["current_accepted_ranges"]}. Proposed additions: {q["proposed_range_additions"] or "None"}.', '', q['conclusion'], '']
        for c in q['candidates']:
            lines += [f'**{c["retrieval_strategy"]}, rank {c["rank"]}, PDF pp{c["pages"][0]}–{c["pages"][1]}, chunk {c["chunk_index"]}: {c["decision"]}**', '',
                      f'Source: `{c["candidate_source"]}`; opinion: {c["opinion_type"]}; author: {c["author"] or "not established"}; similarity (navigation only): {c["similarity"]:.6f}; official page-overlap relevance: {c["official_page_overlap_relevant"]}.', '',
                      '> ' + c['evidence_excerpt'].replace('\n', '\n> '), '', c['rationale'], '',
                      f'Proposed addition: {c["proposed_range_additions"] or "None (already covered, not relevant, or unresolved)"}. Canonical source match: verified.', '']
            if c['trailing_page_marker_without_text']:
                lines += ['Extraction caveat: the final page marker has no following page text in this retrieved chunk.', '']
            if 'Daniel' in c['attribution_note']:
                lines += [c['attribution_note'], '']
    if 'simulation' in audit:
        sim = audit['simulation']
        lines += ['## SIMULATED — PROPOSED LABELS NOT APPLIED', '', sim['method'], '', sim['limitation'], '',
                  '| Strategy | Labels | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---|---:|---:|---:|---:|']
        for strategy, entry in sim['strategies'].items():
            for key, label in [('official_reproduced', 'Official, reproduced locally'), ('simulated', 'SIMULATED — proposed only')]:
                m = entry[key]
                lines.append(f'| {strategy} | {label} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
        lines += ['', '| Question | Fixed official → simulated rank | Structure official → simulated rank |', '|---|---|---|']
        rank_maps = {s: {q['question_id']: q for q in e['audited_ranks']} for s, e in sim['strategies'].items()}
        for qid in QUESTION_IDS:
            cells = []
            for s in STRATEGIES:
                q = rank_maps[s][qid]
                cells.append(f'{q["official_first_relevant_rank"] or "miss"} → {q["simulated_first_relevant_rank"] or "miss"}')
            lines.append(f'| {qid} | {cells[0]} | {cells[1]} |')
    if 'protected_artifacts' in audit:
        verification = audit['protected_artifacts']
        lines += ['', '## Protected artifact verification', '',
                  f'All {verification["file_count"]} protected files are byte-identical by SHA-256 before/after audit processing and simulation. No network/API/embedding call, retrieval, chunk regeneration, vector-store write, commit, or push occurred.', '',
                  f'Frozen decisions SHA-256: `{audit["frozen_decisions_sha256"]}`.', '',
                  '| Protected file | SHA-256 before = after |', '|---|---|']
        lines += [f'| `{p}` | `{h}` |' for p, h in verification['before_sha256'].items()]
    return '\n'.join(lines) + '\n'


def write_outputs(audit, root=ROOT):
    for path, text in ((AUDIT_PATH, serialized(audit)), (REPORT_PATH, report(audit))):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulate', action='store_true', help='Read the already-frozen audit and add an unofficial saved-ranking simulation')
    args = parser.parse_args()
    before = protected_snapshot()
    if args.simulate:
        audit = read_json(ROOT / AUDIT_PATH)
        audit['simulation'] = simulate(audit)
    else:
        audit = build_audit()
    after = protected_snapshot()
    if after != before:
        raise RuntimeError('Protected artifacts changed during audit processing')
    audit['protected_artifacts'] = {'file_count': len(before), 'unchanged': True, 'before_sha256': before, 'after_sha256': after}
    write_outputs(audit)
    if protected_snapshot() != before:
        raise RuntimeError('Protected artifacts changed while writing audit outputs')
    print(f'Wrote {AUDIT_PATH} and {REPORT_PATH}; {len(QUESTION_IDS)} questions, {audit["candidate_count"]} candidates. Protected files unchanged: {len(before)}.')
    print(f'Frozen manual decisions SHA-256: {audit["frozen_decisions_sha256"]}')
    if args.simulate:
        print('SIMULATED — PROPOSED LABELS NOT APPLIED')


if __name__ == '__main__':
    main()
