"""Phase 6A: local pretrained cross-encoder on COMPLETE saved hybrid unions.

No retriever is invoked. The scorer sees only original query/passage pairs.
Labels enter after scoring, for unchanged Top-5 evaluation and isolated oracle.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

from hybrid_retrieval import ChunkCatalog
from run_bm25_experiment import ROOT, BENCHMARK, COLLECTIONS, load_corpus, load, encode, sha, group_metrics
from finalize_chunking_benchmark import aggregate, score_retrieved, saved_result_is_relevant
from run_hybrid_experiment import rank_change, TARGETS

BASE = Path('data/experiments/retrieval/reranking')
ANALYSIS = Path('data/analysis/cross_encoder_evaluation.json')
REPORT = Path('data/analysis/cross_encoder_evaluation.md')
ENVIRONMENT = Path('cross_encoder_environment.json')
LOCK = Path('requirements-cross-encoder.lock.txt')
PAIR_COUNTS = {'fixed_900_150':318, 'structure_aware_v1':294}
METRICS = ('hit_at_1','hit_at_3','hit_at_5','mrr')
BASELINES = {'fixed_900_150':(.700,.950,.975,.8229166666666666),
             'structure_aware_v1':(.850,.950,.975,.9008333333333333)}
LIMITATIONS = [
    'Benchmark v2 is not an independent holdout: it was refined using evaluated dense candidates.',
    'Case/source/page-overlap relevance is coarse and can misclassify actual answer-bearing content.',
    'Candidate availability limits reranking. Only complete saved hybrid unions are used; no new retrieval candidates are generated.',
    'This unmodified MS MARCO pretrained cross-encoder is not specialized in Supreme Court law. No fine-tuning, model selection, legal boosts, or label-informed scoring occurs.',
    'Long passages are deterministically truncated with longest_first, right truncation, to a 512-token paired input. Actual evidence can fall outside the retained prefix. There are no labeled answer spans, so page labels alone cannot establish whether the answer was seen.',
    'Frozen chunk sizes and coverage differ; structure-aware excludes 200 foreign Sturgis/Honold tokens retained in fixed chunks.',
    'Differences and small subgroup results are descriptive; no statistical significance or general superiority is implied.',
    'Saved scores support deterministic replay. Bit-identical new neural inference across hardware/framework versions is not guaranteed; device and versions are frozen and recorded.',
]


def output_paths():
    return {ANALYSIS,REPORT} | {BASE/c/name for c in COLLECTIONS for name in ('manifest.json','rankings.json','results.json')}


def protected_snapshot(root=ROOT):
    return {str(p.relative_to(root)):sha(p) for p in sorted((root/'data').rglob('*')) if p.is_file() and p.relative_to(root) not in output_paths()}


def validate_environment(config):
    if config['model_name']!='cross-encoder/ms-marco-MiniLM-L-6-v2' or not re.fullmatch('[0-9a-f]{40}',config['revision']):
        raise ValueError('Wrong model or non-immutable revision')
    if any(config[k]!=config['revision'] for k in ('model_revision','config_revision','tokenizer_revision')):
        raise ValueError('Revision mismatch')
    if (config['batch_size'],config['max_length'],config['truncation'],config['truncation_side'])!=(8,512,'longest_first','right'):
        raise ValueError('Frozen inference configuration mismatch')
    if config['device'] not in ('mps','cpu') or not config['evaluation_mode'] or config['gradients'] or not config['local_files_only']:
        raise ValueError('Invalid inference mode/device')


def load_inputs(collection, questions, root=ROOT):
    records, hashes = load_corpus(collection,root)
    catalog = ChunkCatalog(collection,records)
    directory = Path('data/experiments/retrieval/hybrid')/collection
    paths = [directory/name for name in ('manifest.json','rankings.json','results.json')]
    manifest, raw, baseline = [load(root/p) for p in paths]
    if any(v['collection']!=collection for v in (manifest,raw,baseline)):
        raise ValueError('Cross-corpus hybrid inputs')
    if manifest['chunk_count']!=len(records) or manifest['question_count']!=40:
        raise ValueError('Hybrid corpus/count mismatch')
    for path,checksum in manifest['input_sha256'].items():
        if sha(root/path)!=checksum:
            raise ValueError('Hybrid provenance input changed')
    if manifest['k']!=60 or manifest['dense_candidate_depth']!=5 or manifest['bm25_candidate_depth']!=5:
        raise ValueError('Unexpected saved hybrid parameters')
    if len(questions)!=40 or len({q['id'] for q in questions})!=40:
        raise ValueError('Expected forty unique questions')
    if any([q['id'] for q in v['questions']] != [q['id'] for q in questions] for v in (raw,baseline)):
        raise ValueError('Question order mismatch')
    pairs=[]
    for q,saved,official in zip(questions,raw['questions'],baseline['questions']):
        if q['question']!=saved['question']:
            raise ValueError('Question wording mismatch')
        for key in ('question','type','expected_case','expected_source_file','relevant_ranges'):
            if official[key]!=q[key]:raise ValueError('Benchmark mismatch')
        rows=saved['retrieved']
        if not 5<=len(rows)<=10 or saved['union_size']!=len(rows):
            raise ValueError('Incomplete hybrid union')
        seen=set()
        for rank,row in enumerate(rows,1):
            ordinal=catalog.verify(row)
            if ordinal in seen or row['rank']!=rank or row['hybrid_rank']!=rank:
                raise ValueError('Duplicate/noncontiguous saved candidates')
            seen.add(ordinal)
            pairs.append((q['question'],records[ordinal]['text']))
        if rows!=sorted(rows,key=lambda r:(-r['rrf_score'],r['corpus_index'])):
            raise ValueError('Saved hybrid order mismatch')
        if score_retrieved(rows,q)!=official['metrics']:
            raise ValueError('Saved hybrid evaluation mismatch')
    if len(pairs)!=PAIR_COUNTS[collection] or aggregate(baseline['questions'])!=baseline['metrics']:
        raise ValueError('Frozen candidate counts/baseline mismatch')
    if any(abs(baseline['metrics'][m]-expected)>1e-12 for m,expected in zip(METRICS,BASELINES[collection])):
        raise ValueError('Hybrid baseline control mismatch')
    return records,raw,baseline,pairs,{**hashes,**{str(p):sha(root/p) for p in paths}}


def token_accounting(tokenizer, pairs):
    """Use the identical tokenizer pair policy as inference; no labels involved."""
    output=[]
    for query,passage in pairs:
        qlen=len(tokenizer(query,add_special_tokens=False,truncation=False)['input_ids'])
        plen=len(tokenizer(passage,add_special_tokens=False,truncation=False)['input_ids'])
        full=tokenizer(query,passage,add_special_tokens=True,truncation=False)
        processed=tokenizer(query,passage,add_special_tokens=True,truncation='longest_first',max_length=512,
                            return_offsets_mapping=True)
        ids=processed.sequence_ids()
        qkeep=sum(i==0 for i in ids);pkeep=sum(i==1 for i in ids)
        ends=[offset[1] for offset,i in zip(processed['offset_mapping'],ids) if i==1]
        end=max(ends,default=0)
        output.append({'query_tokens':qlen,'passage_tokens':plen,'full_pair_tokens':len(full['input_ids']),
                       'processed_pair_tokens':len(processed['input_ids']),'query_tokens_retained':qkeep,
                       'passage_tokens_retained':pkeep,'truncated':len(full['input_ids'])>512,
                       'query_tokens_removed':qlen-qkeep,'passage_tokens_removed':plen-pkeep,
                       'passage_retained_end_character':end,'passage_characters':len(passage)})
    return output


class LocalScorer:
    def __init__(self, config):
        validate_environment(config)
        import importlib.metadata
        import torch
        from sentence_transformers import CrossEncoder
        from huggingface_hub import snapshot_download
        for package,version in config['versions'].items():
            if importlib.metadata.version(package)!=version:
                raise RuntimeError(f'Frozen environment version mismatch: {package}')
        if config['device']=='mps' and not torch.backends.mps.is_available():
            raise RuntimeError('Frozen MPS device unavailable; no silent fallback')
        path=Path(snapshot_download(config['model_name'],revision=config['revision'],local_files_only=True,allow_patterns=list(config['model_files_sha256'])))
        for name,checksum in config['model_files_sha256'].items():
            if sha(path/name)!=checksum:raise RuntimeError('Pinned model file changed')
        self.torch=torch
        self.config=config
        self.model=CrossEncoder(str(path),revision=config['revision'],local_files_only=True,
                                device=config['device'],max_length=512,trust_remote_code=False)
        self.model.eval()
        self.model.requires_grad_(False)
        if self.model.tokenizer.truncation_side!='right' or self.model.max_seq_length!=512:
            raise RuntimeError('Tokenizer truncation/window mismatch')
        if type(self.model.activation_fn).__name__!=config['activation']:
            raise RuntimeError('Model score activation mismatch')

    def score(self,pairs):
        stats=token_accounting(self.model.tokenizer,pairs)
        with self.torch.inference_mode():
            scores=self.model.predict(pairs,batch_size=8,show_progress_bar=False,
                                      processing_kwargs={'text':{'truncation':'longest_first','max_length':512,'padding':True}})
        return [float(value) for value in scores],stats


def rerank(rows,scores,stats):
    if len(rows)!=len(scores) or len(rows)!=len(stats):raise ValueError('Score/accounting alignment mismatch')
    output=[]
    for row,score,info in zip(rows,scores,stats):
        if not math.isfinite(score):raise ValueError('Non-finite cross-encoder score')
        if info['processed_pair_tokens']>512 or info['truncated']!=(info['full_pair_tokens']>512):
            raise ValueError('Invalid truncation accounting')
        candidate=deepcopy(row)
        candidate.pop('relevant',None)
        candidate.update(cross_encoder_score=float(score),truncation=deepcopy(info))
        output.append(candidate)
    output.sort(key=lambda r:(-r['cross_encoder_score'],r['corpus_index']))
    for rank,row in enumerate(output,1):row['rank']=row['cross_encoder_rank']=rank
    return output


def oracle(rows,question):
    """Analysis-only label oracle, called after actual rankings are final."""
    return any(saved_result_is_relevant(r,question) for r in rows)


def inspect_target_windows(rankings,records):
    """Display-only source anchors after scoring; never fed to the model.

    These explicit phrases were inspected in the frozen targeted passages. They
    demonstrate retained/omitted text, not answer-span labels or causal proof.
    """
    patterns = {
        'DRE-04': [('territorial equal-benefit statement',r'territory\s+thus\s+acquired'),
                   ('constitutional limits on Congress',r'Congress\s+can\s+exercise\s+no\s+power'),
                   ('enslaved people as property statement',r'recognises\s+slaves')],
        'OBE-01': [('explicit two-question grant',r'limited\s+to\s+two\s+questions'),
                   ('second question introduction',r'The\s+second')],
    }
    notes=[]
    for q in rankings:
        if q['id'] not in patterns:continue
        for row in q['retrieved']:
            if not row['relevant']:continue
            text=records[row['corpus_index']]['text'];end=row['truncation']['passage_retained_end_character']
            anchors=[]
            for name,pattern in patterns[q['id']]:
                for match in re.finditer(pattern,text,re.I):
                    anchors.append({'description':name,'start_character':match.start(),'end_character':match.end(),
                                    'anchor_retained':match.end()<=end,
                                    'source_excerpt':' '.join(text[match.start():match.start()+250].split())})
            notes.append({'question_id':q['id'],'source_file':row['source_file'],'chunk_index':row['chunk_index'],
                          'hybrid_rank':row['hybrid_rank'],'cross_encoder_rank':row['rank'],
                          'passage_truncated':row['truncation']['passage_tokens_removed']>0,
                          'retained_end_character':end,'passage_characters':len(text),'anchors':anchors,
                          'limitation':'Anchor visibility is direct source evidence, not a new relevance decision or proof that truncation caused the rank.'})
    return notes


def summarize(collection,baseline,results,rankings,questions,records):
    changes=[];trunc=[];covered=0
    for old,new,raw,q in zip(baseline['questions'],results['questions'],rankings,questions):
        before=old['metrics']['first_relevant_rank'];after=new['metrics']['first_relevant_rank']
        covered+=oracle(raw['retrieved'],q)
        changes.append({'question_id':q['id'],'question':q['question'],'hybrid_first_relevant_rank':before,
                        'cross_encoder_first_relevant_rank':after,'change':rank_change(before,after),
                        'rescued_hybrid_miss':before is None and after is not None,
                        'lost_hybrid_hit':before is not None and after is None})
        trunc.extend(raw['retrieved'])
    full=[r['truncation']['passage_tokens'] for r in trunc]
    count=sum(r['truncation']['truncated'] for r in trunc)
    ceiling=covered/40
    types={name:group_metrics(model['questions'],'type') for name,model in [('hybrid',baseline),('cross_encoder',results)]}
    cases={name:group_metrics(model['questions'],'expected_case') for name,model in [('hybrid',baseline),('cross_encoder',results)]}
    def dist(values):
        ordered=sorted(values)
        return {'min':min(values),'max':max(values),'mean':statistics.mean(values),'median':statistics.median(values),
                'p90_nearest_rank':ordered[math.ceil(.9*len(ordered))-1]}
    return {'collection':collection,'hybrid_metrics':baseline['metrics'],'reranked_metrics':results['metrics'],
            'absolute_differences':{m:results['metrics'][m]-baseline['metrics'][m] for m in METRICS},
            'oracle':{'union_relevant_question_count':covered,'question_count':40,'maximum_possible_hit_at_1':ceiling,
                      'maximum_possible_hit_at_3':ceiling,'maximum_possible_hit_at_5':ceiling,'maximum_possible_mrr':ceiling,
                      'definition':'Analysis-only theoretical ceiling: place any label-relevant union candidate first; labels never enter inference.'},
            'truncation':{'candidate_count':len(trunc),'truncated_count':count,'truncated_percentage':100*count/len(trunc),
                          'passage_token_lengths':dist(full),'full_pair_token_lengths':dist([r['truncation']['full_pair_tokens'] for r in trunc]),
                          'query_truncated_count':sum(r['truncation']['query_tokens_removed']>0 for r in trunc),
                          'label_relevant_candidate_count':sum(r['relevant'] for r in trunc),
                          'label_relevant_truncated_count':sum(r['relevant'] and r['truncation']['truncated'] for r in trunc),
                          'answer_outside_window':'Possible, not established by page labels. Retained passage end-character offsets are saved for direct source inspection.'},
            'rank_change_counts':{key:sum(q['change']==key for q in changes) for key in ('improved','worsened','tie','shared_miss')},
            'rescued_question_ids':[q['question_id'] for q in changes if q['rescued_hybrid_miss']],
            'lost_question_ids':[q['question_id'] for q in changes if q['lost_hybrid_hit']],
            'questions':changes,'by_question_type':types,'by_case':cases,
            'targeted_window_observations':inspect_target_windows(rankings,records),
            'targeted_questions':[{'comparison':change,'candidates':raw['retrieved']} for change,raw in zip(changes,rankings) if change['question_id'] in TARGETS]}


def report(a):
    e=a['environment']
    lines=['# CourtLens Phase 6A — local cross-encoder evidence reranking','',
           f'Model: `{e["model_name"]}`, immutable model/config/tokenizer revision `{e["revision"]}`. Device `{e["device"]}`; batch size 8; max paired sequence 512 tokens; `{e["activation"]}` activation; `{e["dtype"]}`. Pretrained and unmodified; eval/inference mode; no gradients or fine-tuning. Framework versions and model-file hashes are in manifests and cross_encoder_environment.json.','',
           'Inference inputs are only the original question and original frozen passage. Complete saved hybrid unions are reranked separately. No dense, BM25, or RRF retrieval is performed. Score descending; original corpus order resolves ties. Existing Benchmark v2 Top-5 metrics and MRR are unchanged.','',
           'Truncation is tokenizer longest_first on the paired input, right side, to 512 INCLUDING special tokens. Query tokens normally survive because questions are shorter; token-level retained query/passage counts and passage end-character offsets are saved. No sentence/window selection or chunk-text editing occurs.','',
           '## Hybrid and cross-encoder comparison','', '| Collection | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |','|---|---|---:|---:|---:|---:|']
    for c in a['comparisons']:
        for label,key in [('hybrid','hybrid_metrics'),('cross_encoder','reranked_metrics')]:
            m=c[key];lines.append(f'| {c["collection"]} | {label} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
    for c in a['comparisons']:
        lines+=['',f'## {c["collection"]}','',f'Absolute changes (reranked minus hybrid): {c["absolute_differences"]}.', '',
                f'First-relevant-rank changes: {c["rank_change_counts"]}. Rescued misses: {c["rescued_question_ids"]}; lost hits: {c["lost_question_ids"]}.', '',
                f'Analysis-only oracle: {c["oracle"]["union_relevant_question_count"]}/40 questions have any label-relevant union candidate. Maximum possible Hit@1, Hit@3, Hit@5, and MRR each {c["oracle"]["maximum_possible_mrr"]:.3f}. This theoretical ceiling is not an achieved ranking and never influences actual scores.', '',
                f'Truncation: {c["truncation"]}.','',
                '### All question changes','', '| Question | Hybrid first rank | Reranked first rank | Change |','|---|---:|---:|---|']
        for q in c['questions']:
            lines.append(f'| {q["question_id"]} | {q["hybrid_first_relevant_rank"] or "miss"} | {q["cross_encoder_first_relevant_rank"] or "miss"} | {q["change"]} |')
        lines+=['','### Targeted complete candidate rankings','']
        for target in c['targeted_questions']:
            q=target['comparison'];lines += [f'**{q["question_id"]}:** {q["question"]}', '',
                '| Source | Pages | Chunk index | Hybrid rank | CE rank | CE score | Relevant | Truncated | Passage tokens kept / full |',
                '|---|---|---:|---:|---:|---:|---|---|---|']
            for r in target['candidates']:
                t=r['truncation'];lines.append(f'| {r["source_file"]} | {r["page_start"]}–{r["page_end"]} | {r["chunk_index"]} | {r["hybrid_rank"]} | {r["rank"]} | {r["cross_encoder_score"]:.6f} | {r["relevant"]} | {t["truncated"]} | {t["passage_tokens_retained"]}/{t["passage_tokens"]} |')
            lines.append('')
        lines+=['','### Targeted retained-window source checks','',
                'The following display-only anchors were inspected in the frozen passages. They do not change labels or scores and do not establish that truncation caused a ranking failure.','']
        for note in c['targeted_window_observations']:
            lines += [f'**{note["question_id"]}, chunk {note["chunk_index"]}:** passage truncated={note["passage_truncated"]}; retained end character {note["retained_end_character"]}/{note["passage_characters"]}.','']
            for anchor in note['anchors']:
                lines += [f'- {anchor["description"]}: characters {anchor["start_character"]}–{anchor["end_character"]}; anchor retained={anchor["anchor_retained"]}. Source context: {anchor["source_excerpt"]}']
            lines.append('')
        for field in ('by_question_type','by_case'):
            lines+=['',f'### {field}','', '| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |','|---|---:|---|---:|---:|---:|---:|']
            for group in c[field]['hybrid']:
                for label in ('hybrid','cross_encoder'):
                    m=c[field][label][group];lines.append(f'| {group} | {m["question_count"]} | {label} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
    lines+=['','## OBE-01 availability and input window','',
            'Fixed OBE-01 has an accepted pp13–14 candidate originally at hybrid rank 7; its cross-encoder rank is shown above. Structure-aware OBE-01 has no accepted candidate anywhere in its saved union, so reranking cannot solve that missing-candidate problem. Neither labels nor the prior Phase 5A possible-gap annotations were changed.','',
            'Relevant page overlap does not prove that the answer survives truncation. Inspect the original chunk at the recorded retained end-character offset; pages alone cannot identify answer spans.','',
            '## Limitations','']+['- '+x for x in LIMITATIONS]
    lines+=['','## Reproducibility and protection','',
            f'All {a["protected_artifacts"]["file_count"]} protected pre-existing data files remain SHA-256 identical. Full before/after hashes are in JSON. No production retrieval, chunks, benchmarks, prior reports, or vector stores were changed. No Vercel calls, new embeddings, fine-tuning, commits, or pushes.','',
            'Network was used only for authorized dependency installation and pinned Hugging Face model download. Benchmark inference is local. `.venv/bin/python run_cross_encoder_experiment.py --replay` validates and reconstructs results from saved scores without loading a model or repeating inference. Real-inference reruns require an explicit `--infer` and refuse overwriting existing results.','',
            'READY for the next phase as a completed evaluation baseline, not evidence that this reranker improves every metric. No subsequent phase has started.','']
    return '\n'.join(lines)


def build_outputs(scorer,root=ROOT):
    before=protected_snapshot(root)
    env=load(root/ENVIRONMENT);validate_environment(env)
    qs=load(root/BENCHMARK)['questions']
    outputs={};comparisons=[]
    for collection in COLLECTIONS:
        records,raw,baseline,pairs,hashes=load_inputs(collection,qs,root)
        scores,stats=scorer.score(pairs)
        if len(scores)!=len(pairs) or len(stats)!=len(pairs):raise ValueError('Inference count mismatch')
        evaluated=[];rankings=[];offset=0
        for q,saved in zip(qs,raw['questions']):
            n=len(saved['retrieved'])
            rows=rerank(saved['retrieved'],scores[offset:offset+n],stats[offset:offset+n]);offset+=n
            for row in rows:row['relevant']=saved_result_is_relevant(row,q)
            rankings.append({'id':q['id'],'question':q['question'],'retrieved':rows,'candidate_count':n})
            item={key:deepcopy(q[key]) for key in ('id','question','type','expected_case','expected_source_file','relevant_ranges')}
            item['metrics']=score_retrieved(rows,q);evaluated.append(item)
        results={'collection':collection,'metrics':aggregate(evaluated),'questions':evaluated,'official_metric_depth':5,'mrr_depth':5}
        comparisons.append(summarize(collection,baseline,results,rankings,qs,records))
        manifest={'phase':'6A','collection':collection,'environment':env,'candidate_pair_count':len(pairs),'chunk_count':len(records),'question_count':40,
                  'ranking_uses_labels_or_metadata':False,'complete_saved_hybrid_union':True,'score_tie_break':'original corpus order',
                  'input_sha256':{**hashes,str(BENCHMARK):sha(root/BENCHMARK),str(ENVIRONMENT):sha(root/ENVIRONMENT),str(LOCK):sha(root/LOCK)},
                  'implementation_sha256':{name:sha(ROOT/name) for name in ('run_cross_encoder_experiment.py','finalize_chunking_benchmark.py','benchmark_relevance.py')}}
        outputs[BASE/collection/'manifest.json']=encode(manifest)
        outputs[BASE/collection/'rankings.json']=encode({'collection':collection,'questions':rankings})
        outputs[BASE/collection/'results.json']=encode(results)
        print(f'{collection}: {len(pairs)} candidate pairs scored.',flush=True)
    after=protected_snapshot(root)
    if before!=after:raise RuntimeError('Protected artifacts changed')
    analysis={'phase':'6A','environment':env,'comparisons':comparisons,'limitations':LIMITATIONS,
              'protected_artifacts':{'file_count':len(before),'unchanged':True,'before_sha256':before,'after_sha256':after}}
    outputs[ANALYSIS]=encode(analysis);outputs[REPORT]=report(analysis)
    return outputs


class ReplayScorer:
    def __init__(self,root=ROOT):
        self.groups=[]
        qs=load(root/BENCHMARK)['questions']
        for collection in COLLECTIONS:
            _,raw,_,pairs,_=load_inputs(collection,qs,root)
            manifest=load(root/BASE/collection/'manifest.json')
            for path,checksum in manifest['input_sha256'].items():
                if sha(root/path)!=checksum:raise ValueError('Replay source/provenance changed')
            for path,checksum in manifest['implementation_sha256'].items():
                if sha(ROOT/path)!=checksum:raise ValueError('Replay implementation changed')
            saved=load(root/BASE/collection/'rankings.json')
            if saved['collection']!=collection or [q['id'] for q in saved['questions']]!=[q['id'] for q in qs]:
                raise ValueError('Replay question/corpus mismatch')
            scores=[];stats=[]
            for original,q in zip(raw['questions'],saved['questions']):
                mapping={r['corpus_index']:r for r in q['retrieved']}
                if len(mapping)!=len(original['retrieved']) or len(mapping)!=len(q['retrieved']):
                    raise ValueError('Replay candidate mismatch')
                for row in original['retrieved']:
                    candidate=mapping[row['corpus_index']]
                    if candidate['hybrid_rank']!=row['rank']:raise ValueError('Replay hybrid rank mismatch')
                    scores.append(candidate['cross_encoder_score']);stats.append(candidate['truncation'])
            self.groups.append((pairs,scores,stats))

    def score(self,pairs):
        expected,scores,stats=self.groups.pop(0)
        if pairs!=expected:raise ValueError('Replay pair order mismatch')
        return scores,stats


def write_outputs(outputs,root=ROOT):
    if set(outputs)!=output_paths():raise ValueError('Only Phase 6A paths allowed')
    for path,text in outputs.items():
        if (root/path).exists() and (root/path).read_bytes()!=text.encode():raise FileExistsError(f'Refusing overwrite: {path}')
    for path,text in outputs.items():
        if not (root/path).exists():
            (root/path).parent.mkdir(parents=True,exist_ok=True)
            with (root/path).open('x',encoding='utf-8') as f:f.write(text)


def main():
    parser=argparse.ArgumentParser();modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--infer',action='store_true');modes.add_argument('--replay',action='store_true');args=parser.parse_args()
    if args.infer and any((ROOT/p).exists() for p in output_paths()):raise FileExistsError('Existing Phase 6A results; use --replay. No inference performed.')
    before=protected_snapshot()
    scorer=LocalScorer(load(ROOT/ENVIRONMENT)) if args.infer else ReplayScorer()
    outputs=build_outputs(scorer)
    if args.replay:
        if any((ROOT/p).read_bytes()!=text.encode() for p,text in outputs.items()):raise ValueError('Saved artifact replay mismatch')
    else:write_outputs(outputs)
    if before!=protected_snapshot():raise RuntimeError('Protected artifacts changed')
    print('Phase 6A '+('saved-score replay verified' if args.replay else 'local inference complete')+f'; {len(before)} protected files unchanged.')


if __name__=='__main__':main()
