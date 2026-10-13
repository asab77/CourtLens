"""Local hybrid chat integration tests; mocked retrievers and generation."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

import assistant_integration as a
import gateway_config as config
import rag
from evidence_context import build_evidence_context
from test_evidence_context import record
import test_application_gateway_migration as previous


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.records = [dict(record(0), score_type='rrf', hybrid_rank=1, rrf_score=2/61),
                        dict(record(1, 'dissent', None), score_type='rrf', hybrid_rank=2, rrf_score=1/62)]
        self.resources = SimpleNamespace(vector_store=('existing', [], {}))
        self.configuration = config.VercelProviderConfig('verified-test/chat', 'fake-key')
        self.patches = [patch.object(a, 'get_gateway_api_key', return_value='fake-key'),
                        patch.object(a, 'get_runtime_setting', side_effect=lambda n: self.configuration.model if n == 'VERCEL_GENERATION_MODEL' else ''),
                        patch.object(a, 'vercel_generation_config', return_value=self.configuration),
                        patch.object(a, 'retrieve_hybrid', return_value=self.records),
                        patch.object(a, 'semantic_search', return_value=self.records),
                        patch.object(a, 'evidence_budget_config', return_value=(12000, .1)),
                        patch.object(a, 'generate_grounded_answer_from_evidence', return_value='Answer [S1].')]
        self.mocks = [p.start() for p in self.patches]
        for p in self.patches: self.addCleanup(p.stop)

    def answer(self, **kwargs):
        return a.answer_question('Original question?', self.resources, self.configuration.model, [], **kwargs)

    def test_hybrid_default_context_mapping_and_question_unchanged(self):
        result = self.answer()
        self.mocks[3].assert_called_once_with('Original question?', self.resources, case_name=None)
        self.mocks[4].assert_not_called()
        context = self.mocks[6].call_args.args[1]
        self.assertEqual(context, build_evidence_context(self.records, 12000, safety_margin=.1))
        self.assertEqual(result['evidence'], context.evidence)
        self.assertEqual(result['source_mapping'], context.sources)
        self.assertEqual(result['context_usage'], context.usage)
        self.assertEqual(result['retrieval_strategy'], a.HYBRID)
        self.assertFalse(result['prompt_accounting']['total_model_capacity_known'])
        self.assertEqual(result['prompt_accounting']['expected_answer_tokens'], 1024)

    def test_dense_strategy_is_explicit(self):
        self.answer(strategy=a.DENSE, dense_top_k=7, case_name='Case v. Case')
        self.mocks[3].assert_not_called()
        self.mocks[4].assert_called_once_with('Original question?', top_k=7, case_name='Case v. Case',
                                             vector_store=self.resources.vector_store)

    def test_empty_and_insufficient_budget_do_not_generate(self):
        self.mocks[3].return_value = []
        result = self.answer()
        self.assertEqual(result['context_status'], 'insufficient_context')
        self.assertEqual(result['content'], rag.INSUFFICIENT_EVIDENCE_MESSAGE)
        self.mocks[6].assert_not_called()
        self.mocks[3].return_value = self.records
        self.mocks[5].return_value = (0, .1)
        result = self.answer()
        self.assertEqual(result['evidence'], [])
        self.assertEqual(result['context_usage']['skipped_count'], 2)
        self.mocks[6].assert_not_called()

    def test_missing_credentials_or_model_stops_before_retrieval(self):
        self.mocks[0].return_value = ''
        with self.assertRaisesRegex(a.AssistantError, 'AI_GATEWAY_API_KEY'): self.answer()
        self.mocks[0].return_value = 'fake-key'
        self.mocks[1].side_effect = None
        self.mocks[1].return_value = ''
        with self.assertRaisesRegex(a.AssistantError, 'VERCEL_GENERATION_MODEL'): self.answer()
        self.mocks[3].assert_not_called()
        self.mocks[6].assert_not_called()

    def test_errors_redact_payloads_and_never_fall_back(self):
        self.mocks[3].side_effect = RuntimeError('sensitive-payload-secret traceback provider body')
        with self.assertRaises(a.AssistantError) as raised: self.answer()
        self.assertNotIn('sensitive', str(raised.exception))
        self.mocks[4].assert_not_called()
        self.mocks[6].assert_not_called()
        self.mocks[3].side_effect = ValueError('Invalid case filter: secret')
        with self.assertRaises(a.AssistantError): self.answer(case_name='unknown')
        self.mocks[4].assert_not_called()

    def test_invalid_citations_and_provider_generation_errors_not_stored(self):
        for value in ('Wrong [S01]', 'Wrong [S999]', 'Wrong [S1', 'No citation'):
            self.mocks[6].return_value = value
            with self.subTest(value=value):
                result = self.answer()
                self.assertEqual(result['response_state'], 'VALIDATION_FAILED')
                self.assertNotEqual(result['content'], value)
        self.mocks[6].side_effect = RuntimeError('private response payload')
        with self.assertRaises(a.AssistantError) as raised: self.answer()
        self.assertNotIn('private', str(raised.exception))

    def test_context_budget_failure_safe_message(self):
        self.mocks[5].side_effect = RuntimeError('bad budget private path')
        with self.assertRaisesRegex(a.AssistantError, 'bounded evidence') as raised: self.answer()
        self.assertNotIn('private', str(raised.exception))

    def test_two_turns_have_distinct_source_maps_and_history_sanitized(self):
        history = [{'role': 'assistant', 'content': 'Prior opinion [S1].'}]
        result = a.answer_question('Question', self.resources, self.configuration.model, history)
        self.assertEqual(result['source_mapping']['S1']['chunk_id'], 'chunk-0')
        self.mocks[3].return_value = [record(5)]
        other = a.answer_question('New question', self.resources, self.configuration.model, history)
        self.assertEqual(other['source_mapping']['S1']['chunk_id'], 'chunk-5')
        self.assertEqual(history[0]['content'], 'Prior opinion [S1].')
        self.assertNotIn('[S1]', rag.format_history(history))


class CacheIdentityTests(unittest.TestCase):
    def test_resource_identity_changes_with_asset_or_source_hash(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); store = root/'bundle/vector_store'; store.mkdir(parents=True)
            for name in ('index.faiss', 'records.jsonl', 'manifest.json'): (store/name).write_text(name)
            (store.parent/'chunks.jsonl').write_text('frozen')
            (store.parent/'manifest.json').write_text(json.dumps({'source_structural_artifact': 'preview.json'}))
            (root/'preview.json').write_text('preview')
            with patch.object(a, 'PROJECT_DIR', root):
                before = a.resource_identity(store)
                (root/'preview.json').write_text('different preview')
                self.assertNotEqual(before, a.resource_identity(store))
                with patch.object(a, 'load_live_resources') as load:
                    with self.assertRaisesRegex(ValueError, 'changed'): a.initialize_resources(store, before)
                    load.assert_not_called()

    def test_streamlit_cache_reuses_same_path_version_and_separates_versions(self):
        import streamlit as st
        cached = st.cache_resource(a.initialize_resources)
        cached.clear()
        with patch.object(a, 'resource_identity', side_effect=lambda path: ('v2',) if str(path).endswith('two') else ('v1',)):
            with patch.object(a, 'load_live_resources', return_value=object()) as load:
                first = cached('/assets/one', ('v1',))
                self.assertIs(first, cached('/assets/one', ('v1',)))
                cached('/assets/two', ('v2',))
                self.assertEqual(load.call_count, 2)
        cached.clear()

    def test_missing_assets_fail_before_initialization(self):
        with patch.object(a, 'load_live_resources') as load:
            with self.assertRaises(FileNotFoundError): a.resource_identity('/missing/courtlens/vector_store')
            load.assert_not_called()


class HybridUITests(previous.ApplicationUITests):
    def test_hybrid_default_rendering_and_session_local_storage(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        control = next(s for s in self.app.selectbox if s.label == 'Assistant retrieval strategy')
        self.assertEqual(control.value, a.HYBRID)
        self.app.chat_input[0].set_value('Hybrid question').run()
        self.assertEqual(len(self.app.exception), 0)
        message = self.app.session_state['court_messages'][-1]
        self.assertEqual(message['retrieval_strategy'], a.HYBRID)
        self.assertIn('S1', message['source_mapping'])
        captions = '\n'.join(c.value for c in self.app.caption)
        self.assertIn('RRF score', captions)
        self.assertIn('Opinion:', captions)
        self.assertIn('Raw author:', captions)
        self.assertNotIn('Similarity', captions)
        from streamlit.testing.v1 import AppTest
        another = AppTest.from_file(str(config.PROJECT_DIR/'app.py')).run()
        self.assertEqual(another.session_state['court_messages'], [])

    def test_missing_assets_show_safe_startup_error(self):
        with patch.object(a, 'resource_identity', side_effect=FileNotFoundError('sensitive-private-path')):
            self.app.run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertTrue(any('validated runtime assets' in err.value for err in self.app.error))
        self.assertFalse(any('sensitive' in err.value for err in self.app.error))
        self.mocks[-1].assert_not_called()

    def test_missing_credentials_show_safe_chat_message(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        with patch.object(a, 'get_gateway_api_key', return_value=''):
            self.app.chat_input[0].set_value('Question').run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertIn('AI_GATEWAY_API_KEY', self.app.session_state['court_messages'][-1]['content'])
        self.mocks[-1].assert_not_called()

    def test_explicit_dense_choice_remains_available(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        control = next(s for s in self.app.selectbox if s.label == 'Assistant retrieval strategy')
        control.set_value(a.DENSE).run()
        self.app.chat_input[0].set_value('Dense question').run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.session_state['court_messages'][-1]['retrieval_strategy'], a.DENSE)
        self.mocks[-3].assert_called_once()


class ResponseStateUITests(previous.ApplicationUITests):
    def test_abstention_is_not_rendered_as_grounded_answer(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        self.mocks[-1].return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"state":"INSUFFICIENT_EVIDENCE","answer":""}'))])
        self.app.chat_input[0].set_value('Dobbs question').run()
        self.assertEqual(len(self.app.exception),0)
        message=self.app.session_state['court_messages'][-1]
        self.assertEqual(message['response_state'],'INSUFFICIENT_EVIDENCE')
        self.assertNotIn('[S',message['content'])
        captions='\n'.join(c.value for c in self.app.caption)
        self.assertIn('do not establish the requested answer',captions)
        self.assertNotIn('Grounded in',captions)
        self.assertEqual(self.mocks[-1].return_value.chat.completions.create.call_count,1)

    def test_validation_failure_does_not_display_original_draft(self):
        self.app.segmented_control(key='application_mode').set_value('AI Assistant').run()
        self.mocks[-1].return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"state":"ANSWERED","answer":"Unsupported imaginary claim [S999]"}'))])
        self.app.chat_input[0].set_value('Question').run()
        self.assertEqual(len(self.app.exception),0)
        message=self.app.session_state['court_messages'][-1]
        self.assertEqual(message['response_state'],'VALIDATION_FAILED')
        self.assertNotIn('Unsupported imaginary claim','\n'.join(m.value for m in self.app.markdown))
        self.assertNotIn('raw_draft',message)
        self.assertEqual(self.mocks[-1].return_value.chat.completions.create.call_count,1)
