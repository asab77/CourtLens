"""Phase 5A: local BM25 on frozen chunks, compared to SAVED Benchmark v2 dense.

No SDK, FAISS, embedding, tokenizer download, dependency install, or network.
BM25 settings are locked before evaluation; metadata is attached after ranking.
"""

from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

from bm25_retrieval import BM25, K1, B, TOKENIZER_DESCRIPTION, TOKENIZER_VERSION, tokenize
from finalize_chunking_benchmark import aggregate, score_retrieved


ROOT = Path(__file__).resolve().parent
BENCHMARK = Path('data/evaluation/chunking_benchmark_v2.json')
DENSE = Path('data/experiments/chunking/benchmark_v2_results.json')
EXPERIMENT_ROOT = Path('data/experiments/retrieval/bm25')
ANALYSIS_JSON = Path('data/analysis/bm25_retrieval_evaluation.json')
ANALYSIS_MD = Path('data/analysis/bm25_retrieval_evaluation.md')
COLLECTIONS = ('fixed_900_150', 'structure_aware_v1')
COUNTS = {'fixed_900_150': 598, 'structure_aware_v1': 433}
DENSE_IDS = {'fixed_900_150': '900_150', 'structure_aware_v1': 'structure_aware_v1'}
CONTROLS = {'fixed_900_150': (.750, .900, .900, .825),
            'structure_aware_v1': (.825, .925, .950, .8770833333333334)}
METRICS = ('hit_at_1', 'hit_at_3', 'hit_at_5', 'mrr')
ROW_FIELDS = ('chunk_id', 'chunk_index', 'case_name', 'source_file', 'original_source_file',
              'page_start', 'page_end', 'token_count', 'opinion_type', 'author',
              'major_unit_id', 'major_unit_type', 'sections')
EVALUATION_DATE = '2026-10-10'
LIMITATIONS = [
    'Benchmark v2 was refined using retrieval candidates from the evaluated dense systems and is not an independent holdout test.',
    'Page-overlap relevance can produce false positives and false negatives, including a chunk carrying only a page marker or lacking the actual answer.',
    'The chunk collections differ in realized size distributions and source coverage: structure-aware excludes 200 cl100k_base tokens of foreign Sturgis/Honold material retained in fixed chunks. No corpus was altered to equalize them.',
    'No hyperparameter tuning or label-driven tokenization choices were conducted. k1=1.5, b=.75, tokenizer, IDF convention, tie and zero-score policies were fixed before evaluation.',
    'Frozen OCR, headers, footnotes, and page-marker text remain in lexical inputs. No OCR repair, stemming, stopword removal, synonyms, expansion, or legal ranking boosts are applied.',
    'Observed differences are descriptive performance on these forty questions, not proof of general superiority. No statistical significance or reliable subgroup routing claim is made.',
    'Higher lexical scores do not establish greater semantic or legal correctness. Existing opinion metadata may be absent, uncertain, or inaccurate; it never affects ranking.',
]

