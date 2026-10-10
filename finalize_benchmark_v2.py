"""Finalize approved Phase 4C.2 labels and rescore five SAVED Top-5 rankings.

Standard-library processing plus the existing local relevance evaluator only.
No API key, SDK, tokenizer, embedding, FAISS, or network operation is needed.
Only the four new versioned output paths below may be written. Existing output
files are accepted only when identical; conflicting files are never overwritten.
"""

import argparse
from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path

from finalize_chunking_benchmark import aggregate, score_retrieved, validate_ranges


ROOT = Path(__file__).resolve().parent
V1 = Path('data/evaluation/chunking_benchmark_reviewed.json')
AUDIT = Path('data/evaluation/chunking_benchmark_phase4c_audit.json')
FIXED = Path('data/experiments/chunking/reviewed_results.json')
STRUCTURE = Path('data/experiments/chunking/structure_aware_v1/results.json')
V2 = Path('data/evaluation/chunking_benchmark_v2.json')
RESULTS = Path('data/experiments/chunking/benchmark_v2_results.json')
ANALYSIS = Path('data/analysis/benchmark_v2_evaluation.json')
REPORT = Path('data/analysis/benchmark_v2_evaluation.md')
OUTPUTS = (V2, RESULTS, ANALYSIS, REPORT)
STRATEGIES = ('600_100', '900_150', '1200_200', '1500_200', 'structure_aware_v1')
METRICS = ('hit_at_1', 'hit_at_3', 'hit_at_5', 'mrr')
EVALUATION_DATE = '2026-10-09'  # Frozen phase date, America/New_York; reproducible.
METHOD = 'CourtLens Phase 4C.2 saved-top5 page-overlap evaluator v1'
ADDITIONS = {
    'DRE-01': [[39, 40], [167, 167]],
    'MIR-04': [[9, 10]],
    'MAR-01': [[32, 32], [36, 36]],
    'DRE-03': [[33, 34]],
    'OBE-04': [[64, 64]],
}
JUSTIFICATIONS = {
    'DRE-01': ['Majority restatement of Scott’s Illinois/Fort Snelling residence.', 'McLean’s factual account of Scott’s Illinois/Fort Snelling residence.'],
    'MIR-04': ['Warren majority explicitly enumerates custodial interrogation safeguards.'],
    'MAR-01': ['Commission withholding and legal entitlement.', 'Requested mandamus delivery remedy and vested commission right.'],
    'DRE-03': ['Majority’s constitutional and founding-era citizenship reasoning.'],
    'OBE-04': ['Roberts dissent explicitly quotes and attributes the majority’s Due Process / Equal Protection reasoning.'],
}
LIMITATIONS = [
    'Benchmark v2 labels were refined after inspecting retrieval candidates from the evaluated systems.',
    'Benchmark v2 is NOT an independent holdout benchmark.',
    'Page-range intersection is a coarse relevance proxy that can generate both false negatives and false positives, including credit from trailing page markers or non-answer-bearing text on a labeled page.',
    'Structure-aware and fixed chunking differ in realized chunk-size distributions; nominal fixed sizes are not equivalent to the structure-aware distribution.',
    'Any apparent advantage is descriptive performance on this benchmark, not proof of general superiority.',
    'No statistical significance claim is made.',
]


def encode(value):
    # Preserve insertion order and the existing benchmark’s formatting style.
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def protected_snapshot(root=ROOT):
    return {str(p.relative_to(root)): sha(p) for p in sorted((root / 'data').rglob('*'))
            if p.is_file() and p.relative_to(root) not in OUTPUTS}


def record_bytes(benchmark):
    return [encode(q).encode('utf-8') for q in benchmark['questions']]


def raw_question_records(text):
    """Return literal serialized object spans, excluding surrounding whitespace."""
    decoder = json.JSONDecoder()
    start = text.index('[', text.index('"questions":')) + 1
    records = []
    while True:
        while text[start].isspace() or text[start] == ',':
            start += 1
        if text[start] == ']':
            return records
        value, end = decoder.raw_decode(text, start)
        if not isinstance(value, dict):
            raise ValueError('Expected question object')
        records.append(text[start:end].encode('utf-8'))
        start = end


