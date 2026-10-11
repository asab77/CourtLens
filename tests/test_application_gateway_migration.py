"""CourtLens provider migration tests with mocked clients and Streamlit UI."""
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import gateway_config as config
import rag
import retrieve
from runtime_assets import load_runtime_vector_store


class ApplicationGatewayTests(unittest.TestCase):
    def setUp(self):
        self.config = config.VercelProviderConfig('verified-test/chat', 'fake-key')
        self.client = Mock()
        self.client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='Supported answer [S1].'))])
        self.evidence = [{'source_id': 'S1', 'text': 'Full evidence text.',
                          'metadata': {'case_name': 'Case', 'page_start': 1, 'page_end': 2}}]

    def test_active_embedding_client_and_default_model(self):
        with patch.object(retrieve, 'vercel_embedding_config', return_value=self.config) as configured:
            with patch.object(retrieve, 'vercel_client') as factory:
                retrieve.embedding_client()
        configured.assert_called_once_with()
        factory.assert_called_once_with(self.config)
        self.assertEqual(retrieve.embed_question.__defaults__[1], config.VERCEL_EMBEDDING_MODEL)

    def test_generation_uses_configured_model_and_existing_citations(self):
        with patch.object(rag, 'vercel_generation_config', return_value=self.config):
            with patch.object(rag, 'vercel_client', return_value=self.client) as factory:
                answer = rag.generate_grounded_answer_from_evidence('Question?', self.evidence, self.config.model)
        factory.assert_called_once_with(self.config)
        self.assertEqual(answer, 'Supported answer [S1].')
        request = self.client.chat.completions.create.call_args.kwargs
        self.assertEqual(request['model'], self.config.model)
        self.assertIn('Full evidence text.', request['messages'][1]['content'])
        self.assertIn('[S1]', request['messages'][1]['content'])

    def test_missing_generation_model_fails_before_client_creation(self):
        with patch.object(rag, 'vercel_generation_config', side_effect=RuntimeError('Set VERCEL_GENERATION_MODEL')):
            with patch.object(rag, 'vercel_client') as factory:
                with self.assertRaisesRegex(RuntimeError, 'VERCEL_GENERATION_MODEL'):
                    rag.generate_grounded_answer_from_evidence('Question?', self.evidence, 'anything')
        factory.assert_not_called()

    def test_arbitrary_unconfigured_model_is_rejected(self):
        with patch.object(rag, 'vercel_generation_config', return_value=self.config):
            with patch.object(rag, 'vercel_client') as factory:
                with self.assertRaisesRegex(ValueError, 'VERCEL_GENERATION_MODEL'):
                    rag.generate_grounded_answer_from_evidence('Question?', self.evidence, 'unconfigured/model')
        factory.assert_not_called()

    def test_model_catalog_has_no_invented_default(self):
        with patch.object(rag, 'get_runtime_setting', return_value=''):
            self.assertEqual(rag.configured_answer_models(), {})
        with patch.object(rag, 'get_runtime_setting', return_value=self.config.model):
            self.assertEqual(rag.configured_answer_models(), {self.config.model: self.config.model})

    def test_default_dense_path_uses_validated_runtime_loader(self):
        store = (Mock(), [], {'embedding_model': config.EMBEDDING_MODEL,
                             'gateway_base_url': config.GATEWAY_BASE_URL})
        with patch('runtime_assets.load_runtime_vector_store', return_value=store) as load:
            with patch.object(retrieve, 'embed_question', return_value='vector') as embed:
                with patch.object(retrieve, 'search_vector_store', return_value=[]) as search:
                    self.assertEqual(retrieve.semantic_search('question'), [])
        load.assert_called_once_with()
        embed.assert_called_once_with('question')
        search.assert_called_once_with('vector', store, top_k=5, case_name=None)

    def test_legacy_store_is_rejected_before_query_embedding(self):
        store = (Mock(), [], {'embedding_model': config.LEGACY_NYU_EMBEDDING_MODEL,
                             'gateway_base_url': config.LEGACY_NYU_BASE_URL})
        with patch.object(retrieve, 'embed_question') as embed:
            with self.assertRaisesRegex(ValueError, 'incompatible'):
                retrieve.semantic_search('question', vector_store=store)
        embed.assert_not_called()

    def test_no_active_nyu_imports_or_model_ids(self):
        root = config.PROJECT_DIR
        for name in ('app.py', 'rag.py', 'retrieve.py', 'build_index.py', 'runtime_assets.py'):
            with self.subTest(file=name):
                source = (root / name).read_text()
                for forbidden in ('NYU_AI_GATEWAY_API_KEY', 'require_nyu', 'get_nyu',
                                  'apps.cloud.rt.nyu.edu', '@vertexai/', '@gpt56sol/', 'x-portkey-provider'):
                    self.assertNotIn(forbidden, source)


class ApplicationUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read-only loading of the existing frozen store; no provider requests.
        cls.store = load_runtime_vector_store(config.DEFAULT_RUNTIME_VECTOR_STORE)

    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.model = 'verified-test/chat'
        self.patches = [
            patch.object(config, 'get_gateway_api_key', return_value='fake-key'),
            patch.object(config, 'require_experiment_api_key', return_value='fake-key'),
            patch.object(config, 'get_runtime_setting', side_effect=lambda name: self.model if name == 'VERCEL_GENERATION_MODEL' else ''),
            patch.object(rag, 'get_runtime_setting', side_effect=lambda name: self.model if name == 'VERCEL_GENERATION_MODEL' else ''),
            patch('runtime_assets.load_runtime_vector_store', return_value=self.store),
            patch.object(retrieve, 'semantic_search', return_value=[dict(
                vector_id=0, similarity=0.9, text=self.store[1][0]['text'], metadata=self.store[1][0]['metadata'])]),
            patch.object(rag, 'vercel_client'),
        ]
        self.mocks = [p.start() for p in self.patches]
        for p in self.patches:
            self.addCleanup(p.stop)
        self.mocks[-1].return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='Test grounded answer [S1].'))])
        self.app = AppTest.from_file(str(config.PROJECT_DIR / 'app.py')).run()
        self.assertEqual(len(self.app.exception), 0)

    def test_retrieval_controls_and_normal_chat_preserve_session(self):
        self.assertTrue(any(s.label == 'Top-K results' for s in self.app.slider))
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(next(s for s in self.app.selectbox if s.label == 'Model').options, [self.model])
        self.app.chat_input[0].set_value('What does the evidence say?').run()
        self.assertEqual(len(self.app.exception), 0)
        messages = self.app.session_state['court_messages']
        self.assertEqual(messages[-1]['content'], 'Test grounded answer [S1].')
        self.assertEqual(messages[-1]['evidence'][0]['source_id'], 'S1')
        self.assertEqual(self.mocks[-1].return_value.chat.completions.create.call_count, 1)

    def test_retrieval_form_preserves_dense_evidence_display(self):
        self.app.text_input(key='retrieval_question').set_value('Find evidence')
        next(b for b in self.app.button if b.label == 'Search').click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.mocks[-2].assert_called_once()
        self.mocks[-1].assert_not_called()
        self.assertTrue(any(h.value == 'Retrieved Evidence' for h in self.app.header))

    def test_compare_models_is_visible_but_explicitly_unavailable(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        self.app.segmented_control(key='assistant_mode').set_value('Compare Models').run()
        self.assertEqual(len(self.app.exception), 0)
        button = next(b for b in self.app.button if b.label == 'Compare answers')
        self.assertTrue(button.disabled)
        self.assertTrue(any('Two verified model configurations' in item.value for item in self.app.info))
        self.mocks[-1].assert_not_called()

    def test_missing_generation_model_stops_before_retrieval(self):
        self.model = ''
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        self.app.chat_input[0].set_value('A question').run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertIn('VERCEL_GENERATION_MODEL', self.app.session_state['court_messages'][-1]['content'])
        self.mocks[-2].assert_not_called()
        self.mocks[-1].assert_not_called()


if __name__ == '__main__':
    unittest.main()