# Populated only by manual inspection of the saved Phase 5A targeted evidence.
# These annotations never enter BM25 or benchmark relevance computation.
TARGETED_REVIEW = {('fixed_900_150', 'DRE-04', 1): {'status': 'CROSS-CASE QUOTATION',
                                  'rationale': 'Roberts quotes Dred Scott property/due-process reasoning in '
                                               'Obergefell. This is a cross-case citation, not a missing '
                                               'Dred Scott page range; the required case/source gate fails.',
                                  'anchor': 'The need for restraint',
                                  'source_attribution_note': 'Obergefell, Roberts dissent, identified from '
                                                             'source headings; absent from fixed metadata.'},
 ('fixed_900_150', 'DRE-04', 2): {'status': 'ACCEPTED EVIDENCE',
                                  'rationale': 'The accepted headnote passage states equal territorial '
                                               'access, constitutional limits on Congress, and protection of '
                                               'enslaved people as property.',
                                  'anchor': 'The territory thus acquired',
                                  'source_attribution_note': 'Dred Scott syllabus/headnotes; fixed metadata '
                                                             'has no attribution.'},
 ('fixed_900_150', 'DRE-04', 3): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'McLean discusses citizenship and outlines territorial-power '
                                               'issues; this dissent does not give the Court’s controlling '
                                               'property/due-process rationale.',
                                  'source_attribution_note': 'McLean dissent, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'DRE-04', 4): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'Harlan discusses judicial restraint and segregation in '
                                               'Plessy. The case/source is wrong and the passage does not '
                                               'supply the requested territorial reasoning.',
                                  'source_attribution_note': 'Plessy, Harlan dissent, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'DRE-04', 5): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'Taney distinguishes the Canter judicial-jurisdiction '
                                               'precedent and introduces territorial acquisition. This '
                                               'passage does not independently state the complete '
                                               'property/due-process rationale.',
                                  'source_attribution_note': 'Taney majority, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'OBE-01', 1): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'Alito criticizes the constitutional basis for the new '
                                               'marriage right; this does not identify both questions in the '
                                               'limited certiorari grant.',
                                  'anchor': 'The Constitution says nothing',
                                  'source_attribution_note': 'Alito dissent, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'OBE-01', 2): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'Roberts discusses religious-liberty consequences and '
                                               'judicial policymaking, not the two questions the Court '
                                               'agreed to decide.',
                                  'anchor': 'Federal courts are blunt',
                                  'source_attribution_note': 'Roberts dissent, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'OBE-01', 3): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'The passage recounts Baehr, DOMA, Goodridge, and Windsor '
                                               'history; it does not state the two granted questions.',
                                  'anchor': 'Against this background',
                                  'source_attribution_note': 'Kennedy majority, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'OBE-01', 4): {'status': 'ACCEPTED EVIDENCE',
                                  'rationale': 'The passage explicitly says review was limited to two '
                                               'questions and states the licensing and out-of-state '
                                               'recognition questions under the Fourteenth Amendment.',
                                  'anchor': 'The petitioners sought certiorari.',
                                  'source_attribution_note': 'Kennedy majority, identified from source '
                                                             'headings.'},
 ('fixed_900_150', 'OBE-01', 5): {'status': 'NO CONFIRMED LABEL GAP',
                                  'rationale': 'This syllabus portion discusses history and the licensing '
                                               'holding, rather than both questions granted for review.',
                                  'source_attribution_note': 'Syllabus, identified from source headings.'},
 ('structure_aware_v1', 'DRE-04', 1): {'status': 'ACCEPTED EVIDENCE',
                                       'rationale': 'The accepted headnote passage states '
                                                    'territorial/property protections and the constitutional '
                                                    'invalidity of the prohibition.',
                                       'anchor': 'The territory thus acquired',
                                       'source_attribution_note': 'Syllabus/headnotes in source; preserved '
                                                                  'chunk metadata says unknown.'},
 ('structure_aware_v1', 'DRE-04', 2): {'status': 'CROSS-CASE QUOTATION',
                                       'rationale': 'Roberts quotes the Dred Scott property/due-process '
                                                    'rationale in Obergefell. This fails the benchmark '
                                                    'case/source gate and is not a Dred Scott page-label '
                                                    'gap.',
                                       'anchor': 'The need for restraint'},
 ('structure_aware_v1', 'DRE-04', 3): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'The Canter discussion distinguishes judicial '
                                                    'jurisdiction from Congress’s regulation of property; it '
                                                    'sets up rather than independently supplies the '
                                                    'requested controlling rationale.',
                                       'source_attribution_note': 'Taney majority in source; recorded author '
                                                                  'Tane is preserved unchanged.'},
 ('structure_aware_v1', 'DRE-04', 4): {'status': 'POSSIBLE LABEL GAP',
                                       'rationale': 'Catron argues that Congress cannot strip a citizen of '
                                                    'property or equal participation in common territory. '
                                                    'This is concrete supporting reasoning outside accepted '
                                                    'pages, but it is a separate-opinion argument: whether '
                                                    'it answers “the Court” requires human review under the '
                                                    'existing controlling-reasoning standard. Not a '
                                                    'confirmed addition; no relevance credit or label '
                                                    'change.',
                                       'anchor': 'We must meet the question',
                                       'source_attribution_note': 'Catron separate opinion in source; '
                                                                  'recorded opinion other and OCR author '
                                                                  'Oatron are preserved unchanged.'},
 ('structure_aware_v1', 'DRE-04', 5): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'McLean discusses citizenship, outlines issues, and '
                                                    'advances the locality-of-slavery principle in dissent; '
                                                    'this does not provide the Court’s supporting rationale.',
                                       'source_attribution_note': 'McLean dissent in source; original OCR '
                                                                  'author Mclean retained.'},
 ('structure_aware_v1', 'OBE-01', 1): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'The majority explains fundamental-marriage-right '
                                                    'principles and autonomy, not the two questions granted '
                                                    'for review.',
                                       'anchor': 'This analysis compels'},
 ('structure_aware_v1', 'OBE-01', 2): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'Roberts discusses democracy and religious-liberty '
                                                    'consequences; the limited certiorari questions are not '
                                                    'stated.',
                                       'anchor': 'Federal courts are blunt'},
 ('structure_aware_v1', 'OBE-01', 3): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'Scalia criticizes democratic representation and the '
                                                    'majority’s reasoning, not the two granted questions.'},
 ('structure_aware_v1', 'OBE-01', 4): {'status': 'NO CONFIRMED LABEL GAP',
                                       'rationale': 'Alito discusses whether the Constitution supplies a '
                                                    'marriage right. The footnote’s shorthand “recognize” is '
                                                    'not an explicit statement of the distinct out-of-state '
                                                    'recognition question.',
                                       'anchor': 'The question in these cases'},
 ('structure_aware_v1', 'OBE-01', 5): {'status': 'AMBIGUOUS — PRIOR AUDIT UNRESOLVED',
                                       'rationale': 'The syllabus reports licensing/recognition claims and '
                                                    'holdings, allowing a holding-based reconstruction. It '
                                                    'does not explicitly identify the two limited certiorari '
                                                    'questions. Preserve the prior audit’s unresolved '
                                                    'ambiguity; do not automatically expand labels.',
                                       'anchor': 'Held:'}}


