"""Offline cap/dispatch tests: fake client only, no smoke main execution."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from run_phase7a3_smoke_test import CappedCalls, SmokeAbort, QUESTIONS, summarize


class SmokeRunnerTests(unittest.TestCase):
    def setUp(self):
        usage = SimpleNamespace(model_dump=lambda: {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30})
        response = SimpleNamespace(usage=usage, choices=[SimpleNamespace(finish_reason='stop', message=SimpleNamespace(content='Answer [S1]'))])
        self.dispatch = Mock(return_value=response)
        client = SimpleNamespace(embeddings=SimpleNamespace(create=self.dispatch),
                                 chat=SimpleNamespace(completions=SimpleNamespace(create=self.dispatch)))
        self.document = {'requests': []}
        self.save = Mock()
        self.capped = CappedCalls(client, self.document, self.save)

    def test_embedding_limit_includes_attempts(self):
        for _, q in QUESTIONS:
            self.capped.embeddings.create(model='openai/text-embedding-3-small', input=[q])
        with self.assertRaises(SmokeAbort):
            self.capped.embeddings.create(model='openai/text-embedding-3-small', input=[QUESTIONS[0][1]])
        self.assertEqual(self.dispatch.call_count, 3)

    def test_generation_cap_and_output_limit(self):
        messages = [{'role': 'user', 'content': 'evidence'}]
        for _ in range(4):
            self.capped.chat.completions.create(model='openai/gpt-4.1-mini', messages=messages)
        with self.assertRaises(SmokeAbort):
            self.capped.chat.completions.create(model='openai/gpt-4.1-mini', messages=messages)
        self.assertEqual(self.dispatch.call_count, 4)
        self.assertEqual(self.dispatch.call_args.kwargs['max_tokens'], 500)
        self.assertEqual(messages, [{'role': 'user', 'content': 'evidence'}])

    def test_provider_failure_aborts_and_does_not_log_body(self):
        self.dispatch.side_effect = RuntimeError('sensitive-provider-body')
        with self.assertRaises(SmokeAbort):
            self.capped.embeddings.create(model='openai/text-embedding-3-small', input=[QUESTIONS[0][1]])
        with self.assertRaises(SmokeAbort):
            self.capped.embeddings.create(model='openai/text-embedding-3-small', input=[QUESTIONS[1][1]])
        self.assertEqual(self.dispatch.call_count, 1)
        self.assertNotIn('sensitive-provider-body', str(self.document))
        self.assertEqual(self.document['requests'][0]['error_type'], 'RuntimeError')

    def test_rejects_document_embeddings_and_fallback_model(self):
        with self.assertRaises(SmokeAbort):
            self.capped.embeddings.create(model='openai/text-embedding-3-small', input=['Document chunk'])
        with self.assertRaises(SmokeAbort):
            self.capped.chat.completions.create(model='other-model', messages=[])
        self.dispatch.assert_not_called()

    def test_records_before_dispatch_and_summarizes_usage(self):
        self.dispatch.side_effect = lambda **kw: (self.assertEqual(self.document['requests'][0]['status'], 'dispatching') or SimpleNamespace(usage=None))
        self.capped.embeddings.create(model='openai/text-embedding-3-small', input=[QUESTIONS[0][1]])
        self.assertTrue(self.save.called)
        summarize(self.document)
        self.assertEqual(self.document['totals']['embedding_calls'], 1)
        self.assertEqual(self.document['totals']['embedding_input_tokens'], 0)


if __name__ == '__main__':
    unittest.main()