def validate_v2(v1, v2):
    before, after = v1['questions'], v2['questions']
    ids = [q['id'] for q in before]
    if len(ids) != 40 or len(set(ids)) != 40 or [q['id'] for q in after] != ids:
        raise ValueError('Exactly 40 unique IDs in original order are required')
    changed = []
    added = 0
    for old, new in zip(before, after):
        expected = deepcopy(old)
        extra = ADDITIONS.get(old['id'], [])
        expected['relevant_ranges'] += deepcopy(extra)
        validate_ranges(expected['relevant_ranges'])
        if new != expected:
            raise ValueError(f'Unapproved record change: {old["id"]}')
        if record_bytes({'questions': [old]}) != record_bytes({'questions': [new]}):
            changed.append(old['id'])
        added += len(extra)
    if set(changed) != set(ADDITIONS) or len(changed) != 5 or added != 7:
        raise ValueError('Require exactly five modified questions and seven added ranges')
    for key, value in v1.items():
        if key != 'questions' and v2.get(key) != value:
            raise ValueError(f'Existing benchmark metadata changed: {key}')
    return {'question_count': 40, 'modified_question_count': 5, 'added_range_count': 7,
            'unchanged_question_count': 35, 'modified_question_ids': changed,
            'original_ranges_preserved': True, 'question_text_and_metadata_preserved': True,
            'original_order_preserved': True, 'duplicates_or_deletions': False,
            'mir_04_page_67_excluded': True, 'dre_04_unchanged': True, 'obe_01_unchanged': True}


def traceability(audit):
    by_id = {q['question_id']: q for q in audit['questions']}
    approved = []
    for qid, ranges in ADDITIONS.items():
        for interval, justification in zip(ranges, JUSTIFICATIONS[qid]):
            candidates = [c for c in by_id[qid]['candidates']
                          if interval in c['proposed_range_additions'] and c['decision'] == 'RELEVANT']
            if not candidates:
                raise ValueError(f'Approved addition lacks an audit reference: {qid} {interval}')
            approved.append({'question_id': qid, 'range': interval, 'justification': justification,
                             'audit_candidate_ids': [c['candidate_id'] for c in candidates]})
    ambiguous = [c['candidate_id'] for q in audit['questions'] for c in q['candidates'] if c['decision'] == 'AMBIGUOUS']
    if len(ambiguous) != 12:
        raise ValueError('Expected the twelve unchanged ambiguous audit judgments')
    return {'audit_path': str(AUDIT), 'approved_additions': approved,
            'approval': 'Human approval supplied in Phase 4C.2 request; exactly seven additions across five questions.',
            'deferred': [{'question_id': 'MIR-04', 'range': [67, 67], 'reason': 'Human review deferred this partial-support passage. The historical Phase 4C judgment remains untouched.'}],
            'unresolved_ambiguous_count': 12, 'unresolved_ambiguous_candidate_ids': ambiguous,
            'questions_receiving_no_new_ranges': ['DRE-04', 'OBE-01'],
            'manual_judgments_unchanged': True,
            'scoring_note': 'Relevance flags in v2 results are mechanical case/source/page-overlap outcomes, not conversions of ambiguous manual audit judgments.'}


def make_v2(v1, provenance, trace):
    v2 = deepcopy(v1)
    for question in v2['questions']:
        question['relevant_ranges'] += deepcopy(ADDITIONS.get(question['id'], []))
    v2['version_metadata'] = {
        'version': 2, 'phase': '4C.2', 'status': 'human-approved labels finalized',
        'base_benchmark': str(V1), 'base_benchmark_sha256': provenance['v1_benchmark_sha256'],
        'audit_path': str(AUDIT), 'audit_sha256': provenance['phase4c_audit_sha256'],
        'evaluation_date': provenance['evaluation_date'], 'question_count': 40,
        'modified_question_count': 5, 'added_range_count': 7, 'unchanged_question_count': 35,
        'approved_additions': trace['approved_additions'],
        'metadata_note': 'All inherited metadata, including review_notes, relevance_changed, and changed_question_count, describes the original v1 review and is preserved verbatim. This version_metadata records the additional v2 changes.',
        'mir_04_page_67': 'deferred; not added', 'unresolved_ambiguous_judgments': 12,
        'independent_holdout': False,
    }
    validate_v2(v1, v2)
    return v2


def check_rank(before, after):
    if (after if after is not None else float('inf')) > (before if before is not None else float('inf')):
        raise ValueError('A relevance expansion must never worsen a rank')
    if before == after:
        return 'unchanged'
    return 'miss → hit' if before is None else 'improved rank'


