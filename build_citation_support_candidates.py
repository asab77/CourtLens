"""Local, manually curated proposed dataset builder. No verifier or provider calls.

Labels/claims below are Codex proposals, not independently human-adjudicated.
Only the two named NEW dataset/review paths may be written by main.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SMOKE = 'data/analysis/phase7a3_smoke_test.json'
RECORDS = 'data/experiments/chunking/structure_aware_v1/vector_store/records.jsonl'
CHUNKS = 'data/experiments/chunking/structure_aware_v1/chunks.jsonl'
CANDIDATES = 'data/evaluation/citation_support_candidates.json'
REVIEW = 'data/evaluation/citation_support_review.md'
GUIDELINES = 'docs/citation_support_labeling_guidelines.md'
LABELS = {
 'SUPPORTED': 'The cited passage establishes every material proposition and attribution of the claim, with necessary qualifications preserved.',
 'PARTIALLY_SUPPORTED': 'The passage establishes a meaningful part but not all of the claim, its scope, or a necessary qualification; identify the supported and missing parts.',
 'UNSUPPORTED': 'The passage does not establish the material claim or asserted attribution. Topic overlap, a valid ID, and plausibility outside the passage are insufficient; absence alone is not contradiction.',
 'CONTRADICTED': 'The passage affirmatively states a proposition incompatible with the claim, including an explicitly reversed position. Distinguish this from mere missing support.'}
CATEGORIES = dict(zip('ABCDEFGHIJKLMNO', [
 'Direct factual support','Correct legal holding attribution','Partial support','Unsupported conclusion',
 'Contradiction','Majority versus dissent confusion','Concurrence cited for majority reasoning',
 'Correct majority quotation reproduced inside dissent','Misleading topically related citation',
 'Missing legal qualification','Multi-part claim with incomplete support','Accurate quotation versus inaccurate paraphrase',
 'Uncertainty in OCR-derived attribution','Correct insufficient-evidence response','Unsupported out-of-corpus answer']))


def sha(data): return hashlib.sha256(data).hexdigest()
def encode(value): return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n'


def build_dataset():
    smoke=json.loads((ROOT/SMOKE).read_text())
    rows=[json.loads(line) for line in (ROOT/RECORDS).read_text().splitlines()]
    chunks=[json.loads(line) for line in (ROOT/CHUNKS).read_text().splitlines()]
    by_id={r['metadata']['chunk_id']:r for r in rows}
    frozen={r['metadata']['chunk_id']:r for r in chunks}
    cases={c['id']:c for c in smoke['cases']}
    passages={}; bindings={}
    for cid,case in cases.items():
        for record in case['result']['evidence']:
            key=cid+record['source_id']; passages[key]=record
            bindings[key]={'kind':'smoke_generation_context','case_id':cid,'citation_identifier':record['source_id'],
                           'json_pointer':f"/cases/{list(cases).index(cid)}/result/evidence/{case['result']['evidence'].index(record)}"}
    for key,chunk_id in [('H','gideon_v_wainwright:structure_aware_v1:00011'),
                         ('W','new_york_times_co_v_united_states:structure_aware_v1:00013'),
                         ('T','tinker_v_des_moines_school_dist:structure_aware_v1:00009')]:
        passages[key]=by_id[chunk_id]
        bindings[key]={'kind':'constructed_local_context','case_id':None,'citation_identifier':'S1',
                       'json_pointer':None}
    for key,record in passages.items():
        chunk_id=record['metadata']['chunk_id']
        assert record['text']==by_id[chunk_id]['text']==frozen[chunk_id]['text']
        assert record['metadata']==by_id[chunk_id]['metadata']==frozen[chunk_id]['metadata']
    q=lambda key: cases[key[0]]['question'] if key[0] in cases else {
        'H':'How did Harlan describe Betts v. Brady in his Gideon concurrence?',
        'W':'What position did White take on prior restraints in New York Times Co. v. United States?',
        'T':'What did Stewart say about children’s First Amendment rights in Tinker?'}[key]
    specs=[]
    def add(key,claim,label,categories,reason,origin='synthetic',attention=False,components=None):
        specs.append((key,claim,label,categories,reason,origin,attention,components))
    add('AS1','The person must be warned prior to questioning that they have the right to remain silent.','SUPPORTED','AB','S1 explicitly requires a warning of the right to remain silent before questioning, subject to the passage’s alternative-safeguards framework. This isolated warning description does not assert that alternatives are forbidden.','verbatim_smoke')
    add('AS1','The person must be informed that any statement they do make can be used as evidence against them.','SUPPORTED','A','S1 explicitly describes the warning that any statement may be used as evidence.','verbatim_smoke')
    add('AS2','If the person is indigent, a lawyer will be appointed to represent them.','SUPPORTED','ABM','The extracted Syllabus text explicitly states the indigence/appointed-lawyer warning. The claim describes its substance; it does not invent an author for the unknown-labeled source.','verbatim_smoke',True)
    add('AS1','The waiver of these rights must be made voluntarily, knowingly, and intelligently.','SUPPORTED','AB','S1 states that a waiver must be voluntary, knowing and intelligent.','verbatim_smoke')
    add('AS3','The Court reversed Miranda’s conviction after finding his confession inadmissible without effective protection of his rights.','SUPPORTED','AB','The passage says “We reverse” and explains the missing warnings and lack of otherwise effective protection. The qualification is preserved.')
    b_sentence=cases['B']['result']['content'].split('\n\n')[0].split('. The Court')[0]+'.'
    add('BS2',b_sentence,'SUPPORTED','B','Kennedy majority S2 explicitly says the two clauses are profoundly connected but independent.','verbatim_smoke')
    quote_text=passages['BS2']['text']; start=quote_text.index('Each con'); exact_quote=quote_text[start:quote_text.index('.',start)+1]
    add('BS2',exact_quote,'SUPPORTED','L','This quotation exactly matches the original extracted majority text, including its em dash.',attention=True)
    add('BS1','Roberts reproduced the majority’s statement that liberty and equal protection may rest on different precepts and are not always co-extensive.','SUPPORTED','HFL','The dissent explicitly introduces the quoted language as “The majority’s approach today” (with straight extracted apostrophe). Reproducing an opponent’s reasoning is not endorsing it.',attention=True)
    add('H','Harlan agreed that Betts v. Brady should be overruled.','SUPPORTED','A','The concurrence opens with his express agreement; the claim is about Harlan, not the majority.')
    add('W','White declined to say that the First Amendment would forbid injunctions in every circumstance.','SUPPORTED','JL','He expressly writes “I do not say that in no circumstances” an injunction would be permitted. Attribution and conditional scope are preserved.')
    add('AS1','Miranda required the right-to-silence warning and a signed written waiver in every interrogation.','PARTIALLY_SUPPORTED','CKJ','The silence warning is supported; a signed written waiver in every interrogation is not established. The compound probe has two declared components.',components=['A right-to-silence warning is required within the stated safeguards framework.','Every interrogation requires a signed written waiver.'])
    add('AS1','Miranda’s specified warnings are the only lawful safeguards for all custodial questioning.','PARTIALLY_SUPPORTED','CJ','The warning framework is supported, but the claim omits the express allowance for other fully effective means and overstates exclusivity. Review whether the absolute “only” instead warrants CONTRADICTED.',attention=True)
    b_final=cases['B']['result']['content'].split('\n\n')[-1].split('This connection')[1]
    add('BS2','This connection'+b_final,'PARTIALLY_SUPPORTED','CD','The clause interrelation is directly supported, but this selected majority chunk does not state the operative same-sex-marriage holding. The next majority chunk was not generation evidence. Review scope relative to implication versus explicit holding.','verbatim_smoke',True)
    add('AS3','Miranda’s confession was inadmissible, and every spontaneous statement to police is inadmissible.','PARTIALLY_SUPPORTED','CK','The specific confession finding is supported; the universal spontaneous-statement rule is not. These two components intentionally form one compound diagnostic probe.',components=['Miranda’s confession in the described case was inadmissible.','Every spontaneous statement to police is inadmissible.'])
    add('AS2','This is a syllabus passage authored by Warren.','PARTIALLY_SUPPORTED','CM','The source text identifies Syllabus, but its author metadata is null/unknown and the passage does not establish Warren as the syllabus author.',attention=True)
    add('BS2','Loving invalidated racial marriage restrictions under both clauses, and imposed damages on each state official.','PARTIALLY_SUPPORTED','CK','The first proposition is explicitly described; the passage supplies no damages disposition.',components=['Loving invalidated racial marriage restrictions under both clauses.','Loving imposed damages on each state official.'])
    add('H','Harlan agreed with overruling Betts and adopted every part of the majority’s historical account.','PARTIALLY_SUPPORTED','CG','Overruling agreement is explicit, but Harlan criticizes the majority’s description of precedent. Human review should consider CONTRADICTED for the second component.',attention=True,components=['Harlan agreed with overruling Betts.','Harlan adopted every part of the majority historical account.'])
    add('W','White agreed with denying the injunction and said publication could cause no public-interest damage.','PARTIALLY_SUPPORTED','CKJ','Agreement with the judgment is explicit; the no-damage clause conflicts with his expressed confidence in substantial damage. Review compound-label convention versus CONTRADICTED.',attention=True,components=['White agreed with denying the injunction in these cases.','White said publication could cause no public-interest damage.'])
    add('CS1','Dobbs held that the Constitution protects a right to abortion.','UNSUPPORTED','IO','The cited passage lists lower-court marriage decisions and supplies no Dobbs holding. Do not use outside knowledge to turn absence into contradiction.')
    add('CS2','Dobbs overruled Roe v. Wade.','UNSUPPORTED','IO','This passage concerns Obergefell’s questions presented and amicus listings, not Dobbs. A proposition’s possible external truth does not make this citation support it.')
    add('CS3','The Court in Dobbs applied strict scrutiny to every abortion restriction.','UNSUPPORTED','DOI','The passage recounts marriage/social history and other cases; no Dobbs standard appears.')
    add('AS3','Miranda requires all custodial interrogations to be videotaped.','UNSUPPORTED','DI','The passage about Miranda’s interrogation and reversal does not establish a videotaping rule.')
    add('BS1','Roberts endorsed the majority’s due-process/equal-protection synergy.','CONTRADICTED','EF','The dissent calls the discussion difficult to follow and criticizes the purported independent equal-protection basis; endorsement reverses his position.')
    add('H','The Gideon majority said that Betts deserved a more respectful burial.','UNSUPPORTED','G','The words appear as Harlan’s separate concurring criticism, not an attributed majority rationale. A concurrence cannot establish this asserted majority attribution.',attention=True)
    add('T','Every line of this passage is reliably verified to have been written by Stewart.','UNSUPPORTED','M','The corpus labels concurrence/Stewart, but the extracted text contains a Black dissent header amid Stewart prose. Raw labels do not independently verify every line’s author.',attention=True)
    add('BS2','The two Fourteenth Amendment clauses always have identical reach.','CONTRADICTED','EL','The majority says they set forth independent principles and are not always co-extensive; this paraphrase reverses that limitation.')
    add('AS1','A defendant may waive Miranda rights involuntarily.','CONTRADICTED','E','The source expressly requires a voluntary, knowing and intelligent waiver.')
    add('AS4','States are forbidden to develop equally effective alternative safeguards.','CONTRADICTED','EJ','The source expressly says Congress and States are free to develop safeguards fully as effective as those described.')
    add('H','Harlan opposed overruling Betts v. Brady.','CONTRADICTED','E','The concurrence opens “I agree that Betts v. Brady should be overruled”.')
    add('W','White believed disclosing the documents would cause no substantial damage to public interests.','CONTRADICTED','EL','White expressly says he is confident disclosure will cause substantial damage.')
    add('BS1','Roberts’s own controlling-majority opinion established the synergy of the two clauses.','UNSUPPORTED','FH','The metadata/text identify Roberts dissenting. His reproduction of majority words does not make this his controlling-majority opinion.',attention=True)
    add('T','The Tinker majority adopted Stewart’s separate objection to co-extensive child/adult speech rights.','UNSUPPORTED','GM','This concurrence expressly disputes the Court’s assumption, and a mixed extracted header adds attribution uncertainty. It does not establish majority adoption.',attention=True)

    examples=[]
    for index,(key,claim,label,categories,reason,origin,attention,components) in enumerate(specs,1):
        record=passages[key];m=record['metadata'];binding=bindings[key]
        text=record['text']; quote=None
        if index==7: quote=claim;assert quote in text
        claim_authentic=origin=='verbatim_smoke'
        if claim_authentic: assert claim in cases[key[0]]['result']['content']
        authentic_pair=claim_authentic and key.startswith('B')
        examples.append({'example_id':f'CS-{index:03d}','level':'claim','review_status':'PROPOSED',
                         'source_question':q(key),'claim':claim,'claim_components':components or [claim],
                         'claim_type':'compound_probe' if components else 'atomic',
                         'cited_evidence_text':text,'citation_identifier':binding['citation_identifier'],
                         'case_name':m['case_name'],'opinion_type':m['opinion_type'],'author':m.get('author'),
                         'pdf_page_range':[m['page_start'],m['page_end']],
                         'gold_support_label':label,'justification':reason,'coverage_categories':list(categories),
                         'example_kind':'authentic' if authentic_pair else 'synthetic',
                         'claim_origin':'verbatim_smoke_answer' if claim_authentic else 'constructed_claim',
                         'pairing_origin':'original_smoke_citation' if authentic_pair else 'constructed_evidence_pairing',
                         'human_judgment_required':True,'review_priority':'HIGH' if attention else 'NORMAL',
                         'exact_quotation':quote,
                         'provenance':{'corpus_records_path':RECORDS,'frozen_chunks_path':CHUNKS,
                           'records_sha256':sha((ROOT/RECORDS).read_bytes()),'chunks_sha256':sha((ROOT/CHUNKS).read_bytes()),
                           'chunk_id':m['chunk_id'],'chunk_index':m['chunk_index'],'vector_id':by_id[m['chunk_id']]['vector_id'],
                           'source_pdf':m['original_source_file'],'source_file':m['source_file'],
                           'text_sha256':sha(text.encode()),'metadata':deepcopy(m),
                           'evidence_origin':binding['kind'],'citation_binding':deepcopy(binding),
                           'smoke_path':SMOKE if binding['case_id'] else None,
                           'smoke_sha256':sha((ROOT/SMOKE).read_bytes()) if binding['case_id'] else None,
                           'claim_answer_path':SMOKE if claim_authentic else None,
                           'claim_case_id':key[0] if claim_authentic else None}})
    responses=[]
    def response(cid,answer,kind,assessment,reason,categories):
        case=cases[cid]; contexts=[]
        for r in case['result']['evidence']:
            contexts.append({'citation_identifier':r['source_id'],'text':r['text'],
                             'metadata':deepcopy(r['metadata']),'text_sha256':sha(r['text'].encode())})
        responses.append({'example_id':f'AR-{len(responses)+1:03d}','level':'answer','review_status':'PROPOSED',
                          'source_question':case['question'],'answer':answer,'example_kind':kind,
                          'context':contexts,'response_assessment':assessment,'justification':reason,
                          'coverage_categories':list(categories),'human_judgment_required':True,
                          'provenance':{'smoke_path':SMOKE,'smoke_sha256':sha((ROOT/SMOKE).read_bytes()),
                                        'case_id':cid,'corpus_records_path':RECORDS,'frozen_chunks_path':CHUNKS,
                                        'response_origin':'saved_smoke_answer' if kind=='authentic' else 'constructed_response'}})
    def assessment(completeness='NOT_APPLICABLE',abstention='NOT_APPLICABLE',certainty='NOT_APPLICABLE',coverage='NOT_APPLICABLE'):
        return dict(completeness=completeness,abstention=abstention,certainty=certainty,citation_coverage=coverage)
    response('A',cases['A']['result']['content'],'authentic',assessment('INCOMPLETE',certainty='OVERSTATED',coverage='INCOMPLETE'),
             'Safeguards are covered, but the evidence also allows equally effective alternatives; grouping citations at the end weakens claim-level attribution. Completeness is judged against the supplied context, not all law.','JK')
    response('B',cases['B']['result']['content'],'authentic',assessment('COMPLETE',certainty='OVERSTATED',coverage='INCOMPLETE'),
             'It addresses the requested clause relationship. The final holding extension is not directly established by the cited majority chunk. Completeness and support are separate dimensions.','DF')
    response('C',cases['C']['result']['content'],'authentic',assessment(abstention='APPROPRIATE',certainty='JUSTIFIED',coverage='MISLEADING'),
             'It refuses to invent a Dobbs holding, but appends references to unrelated Obergefell text. Appropriate abstention can coexist with misleading citations.','NI')
    response('C','The available Supreme Court documents do not provide enough evidence to answer this question.','synthetic',assessment(abstention='APPROPRIATE',certainty='JUSTIFIED'),
             'The supplied passages contain no Dobbs holding. This is a deliberately constructed canonical refusal, not a new model run. No supporting citation is needed.','N')
    response('A','The available Supreme Court documents do not provide enough evidence to answer this question.','synthetic',assessment(abstention='UNWARRANTED',certainty='OVERSTATED'),
             'The selected Miranda majority and syllabus excerpts directly supply the requested safeguards. The same refusal is not justified for this evidence context.','A')
    response('C','Dobbs held that every abortion regulation is unconstitutional [S1].','synthetic',assessment('INCOMPLETE',certainty='OVERSTATED',coverage='MISLEADING'),
             'Obergefell excerpts do not establish this Dobbs holding; this synthetic out-of-corpus answer asserts certainty without support. No outside legal truth judgment is needed.','OI')
    return {'schema_version':'1.0','dataset_name':'CourtLens citation-support candidates',
            'status':'PROPOSED','frozen':False,'independently_human_adjudicated':False,
            'labeler':'Codex initial proposals; human approval required',
            'label_definitions':LABELS,'coverage_categories':CATEGORIES,
            'support_scope':'Exact cited passage only, including explicit speaker/quotation context. No outside knowledge or retrieval scores.',
            'claim_examples':examples,'answer_examples':responses,
            'schema':{'claim_required_fields':list(examples[0]),'answer_required_fields':list(responses[0]),
                      'response_assessment_values':{'completeness':['COMPLETE','INCOMPLETE','NOT_APPLICABLE'],
                         'abstention':['APPROPRIATE','UNWARRANTED','NOT_APPLICABLE'],
                         'certainty':['JUSTIFIED','OVERSTATED','NOT_APPLICABLE'],
                         'citation_coverage':['ADEQUATE','INCOMPLETE','MISLEADING','NOT_APPLICABLE']}},
            'limitations':['Small curated challenge set, not population-representative or a frozen benchmark.',
               'Most passages are Miranda/Obergefell; supplemental concurrence cases broaden attribution coverage only.',
               'Original smoke citations are sometimes paragraph/grouped; newly assigned claim-passage pairings are marked synthetic.',
               'Five compound diagnostic probes intentionally relax atomicity for coverage K; primary units otherwise target one proposition.',
               'Some OCR/opinion boundaries are uncertain; raw metadata is preserved and not verified authorship.',
               'Proposed labels, especially partial versus contradicted and implicit majority support, require independent human review.',
               'No verifier, judge, model requests, metric computation, or training/test split is implemented.']}


def review_report(dataset):
    rows=dataset['claim_examples'];answers=dataset['answer_examples']
    counts=Counter(r['gold_support_label'] for r in rows)
    coverage={k:[r['example_id'] for r in rows+answers if k in r['coverage_categories']] for k in CATEGORIES}
    lines=['# Citation-support candidate review','','**PROPOSED — not human-adjudicated; not frozen.**',
           '',f'{len(rows)} claim examples and {len(answers)} answer-level examples.',
           '', 'Claim label counts: '+', '.join(f'{k}: {counts[k]}' for k in LABELS)+'.',
           '', 'All sources are exact corpus chunks. Synthetic design changes claims or pairings, never source wording. Labels evaluate the specified passage, not legal truth across the corpus.',
           '', '## Coverage', '', '| Category | Requirement | Examples |','|---|---|---|']
    lines += [f"| {k} | {v} | {', '.join(coverage[k])} |" for k,v in CATEGORIES.items()]
    lines += ['','## Human adjudication','',
              'Every example needs approval. Prioritize partial/contradicted boundaries, dissent quotations, concurrence/majority attribution, missing qualifications, and OCR uncertainty. Review may change labels; no approval is inferred from these proposals.',
              '', 'For each item record reviewer, decision (approve/relabel/reject), final proposed label or response assessment, reason, and date in a separate reviewed artifact. Do not overwrite frozen source material or mark this dataset frozen automatically.',
              '', '## Claim examples', '', '| ID | Label (proposed) | Kind | Case / PDF pages | Priority |','|---|---|---|---|---|']
    lines += [f"| {r['example_id']} | {r['gold_support_label']} | {r['example_kind']} | {r['case_name']} / {r['pdf_page_range'][0]}–{r['pdf_page_range'][1]} | {r['review_priority']} |" for r in rows]
    for r in rows:
        p=r['provenance']
        lines += ['',f"### {r['example_id']} — {r['gold_support_label']} (PROPOSED)",'',
                  '**Question:** '+r['source_question'],'','**Claim:** '+r['claim'],'',
                  '**Rationale:** '+r['justification'],'',
                  f"**Source:** [{r['citation_identifier']}], {r['case_name']}, PDF pages {r['pdf_page_range']}; raw opinion {r['opinion_type']}, raw author {r['author'] or 'Unknown'}. Chunk `{p['chunk_id']}`; original index {p['chunk_index']}; vector row {p['vector_id']}.",
                  '',f"**Origin:** {r['example_kind']}; claim {r['claim_origin']}; pairing {r['pairing_origin']}; evidence {p['evidence_origin']}.",
                  '', '**Exact cited passage (complete chunk; OCR unchanged):**', '', '```text',r['cited_evidence_text'],'```']
    lines += ['','## Answer-level examples — separate assessment axes']
    for r in answers:
        lines += ['',f"### {r['example_id']} (PROPOSED)",'','**Question:** '+r['source_question'],'',
                  '**Answer:** '+r['answer'],'','**Assessment:** '+json.dumps(r['response_assessment']),
                  '', '**Rationale:** '+r['justification'],'',
                  '**Context:** '+', '.join(f"[{c['citation_identifier']}] {c['metadata']['chunk_id']} (PDF {c['metadata']['page_start']}–{c['metadata']['page_end']})" for c in r['context']),
                  '', 'Exact complete response contexts and provenance are embedded in the JSON; answer-level outcomes are not claim-support labels.']
    lines += ['','## Limitations','']+[f'- {v}' for v in dataset['limitations']]
    return '\n'.join(lines)+'\n'


def main():
    dataset=build_dataset()
    outputs={CANDIDATES:encode(dataset),REVIEW:review_report(dataset)}
    for relative,text in outputs.items():
        path=ROOT/relative
        if path.exists() and path.read_text()!=text:
            raise FileExistsError('Refusing to overwrite different candidate/review artifacts')
    for relative,text in outputs.items(): (ROOT/relative).write_text(text)
    print('Created PROPOSED candidates:',len(dataset['claim_examples']),'claims,',len(dataset['answer_examples']),'answers.')


if __name__=='__main__':main()
