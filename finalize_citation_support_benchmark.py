"""Deterministic user-authorized finalization; no semantic verifier/API calls.

Original candidate/review/guideline artifacts are read-only. Writes only new v1
adjudication, benchmark, checksum and documentation paths, refusing differences.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from build_citation_support_candidates import ROOT, CANDIDATES, REVIEW, GUIDELINES, encode, LABELS
from citation_support_dataset import validate_dataset, AXES

ADJUDICATION = 'data/evaluation/citation_support_adjudication_v1.json'
BENCHMARK = 'data/evaluation/citation_support_benchmark_v1.json'
CHECKSUM = 'data/evaluation/citation_support_benchmark_v1.sha256'
DOCUMENTATION = 'docs/citation_support_benchmark_v1.md'
METHOD = 'AI-assisted, user-authorized'
EXPECTED_DISTRIBUTION = {'SUPPORTED':10,'PARTIALLY_SUPPORTED':7,'UNSUPPORTED':7,'CONTRADICTED':8}
REVISIONS = {
    'CS-012': 'The assertion that Miranda’s warnings are the only lawful safeguards directly conflicts with the opinion’s allowance for equally effective alternatives.',
    'CS-031': 'The cited passage explicitly identifies Roberts as dissenting, directly conflicting with the claim that he authored the controlling majority opinion.'}
AR006_REASON = (
    'Completeness is context/task coverage, separate from factual support. The supplied '
    'Obergefell context establishes no Dobbs answer or material answer points against which '
    'completeness can be judged. Use the existing NOT_APPLICABLE value for this dimension; '
    'do not redefine INCOMPLETE as entirely unsupported or infer COMPLETE from surface '
    'responsiveness. Certainty remains OVERSTATED and citation coverage MISLEADING. '
    'This is AI-assisted rubric application under user-authorized finalization, not '
    'a separately documented human legal-expert approval.')
POLICY = {
    'all_material_components_supported':'SUPPORTED',
    'meaningful_supported_component_plus_unsupported_or_contradicted_component':'PARTIALLY_SUPPORTED',
    'central_assertion_directly_incompatible_without_meaningful_supported_component':'CONTRADICTED',
    'no_meaningful_supported_component_and_no_affirmative_contradiction':'UNSUPPORTED',
    'contradicted_components_must_be_recorded':True,
    'labels_are_component_annotations_not_automated_semantic_predictions':True}
LIMITATIONS = [
    '32 claims and 6 answers: small curated challenge set, not deployment-representative.',
    '30 of 32 claim examples are synthetic pairings/claims; original source passages remain authentic.',
    'Concentrated on Miranda and Obergefell, with three supplementary concurrence cases.',
    'Example selection was influenced by observed CourtLens failures.',
    'AI-assisted, user-authorized adjudication; no independent human legal-expert review.',
    'Not an independent generalization benchmark; no held-out split or leakage-resistant evaluation design.',
    'Success does not establish legal accuracy, claim completeness or deployment safety.',
    'OCR-derived attribution remains uncertain; original metadata and text are preserved.',
    'No semantic verifier, LLM judge, NLI model or generation/retrieval change is implemented.']

# Manual component annotations explicitly apply the authorized convention.
COMPONENT_DECISIONS = {
    'CS-011': [('SUPPORTED','The cited safeguards framework includes a right-to-silence warning.'),
               ('UNSUPPORTED','The passage does not establish a signed written waiver for every interrogation.')],
    'CS-014': [('SUPPORTED','The passage finds Miranda’s particular confession inadmissible.'),
               ('UNSUPPORTED','It does not establish a universal rule for every spontaneous statement.')],
    'CS-016': [('SUPPORTED','The passage describes Loving invalidating the restriction under both clauses.'),
               ('UNSUPPORTED','It provides no damages disposition against each state official.')],
    'CS-017': [('SUPPORTED','Harlan expressly agrees that Betts should be overruled.'),
               ('CONTRADICTED','Harlan says he cannot subscribe to the majority’s abrupt-break characterization.')],
    'CS-018': [('SUPPORTED','White expressly concurs in the judgments and agrees the injunction burden was not met.'),
               ('CONTRADICTED','White expressly expresses confidence that disclosure will cause substantial public-interest damage.')],
}


def digest(data): return hashlib.sha256(data).hexdigest()


def compound_label(component_labels):
    """Aggregate already-adjudicated labels only; no text classification."""
    if not component_labels or any(label not in ('SUPPORTED','UNSUPPORTED','CONTRADICTED') for label in component_labels):
        raise ValueError('Invalid component annotations')
    if all(label=='SUPPORTED' for label in component_labels): return 'SUPPORTED'
    if 'SUPPORTED' in component_labels: return 'PARTIALLY_SUPPORTED'
    if 'CONTRADICTED' in component_labels: return 'CONTRADICTED'
    return 'UNSUPPORTED'


def produce(root=ROOT):
    candidate=json.loads((root/CANDIDATES).read_text())
    validate_dataset(candidate, root)
    source_hashes={name:digest((root/name).read_bytes()) for name in (CANDIDATES,REVIEW,GUIDELINES)}
    claims=deepcopy(candidate['claim_examples']);answers=deepcopy(candidate['answer_examples'])
    decisions=[]
    for row in claims:
        original=row['gold_support_label'];reason=REVISIONS.get(row['example_id'],row['justification'])
        final='CONTRADICTED' if row['example_id'] in REVISIONS else original
        components=[]
        if row['claim_type']=='compound_probe':
            for text,(label,rationale) in zip(row['claim_components'],COMPONENT_DECISIONS[row['example_id']]):
                components.append({'component':text,'gold_support_label':label,'justification':rationale,
                                   'review_status':'FINALIZED','review_method':METHOD})
            assert len(components)==len(row['claim_components'])
            assert compound_label([c['gold_support_label'] for c in components])==final
            reason += ' Under the finalized compound convention the overall label is PARTIALLY_SUPPORTED; component outcomes are explicitly recorded.'
        decision={'example_id':row['example_id'],'level':'claim','original_proposed_label':original,
                  'final_label':final,'decision':'revised' if final!=original else 'retained',
                  'justification':reason,'review_status':'FINALIZED','review_method':METHOD,
                  'authorization_basis':'Explicit user label revision' if row['example_id'] in REVISIONS else 'User instruction to retain the other 30 claim labels',
                  'source_provenance':deepcopy(row['provenance']),
                  'component_decisions':components,'limitations':LIMITATIONS}
        decisions.append(decision)
        row['gold_support_label']=final;row['justification']=reason
        row['review_status']='FINALIZED';row['human_judgment_required']=False
        row['independent_legal_expert_review']=False
        if components:row['component_adjudication']=deepcopy(components)
    for row in answers:
        original=deepcopy(row['response_assessment']);final=deepcopy(original)
        reason=row['justification']
        if row['example_id']=='AR-006': final['completeness']='NOT_APPLICABLE';reason=AR006_REASON
        decisions.append({'example_id':row['example_id'],'level':'answer','original_proposed_assessment':original,
                          'final_assessment':final,'decision':'retained' if original==final else 'revised',
                          'justification':reason,'review_status':'FINALIZED','review_method':METHOD,
                          'authorization_basis':'User-authorized AR-006 rubric resolution; no separately asserted human approval' if row['example_id']=='AR-006' else 'User instruction to preserve reviewed AR-001 through AR-005 assessments',
                          'source_provenance':deepcopy(row['provenance']),'limitations':LIMITATIONS})
        row['response_assessment']=final;row['justification']=reason;row['review_status']='FINALIZED'
        row['human_judgment_required']=False;row['independent_legal_expert_review']=False
    adjudication={'schema_version':'1.0','adjudication_version':'1.0','status':'FINALIZED',
                  'review_method':METHOD,'independent_human_legal_expert_adjudication':False,
                  'source_artifact_sha256':source_hashes,'compound_claim_policy':POLICY,
                  'ar006_resolution':{'completeness':'NOT_APPLICABLE','new_status_added':False,
                      'justification':AR006_REASON,'scoring':'Exclude NOT_APPLICABLE from completeness scoring denominator; retain AR-006 for certainty/citation-coverage evaluation. Report applicable counts. No metrics are calculated here.'},
                  'decisions':decisions,'limitations':LIMITATIONS}
    adjudication_text=encode(adjudication)
    benchmark={'schema_version':'1.0','benchmark_version':'1.0','name':'CourtLens Citation Support Benchmark v1',
               'status':'FINALIZED','frozen':False,'review_method':METHOD,
               'independently_human_adjudicated':False,'independent_legal_expert_review':False,
               'source_artifact_sha256':source_hashes,'label_definitions':deepcopy(candidate['label_definitions']),
               'coverage_categories':deepcopy(candidate['coverage_categories']),
               'support_scope':candidate['support_scope'],'schema':deepcopy(candidate['schema']),
               'compound_claim_policy':POLICY,'ar006_resolution':deepcopy(adjudication['ar006_resolution']),
               'claim_examples':claims,'answer_examples':answers,
               'adjudication_provenance':{'path':ADJUDICATION,'sha256':digest(adjudication_text.encode()),
                                         'review_method':METHOD,'decision_count':38},
               'limitations':LIMITATIONS}
    for row in claims+answers:
        row['adjudication_provenance']={'path':ADJUDICATION,'example_id':row['example_id'],
                                      'review_method':METHOD,'decision_status':'FINALIZED'}
    validate_final(benchmark,adjudication,root,require_frozen=False)
    benchmark['frozen']=True  # Only after successful source/decision validation.
    validate_final(benchmark,adjudication,root)
    text=encode(benchmark);checksum=digest(text.encode())
    return {ADJUDICATION:adjudication_text,BENCHMARK:text,
            CHECKSUM:f'{checksum}  {Path(BENCHMARK).name}\n',
            DOCUMENTATION:documentation(benchmark,checksum)}


def validate_final(benchmark,adjudication,root=ROOT,require_frozen=True):
    """Validate frozen integrity/approved decisions, never semantic support."""
    def require(condition,reason):
        if not condition:raise ValueError(reason)
    candidate=json.loads((root/CANDIDATES).read_text());validate_dataset(candidate,root)
    for name,h in benchmark['source_artifact_sha256'].items():require(digest((root/name).read_bytes())==h,'historical input hash')
    require(benchmark['status']=='FINALIZED' and adjudication['status']=='FINALIZED','final status')
    require(benchmark['frozen'] is require_frozen,'freeze gate')
    require(benchmark['source_artifact_sha256']==adjudication['source_artifact_sha256'],'source hash agreement')
    require(benchmark['review_method']==adjudication['review_method']==METHOD,'review method')
    require(not benchmark['independently_human_adjudicated'] and not benchmark['independent_legal_expert_review'] and not adjudication['independent_human_legal_expert_adjudication'],'review disclosure')
    require(benchmark['schema']==candidate['schema'],'preserved schema')
    require(benchmark['compound_claim_policy']==adjudication['compound_claim_policy']==POLICY,'compound policy')
    require(benchmark['ar006_resolution']==adjudication['ar006_resolution'],'AR-006 resolution agreement')
    all_rows=benchmark['claim_examples']+benchmark['answer_examples'];decisions=adjudication['decisions']
    expected_ids=[r['example_id'] for r in candidate['claim_examples']+candidate['answer_examples']]
    require([r['example_id'] for r in all_rows]==expected_ids,'stable example order')
    require([d['example_id'] for d in decisions]==expected_ids and len(set(expected_ids))==38,'unique adjudication IDs')
    require(len(benchmark['claim_examples'])==32 and len(benchmark['answer_examples'])==6,'example counts')
    require(dict(Counter(r['gold_support_label'] for r in benchmark['claim_examples']))==EXPECTED_DISTRIBUTION,'final label distribution')
    require(benchmark['adjudication_provenance']['sha256']==digest(encode(adjudication).encode()),'adjudication digest')
    mutable={'review_status','human_judgment_required','justification','gold_support_label','response_assessment',
             'independent_legal_expert_review','component_adjudication','adjudication_provenance'}
    for row,old,decision in zip(all_rows,candidate['claim_examples']+candidate['answer_examples'],decisions):
        require(row['review_status']==decision['review_status']=='FINALIZED' and row['human_judgment_required'] is False,'remaining proposed decision')
        require(row['independent_legal_expert_review'] is False,'expert review disclosure')
        require({k:v for k,v in row.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable},'exact original example/source preservation')
        require(decision['source_provenance']==old['provenance'] and row['justification']==decision['justification'],'decision provenance/justification')
        require(decision['review_method']==METHOD and decision['level']==row['level'],'decision method/level')
        require(row['adjudication_provenance']=={'path':ADJUDICATION,'example_id':row['example_id'],'review_method':METHOD,'decision_status':'FINALIZED'},'example adjudication identity')
        if row['level']=='claim':
            expected='CONTRADICTED' if row['example_id'] in REVISIONS else old['gold_support_label']
            require(row['gold_support_label']==decision['final_label']==expected,'approved claim label')
            require(decision['original_proposed_label']==old['gold_support_label'],'original claim label')
            require(decision['decision']==('revised' if expected!=old['gold_support_label'] else 'retained'),'claim decision classification')
            if row['claim_type']=='compound_probe':
                components=row['component_adjudication']
                require(components==decision['component_decisions'],'compound decision agreement')
                require([c['component'] for c in components]==old['claim_components'],'original component text')
                require([(c['gold_support_label'],c['justification']) for c in components]==COMPONENT_DECISIONS[row['example_id']],'component annotations')
                require(compound_label([c['gold_support_label'] for c in components])==expected,'compound aggregate label')
                require(all(c['review_status']=='FINALIZED' and c['review_method']==METHOD for c in components),'component finalization')
            else:require(not decision['component_decisions'] and 'component_adjudication' not in row,'atomic component separation')
        else:
            expected=deepcopy(old['response_assessment'])
            if row['example_id']=='AR-006':expected['completeness']='NOT_APPLICABLE'
            require(row['response_assessment']==decision['final_assessment']==expected,'answer assessment')
            require(decision['original_proposed_assessment']==old['response_assessment'],'original answer assessment')
            require(decision['decision']==('retained' if expected==old['response_assessment'] else 'revised'),'answer decision classification')
            require(all(row['response_assessment'][k] in values for k,values in AXES.items()),'answer vocabulary')
            require('gold_support_label' not in row,'claim/answer separation')
    return {'claims':32,'answers':6,'distribution':EXPECTED_DISTRIBUTION,'source_references':52,'finalized_decisions':38}


def load_frozen(root=ROOT):
    raw=(root/BENCHMARK).read_bytes();expected=(root/CHECKSUM).read_text()
    if expected!=f'{digest(raw)}  {Path(BENCHMARK).name}\n':raise ValueError('Benchmark checksum mismatch')
    benchmark=json.loads(raw);adjudication=json.loads((root/ADJUDICATION).read_text())
    validate_final(benchmark,adjudication,root)
    if raw!=encode(benchmark).encode():raise ValueError('Noncanonical benchmark serialization')
    return benchmark


def documentation(benchmark,checksum):
    lines=['# Citation Support Benchmark v1 — finalized adjudication','',
           '**Frozen after local integrity validation. Review method: AI-assisted, user-authorized. No independent human legal-expert adjudication.**','',
           'Original candidates, review and labeling guidelines remain unchanged historical records. This document records the finalized convention and rubric application; it does not retroactively describe prior proposals as approved expert labels.','',
           '## Claims','', '32 claims: SUPPORTED 10; PARTIALLY_SUPPORTED 7; UNSUPPORTED 7; CONTRADICTED 8. Only CS-012 and CS-031 labels changed, both to CONTRADICTED under explicit user instructions. Other 30 labels are retained.','',
           '## Compound convention','',
           '- All material components supported: SUPPORTED.',
           '- Meaningful supported component plus unsupported or contradicted component: PARTIALLY_SUPPORTED.',
           '- Central assertion directly incompatible, without an independently meaningful supported component: CONTRADICTED.',
           '- No meaningful supported component and no affirmative contradiction: UNSUPPORTED.','',
           'Component outcomes are recorded independently and are never hidden by the aggregate label. CS-017 and CS-018 have CONTRADICTED second components but supported first components; their overall PARTIALLY_SUPPORTED labels remain. CS-011, CS-014 and CS-016 have SUPPORTED first and UNSUPPORTED second components.','',
           '## Answer-level rubric','',AR006_REASON,'',
           'No new enum/status is added. INCOMPLETE continues to mean omitted requested material points against an applicable evidence-grounded task, not merely unsupported content. NOT_APPLICABLE is used when that dimension cannot meaningfully be applied, including an out-of-corpus question with no established answer in its context. This is not a correctness credit. Exclude these examples from completeness scoring denominators, report applicable counts, and still evaluate other axes. No scoring is implemented here.','',
           '| ID | Completeness | Abstention | Certainty | Citation coverage |','|---|---|---|---|---|']
    for row in benchmark['answer_examples']:
        a=row['response_assessment'];lines.append(f"| {row['example_id']} | {a['completeness']} | {a['abstention']} | {a['certainty']} | {a['citation_coverage']} |")
    lines += ['','AR-001 through AR-005 are retained. AR-006 changes completeness only, from INCOMPLETE to NOT_APPLICABLE; its other three assessment values remain unchanged.','',
              '## Reproduction and validation','',
              '`finalize_citation_support_benchmark.py` reads the historical artifacts, validates exact corpus provenance, applies recorded decisions, validates before freezing, and reproduces the v1 files deterministically. Existing differing outputs are rejected. `load_frozen()` verifies checksum, canonical serialization, adjudication agreement, approved revisions, component consistency, and all unchanged source fields. No provider calls or semantic verifier are involved.','',
              f'Benchmark: `{BENCHMARK}`',f'Adjudication: `{ADJUDICATION}`',f'Checksum: `{CHECKSUM}`','',f'SHA-256: `{checksum}`','',
              'Source hashes and each complete original provenance object are retained. Final example review statuses are FINALIZED. Original proposed labels/assessments appear only as historical fields in the adjudication record, not as pending decisions. No fabricated or normalized source text is introduced.','',
              '## Limitations','']+[f'- {limitation}' for limitation in LIMITATIONS]
    return '\n'.join(lines)+'\n'


def main():
    outputs=produce()
    # Preflight every destination before any write; never overwrite different v1 files.
    for name,text in outputs.items():
        p=ROOT/name
        if p.exists() and p.read_bytes()!=text.encode():raise FileExistsError('Refusing to overwrite differing finalized artifact')
    for name,text in outputs.items():(ROOT/name).write_bytes(text.encode())
    benchmark=load_frozen();print('Validated frozen benchmark: 32 claims, 6 answers.')
    print('SHA-256:',digest((ROOT/BENCHMARK).read_bytes()))


if __name__=='__main__':main()