# Display-only anchors selected after reading the complete retrieved chunks.
# They affect evidence excerpts, never scoring or benchmark decisions.
UNIQUE_HIT_EXCERPT_ANCHORS = {
    ('fixed_900_150', 'GID-05'): 'heard by counsel.',
    ('fixed_900_150', 'NYT-01'): 'We granted certiorari',
}


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def output_paths():
    return {ANALYSIS_JSON, ANALYSIS_MD} | {EXPERIMENT_ROOT / c / name for c in COLLECTIONS for name in ('manifest.json', 'rankings_top20.json', 'results.json')}


def protected_snapshot(root=ROOT):
    return {str(p.relative_to(root)): sha(p) for p in sorted((root / 'data').rglob('*'))
            if p.is_file() and p.relative_to(root) not in output_paths()}


def load_corpus(collection, root=ROOT):
    if collection == 'fixed_900_150':
        paths = sorted((root / 'data/experiments/chunking/900_150/chunks').glob('*.jsonl'))
        if len(paths) != 8:
            raise ValueError('Expected eight fixed chunk source files')
    elif collection == 'structure_aware_v1':
        paths = [root / 'data/experiments/chunking/structure_aware_v1/chunks.jsonl']
    else:
        raise ValueError('Unknown frozen collection')
    records = [json.loads(line) for path in paths for line in path.read_text().splitlines() if line.strip()]
    if len(records) != COUNTS[collection]:
        raise ValueError(f'Frozen corpus count mismatch: {collection}')
    references = []
    for r in records:
        m = r['metadata']
        if not isinstance(r['text'], str) or not r['text'].strip():
            raise ValueError('Frozen chunk has missing text')
        if type(m['chunk_index']) is not int or m['chunk_index'] < 0:
            raise ValueError('Invalid original chunk index')
        if not m['source_file'] or not m['case_name'] or type(m['page_start']) is not int or type(m['page_end']) is not int or not 1 <= m['page_start'] <= m['page_end']:
            raise ValueError('Invalid frozen chunk metadata')
        references.append((m['source_file'], m['chunk_index']))
    if len(set(references)) != len(records) or len({r['metadata']['source_file'] for r in records}) != 8:
        raise ValueError('Duplicate chunk identity or incomplete source coverage')
    if collection == 'structure_aware_v1' and len({r['metadata']['chunk_id'] for r in records}) != len(records):
        raise ValueError('Structure-aware IDs are not unique')
    hashes = {str(p.relative_to(root)): sha(p) for p in paths}
    return records, hashes


