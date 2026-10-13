"""Candidate schema/provenance checks only; never assess semantic support."""
import json
import re
from pathlib import Path
from build_citation_support_candidates import ROOT, LABELS, CATEGORIES, SMOKE, RECORDS, CHUNKS, sha

CLAIM_REQUIRED = {'example_id','level','review_status','source_question','claim','claim_components','claim_type',
                  'cited_evidence_text','citation_identifier','case_name','opinion_type','author','pdf_page_range',
                  'gold_support_label','justification','coverage_categories','example_kind','claim_origin',
                  'pairing_origin','human_judgment_required','review_priority','exact_quotation','provenance'}
ANSWER_REQUIRED = {'example_id','level','review_status','source_question','answer','example_kind','context',
                   'response_assessment','justification','coverage_categories','human_judgment_required','provenance'}
AXES = {'completeness':{'COMPLETE','INCOMPLETE','NOT_APPLICABLE'},
        'abstention':{'APPROPRIATE','UNWARRANTED','NOT_APPLICABLE'},
        'certainty':{'JUSTIFIED','OVERSTATED','NOT_APPLICABLE'},
        'citation_coverage':{'ADEQUATE','INCOMPLETE','MISLEADING','NOT_APPLICABLE'}}


def validate_dataset(dataset, root=ROOT):
    """Raise ValueError for integrity errors. Never derive or change labels."""
    def require(condition, reason):
        if not condition: raise ValueError(reason)
    require(dataset.get('status')=='PROPOSED' and dataset.get('frozen') is False
            and dataset.get('independently_human_adjudicated') is False,'candidate review status')
    records=[json.loads(l) for l in (root/RECORDS).read_text().splitlines()]
    chunks=[json.loads(l) for l in (root/CHUNKS).read_text().splitlines()]
    corpus={r['metadata']['chunk_id']:r for r in records}
    frozen={r['metadata']['chunk_id']:r for r in chunks}
    smoke=json.loads((root/SMOKE).read_text());cases={c['id']:c for c in smoke['cases']}
    hashes={p:sha((root/p).read_bytes()) for p in (SMOKE,RECORDS,CHUNKS)}
    all_examples=dataset['claim_examples']+dataset['answer_examples'];ids=set();coverage=set()
    def source(text, metadata):
        cid=metadata.get('chunk_id'); require(cid in corpus and cid in frozen,'missing corpus identity')
        require(text==corpus[cid]['text']==frozen[cid]['text'],'source text mismatch')
        require(metadata==corpus[cid]['metadata']==frozen[cid]['metadata'],'metadata/provenance mismatch')
    for row in all_examples:
        level=row.get('level');require(level in ('claim','answer'),'example level')
        required=CLAIM_REQUIRED if level=='claim' else ANSWER_REQUIRED
        require(required<=set(row),'required fields')
        require(row['example_id'] not in ids,'duplicate example ID');ids.add(row['example_id'])
        require(re.fullmatch(r'(CS|AR)-[0-9]{3}',row['example_id']) is not None,'example ID format')
        require(row['example_id'].startswith('CS-' if level=='claim' else 'AR-'),'level/ID mismatch')
        require(row['review_status']=='PROPOSED' and row['human_judgment_required'] is True,'review status')
        require(row['example_kind'] in ('authentic','synthetic'),'example origin')
        require(bool(row['source_question'].strip()) and bool(row['justification'].strip()),'question/rationale')
        require(set(row['coverage_categories'])<=set(CATEGORIES),'coverage vocabulary');coverage.update(row['coverage_categories'])
        p=row['provenance'];require(p['corpus_records_path']==RECORDS and p['frozen_chunks_path']==CHUNKS,'corpus provenance path')
        if level=='claim':
            require(row['gold_support_label'] in LABELS,'support label')
            require('response_assessment' not in row,'claim/answer separation')
            require(row['claim_type'] in ('atomic','compound_probe') and bool(row['claim_components']),'claim unit')
            require(len(row['claim_components'])==1 if row['claim_type']=='atomic' else len(row['claim_components'])>=2,'claim components')
            require(bool(row['claim'].strip()),'empty claim')
            text=row['cited_evidence_text'];m=p['metadata'];source(text,m)
            require(p['records_sha256']==hashes[RECORDS] and p['chunks_sha256']==hashes[CHUNKS],'corpus file hash')
            require(p['text_sha256']==sha(text.encode()),'text digest')
            require(p['chunk_id']==m['chunk_id'] and p['chunk_index']==m['chunk_index'],'chunk identity')
            require(p['source_file']==m['source_file'] and p['source_pdf']==m['original_source_file'],'PDF identity')
            require(p['vector_id']==corpus[m['chunk_id']]['vector_id'],'corpus row identity')
            for field in ('case_name','opinion_type','author'): require(row[field]==m.get(field),'attribution identity')
            require(row['pdf_page_range']==[m['page_start'],m['page_end']],'page provenance')
            require(re.fullmatch(r'S[1-9][0-9]*',row['citation_identifier']) is not None,'citation syntax')
            binding=p['citation_binding'];require(binding['citation_identifier']==row['citation_identifier'],'citation binding')
            require(binding['kind']==p['evidence_origin'],'evidence origin')
            if p['evidence_origin']=='smoke_generation_context':
                require(p['smoke_path']==SMOKE and p['smoke_sha256']==hashes[SMOKE],'smoke hash/path')
                case=cases[binding['case_id']]
                selected=case['result']['evidence']
                matching=[r for r in selected if r['source_id']==row['citation_identifier']]
                require(len(matching)==1 and matching[0]['text']==text and matching[0]['metadata']==m,'turn-scoped citation identity')
                current=smoke
                try:
                    for part in binding['json_pointer'].split('/')[1:]: current=current[int(part)] if isinstance(current,list) else current[part]
                except (KeyError,IndexError,ValueError,TypeError):raise ValueError('smoke JSON pointer') from None
                require(current==matching[0],'smoke JSON pointer identity')
                require(row['source_question']==case['question'],'original source question')
            else:
                require(p['evidence_origin']=='constructed_local_context' and binding['case_id'] is None
                        and binding['json_pointer'] is None and row['citation_identifier']=='S1','constructed citation scope')
            if row['claim_origin']=='verbatim_smoke_answer':
                require(p['claim_answer_path']==SMOKE and row['claim'] in cases[p['claim_case_id']]['result']['content'],'authentic claim text')
            else:require(row['claim_origin']=='constructed_claim' and row['example_kind']=='synthetic','constructed claim origin')
            require(row['pairing_origin'] in ('original_smoke_citation','constructed_evidence_pairing'),'pairing origin')
            require((row['example_kind']=='authentic')==(row['pairing_origin']=='original_smoke_citation'),'pairing authenticity')
            if row['exact_quotation'] is not None:require(row['exact_quotation'] in text,'fabricated quotation')
        else:
            require('gold_support_label' not in row and 'claim' not in row,'answer/claim separation')
            require(set(row['response_assessment'])==set(AXES),'response axes')
            require(all(row['response_assessment'][k] in v for k,v in AXES.items()),'response outcome vocabulary')
            require(p['smoke_path']==SMOKE and p['smoke_sha256']==hashes[SMOKE],'answer provenance')
            case=cases[p['case_id']];require(row['source_question']==case['question'],'answer source question')
            expected=case['result']['evidence']; require(len(row['context'])==len(expected),'complete answer context')
            for c,r in zip(row['context'],expected):
                source(c['text'],c['metadata']);require(c['text_sha256']==sha(c['text'].encode()),'answer source digest')
                require(c['citation_identifier']==r['source_id'] and c['text']==r['text'] and c['metadata']==r['metadata'],'answer citation scope')
            if row['example_kind']=='authentic':require(row['answer']==case['result']['content'],'authentic answer text')
    require(coverage==set(CATEGORIES),'required category coverage')
    return {'claim_count':len(dataset['claim_examples']),'answer_count':len(dataset['answer_examples']),
            'verified_source_pairs':sum(len(r['context']) if r['level']=='answer' else 1 for r in all_examples)}
