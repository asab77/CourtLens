"""Local checks for audit scope, source integrity, freezing, and simulation."""

import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import audit_chunking_benchmark as audit


class Phase4CAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = audit.protected_snapshot()
        # Neither packaging nor simulation should open a network socket.
        with patch.object(socket, 'create_connection', side_effect=AssertionError('Network forbidden')), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            cls.frozen = audit.build_audit()

    def test_exact_eight_questions_and_ten_candidates_each(self):
        self.assertEqual(tuple(q['question_id'] for q in self.frozen['questions']), audit.QUESTION_IDS)
        self.assertEqual(self.frozen['candidate_count'], 80)
        for q in self.frozen['questions']:
            self.assertEqual(len(q['candidates']), 10)
            for strategy in audit.STRATEGIES:
                self.assertEqual([c['rank'] for c in q['candidates'] if c['retrieval_strategy'] == strategy], [1, 2, 3, 4, 5])

    def test_deterministic_decisions_and_serialization(self):
        self.assertEqual(audit.serialized(self.frozen), audit.serialized(audit.build_audit()))
        self.assertEqual(audit.digest(self.frozen['questions']), self.frozen['frozen_decisions_sha256'])
        self.assertNotIn('simulation', self.frozen)

    def test_all_text_is_source_verified_and_additions_have_actual_page_text(self):
        for q in self.frozen['questions']:
            for c in q['candidates']:
                self.assertTrue(c['source_verified'])
                self.assertTrue(c['evidence_excerpt'])
                self.assertTrue(c['full_candidate_text'])
                self.assertTrue(c['rationale'])
                if c['decision'] != audit.R:
                    self.assertEqual(c['proposed_range_additions'], [])
                for evidence in c['canonical_proposed_page_evidence']:
                    self.assertTrue(evidence['canonical_text'].strip())
                    self.assertIn(evidence['pages'], c['proposed_range_additions'])

    def test_page_marker_caveat_and_source_author_are_preserved(self):
        by_id = {q['question_id']: q for q in self.frozen['questions']}
        mar = by_id['MAR-04']['candidates'][0]
        self.assertTrue(mar['trailing_page_marker_without_text'])
        self.assertEqual(mar['decision'], audit.A)
        self.assertTrue(mar['official_page_overlap_relevant'])
        daniel = by_id['DRE-04']['candidates'][6]
        self.assertEqual(daniel['saved_author'], 'Grier')
        self.assertEqual(daniel['author'], 'Daniel')
        self.assertEqual(daniel['decision'], audit.A)

    def test_simulation_roundtrip_is_nonmutating_and_official_baseline_reproduces(self):
        frozen = json.loads(audit.serialized(self.frozen))
        frozen_bytes = audit.serialized(frozen)
        with patch.object(socket, 'create_connection', side_effect=AssertionError('Network forbidden')), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            simulation = audit.simulate(frozen)
        self.assertEqual(audit.serialized(frozen), frozen_bytes)
        self.assertEqual(simulation['status'], 'SIMULATED — PROPOSED LABELS NOT APPLIED')
        for strategy, config in audit.configurations(audit.ROOT).items():
            self.assertEqual(simulation['strategies'][strategy]['official_reproduced'], config['metrics'])
        self.assertEqual(audit.protected_snapshot(), self.before)

    def test_changed_frozen_decisions_are_rejected(self):
        changed = copy.deepcopy(self.frozen)
        changed['questions'][0]['candidates'][0]['decision'] = audit.N
        with self.assertRaisesRegex(ValueError, 'Frozen decisions changed'):
            audit.simulate(changed)

    def test_scope_expansion_is_rejected(self):
        changed = copy.deepcopy(self.frozen)
        changed['scope'].append('GID-01')
        with self.assertRaisesRegex(ValueError, 'exactly the eight'):
            audit.simulate(changed)

    def test_scoring_uses_correct_case_source_and_inclusive_overlap(self):
        q = {'expected_case': 'Target', 'expected_source_file': 'target.pdf', 'relevant_ranges': [[9, 10]]}
        rows = [
            {'rank': 1, 'case_name': 'Wrong', 'source_file': 'target.pdf', 'page_start': 9, 'page_end': 10},
            {'rank': 2, 'case_name': 'Target', 'source_file': 'wrong.pdf', 'page_start': 9, 'page_end': 10},
            {'rank': 3, 'case_name': 'Target', 'source_file': 'target.pdf', 'page_start': 8, 'page_end': 9},
        ]
        self.assertEqual(audit.first_rank({'metrics': {'retrieved': rows}}, q), 3)
        self.assertEqual(audit.rank_metrics([1, 3, None]), {'question_count': 3, 'hit_at_1': 1 / 3, 'hit_at_3': 2 / 3, 'hit_at_5': 2 / 3, 'mrr': (1 + 1 / 3) / 3})

    def test_only_new_outputs_are_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit.write_outputs(self.frozen, root)
            files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
            self.assertEqual(files, {str(audit.AUDIT_PATH), str(audit.REPORT_PATH)})
            self.assertEqual(audit.read_json(root / audit.AUDIT_PATH), self.frozen)
        self.assertEqual(audit.protected_snapshot(), self.before)

    @classmethod
    def tearDownClass(cls):
        if audit.protected_snapshot() != cls.before:
            raise AssertionError('Existing benchmark, source, result, chunk, parser, or vector-store files changed')


if __name__ == '__main__':
    unittest.main()