def rank_queries(records, queries):
    """queries is only (question ID, text); no relevance/case/type inputs."""
    index = BM25([r['text'] for r in records])
    questions = []
    for qid, text in queries:
        scores = index.scores(text)
        ranked = index.rank(text, 20)
        rows = []
        for rank, (ordinal, score) in enumerate(ranked, 1):
            row = {field: deepcopy(records[ordinal]['metadata'].get(field)) for field in ROW_FIELDS}
            row.update({'rank': rank, 'corpus_index': ordinal, 'bm25_score': score,
                        'chunk_reference': {'source_file': row['source_file'], 'chunk_index': row['chunk_index']}})
            rows.append(row)
        if len(rows) != min(20, sum(score > 0 for score in scores)):
            raise ValueError('Incorrect positive-score Top-20 length')
        if any(not math.isfinite(r['bm25_score']) or r['bm25_score'] <= 0 for r in rows):
            raise ValueError('Invalid serialized score')
        questions.append({'id': qid, 'question': text, 'query_terms': tokenize(text),
                          'positive_score_chunk_count': sum(score > 0 for score in scores),
                          'zero_score_chunk_count': sum(score == 0 for score in scores), 'retrieved': rows})
    return index, questions


def complementarity(dense_rank, bm25_rank):
    if dense_rank is None and bm25_rank is None:
        return 'both_miss', 'shared_miss'
    hit = 'both_hit' if dense_rank is not None and bm25_rank is not None else ('dense_only' if bm25_rank is None else 'bm25_only')
    a, b = dense_rank or float('inf'), bm25_rank or float('inf')
    rank = 'bm25_win' if b < a else ('dense_win' if a < b else 'tie')
    return hit, rank


def group_metrics(questions, field):
    values = sorted({q[field] for q in questions})
    return {value: aggregate([q for q in questions if q[field] == value]) for value in values}


def excerpt(text, anchor=None, limit=650):
    flattened = ' '.join(text.split())
    start = flattened.casefold().find(anchor.casefold()) if anchor else 0
    if start < 0:
        raise ValueError('Manual evidence excerpt anchor not found')
    return flattened[start:start + limit]


