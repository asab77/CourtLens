"""Phase 4C.2 approvals, unchanged records, scoring, and local reproducibility."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import finalize_benchmark_v2 as v2
from finalize_chunking_benchmark import aggregate, score_retrieved


class BenchmarkV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = v2.protected_snapshot()
        cls.outputs = v2.build_outputs()
        cls.original = v2.load(v2.ROOT / v2.V1)
        cls.benchmark = json.loads(cls.outputs[v2.V2])
        cls.analysis = json.loads(cls.outputs[v2.ANALYSIS])
        cls.results = json.loads(cls.outputs[v2.RESULTS])

    def test_exact_seven_additions_and_five_modified_records(self):
        expected = {'DRE-01': [[39, 40], [167, 167]], 'MIR-04': [[9, 10]],
                    'MAR-01': [[32, 32], [36, 36]], 'DRE-03': [[33, 34]], 'OBE-04': [[64, 64]]}
        changed = {}
        for old, new in zip(self.original['questions'], self.benchmark['questions']):
            if old != new:
                changed[old['id']] = new['relevant_ranges'][len(old['relevant_ranges']):]
        self.assertEqual(changed, expected)
        self.assertEqual(sum(map(len, changed.values())), 7)

    def test_35_other_records_are_literal_byte_identical(self):
        before = v2.raw_question_records((v2.ROOT / v2.V1).read_text())
        after = v2.raw_question_records(self.outputs[v2.V2])
        self.assertEqual(sum(a == b for a, b in zip(before, after)), 35)
        for old, new in zip(self.original['questions'], self.benchmark['questions']):
            if old['id'] not in v2.ADDITIONS:
                self.assertEqual(v2.encode(old).encode(), v2.encode(new).encode())

    def test_original_ranges_and_all_record_metadata_preserved(self):
        for old, new in zip(self.original['questions'], self.benchmark['questions']):
            self.assertEqual(new['relevant_ranges'][:len(old['relevant_ranges'])], old['relevant_ranges'])
            self.assertEqual({k: x for k, x in old.items() if k != 'relevant_ranges'},
                             {k: x for k, x in new.items() if k != 'relevant_ranges'})
            ranges = new['relevant_ranges']
            self.assertEqual(len(ranges), len(set(map(tuple, ranges))))
        for key, value in self.original.items():
            if key != 'questions':
                self.assertEqual(self.benchmark[key], value)

    def test_question_count_text_types_and_order_preserved(self):
        self.assertEqual(len(self.benchmark['questions']), 40)
        self.assertEqual([q['id'] for q in self.original['questions']], [q['id'] for q in self.benchmark['questions']])
        for field in ('question', 'type', 'expected_case', 'expected_source_file'):
            self.assertEqual([q[field] for q in self.original['questions']], [q[field] for q in self.benchmark['questions']])

    def test_deferred_and_unapproved_questions_unchanged(self):
        before = {q['id']: q for q in self.original['questions']}
        after = {q['id']: q for q in self.benchmark['questions']}
        self.assertEqual(after['MIR-04']['relevant_ranges'], [[2, 2], [34, 40], [9, 10]])
        self.assertNotIn([67, 67], after['MIR-04']['relevant_ranges'])
        for qid in ('DRE-04', 'OBE-01'):
            self.assertEqual(before[qid], after[qid])
        trace = self.analysis['audit_traceability']
        self.assertEqual(trace['unresolved_ambiguous_count'], 12)
        self.assertEqual(len(trace['approved_additions']), 7)

    def test_unapproved_record_edit_rejected(self):
        changed = deepcopy(self.benchmark)
        changed['questions'][0]['review_notes'] = 'new note'
        with self.assertRaisesRegex(ValueError, 'Unapproved record change'):
            v2.validate_v2(self.original, changed)

    def test_saved_ranking_order_and_payloads_are_unchanged(self):
        original_configs = v2.load(v2.ROOT / v2.FIXED)['configurations'] + v2.load(v2.ROOT / v2.STRUCTURE)['configurations']
        self.assertEqual(tuple(c['id'] for c in self.results['configurations']), v2.STRATEGIES)
        for old, new in zip(original_configs, self.results['configurations']):
            for old_q, new_q in zip(old['questions'], new['questions']):
                a, b = old_q['metrics']['retrieved'], new_q['metrics']['retrieved']
                self.assertEqual([r['rank'] for r in b], [1, 2, 3, 4, 5])
                self.assertEqual([{k: v for k, v in r.items() if k != 'relevant'} for r in a],
                                 [{k: v for k, v in r.items() if k != 'relevant'} for r in b])

    def test_reordered_saved_results_rejected(self):
        config = deepcopy(v2.load(v2.ROOT / v2.FIXED)['configurations'][0])
        rows = config['questions'][0]['metrics']['retrieved']
        rows[0], rows[1] = rows[1], rows[0]
        with self.assertRaisesRegex(ValueError, 'consecutive rank order'):
            v2.rescore(config, self.original, self.benchmark)

    def test_no_question_regressions_and_summary_counts_match(self):
        for strategy in self.analysis['strategies']:
            questions = strategy['questions']
            for q in questions:
                before, after = q['v1_first_relevant_rank'], q['v2_first_relevant_rank']
                self.assertLessEqual(after if after else 6, before if before else 6)
            self.assertEqual(strategy['improved_question_count'], sum(q['classification'] != 'unchanged' for q in questions))
            self.assertEqual(strategy['top5_misses_became_hits'], sum(q['v1_first_relevant_rank'] is None and q['v2_first_relevant_rank'] is not None for q in questions))
            self.assertEqual(strategy['added_first_rank_successes'], sum(q['v2_first_relevant_rank'] == 1 for q in questions) - sum(q['v1_first_relevant_rank'] == 1 for q in questions))
        with self.assertRaisesRegex(ValueError, 'never worsen'):
            v2.check_rank(2, None)

    def test_deterministic_outputs_match_created_files(self):
        self.assertEqual(self.outputs, v2.build_outputs())
        for path, text in self.outputs.items():
            self.assertEqual((v2.ROOT / path).read_bytes(), text.encode('utf-8'))
        expected_hash = v2.sha(v2.ROOT / v2.V2)
        self.assertEqual(self.analysis['provenance']['v2_benchmark_sha256'], expected_hash)

    def test_protected_existing_artifacts_unchanged(self):
        self.assertEqual(v2.protected_snapshot(), self.before)
        verification = self.analysis['protected_artifacts']
        self.assertEqual(verification['before_sha256'], verification['after_sha256'])
        for path, checksum in verification['before_sha256'].items():
            self.assertEqual(v2.sha(v2.ROOT / path), checksum)

    def test_writer_creates_only_new_files_and_refuses_conflicting_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            v2.write_new_outputs(self.outputs, root)
            self.assertEqual({p.relative_to(root) for p in root.rglob('*') if p.is_file()}, set(v2.OUTPUTS))
            v2.write_new_outputs(self.outputs, root)  # Byte-identical replay is a no-op.
            (root / v2.V2).write_text('preserve this existing file')
            with self.assertRaises(FileExistsError):
                v2.write_new_outputs(self.outputs, root)
            self.assertEqual((root / v2.V2).read_text(), 'preserve this existing file')


class ExistingScoringContractTests(unittest.TestCase):
    def test_multirange_source_matching_and_metrics(self):
        question = {'expected_case': 'Target', 'expected_source_file': 'target.pdf', 'relevant_ranges': [[2, 2], [9, 10]]}
        rows = [{'rank': i, 'case_name': 'Target', 'source_file': 'target.pdf', 'page_start': start, 'page_end': end}
                for i, (start, end) in enumerate([(3, 4), (8, 9), (11, 12), (1, 1), (20, 21)], 1)]
        scored = score_retrieved(rows, question)
        self.assertEqual([r['relevant'] for r in scored['retrieved']], [False, True, False, False, False])
        self.assertEqual((scored['hit_at_1'], scored['hit_at_3'], scored['hit_at_5'], scored['reciprocal_rank']), (0., 1., 1., .5))
        wrong = deepcopy(rows)
        wrong[1]['source_file'] = 'wrong.pdf'
        self.assertIsNone(score_retrieved(wrong, question)['first_relevant_rank'])
        wrong[1]['original_source_file'] = 'target.pdf'
        self.assertEqual(score_retrieved(wrong, question)['first_relevant_rank'], 2)
        wrong[1]['case_name'] = 'Other'
        self.assertIsNone(score_retrieved(wrong, question)['first_relevant_rank'])

    def test_hit_cutoffs_mrr_and_aggregation(self):
        question = {'expected_case': 'Target', 'expected_source_file': 'target.pdf', 'relevant_ranges': [[9, 9]]}
        scored = []
        for first in (1, 3, 5, None):
            rows = [{'rank': i, 'case_name': 'Target', 'source_file': 'target.pdf', 'page_start': 9 if i == first else 1, 'page_end': 9 if i == first else 1} for i in range(1, 6)]
            scored.append({'metrics': score_retrieved(rows, question)})
        self.assertEqual(aggregate(scored), {'question_count': 4, 'hit_at_1': .25, 'hit_at_3': .5, 'hit_at_5': .75, 'mrr': (1 + 1 / 3 + 1 / 5) / 4})


if __name__ == '__main__':
    unittest.main()