def rescore(config, v1, v2):
    expected_ids = [q['id'] for q in v1['questions']]
    saved = config['questions']
    if [q['id'] for q in saved] != expected_ids:
        raise ValueError(f'Saved question order/IDs mismatch: {config["id"]}')
    before_questions, after_questions, changes = [], [], []
    for saved_q, old, new in zip(saved, v1['questions'], v2['questions']):
        for field in ('id', 'type', 'question', 'expected_case', 'expected_source_file', 'relevant_ranges'):
            if saved_q[field] != old[field]:
                raise ValueError(f'Saved v1 question mismatch: {config["id"]} {old["id"]} {field}')
        rows = saved_q['metrics']['retrieved']
        if len(rows) != 5 or [r['rank'] for r in rows] != [1, 2, 3, 4, 5]:
            raise ValueError('Exactly five saved results in consecutive rank order are required')
        before = score_retrieved(rows, old)
        after = score_retrieved(rows, new)
        for field in ('hit_at_1', 'hit_at_3', 'hit_at_5', 'reciprocal_rank', 'first_relevant_rank'):
            if before[field] != saved_q['metrics'][field]:
                raise ValueError(f'Saved v1 scores cannot be reproduced: {config["id"]} {old["id"]} {field}')
        if before['retrieved'] != rows:
            raise ValueError('Saved v1 relevance flags cannot be reproduced')
        classification = check_rank(before['first_relevant_rank'], after['first_relevant_rank'])
        became_relevant = []
        for original, rescored in zip(rows, after['retrieved']):
            if {k: v for k, v in original.items() if k != 'relevant'} != {k: v for k, v in rescored.items() if k != 'relevant'}:
                raise ValueError('Rankings or retrieval metadata changed')
            if original['relevant'] and not rescored['relevant']:
                raise ValueError('An expanded label removed relevance')
            if not original['relevant'] and rescored['relevant']:
                became_relevant.append({k: rescored.get(k) for k in ('rank', 'vector_id', 'chunk_index', 'chunk_id', 'case_name', 'source_file', 'original_source_file', 'page_start', 'page_end', 'similarity')})
        changes.append({'question_id': old['id'], 'question': old['question'], 'case_name': old['expected_case'],
                        'v1_first_relevant_rank': before['first_relevant_rank'], 'v2_first_relevant_rank': after['first_relevant_rank'],
                        'classification': classification, 'previously_irrelevant_chunks_now_relevant': became_relevant})
        before_questions.append({'metrics': before})
        record = deepcopy(saved_q)
        record['relevant_ranges'] = deepcopy(new['relevant_ranges'])
        record['metrics'] = after
        after_questions.append(record)
    baseline, updated = aggregate(before_questions), aggregate(after_questions)
    for key in ('question_count',) + METRICS:
        if abs(baseline[key] - config['metrics'][key]) > 1e-12:
            raise ValueError(f'Saved v1 aggregate mismatch: {config["id"]} {key}')
    output_config = deepcopy(config)
    output_config['questions'], output_config['metrics'] = after_questions, updated
    improved = [q for q in changes if q['classification'] != 'unchanged']
    analysis = {'strategy': config['id'], 'chunk_count': config['vector_count'], 'v1_metrics': baseline, 'v2_metrics': updated,
                'absolute_differences': {k: updated[k] - baseline[k] for k in METRICS},
                'improved_question_count': len(improved),
                'improved_rank_count': sum(q['classification'] == 'improved rank' for q in changes),
                'added_first_rank_successes': int(sum(q['metrics']['hit_at_1'] for q in after_questions) - sum(q['metrics']['hit_at_1'] for q in before_questions)),
                'top5_misses_became_hits': sum(q['classification'] == 'miss → hit' for q in changes),
                'remaining_top5_misses': [q['question_id'] for q in changes if q['v2_first_relevant_rank'] is None],
                'no_rank_regressions': True, 'questions': changes}
    return output_config, analysis