def comparison(collection, dense, bm25, records):
    dense_map = {q['id']: q for q in dense['questions']}
    outcomes = []
    only_evidence = []
    targeted = []
    for q in bm25['questions']:
        d = dense_map[q['id']]
        dr, br = d['metrics']['first_relevant_rank'], q['metrics']['first_relevant_rank']
        hit, rank = complementarity(dr, br)
        outcomes.append({'question_id': q['id'], 'dense_first_relevant_rank': dr,
                         'bm25_first_relevant_rank': br, 'top5_classification': hit, 'first_relevant_rank_comparison': rank})
        if hit == 'bm25_only':
            row = q['metrics']['retrieved'][br - 1]
            only_evidence.append({'question_id': q['id'], 'question': q['question'], 'bm25_first_relevant': row,
                                  'evidence_excerpt': excerpt(records[row['corpus_index']]['text'], TARGETED_REVIEW.get((collection, q['id'], row['rank']), {}).get('anchor') or UNIQUE_HIT_EXCERPT_ANCHORS.get((collection, q['id']))),
                                  'dense_top5_outcome': {'hit_at_5': d['metrics']['hit_at_5'], 'first_relevant_rank': dr,
                                      'retrieved': [{field: r.get(field) for field in ROW_FIELDS + ('rank', 'similarity', 'relevant')} for r in d['metrics']['retrieved']]}})
        if q['id'] in ('DRE-04', 'OBE-01'):
            evidence = []
            for row in q['metrics']['retrieved']:
                manual = TARGETED_REVIEW.get((collection, q['id'], row['rank']), {})
                evidence.append({**row, 'evidence_excerpt': excerpt(records[row['corpus_index']]['text'], manual.get('anchor')),
                                 'manual_inspection': {k: v for k, v in manual.items() if k != 'anchor'}})
            targeted.append({'question_id': q['id'], 'question': q['question'], 'accepted_ranges': q['relevant_ranges'],
                             'dense_first_relevant_rank': dr, 'bm25_first_relevant_rank': br,
                             'bm25_finds_accepted_evidence_dense_missed': dr is None and br is not None,
                             'bm25_top5': evidence,
                             'possible_label_gaps': [r for r in evidence if r['manual_inspection'].get('status') == 'POSSIBLE LABEL GAP']})
    hits = Counter(q['top5_classification'] for q in outcomes)
    ranks = Counter(q['first_relevant_rank_comparison'] for q in outcomes)
    return {'collection': collection, 'chunk_count': len(records), 'dense_metrics': dense['metrics'], 'bm25_metrics': bm25['metrics'],
            'top5_complementarity': {key: hits[key] for key in ('both_hit', 'dense_only', 'bm25_only', 'both_miss')},
            'first_relevant_rank_comparison': {key: ranks[key] for key in ('bm25_win', 'dense_win', 'tie', 'shared_miss')},
            'comparison_definition': 'Lower first relevant rank within Top-5 wins; a miss is infinity. Ties are equal finite ranks; shared misses are counted separately. No outcome is based on score magnitude.',
            'questions': outcomes, 'bm25_only_hits': only_evidence,
            'dense_only_question_ids': [q['question_id'] for q in outcomes if q['top5_classification'] == 'dense_only'],
            'bm25_only_question_ids': [q['question_id'] for q in outcomes if q['top5_classification'] == 'bm25_only'],
            'targeted_failures': targeted,
            'by_question_type': {'dense': group_metrics(dense['questions'], 'type'), 'bm25': group_metrics(bm25['questions'], 'type')},
            'by_case': {'dense': group_metrics(dense['questions'], 'expected_case'), 'bm25': group_metrics(bm25['questions'], 'expected_case')}}


