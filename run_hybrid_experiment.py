"""Phase 5B: fuse SAVED rankings locally; no retriever or API is invoked."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from hybrid_retrieval import ChunkCatalog, fuse, K, DEPTH
from run_bm25_experiment import (ROOT, BENCHMARK, DENSE, COLLECTIONS, DENSE_IDS,
                                COUNTS, ROW_FIELDS, load_corpus, load, encode, sha, group_metrics)
from finalize_chunking_benchmark import aggregate, score_retrieved, saved_result_is_relevant

BASE = Path('data/experiments/retrieval/hybrid')
ANALYSIS = Path('data/analysis/hybrid_retrieval_evaluation.json')
REPORT = Path('data/analysis/hybrid_retrieval_evaluation.md')
METRICS = ('hit_at_1', 'hit_at_3', 'hit_at_5', 'mrr')
LOCKED = {
    'fixed_900_150': {'dense': (.750, .900, .900, .825), 'bm25': (.725, .875, .950, .805)},
    'structure_aware_v1': {'dense': (.825, .925, .950, .8770833333333334),
                           'bm25': (.675, .875, .925, .7820833333333334)},
}
TARGETS = ('DRE-04', 'OBE-01', 'GID-05', 'NYT-01', 'MAR-05', 'MIR-02')
LIMITATIONS = [
    'Benchmark v2 was refined using evaluated dense candidates; it is not an independent holdout.',
    'Case/source/page-overlap relevance is a coarse proxy and can produce false positives and negatives.',
    'Only saved dense Top-5 and BM25 Top-5 are fused. The union has at most ten unique chunks; relevant union candidates can fall below hybrid rank five. Deeper fusion is a future experiment.',
    'Chunk-size distributions differ; structure-aware excludes 200 tokenizer tokens of foreign Sturgis/Honold material retained in fixed chunks.',
    'RRF k=60 and both candidate depths=5 were fixed before evaluation and never tuned. Raw scores, labels, and opinion/case metadata do not affect fusion.',
    'Findings and small subgroup comparisons are descriptive; no statistical significance, general superiority, or routing rule is implied.',
]


def output_paths():
    return {ANALYSIS, REPORT} | {BASE / c / name for c in COLLECTIONS for name in ('manifest.json', 'rankings.json', 'results.json')}


def protected_snapshot(root=ROOT):
    return {str(p.relative_to(root)): sha(p) for p in sorted((root / 'data').rglob('*'))
            if p.is_file() and p.relative_to(root) not in output_paths()}


def check_questions(saved, questions):
    if len(saved) != 40 or [q['id'] for q in saved] != [q['id'] for q in questions]:
        raise ValueError('Saved question order/count mismatch')
    for old, q in zip(saved, questions):
        for field in ('question', 'type', 'expected_case', 'expected_source_file', 'relevant_ranges'):
            if field in old and old[field] != q[field]:
                raise ValueError(f'Saved benchmark mismatch: {field}')


def rank_change(before, after):
    if before is None and after is None:
        return 'shared_miss'
    a, b = before or float('inf'), after or float('inf')
    return 'improved' if b < a else ('worsened' if b > a else 'tie')


def summarize(collection, controls, results, rankings):
    rows = []
    for i, q in enumerate(results['questions']):
        d = controls['dense']['questions'][i]['metrics']['first_relevant_rank']
        b = controls['bm25']['questions'][i]['metrics']['first_relevant_rank']
        h = q['metrics']['first_relevant_rank']
        union = rankings[i]['retrieved']
        relevant = [r for r in union if r['relevant']]
        below = [r['rank'] for r in relevant if r['rank'] > 5]
        rows.append({'question_id': q['id'], 'question': q['question'], 'dense_first_relevant_rank': d,
                     'bm25_first_relevant_rank': b, 'hybrid_first_relevant_rank': h,
                     'union_has_relevant_candidate': bool(relevant),
                     'union_first_relevant_rank': relevant[0]['rank'] if relevant else None,
                     'relevant_candidates_below_top5': below,
                     'relevant_candidate_falls_below_top5': bool(below),
                     'all_relevant_candidates_fall_below_top5': bool(relevant) and h is None,
                     'rescues_dense_miss': d is None and h is not None,
                     'rescues_bm25_miss': b is None and h is not None,
                     'rescues_shared_miss': d is None and b is None and h is not None,
                     'loses_dense_hit': d is not None and h is None,
                     'loses_bm25_hit': b is not None and h is None,
                     'rank_change_vs_dense': rank_change(d, h), 'rank_change_vs_bm25': rank_change(b, h),
                     'ranking_explanation': '; '.join(f"hybrid {r['rank']}: corpus ordinal {r['corpus_index']}, dense {r['dense_rank']}, BM25 {r['bm25_rank']}, RRF {r['rrf_score']:.9f}, benchmark relevant {r['relevant']}" for r in union)})
    def ids(predicate):
        return [q['question_id'] for q in rows if predicate(q)]
    events = {key: ids(lambda q, key=key: q[key]) for key in ('rescues_dense_miss', 'rescues_bm25_miss', 'rescues_shared_miss', 'loses_dense_hit', 'loses_bm25_hit', 'all_relevant_candidates_fall_below_top5')}
    events['dense_only_hits_recovered'] = ids(lambda q: q['dense_first_relevant_rank'] is not None and q['bm25_first_relevant_rank'] is None and q['hybrid_first_relevant_rank'] is not None)
    events['bm25_only_hits_recovered'] = ids(lambda q: q['bm25_first_relevant_rank'] is not None and q['dense_first_relevant_rank'] is None and q['hybrid_first_relevant_rank'] is not None)
    events['hybrid_top5_misses'] = ids(lambda q: q['hybrid_first_relevant_rank'] is None)
    models = {**controls, 'hybrid': results}
    return {'collection': collection, 'metrics': {name: model['metrics'] for name, model in models.items()},
            'absolute_differences': {name: {m: results['metrics'][m] - controls[name]['metrics'][m] for m in METRICS} for name in ('dense', 'bm25')},
            'union_size_distribution': dict(sorted(Counter(len(q['retrieved']) for q in rankings).items())),
            'candidate_union_hit_count': sum(q['union_has_relevant_candidate'] for q in rows),
            'candidate_union_coverage': sum(q['union_has_relevant_candidate'] for q in rows) / 40,
            'hybrid_hit_count': sum(q['hybrid_first_relevant_rank'] is not None for q in rows),
            'events': events, 'event_counts': {key: len(value) for key, value in events.items()},
            'rank_change_counts': {name: dict(Counter(q['rank_change_vs_' + name] for q in rows)) for name in ('dense', 'bm25')},
            'questions': rows, 'targeted_questions': [q for q in rows if q['question_id'] in TARGETS],
            'by_question_type': {name: group_metrics(model['questions'], 'type') for name, model in models.items()},
            'by_case': {name: group_metrics(model['questions'], 'expected_case') for name, model in models.items()}}


def report(a):
    lines = ['# CourtLens Phase 5B — reciprocal rank fusion', '',
             'Rank-only RRF: `RRF(d)=Σ 1/(60+rank_i(d))`, with one-based ranks. Dense depth=5; BM25 depth=5. An absent candidate contributes zero. Duplicate cross-list identities are merged; duplicates within a list are rejected. Ties use original corpus order. Raw scores and metadata are diagnostic only.', '',
             'Saved dense rankings contain exactly five results per question. BM25 saved Top-20 is validated but only Top-5 enters fusion. No dense or BM25 retrieval is rerun by this experiment. Official Hit@K and MRR use the fused Top-5 and the existing unchanged evaluator.', '',
             '## Six configurations', '', '| Collection | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---|---:|---:|---:|---:|']
    for c in a['comparisons']:
        for name, m in c['metrics'].items():
            lines.append(f'| {c["collection"]} | {name} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
    for c in a['comparisons']:
        lines += ['', f'## {c["collection"]} — coverage and changes', '',
                  f'Union sizes (unique chunks: number of questions): {c["union_size_distribution"]}. Candidate union coverage: {c["candidate_union_hit_count"]}/40 ({c["candidate_union_coverage"]:.3f}). Final hybrid Hit@5: {c["hybrid_hit_count"]}/40 ({c["metrics"]["hybrid"]["hit_at_5"]:.3f}). Union coverage is an availability ceiling, not achieved hybrid performance.', '',
                  '| Hybrid minus | ΔHit@1 | ΔHit@3 | ΔHit@5 | ΔMRR |', '|---|---:|---:|---:|---:|']
        for name, d in c['absolute_differences'].items():
            lines.append(f'| {name} | ' + ' | '.join(f'{d[m]:+.6f}' for m in METRICS) + ' |')
        lines += ['', f'First relevant rank comparisons (miss treated as infinity): {c["rank_change_counts"]}.', '']
        for name, ids in c['events'].items():
            lines.append(f'- {name}: {len(ids)} — ' + (', '.join(ids) or 'None'))
        lines += ['', '### Targeted questions', '', '| Question | Dense rank | BM25 rank | Hybrid rank | Rescues dense / BM25 miss | Relevant ranks below 5 |', '|---|---:|---:|---:|---|---|']
        for q in c['targeted_questions']:
            rank = lambda key: q[key] if q[key] is not None else 'miss'
            lines.append(f'| {q["question_id"]} | {rank("dense_first_relevant_rank")} | {rank("bm25_first_relevant_rank")} | {rank("hybrid_first_relevant_rank")} | {q["rescues_dense_miss"]} / {q["rescues_bm25_miss"]} | {q["relevant_candidates_below_top5"]} |')
        for q in c['targeted_questions']:
            lines += ['', f'**{q["question_id"]}:** {q["question"]}', '', q['ranking_explanation'], '']
        for field in ('by_question_type', 'by_case'):
            lines += ['', f'### {field}', '', '| Group | N | Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---:|---|---:|---:|---:|---:|']
            for group in c[field]['hybrid']:
                for name in ('dense', 'bm25', 'hybrid'):
                    m = c[field][name][group]
                    lines.append(f'| {group} | {m["question_count"]} | {name} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
    lines += ['', '## Identity verification and reproducibility', '',
              'Each corpus uses its own namespace plus source_file + original chunk_index. Structure-aware chunk IDs are also verified exactly. Dense vector_id is verified against saved vector-store records, which are matched by complete text/metadata to frozen chunks. BM25 corpus_index and chunk_reference are verified. Page overlap never defines identity. Corpus counts are 598 and 433; all 40 questions follow benchmark order.', '',
              'The complete deduplicated union, including relevance decisions below rank five, is saved separately from official Top-5 metrics. Reproduce with `.venv/bin/python run_hybrid_experiment.py`. Conflicting output files are rejected; identical replay is a no-op. Manifests record input/source hashes and fixed parameters.', '',
              f'All {a["protected_artifacts"]["file_count"]} pre-existing data files are SHA-256 identical. Full before/after hashes are in the analysis JSON. No API, embedding, index rebuild, label change, commit, or push.', '', '## Limitations', '']
    lines += ['- ' + s for s in LIMITATIONS]
    lines += ['', 'READY for Phase 6 as an evaluation baseline, not a claim that RRF improves every metric. Phase 6 has not started; no reranking, query expansion, or routing is implemented.', '']
    return '\n'.join(lines)


def build_outputs(root=ROOT):
    before = protected_snapshot(root)
    benchmark = load(root / BENCHMARK)
    qs = benchmark['questions']
    if len(qs) != 40 or len({q['id'] for q in qs}) != 40:
        raise ValueError('Require forty unique benchmark questions')
    dense_configs = {c['id']: c for c in load(root / DENSE)['configurations']}
    outputs, comparisons = {}, []
    for collection in COLLECTIONS:
        records, hashes = load_corpus(collection, root)
        catalog = ChunkCatalog(collection, records)
        vs = Path('data/experiments/chunking') / DENSE_IDS[collection] / 'vector_store/records.jsonl'
        vectors = [json.loads(line) for line in (root / vs).read_text().splitlines() if line.strip()]
        if len(vectors) != COUNTS[collection]:
            raise ValueError('Dense records count mismatch')
        vector_ordinals = {}
        for i, r in enumerate(vectors):
            if type(r['vector_id']) is not int or r['vector_id'] != i:
                raise ValueError('Dense vector ID/order mismatch')
            ordinal = catalog.verify({**r['metadata'], 'text': r['text']})
            if r['metadata'] != records[ordinal]['metadata']:
                raise ValueError('Dense full metadata mismatch')
            vector_ordinals[i] = ordinal
        if len(set(vector_ordinals.values())) != len(records):
            raise ValueError('Dense records are not bijective with frozen chunks')
        directory = Path('data/experiments/retrieval/bm25') / collection
        paths = [BENCHMARK, DENSE, vs, directory/'rankings_top20.json', directory/'results.json', directory/'manifest.json']
        manifest = load(root / paths[-1])
        if manifest['collection'] != collection or manifest['chunk_count'] != len(records) or manifest['corpus_source_sha256'] != hashes or manifest['benchmark_sha256'] != sha(root/BENCHMARK) or manifest['dense_result_sha256'] != sha(root/DENSE):
            raise ValueError('BM25 manifest provenance mismatch')
        bm25 = load(root / directory / 'results.json')
        raw = load(root / directory / 'rankings_top20.json')
        dense = dense_configs[DENSE_IDS[collection]]
        if dense['vector_count'] != len(records) or bm25['collection'] != collection or raw['collection'] != collection:
            raise ValueError('Saved retrieval corpus mismatch')
        controls = {'dense': dense, 'bm25': bm25}
        for model in (dense, bm25, raw):
            check_questions(model['questions'], qs)
        evaluated, ranked = [], []
        for q, d, b, rawq in zip(qs, dense['questions'], bm25['questions'], raw['questions']):
            dr = d['metrics']['retrieved']
            br = rawq['retrieved']
            if len(dr) != 5 or len(br) != 20:
                raise ValueError('Expected saved dense Top-5 and BM25 Top-20')
            for r in dr:
                if type(r.get('vector_id')) is not int or vector_ordinals.get(r['vector_id']) != catalog.verify(r):
                    raise ValueError('Dense ranking vector identity mismatch')
            seen = set()
            for i, r in enumerate(br, 1):
                ordinal = catalog.verify(r)
                if r['rank'] != i or ordinal in seen:
                    raise ValueError('Invalid BM25 saved ranks/duplicates')
                seen.add(ordinal)
            if br != sorted(br, key=lambda r: (-r['bm25_score'], r['corpus_index'])):
                raise ValueError('BM25 saved score order mismatch')
            for name, rows, saved in [('dense', dr, d), ('bm25', br, b)]:
                scored = score_retrieved(rows, q)
                if scored != saved['metrics']:
                    raise ValueError(f'Saved {name} scoring mismatch')
            union = fuse(catalog, dr, br)
            for r in union:
                r['relevant'] = saved_result_is_relevant(r, q)
            ranked.append({'id': q['id'], 'question': q['question'], 'union_size': len(union), 'retrieved': union})
            item = {field: deepcopy(q[field]) for field in ('id', 'question', 'type', 'expected_case', 'expected_source_file', 'relevant_ranges')}
            item['metrics'] = score_retrieved(union, q)
            evaluated.append(item)
        for name, model in controls.items():
            recomputed = aggregate(model['questions'])
            if recomputed != model['metrics'] or any(abs(recomputed[m]-v)>1e-12 for m,v in zip(METRICS,LOCKED[collection][name])):
                raise ValueError('Control metrics mismatch')
        result = {'collection': collection, 'metrics': aggregate(evaluated), 'questions': evaluated, 'official_metric_depth': 5, 'mrr_depth': 5}
        comparison = summarize(collection, controls, result, ranked)
        comparisons.append(comparison)
        m = {'phase': '5B', 'collection': collection, 'k': K, 'dense_candidate_depth': DEPTH, 'bm25_candidate_depth': DEPTH,
             'chunk_count': len(records), 'question_count': 40, 'saved_dense_depths': [5], 'saved_bm25_depth': 20,
             'tie_break': 'original frozen corpus ordinal ascending', 'identity': 'corpus namespace + source_file + original chunk_index; original IDs additionally verified',
             'ranking_uses_raw_scores_metadata_or_labels': False, 'parameters_tuned': False, 'input_sha256': {**hashes, **{str(p):sha(root/p) for p in paths}},
             'source_sha256': {name:sha(ROOT/name) for name in ('hybrid_retrieval.py','run_hybrid_experiment.py','finalize_chunking_benchmark.py','benchmark_relevance.py')},
             'foreign_tokens_excluded': 200 if collection=='structure_aware_v1' else 0}
        outputs[BASE/collection/'manifest.json'] = encode(m)
        outputs[BASE/collection/'rankings.json'] = encode({'collection': collection, 'candidate_depths': {'dense':5,'bm25':5}, 'questions':ranked})
        outputs[BASE/collection/'results.json'] = encode(result)
    after = protected_snapshot(root)
    if before != after:
        raise RuntimeError('Protected input mutation detected')
    a = {'phase':'5B', 'comparisons':comparisons, 'limitations':LIMITATIONS, 'protected_artifacts':{'file_count':len(before),'unchanged':True,'before_sha256':before,'after_sha256':after}}
    outputs[ANALYSIS] = encode(a)
    outputs[REPORT] = report(a)
    return outputs


def write_outputs(outputs, root=ROOT):
    if set(outputs) != output_paths():
        raise ValueError('Only eight new Phase 5B paths may be written')
    for p, text in outputs.items():
        if (root/p).exists() and (root/p).read_bytes() != text.encode():
            raise FileExistsError(f'Refusing conflicting output: {p}')
    for p, text in outputs.items():
        path = root/p
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('x',encoding='utf-8') as f:
                f.write(text)


def main():
    before = protected_snapshot()
    outputs = build_outputs()
    write_outputs(outputs)
    if before != protected_snapshot():
        raise RuntimeError('Protected input mutation detected')
    print(f'Phase 5B complete: saved-rank fusion for 40 questions × 2 corpora; {len(before)} existing data files unchanged.')


if __name__=='__main__':
    main()