def report(analysis):
    p = analysis['provenance']
    lines = ['# CourtLens Phase 4C.2 — Benchmark v2 finalization', '',
             'Benchmark v2 applies exactly seven human-approved additions to five questions. The other 35 question records are byte-identical, including their literal JSON object spans. The original benchmark, audit, rankings, chunks, vector stores, and reports remain unchanged.', '',
             'Inherited benchmark metadata describes the v1 review and is preserved; version_metadata separately records v2 approval and provenance.', '',
             f'Evaluation date: {p["evaluation_date"]} ({p["evaluation_timezone"]}). Method: {p["evaluation_method"]}. Forty questions per strategy; saved Top-5 only. Existing score_retrieved and aggregate functions are reused without changes.', '',
             '## Approved additions and traceability', '', '| Question | Added PDF range | Human-approved justification |', '|---|---|---|']
    for addition in analysis['audit_traceability']['approved_additions']:
        lines.append(f'| {addition["question_id"]} | {addition["range"]} | {addition["justification"]} |')
    lines += ['', f'Audit reference: `{AUDIT}`. MIR-04 page 67 remains unapproved/deferred. All 12 ambiguous audit judgments remain unresolved and untouched. DRE-04 and OBE-01 receive no new ranges. Mechanical page-overlap relevance flags are not new manual passage judgments.', '',
              '## Five-strategy comparison', '', '| Strategy | Chunks | v1 H@1 | v2 H@1 | v1 H@3 | v2 H@3 | v1 H@5 | v2 H@5 | v1 MRR | v2 MRR |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s in analysis['strategies']:
        cells = [f'{s[version][metric]:.6f}' for metric in METRICS for version in ('v1_metrics', 'v2_metrics')]
        lines.append(f'| {s["strategy"]} | {s["chunk_count"]} | ' + ' | '.join(cells) + ' |')
    lines += ['', 'Absolute differences below are v2 − v1, not relative percentages.', '', '| Strategy | Δ Hit@1 | Δ Hit@3 | Δ Hit@5 | Δ MRR | Improved questions | Added rank-1 successes | Miss → Top-5 hit |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for s in analysis['strategies']:
        cells = [f'{s["absolute_differences"][metric]:+.6f}' for metric in METRICS]
        lines.append(f'| {s["strategy"]} | ' + ' | '.join(cells) + f' | {s["improved_question_count"]} | {s["added_first_rank_successes"]} | {s["top5_misses_became_hits"]} |')
    lines += ['', '## Per-question improvements and remaining misses', '']
    for s in analysis['strategies']:
        lines += [f'### {s["strategy"]}', '', '| Question | v1 first rank | v2 first rank | Classification | Newly relevant saved chunks (rank; pages; chunk index) |', '|---|---:|---:|---|---|']
        for q in s['questions']:
            if q['classification'] != 'unchanged' or q['previously_irrelevant_chunks_now_relevant']:
                chunks = '; '.join(f'r{r["rank"]}; pp{r["page_start"]}–{r["page_end"]}; chunk {r["chunk_index"]}' for r in q['previously_irrelevant_chunks_now_relevant'])
                lines.append(f'| {q["question_id"]} | {q["v1_first_relevant_rank"] or "miss"} | {q["v2_first_relevant_rank"] or "miss"} | {q["classification"]} | {chunks} |')
        lines += ['', 'Remaining Top-5 misses: ' + (', '.join(s['remaining_top5_misses']) or 'None') + '.', '',
                  'All 40 before/after ranks, classifications, and newly relevant chunk identifiers are recorded in the analysis JSON. No rank regressions occurred.', '']
    lines += ['## Experimental limitations', ''] + [f'- {item}' for item in LIMITATIONS]
    lines += ['', '## Reproducibility and protected artifacts', '',
              f'Local reproduction: `.venv/bin/python finalize_benchmark_v2.py --evaluation-date {p["evaluation_date"]}`. No API credentials, network, embeddings, or FAISS retrieval required. Existing versioned outputs are only accepted if identical; conflicting outputs are not overwritten.', '',
              '| Artifact | SHA-256 |', '|---|---|',
              f'| Benchmark v1 | `{p["v1_benchmark_sha256"]}` |',
              f'| Benchmark v2 | `{p["v2_benchmark_sha256"]}` |',
              f'| Phase 4C audit | `{p["phase4c_audit_sha256"]}` |']
    for path, value in p['saved_retrieval_result_sha256'].items():
        lines.append(f'| `{path}` | `{value}` |')
    verification = analysis['protected_artifacts']
    lines += ['', f'All {verification["file_count"]} pre-existing data artifacts were verified byte-identical by SHA-256 before and after processing/writing. This includes all five strategies’ saved rankings, fixed and structure-aware chunks/stores, production store, original/reviewed benchmarks, Phase 4C audit, and existing analysis reports. Full before/after hashes are in the analysis JSON.', '',
              '**READY for Phase 5A** on benchmark/versioning and local reproducibility checks, with the stated methodological limitations. Phase 5A has not been started.', '']
    return '\n'.join(lines)


def build_outputs(root=ROOT, evaluation_date=EVALUATION_DATE):
    date.fromisoformat(evaluation_date)
    before = protected_snapshot(root)
    v1 = load(root / V1)
    audit = load(root / AUDIT)
    trace = traceability(audit)
    provenance = {'evaluation_date': evaluation_date, 'evaluation_timezone': 'America/New_York',
                  'evaluation_method': METHOD, 'evaluation_implementation': 'finalize_chunking_benchmark.score_retrieved / aggregate',
                  'evaluation_source_sha256': sha(root / 'finalize_chunking_benchmark.py'),
                  'relevance_source_sha256': sha(root / 'benchmark_relevance.py'),
                  'finalization_source_sha256': sha(Path(__file__)),
                  'v1_benchmark_path': str(V1), 'v1_benchmark_sha256': sha(root / V1),
                  'phase4c_audit_sha256': sha(root / AUDIT),
                  'saved_retrieval_result_sha256': {str(p): sha(root / p) for p in (FIXED, STRUCTURE)},
                  'ranking_artifacts_note': 'The four fixed strategies share reviewed_results.json; structure-aware has its own results.json.',
                  'question_count': 40, 'added_range_count': 7}
    v2 = make_v2(v1, provenance, trace)
    v2_text = encode(v2)
    validation = validate_v2(v1, v2)
    literal_before, literal_after = raw_question_records((root / V1).read_text()), raw_question_records(v2_text)
    unchanged = sum(a == b for a, b in zip(literal_before, literal_after))
    if unchanged != 35:
        raise ValueError(f'Expected 35 literally byte-identical JSON question records; found {unchanged}')
    validation['literal_byte_identical_question_records'] = unchanged
    provenance['v2_benchmark_path'] = str(V2)
    provenance['v2_benchmark_sha256'] = hashlib.sha256(v2_text.encode('utf-8')).hexdigest()
    fixed, structure = load(root / FIXED), load(root / STRUCTURE)
    configs = fixed['configurations'] + structure['configurations']
    if tuple(c['id'] for c in configs) != STRATEGIES:
        raise ValueError('Expected the five existing strategies in original order')
    rescored, comparisons = [], []
    for config in configs:
        output, comparison = rescore(config, v1, v2)
        rescored.append(output)
        comparisons.append(comparison)
    if protected_snapshot(root) != before:
        raise RuntimeError('Protected input artifacts changed')
    results = {'experiment': 'CourtLens five-strategy evaluation — Benchmark v2',
               'status': 'human-approved Benchmark v2; saved rankings rescored locally',
               'benchmark_path': str(V2), 'ranking_depth': 5, 'method': METHOD,
               'provenance': provenance, 'audit_traceability': trace, 'configurations': rescored}
    analysis = {'phase': '4C.2', 'status': 'READY for Phase 5A; Phase 5A not started',
                'provenance': provenance, 'benchmark_validation': validation, 'audit_traceability': trace,
                'strategies': comparisons, 'limitations': LIMITATIONS,
                'protected_artifacts': {'file_count': len(before), 'unchanged': True,
                                        'before_sha256': before, 'after_sha256': protected_snapshot(root)}}
    return {V2: v2_text, RESULTS: encode(results), ANALYSIS: encode(analysis), REPORT: report(analysis)}


def write_new_outputs(outputs, root=ROOT):
    if set(outputs) != set(OUTPUTS):
        raise ValueError('Only four Phase 4C.2 output paths may be written')
    # Preflight all paths before writing any: preserve existing files on conflict.
    for relative, text in outputs.items():
        path = root / relative
        if path.exists() and path.read_bytes() != text.encode('utf-8'):
            raise FileExistsError(f'Conflicting output already exists; refusing overwrite: {relative}')
    for relative, text in outputs.items():
        path = root / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8') as handle:
                handle.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluation-date', default=EVALUATION_DATE, help='ISO date recorded in reproducible artifacts')
    args = parser.parse_args()
    before = protected_snapshot()
    outputs = build_outputs(evaluation_date=args.evaluation_date)
    write_new_outputs(outputs)
    if protected_snapshot() != before:
        raise RuntimeError('Protected artifacts changed while writing outputs')
    print(f'Created/verified four new Phase 4C.2 outputs. Exactly 40 questions, 5 modified records, 7 added ranges, 35 literal byte-identical records. Protected existing data files: {len(before)}, unchanged.')


if __name__ == '__main__':
    main()