def report(analysis):
    lines = ['# CourtLens Phase 5A — BM25 lexical retrieval', '',
             'Standard Okapi BM25, implemented locally without adding a dependency. k1=1.5; b=0.75. Settings fixed before evaluation; no tuning.', '',
             '`IDF(t)=ln(1+(N-df(t)+0.5)/(df(t)+0.5))`', '',
             '`score(q,d)=Σ qtf(t) × IDF(t) × tf(t,d) × (k1+1) / (tf(t,d)+k1×(1-b+b×len(d)/avgdl))`', '',
             'This uses the positive smoothed Robertson IDF convention; repeated query terms contribute linearly. Lengths are lexical-term counts. The scorer accepts strings only, with no metadata, labels, or dense scores.', '', TOKENIZER_DESCRIPTION, '',
             'Positive scores only: zero-score chunks are excluded, not padded into Top-20. Empty/no-match queries return no results and zero official metrics. Ties use original corpus ordinal ascending: sorted fixed artifact filenames then original rows, or original structure-aware JSONL rows. Original chunk IDs and local indexes are retained; fixed chunks lacking IDs are referenced by source_file + chunk_index.', '',
             'Full Top-20 lexical rankings are saved separately without relevance labels. Official metrics, including MRR, use only Top-5 and the unchanged existing case/source/page-overlap evaluator. No exploratory Top-20 metrics are reported.', '',
             '## Locked dense controls and BM25 comparison', '', '| Chunk collection | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---|---:|---:|---:|---:|']
    for c in analysis['comparisons']:
        for retrieval, field in [('Dense (saved v2)', 'dense_metrics'), ('BM25', 'bm25_metrics')]:
            m = c[field]
            lines.append(f'| {c["collection"]} | {retrieval} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
    lines += ['', '## Complementarity', '', '| Collection | Both hit | Dense only | BM25 only | Both miss | BM25 rank wins | Dense rank wins | Finite ties | Shared misses |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in analysis['comparisons']:
        hit, rank = c['top5_complementarity'], c['first_relevant_rank_comparison']
        cells = [hit[key] for key in ('both_hit', 'dense_only', 'bm25_only', 'both_miss')] + [rank[key] for key in ('bm25_win', 'dense_win', 'tie', 'shared_miss')]
        lines.append(f'| {c["collection"]} | ' + ' | '.join(map(str, cells)) + ' |')
    lines += ['', 'Rank wins mean lower first relevant rank within Top-5, with misses treated as infinity. Ties are finite equal ranks; shared misses are a separate category.', '']
    for c in analysis['comparisons']:
        lines += [f'### {c["collection"]} — unique hits', '',
                  'BM25-only question IDs: ' + (', '.join(c['bm25_only_question_ids']) or 'None') + '.', '',
                  'Dense-only question IDs: ' + (', '.join(c['dense_only_question_ids']) or 'None') + '.', '']
        for hit in c['bm25_only_hits']:
            row = hit['bm25_first_relevant']
            lines += [f'**{hit["question_id"]}, BM25 rank {row["rank"]}: {row["case_name"]}, PDF pp{row["page_start"]}–{row["page_end"]}, chunk {row["chunk_index"]}.**', '', hit['question'], '',
                      f'BM25 score: {row["bm25_score"]:.6f}. Dense Top-5: no accepted evidence.', '', '> ' + hit['evidence_excerpt'], '']
    lines += ['## DRE-04 and OBE-01 — targeted source inspection', '',
              'Relevance below is the benchmark’s mechanical page-overlap decision. Manual possible-gap annotations do not alter labels, rankings, or metrics. Opinion/author fields are preserved as recorded; fixed chunks have no opinion attribution. Full text remains in the frozen source artifacts, avoiding a duplicate corpus.', '']
    for c in analysis['comparisons']:
        for q in c['targeted_failures']:
            lines += [f'### {c["collection"]} — {q["question_id"]}', '', q['question'], '',
                      f'Accepted PDF ranges: {q["accepted_ranges"]}. Dense first relevant rank: {q["dense_first_relevant_rank"] or "miss"}; BM25: {q["bm25_first_relevant_rank"] or "miss"}. BM25 finds accepted evidence dense missed: {q["bm25_finds_accepted_evidence_dense_missed"]}.', '']
            for row in q['bm25_top5']:
                lines += [f'**Rank {row["rank"]}; score {row["bm25_score"]:.6f}; {row["case_name"]}; `{row["source_file"]}`; pp{row["page_start"]}–{row["page_end"]}; chunk {row["chunk_index"]}.**', '',
                          f'Opinion: {row.get("opinion_type") or "not recorded"}; author: {row.get("author") or "not recorded"}. Benchmark relevant: {row["relevant"]}.', '', '> ' + row['evidence_excerpt'], '',
                          f'**{row["manual_inspection"].get("status", "Not manually annotated")}:** {row["manual_inspection"].get("rationale", "")}', '', row['manual_inspection'].get('source_attribution_note', ''), '']
    lines += ['## Question-type and case metrics', '', 'Small subgroups; these comparisons do not establish statistically reliable routing rules.', '']
    for c in analysis['comparisons']:
        for field in ('by_question_type', 'by_case'):
            lines += [f'### {c["collection"]} — {field}', '', '| Group | N | Retrieval | Hit@1 | Hit@3 | Hit@5 | MRR |', '|---|---:|---|---:|---:|---:|---:|']
            for group in c[field]['bm25']:
                for retrieval in ('dense', 'bm25'):
                    m = c[field][retrieval][group]
                    lines.append(f'| {group} | {m["question_count"]} | {retrieval} | {m["hit_at_1"]:.3f} | {m["hit_at_3"]:.3f} | {m["hit_at_5"]:.3f} | {m["mrr"]:.6f} |')
            lines.append('')
    lines += ['## Corpus validation and coverage', '']
    for c, manifest in analysis['manifests'].items():
        lines += [f'- {c}: {manifest["chunk_count"]} chunks; corpus SHA-256 `{manifest["corpus_sha256"]}`; average BM25 term length {manifest["average_lexical_length"]:.3f}; frozen tokenizer-token distribution {manifest["frozen_token_count_distribution"]}.']
    lines += ['', 'Structure-aware excludes 200 cl100k_base tokens of foreign Sturgis/Honold material from the opening Dred Scott extraction. Fixed retains that material. These are the existing frozen corpora, not newly equalized inputs.', '',
              '## Experimental limitations', ''] + [f'- {s}' for s in LIMITATIONS]
    lines += ['', '## Reproducibility and protected artifacts', '',
              f'Evaluation date: {EVALUATION_DATE}, America/New_York. Reproduce locally with `.venv/bin/python run_bm25_experiment.py`. Existing output conflicts are rejected; identical replay is a no-op.', '',
              f'Benchmark v2 SHA-256: `{analysis["benchmark_sha256"]}`. Saved dense v2 SHA-256: `{analysis["dense_sha256"]}`.', '',
              f'All {analysis["protected_artifacts"]["file_count"]} pre-existing data files verified byte-identical by SHA-256. Full before/after hashes are recorded in the analysis JSON. No API, embedding, dense retrieval, FAISS rebuild, corpus modification, commit, or push.', '',
              'READY for Phase 5B on local lexical ranking/artifact reproducibility checks. Phase 5B has not been started; no hybrid retrieval, RRF, or reranking is implemented.', '']
    return '\n'.join(lines)


def build_outputs(root=ROOT):
    before = protected_snapshot(root)
    benchmark = load(root / BENCHMARK)
    questions = benchmark['questions']
    if len(questions) != 40 or len({q['id'] for q in questions}) != 40:
        raise ValueError('Require forty unique Benchmark v2 questions')
    dense_configs = {c['id']: c for c in load(root / DENSE)['configurations']}
    output, comparisons, manifests = {}, [], {}
    for collection in COLLECTIONS:
        records, source_hashes = load_corpus(collection, root)
        index, rankings = rank_queries(records, [(q['id'], q['question']) for q in questions])
        dense = dense_configs[DENSE_IDS[collection]]
        if dense['vector_count'] != len(records) or [q['id'] for q in dense['questions']] != [q['id'] for q in questions]:
            raise ValueError('Frozen dense/corpus/benchmark mismatch')
        if any(abs(dense['metrics'][k] - expected) > 1e-12 for k, expected in zip(METRICS, CONTROLS[collection])):
            raise ValueError('Saved dense metrics disagree with locked controls')
        evaluated = []
        for q, ranked, d in zip(questions, rankings, dense['questions']):
            for key in ('id', 'type', 'question', 'expected_case', 'expected_source_file', 'relevant_ranges'):
                if d[key] != q[key]:
                    raise ValueError('Dense comparison is not against Benchmark v2')
            evaluated.append({key: deepcopy(q[key]) for key in ('id', 'type', 'question', 'expected_case', 'expected_source_file', 'relevant_ranges')})
            evaluated[-1]['metrics'] = score_retrieved(ranked['retrieved'], q)
        results = {'collection': collection, 'benchmark_path': str(BENCHMARK), 'official_ranking_depth': 5,
                   'mrr_depth': 5, 'metrics': aggregate(evaluated), 'questions': evaluated}
        tokens = [r['metadata']['token_count'] for r in records]
        manifest = {'experiment': 'CourtLens Phase 5A BM25', 'collection': collection, 'evaluation_date': EVALUATION_DATE,
                    'implementation': 'standard-library text-only Okapi BM25 with positive smoothed Robertson IDF',
                    'k1': K1, 'b': B, 'idf': 'ln(1+(N-df+.5)/(df+.5))', 'query_tf': 'linear multiplicity; sorted query-term accumulation',
                    'tokenizer_version': TOKENIZER_VERSION, 'tokenizer_description': TOKENIZER_DESCRIPTION,
                    'tie_break': 'score descending; stable original corpus ordinal ascending',
                    'corpus_order': 'sorted artifact paths; original JSONL row order',
                    'zero_score_policy': 'exclude; never pad; no-match/empty query has no results and zero Top-5 metrics',
                    'saved_ranking_depth': 20, 'official_metric_depth': 5, 'mrr_depth': 5,
                    'chunk_count': len(records), 'question_count': 40, 'vocabulary_size': len(index.idf),
                    'average_lexical_length': index.average_length,
                    'frozen_token_count_distribution': {'min': min(tokens), 'max': max(tokens), 'mean': statistics.mean(tokens), 'median': statistics.median(tokens)},
                    'corpus_source_sha256': source_hashes,
                    'corpus_sha256': hashlib.sha256(encode(source_hashes).encode()).hexdigest(),
                    'corpus_hash_method': 'SHA-256 of sorted UTF-8 JSON mapping relative artifact paths to their byte SHA-256 hashes',
                    'chunk_identity_text_sequence_sha256': hashlib.sha256(encode(records).encode()).hexdigest(),
                    'benchmark_sha256': sha(root / BENCHMARK), 'dense_result_sha256': sha(root / DENSE),
                    'implementation_sha256': {name: sha(ROOT / name) for name in ('bm25_retrieval.py', 'run_bm25_experiment.py', 'finalize_chunking_benchmark.py', 'benchmark_relevance.py')},
                    'ranking_uses_labels_or_metadata': False, 'parameters_tuned': False,
                    'foreign_sturgis_honold_tokens_excluded': 200 if collection == 'structure_aware_v1' else 0}
        directory = EXPERIMENT_ROOT / collection
        output[directory / 'manifest.json'] = encode(manifest)
        output[directory / 'rankings_top20.json'] = encode({'collection': collection, 'ranking_depth': 20, 'questions': rankings})
        output[directory / 'results.json'] = encode(results)
        comparisons.append(comparison(collection, dense, results, records))
        manifests[collection] = manifest
    if before != protected_snapshot(root):
        raise RuntimeError('Protected artifacts changed during local ranking')
    analysis = {'phase': '5A', 'evaluation_date': EVALUATION_DATE, 'benchmark_path': str(BENCHMARK),
                'benchmark_sha256': sha(root / BENCHMARK), 'dense_sha256': sha(root / DENSE),
                'comparisons': comparisons, 'manifests': manifests, 'limitations': LIMITATIONS,
                'protected_artifacts': {'file_count': len(before), 'unchanged': True, 'before_sha256': before, 'after_sha256': protected_snapshot(root)}}
    output[ANALYSIS_JSON] = encode(analysis)
    output[ANALYSIS_MD] = report(analysis)
    return output


def write_outputs(output, root=ROOT):
    if set(output) != output_paths():
        raise ValueError('Only new Phase 5A output paths may be written')
    for relative, text in output.items():
        path = root / relative
        if path.exists() and path.read_bytes() != text.encode():
            raise FileExistsError(f'Conflicting output exists; refusing overwrite: {relative}')
    for relative, text in output.items():
        path = root / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8') as handle:
                handle.write(text)


def main():
    before = protected_snapshot()
    output = build_outputs()
    write_outputs(output)
    if before != protected_snapshot():
        raise RuntimeError('Protected artifacts changed while writing outputs')
    print(f'Phase 5A complete: 598 fixed chunks, 433 structure-aware chunks, 40 queries each. {len(before)} protected data files unchanged. Eight new experiment/analysis artifacts.')


if __name__ == '__main__':
    main()
