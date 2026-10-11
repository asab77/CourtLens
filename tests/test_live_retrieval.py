"""Synthetic live-adapter tests and saved Phase 5B parity; no provider calls."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import faiss
import numpy as np

import gateway_config
import live_retrieval as live
from rag import format_evidence


def fake_client(dimension=1536):
    client = Mock()
    vector = np.zeros(dimension, dtype='float32')
    vector[0] = 3.0  # Verify the existing embed_question normalizes it.
    client.embeddings.create.return_value = SimpleNamespace(data=[SimpleNamespace(embedding=vector.tolist())])
    return client


def fixture():
    records = []
    for i in range(12):
        case = 'A' if i < 7 else 'B'
        records.append({'vector_id': i, 'text': ('target ' * (20 if case == 'A' else 1)) + f'evidence {i}',
                        'metadata': {'chunk_id': f'{case}:{i}', 'chunk_index': i if case == 'A' else i - 7,
                                     'case_name': case, 'source_file': f'{case}.pdf', 'original_source_file': f'raw-{case}.pdf',
                                     'page_start': i + 1, 'page_end': i + 2, 'opinion_type': 'dissent' if i % 2 else 'majority',
                                     'author': None if i % 2 else 'Raw Author', 'sections': [{'marker': 'I', 'title': ''}],
                                     'provenance': [{'sentence_id': f's{i}'}]}})
    index = faiss.IndexFlatIP(1536)
    index.add(np.eye(12, 1536, dtype='float32'))
    return index, records, {'embedding_model': gateway_config.VERCEL_EMBEDDING_MODEL, 'strategy': 'structure_aware_v1'}


class LiveAdapterTests(unittest.TestCase):
    def setUp(self):
        self.store = fixture()
        with patch.object(live, 'load_runtime_vector_store', return_value=self.store):
            self.resources = live.load_live_resources()
        self.client = fake_client()

    def test_loader_preserves_alignment_and_initializes_once(self):
        with patch.object(live, 'load_runtime_vector_store', return_value=self.store) as loader:
            with patch.object(live, 'BM25', wraps=live.BM25) as build:
                resources = live.load_live_resources(Path('/local/bundle/vector_store'))
                for _ in range(2):
                    live.retrieve_hybrid('target', resources, client=self.client)
        loader.assert_called_once_with(Path('/local/bundle/vector_store'))
        build.assert_called_once()
        self.assertIs(resources.catalog.records, resources.vector_store[1])
        self.assertEqual(resources.bm25.document_count, 12)
        self.assertEqual((resources.bm25.k1, resources.bm25.b), (1.5, .75))

    def test_dense_and_bm25_depths_and_query_normalization(self):
        with patch.object(live, 'search_vector_store', wraps=live.search_vector_store) as dense:
            with patch.object(live, 'fuse', wraps=live.fuse) as fusion:
                result = live.retrieve_hybrid(' target ', self.resources, client=self.client)
        dense.assert_called_once()
        self.assertEqual(dense.call_args.kwargs['top_k'], 5)
        self.assertEqual(np.linalg.norm(dense.call_args.args[0]), 1.0)
        self.assertEqual(len(fusion.call_args.args[1]), 5)
        self.assertEqual(len(fusion.call_args.args[2]), 5)
        self.assertEqual(len(result), 5)
        self.client.embeddings.create.assert_called_once_with(model='openai/text-embedding-3-small', input=['target'])

    def test_case_filter_before_top5_and_full_corpus_statistics(self):
        full_stats = (self.resources.bm25.document_count, self.resources.bm25.average_length, dict(self.resources.bm25.idf))
        self.assertTrue(all(self.store[1][i]['metadata']['case_name'] == 'A'
                            for i, _ in self.resources.bm25.rank('target', limit=5)))
        with patch.object(live, 'fuse', wraps=live.fuse) as fusion:
            result = live.retrieve_hybrid('target', self.resources, case_name='B', client=self.client)
        for candidates in fusion.call_args.args[1:]:
            self.assertEqual(len(candidates), 5)
            self.assertTrue(all(row['case_name'] == 'B' for row in candidates))
        self.assertTrue(all(row['case_name'] == 'B' for row in result))
        self.assertEqual(full_stats, (self.resources.bm25.document_count,
                                     self.resources.bm25.average_length, dict(self.resources.bm25.idf)))

    def test_hydration_metadata_scores_and_rag_compatibility(self):
        result = live.retrieve_hybrid('target', self.resources, client=self.client)
        for row in result:
            original = self.store[1][row['corpus_index']]
            self.assertEqual(row['text'], original['text'])
            self.assertEqual(row['metadata'], original['metadata'])
            for field in ('chunk_id', 'source_file', 'original_source_file', 'chunk_index',
                          'case_name', 'page_start', 'page_end', 'opinion_type', 'author', 'sections'):
                self.assertEqual(row[field], original['metadata'][field])
            expected = sum(1/(60 + row[key]) for key in ('dense_rank', 'bm25_rank') if row[key] is not None)
            self.assertEqual(row['rrf_score'], expected)
            for field in ('dense_rank', 'bm25_rank', 'dense_similarity', 'bm25_score'):
                self.assertIn(field, row)
            self.assertNotIn('similarity', row)
            self.assertEqual(row['score_type'], 'rrf')
        self.assertIn(result[0]['text'], format_evidence([dict(result[0], source_id='S1')]))
        result[0]['metadata']['author'] = 'Changed returned copy'
        self.assertNotEqual(result[0]['metadata'], self.store[1][result[0]['corpus_index']]['metadata'])

    def test_deterministic_ties_and_optional_scores(self):
        record = self.store[1][5]
        dense = [{'vector_id': 5, 'similarity': 999., 'text': record['text'], 'metadata': record['metadata']}]
        with patch.object(live, 'search_vector_store', return_value=dense):
            with patch.object(self.resources.bm25, 'rank', return_value=[(0, .001)]):
                result = live.retrieve_hybrid('target', self.resources, client=self.client)
        self.assertEqual([r['corpus_index'] for r in result], [0, 5])
        self.assertEqual([r['rrf_score'] for r in result], [1/61, 1/61])
        self.assertIsNone(result[0]['dense_rank'])
        self.assertIsNone(result[0]['dense_similarity'])
        self.assertIsNone(result[1]['bm25_rank'])
        self.assertIsNone(result[1]['bm25_score'])

    def test_empty_lexical_matches_and_both_empty_candidates(self):
        result = live.retrieve_hybrid('zzzzneverpresent', self.resources, client=self.client)
        self.assertEqual(len(result), 5)
        self.assertTrue(all(row['bm25_rank'] is None and row['bm25_score'] is None for row in result))
        with patch.object(live, 'search_vector_store', return_value=[]):
            self.assertEqual(live.retrieve_hybrid('zzzzneverpresent', self.resources, client=self.client), [])

    def test_invalid_questions_and_filters_fail_before_embedding(self):
        for question in ('', '  ', None, 123):
            with self.subTest(question=question), self.assertRaisesRegex(ValueError, 'non-empty'):
                live.retrieve_hybrid(question, self.resources, client=self.client)
        for case in ('unknown', '', 12):
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, 'case filter'):
                live.retrieve_hybrid('target', self.resources, case_name=case, client=self.client)
        self.client.embeddings.create.assert_not_called()

    def test_missing_credentials_and_provider_errors_propagate(self):
        with patch.object(gateway_config, 'require_experiment_api_key', side_effect=RuntimeError('Missing AI_GATEWAY_API_KEY')):
            with patch('openai.OpenAI') as client_factory:
                with self.assertRaisesRegex(RuntimeError, 'AI_GATEWAY_API_KEY'):
                    live.retrieve_hybrid('target', self.resources)
        client_factory.assert_not_called()
        error = RuntimeError('Provider failure')
        self.client.embeddings.create.side_effect = error
        with self.assertRaises(RuntimeError) as raised:
            live.retrieve_hybrid('target', self.resources, client=self.client)
        self.assertIs(raised.exception, error)
        self.client.embeddings.create.assert_called_once()

    def test_missing_assets_propagate_without_bm25_build(self):
        with patch.object(live, 'load_runtime_vector_store', side_effect=ValueError('Required runtime asset missing')):
            with patch.object(live, 'BM25') as build:
                with self.assertRaisesRegex(ValueError, 'missing'):
                    live.load_live_resources()
        build.assert_not_called()

    def test_changed_resource_records_and_misaligned_vector_ids_fail(self):
        self.store[1][0]['text'] = 'changed text'
        with self.assertRaisesRegex(ValueError, 'mismatched corpus'):
            live.retrieve_hybrid('target', self.resources, client=self.client)
        self.client.embeddings.create.assert_not_called()
        self.store[1][0]['vector_id'] = 2
        with patch.object(live, 'load_runtime_vector_store', return_value=self.store):
            with self.assertRaisesRegex(ValueError, 'aligned'):
                live.load_live_resources()

    def test_cross_corpus_and_wrong_chunk_candidates_rejected(self):
        original = self.store[1][0]
        for metadata in (dict(original['metadata'], source_file='other-corpus.pdf'),
                         dict(original['metadata'], chunk_id='wrong-chunk')):
            with self.subTest(metadata=metadata):
                row = {'vector_id': 0, 'similarity': .9, 'text': original['text'], 'metadata': metadata}
                with patch.object(live, 'search_vector_store', return_value=[row]):
                    with self.assertRaisesRegex(ValueError, 'identity|chunk ID|metadata mismatch'):
                        live.retrieve_hybrid('target', self.resources, client=self.client)

    def test_invalid_query_vectors_rejected(self):
        for embedding in ([1., 0.], [0.] * 1536, [float('nan')] * 1536):
            self.client.embeddings.create.return_value.data[0].embedding = embedding
            with self.subTest(length=len(embedding)), self.assertRaisesRegex(ValueError, 'Query embedding'):
                live.retrieve_hybrid('target', self.resources, client=self.client)


class SavedParityTests(unittest.TestCase):
    def test_all_40_benchmark_v2_questions_match_saved_phase5b(self):
        root = gateway_config.PROJECT_DIR
        resources = live.load_live_resources(gateway_config.DEFAULT_RUNTIME_VECTOR_STORE)
        read = lambda name: json.loads((root / name).read_text())
        questions = read('data/evaluation/chunking_benchmark_v2.json')['questions']
        dense_config = next(c for c in read('data/experiments/chunking/benchmark_v2_results.json')['configurations']
                            if c['id'] == 'structure_aware_v1')
        dense_by_id = {q['id']: q for q in dense_config['questions']}
        bm25_by_id = {q['id']: q for q in read('data/experiments/retrieval/bm25/structure_aware_v1/rankings_top20.json')['questions']}
        hybrid_by_id = {q['id']: q for q in read('data/experiments/retrieval/hybrid/structure_aware_v1/rankings.json')['questions']}
        self.assertEqual(len(questions), 40)
        for q in questions:
            with self.subTest(question=q['id']):
                saved_dense = dense_by_id[q['id']]['metrics']['retrieved']
                dense = []
                for row in saved_dense:
                    record = resources.vector_store[1][row['vector_id']]
                    self.assertEqual(row['source_file'], record['metadata']['source_file'])
                    self.assertEqual(row['chunk_index'], record['metadata']['chunk_index'])
                    dense.append({'vector_id': row['vector_id'], 'similarity': row['similarity'],
                                  'text': record['text'], 'metadata': record['metadata']})
                saved_bm25 = bm25_by_id[q['id']]['retrieved'][:5]
                ranked = resources.bm25.rank(q['question'], limit=5)
                self.assertEqual([i for i, _ in ranked], [r['corpus_index'] for r in saved_bm25])
                self.assertEqual([score for _, score in ranked], [r['bm25_score'] for r in saved_bm25])
                with patch.object(live, 'embed_question', return_value=np.eye(1, 1536, dtype='float32')) as embedding:
                    with patch.object(live, 'search_vector_store', return_value=dense):
                        result = live.retrieve_hybrid(q['question'], resources, client=object())
                embedding.assert_called_once()
                saved_hybrid = hybrid_by_id[q['id']]['retrieved'][:5]
                self.assertEqual([r['chunk_id'] for r in result], [r['chunk_id'] for r in saved_hybrid])
                for actual, saved in zip(result, saved_hybrid):
                    for key in ('corpus_index', 'hybrid_rank', 'rrf_score', 'dense_rank', 'bm25_rank', 'dense_similarity', 'bm25_score'):
                        self.assertEqual(actual[key], saved[key])


if __name__ == '__main__':
    unittest.main()
