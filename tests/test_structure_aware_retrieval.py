"""Phase 4B.2 tests use fake embedding clients and local temporary FAISS stores."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

import run_structure_aware_experiment as experiment
from benchmark_relevance import page_range_overlaps


def item(qid='DRE-04', qtype='legal_rule', case='Example v. Sample'):
    return {'id': qid, 'type': qtype, 'question': 'Why did the Court decide this?',
            'expected_case': case, 'expected_source_file': 'example.pdf', 'relevant_ranges': [[2, 3], [8, 9]], 'validated': True}


def record(index, opinion='majority', page=2, case='Example v. Sample'):
    return {'text': f'Evidence passage {index}.', 'metadata': {
        'chunk_id': f'example:{index}', 'chunk_index': index, 'case_name': case, 'source_file': 'example.pdf',
        'original_source_file': 'original.pdf', 'page_start': page, 'page_end': page, 'token_count': 10,
        'major_unit_id': f'example:u{index}', 'major_unit_type': 'major_legal_component',
        'opinion_type': opinion, 'author': 'Author', 'sections': [], 'chunking_strategy': experiment.STRATEGY}}


def ranked(records):
    return [{'vector_id': i, 'similarity': 0.9 - i / 10, **r} for i, r in enumerate(records)]


class LoadingAndScoringTests(unittest.TestCase):
    def test_frozen_records_and_order(self):
        records, manifest = experiment.load_frozen_records()
        self.assertEqual(len(records), 433)
        self.assertEqual(manifest['strategy'], 'structure_aware_v1')
        self.assertEqual(len({r['metadata']['chunk_id'] for r in records}), 433)
        self.assertFalse(any(r['metadata']['opinion_type'] == 'foreign' for r in records))

    def test_changed_frozen_hash_rejected(self):
        with patch.object(experiment, 'EXPECTED_CHUNKS_HASH', 'wrong'):
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                experiment.load_frozen_records()

    def test_reviewed_benchmark_only(self):
        questions = experiment.load_reviewed_benchmark()
        self.assertEqual(len(questions), 40)
        self.assertEqual({q['id'] for q in questions} & set(experiment.SPECIAL_IDS), set(experiment.SPECIAL_IDS))
        self.assertTrue(all('relevant_ranges' in q for q in questions))
        with patch.object(experiment, 'load_json', return_value={'status': 'draft'}):
            with self.assertRaisesRegex(ValueError, 'reviewed'):
                experiment.load_reviewed_benchmark()

    def test_multirange_source_and_case_relevance(self):
        records = [record(0, page=5), record(1, page=8), record(2, page=2, case='Wrong case')]
        q = experiment.score_question(item(), ranked(records))
        self.assertEqual(q['metrics']['first_relevant_rank'], 2)
        self.assertEqual([r['relevant'] for r in q['metrics']['retrieved']], [False, True, False])
        self.assertTrue(page_range_overlaps(7, 8, [[2, 3], [8, 9]]))
        records[1]['metadata']['source_file'] = 'wrong.pdf'
        self.assertIsNone(experiment.score_question(item(), ranked(records))['metrics']['first_relevant_rank'])

    def test_metrics_match_existing_and_preserve_opinion_metadata(self):
        q = experiment.score_question(item(), ranked([record(0, page=5), record(1, 'dissent', page=8)]))
        self.assertEqual(q['metrics']['hit_at_1'], 0)
        self.assertEqual(q['metrics']['hit_at_3'], 1)
        self.assertEqual(q['metrics']['reciprocal_rank'], 0.5)
        self.assertEqual(q['metrics']['retrieved'][1]['opinion_type'], 'dissent')
        self.assertTrue(q['metrics']['retrieved'][1]['relevant'])
        aggregated = experiment.aggregate_metrics([q])
        self.assertEqual(aggregated['mrr'], 0.5)

    def test_per_type_and_per_case_aggregation(self):
        a = experiment.score_question(item(qid='A', qtype='facts'), ranked([record(0)]))
        b = experiment.score_question(item(qid='B', qtype='reasoning', case='Other'), ranked([record(0)]))
        configuration = {'questions': [a, b]}
        self.assertEqual(experiment.aggregate_by_field(configuration, 'type')['facts']['hit_at_1'], 1)
        self.assertEqual(experiment.aggregate_by_field(configuration, 'expected_case')['Other']['hit_at_5'], 0)

    def test_win_classification_and_conversions(self):
        def configuration(ranks):
            return {'questions': [{'id': str(i), 'type': 'facts', 'expected_case': 'Case',
                                   'metrics': {'first_relevant_rank': rank}} for i, rank in enumerate(ranks)]}
        result = experiment.win_analysis(configuration([1, 4, 2, None, 3, None]), configuration([3, 1, 2, None, None, 5]))
        self.assertEqual(result['counts'], {'structure_aware_wins': 2, 'fixed_wins': 2, 'tie': 1, 'both_miss_top_5': 1})
        self.assertEqual(result['fixed_miss_to_structure_hit'], ['4'])
        self.assertEqual(result['structure_miss_to_fixed_hit'], ['5'])

    def test_opinion_flags_do_not_change_relevance_or_rank(self):
        q = experiment.score_question(item(), ranked([record(0, 'dissent'), record(1, 'concurrence')]))
        before = copy.deepcopy(q)
        observations = experiment.opinion_observations({'questions': [q]})
        self.assertEqual(q, before)
        self.assertEqual(observations['candidate_count'], 2)
        self.assertTrue(all(r['reviewed_relevant'] for r in observations['wrong_opinion_candidates']))

    def test_deterministic_question_results(self):
        r = ranked([record(0), record(1)])
        self.assertEqual(experiment.score_question(item(), r), experiment.score_question(item(), r))


class StoreAndResumeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.chunks = self.root / 'chunks.jsonl'
        self.chunk_manifest = self.root / 'manifest.json'
        self.records = [record(0), record(1, 'dissent')]
        self.chunks.write_text(''.join(json.dumps(r) + '\n' for r in self.records))
        self.chunk_manifest.write_text(json.dumps({'logic_version': 'test'}))
        self.identity = {'chunks_sha256': experiment.sha256(self.chunks), 'chunk_manifest_sha256': experiment.sha256(self.chunk_manifest)}
        self.patches = [patch.object(experiment, 'ROOT', self.root), patch.object(experiment, 'STORE', self.root / 'vector_store'),
                        patch.object(experiment, 'CHUNKS', self.chunks), patch.object(experiment, 'CHUNK_MANIFEST', self.chunk_manifest),
                        patch.object(experiment, 'EXPECTED_RECORDS', 2), patch.object(experiment, 'EXPECTED_DIMENSION', 3)]
        for p in self.patches:
            p.start()
        self.matrix = np.array([[3, 0, 0], [0, 4, 0]], dtype='float32')

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.directory.cleanup()

    def build(self):
        factory = Mock(return_value=object())
        with patch.object(experiment, 'create_embeddings', return_value=self.matrix.copy()) as create:
            store = experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, factory)
        self.assertEqual(create.call_args.kwargs['model'], experiment.EXPERIMENT_EMBEDDING_MODEL)
        return store

    def test_separate_store_alignment_and_normalization(self):
        store = self.build()
        self.assertEqual(store[0].ntotal, 2)
        self.assertEqual(store[1][0]['text'], self.records[0]['text'])
        self.assertTrue(np.allclose(np.linalg.norm(store[0].reconstruct_n(0, 2), axis=1), 1))
        bad = copy.deepcopy(self.records)
        bad[0]['text'] = 'Different order/content'
        with self.assertRaisesRegex(ValueError, 'frozen chunks/order'):
            experiment.validate_store(experiment.STORE, bad, self.identity)

    def test_existing_valid_store_does_not_reembed(self):
        self.build()
        factory = Mock(side_effect=AssertionError('No API client should be created'))
        experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, factory)
        factory.assert_not_called()

    def test_embedding_failure_publishes_no_final_store(self):
        with patch.object(experiment, 'create_embeddings', side_effect=RuntimeError('test failure')):
            with self.assertRaisesRegex(RuntimeError, 'test failure'):
                experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, lambda: object())
        self.assertFalse(experiment.STORE.exists())

    def test_incomplete_matrix_and_partial_store_rejected(self):
        with patch.object(experiment, 'create_embeddings', return_value=np.array([[1, 0, 0]], dtype='float32')):
            with self.assertRaisesRegex(ValueError, 'matrix'):
                experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, lambda: object())
        self.assertFalse(experiment.STORE.exists())
        experiment.STORE.mkdir()
        (experiment.STORE / 'index.faiss').write_text('incomplete')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, lambda: object())

    def test_staging_validation_failure_publishes_no_store(self):
        with patch.object(experiment, 'create_embeddings', return_value=self.matrix.copy()), patch.object(experiment, 'validate_store', side_effect=ValueError('staged invalid')):
            with self.assertRaisesRegex(ValueError, 'staged invalid'):
                experiment.build_or_load_store(self.records, {'logic_version': 'test'}, self.identity, lambda: object())
        self.assertFalse(experiment.STORE.exists())
        self.assertFalse(list(self.root.glob('.structure-aware-store-*')))

    def test_search_ranking_has_no_opinion_metadata_influence(self):
        store = self.build()
        query = np.array([[1, 0, 0]], dtype='float32')
        original = experiment.search_vector_store(query, store, top_k=2)
        store[1][0]['metadata']['opinion_type'] = 'dissent'
        store[1][1]['metadata']['opinion_type'] = 'majority'
        store[1][0]['metadata']['author'] = 'Unrelated author'
        changed = experiment.search_vector_store(query, store, top_k=2)
        self.assertEqual([(r['vector_id'], r['similarity']) for r in original], [(r['vector_id'], r['similarity']) for r in changed])

    def test_query_checkpoint_resume_only_unfinished_queries(self):
        # Five records are needed for the mandatory Top-5 checkpoint validation.
        (experiment.STORE).mkdir()
        (experiment.STORE / 'index.faiss').write_bytes(b'test index identity')
        (experiment.STORE / 'manifest.json').write_text('{}')
        records = [record(i) for i in range(5)]
        store = (None, [{'vector_id': i, **r} for i, r in enumerate(records)], {})
        questions = [item('A'), item('B')]
        with patch.object(experiment, 'embed_question', side_effect=[np.array([[1, 0, 0]], dtype='float32'), RuntimeError('transient')]), patch.object(experiment, 'search_vector_store', return_value=ranked(records)) as search:
            with self.assertRaisesRegex(RuntimeError, 'transient'):
                experiment.evaluate(questions, store, self.identity, lambda: object())
        progress = experiment.load_json(self.root / 'evaluation_progress.json')
        self.assertEqual(len(progress['questions']), 1)
        with patch.object(experiment, 'embed_question', return_value=np.array([[1, 0, 0]], dtype='float32')) as embed, patch.object(experiment, 'search_vector_store', return_value=ranked(records)) as search:
            completed = experiment.evaluate(questions, store, self.identity, lambda: object())
        self.assertEqual([q['id'] for q in completed], ['A', 'B'])
        self.assertEqual(embed.call_count, 1)
        self.assertEqual(search.call_args.kwargs, {'top_k': 5})
        self.assertEqual(embed.call_args.args, ('Why did the Court decide this?',))
        self.assertEqual(embed.call_args.kwargs['model'], experiment.EXPERIMENT_EMBEDDING_MODEL)


class AccountingAndReportingTests(unittest.TestCase):
    def test_end_to_end_fake_gateway_and_complete_rerun(self):
        # Exercise all 433 records and 40 reviewed questions in a temporary
        # strategy directory. Only the injected fake client can create vectors.
        calls = []
        def create(model, input):
            self.assertEqual(model, experiment.EXPERIMENT_EMBEDDING_MODEL)
            calls.append(len(input))
            vector = [1.0] + [0.0] * 1535
            return SimpleNamespace(
                data=[SimpleNamespace(index=i, embedding=vector) for i in reversed(range(len(input)))],
                usage=SimpleNamespace(prompt_tokens=len(input) * 10, total_tokens=len(input) * 10))
        client = SimpleNamespace(embeddings=SimpleNamespace(create=create))
        fixed_hash = experiment.sha256(experiment.FIXED_RESULTS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(experiment, 'ROOT', root), patch.object(experiment, 'STORE', root / 'vector_store'), patch.object(experiment, 'ANALYSIS', root / 'analysis'), patch.object(experiment, 'experiment_embedding_client', return_value=client), patch('build_index.time.sleep'), patch('builtins.print'):
                output = experiment.run()
                self.assertEqual(len(output['configurations'][0]['questions']), 40)
                self.assertEqual(output['embedding_usage']['document']['sdk_embedding_calls'], 5)
                self.assertEqual(output['embedding_usage']['query']['sdk_embedding_calls'], 40)
                self.assertEqual(calls[:5], [100, 100, 100, 100, 33])
                self.assertEqual(len(calls), 45)
                self.assertTrue(output['protected_artifacts']['unchanged'])
                frozen_outputs = {p: p.read_bytes() for p in (root / 'results.json', root / 'analysis.json', root / 'analysis.md')}
                with patch.object(experiment, 'experiment_embedding_client', side_effect=AssertionError('Do not reembed')):
                    again = experiment.run()
                self.assertEqual(again, output)
                self.assertTrue(all(p.read_bytes() == contents for p, contents in frozen_outputs.items()))
        self.assertEqual(experiment.sha256(experiment.FIXED_RESULTS), fixed_hash)

    def test_usage_accounts_success_and_reraises_unrelated_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = experiment.UsageLedger(Path(directory) / 'usage.json', {'test': True})
            response = SimpleNamespace(usage=SimpleNamespace(prompt_tokens=17, total_tokens=17))
            create = Mock(side_effect=[response, RuntimeError('do not swallow')])
            client = ledger.client(SimpleNamespace(embeddings=SimpleNamespace(create=create)), 'document')
            self.assertIs(client.embeddings.create(model='model', input=['text']), response)
            with self.assertRaisesRegex(RuntimeError, 'do not swallow'):
                client.embeddings.create(model='model', input=['text'])
            summary = ledger.summary()['document']
            self.assertEqual(summary['sdk_embedding_calls'], 2)
            self.assertEqual(summary['input_tokens_returned'], 17)
            self.assertEqual(summary['failed_calls'], 1)
            self.assertNotIn('do not swallow', ledger.path.read_text())
            self.assertIsNone(ledger.summary()['cost'])

    def test_special_question_paths_and_fixed_result_nonmutation(self):
        questions = [experiment.score_question(item(qid), ranked([record(0, page=5)])) for qid in experiment.SPECIAL_IDS]
        new = {'id': experiment.STRATEGY, 'vector_count': 433, 'questions': questions, 'metrics': experiment.aggregate_metrics(questions)}
        fixed = {'configurations': [{**copy.deepcopy(new), 'id': cid, 'vector_count': 598} for cid in ('600_100', '900_150', '1200_200', '1500_200')]}
        before = copy.deepcopy(fixed)
        output = {'configurations': [new], 'embedding_usage': {}, 'protected_artifacts': {}}
        with patch.object(experiment, 'fixed_evidence', return_value={'configuration': 'mock', 'first_relevant_rank': None, 'retrieved': []}):
            analysis = experiment.analyze(output, fixed)
            repeat = experiment.analyze(output, fixed)
        self.assertEqual(analysis, repeat)
        self.assertEqual(fixed, before)
        self.assertEqual(set(analysis['special_questions']), set(experiment.SPECIAL_IDS))
        report = experiment.render_report(output, analysis)
        self.assertIn('DRE-04', report)
        self.assertIn('OBE-01', report)
        self.assertIn('Top-5 miss', report)
        self.assertIn('realized chunk-size distribution', report)
        self.assertIn('regressions', report)


if __name__ == '__main__':
    unittest.main()
