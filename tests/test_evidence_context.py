"""Local Phase 7A.2C evidence/context and mocked generation tests."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import evidence_context as e
import gateway_config as config
import rag


def record(i=0, opinion='majority', author='Raw Author', text=None):
    return {'chunk_id': f'chunk-{i}', 'text': text or f'Exact original opinion text {i}.',
            'collection': 'structure_aware_v1', 'hybrid_rank': i+1,
            'metadata': {'chunk_id': f'chunk-{i}', 'source_file': 'case.pdf', 'original_source_file': 'raw-case.pdf',
                         'chunk_index': i, 'case_name': 'Case v. Case', 'page_start': 10, 'page_end': 12,
                         'opinion_type': opinion, 'author': author, 'sections': [{'marker': 'II', 'title': 'Reasons'}],
                         'provenance': [{'sentence_id': f's{i}', 'page_start': 10}]}}


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoding = e.default_tokenizer()

    def build(self, records, budget=12000, margin=0):
        return e.build_evidence_context(records, budget, safety_margin=margin, tokenizer=self.encoding)

    def test_canonical_ids_mapping_and_input_not_mutated(self):
        records = [record(5), record(2)]
        records[0]['source_id'] = 'S001'
        before = deepcopy(records)
        context = self.build(records)
        self.assertEqual([r['source_id'] for r in context.evidence], ['S1', 'S2'])
        self.assertEqual(context.sources['S1']['chunk_id'], 'chunk-5')
        self.assertEqual(context.sources['S2']['retrieved_position'], 2)
        self.assertEqual(context.sources['S1']['metadata']['provenance'], records[0]['metadata']['provenance'])
        self.assertEqual(records, before)

    def test_duplicate_identity_and_chunk_id_rejected_before_skipping(self):
        for records in ([record(), record()], [record(), dict(record(1), metadata=dict(record(1)['metadata'], chunk_id='chunk-0'), chunk_id='chunk-0')]):
            with self.subTest(records=records), self.assertRaisesRegex(ValueError, 'Duplicate'):
                self.build(records, budget=0)

    def test_opinions_remain_distinct_on_overlapping_pages(self):
        records = [record(0, 'majority'), record(1, 'dissent'), record(2, 'concurrence')]
        context = self.build(records)
        self.assertEqual(len(context.evidence), 3)
        for label in ('majority', 'dissent', 'concurrence'):
            self.assertIn(f'Opinion (source metadata): {label}', context.text)
        self.assertEqual([r['text'] for r in context.evidence], [r['text'] for r in records])

    def test_unknown_uncertain_and_raw_ocr_author_preserved(self):
        records = [record(0, 'unknown', None), record(1, 'other', 'KENNEDY, J ust1ce (?)')]
        context = self.build(records)
        self.assertIn('Author (raw source metadata): Unknown', context.text)
        self.assertIn('Opinion (source metadata): unknown', context.text)
        self.assertIn('KENNEDY, J ust1ce (?)', context.text)
        self.assertIsNone(context.evidence[0]['metadata']['author'])
        self.assertEqual(context.evidence[1]['metadata']['author'], records[1]['metadata']['author'])

    def test_missing_optional_metadata_not_invented(self):
        item = record()
        for field in ('opinion_type', 'author', 'sections', 'chunk_id'):
            item['metadata'].pop(field)
        item.pop('chunk_id')
        context = self.build([item])
        self.assertIn('Opinion (source metadata): Unknown', context.text)
        self.assertIn('Sections (source metadata): Unknown', context.text)
        self.assertIsNone(context.sources['S1']['chunk_id'])
        self.assertNotIn('author', context.evidence[0]['metadata'])

    def test_case_source_pages_sections_and_text_exact(self):
        item = record(text='OCR  w0rd\n===== PAGE 10 =====\nQuoted text.')
        context = self.build([item])
        self.assertIn('Case: Case v. Case', context.text)
        self.assertIn('Source: raw-case.pdf', context.text)
        self.assertIn('PDF pages: 10-12', context.text)
        self.assertIn('Sections (source metadata): II Reasons', context.text)
        self.assertTrue(context.text.endswith(item['text']))
        self.assertFalse(context.evidence[0]['truncated'])

    def test_actual_formatted_token_count_includes_headers_and_separators(self):
        context = self.build([record(), record(1)])
        self.assertEqual(context.usage['evidence_tokens'], len(self.encoding.encode(context.text, disallowed_special=())))
        self.assertGreater(context.usage['evidence_tokens'], sum(r['included_text_tokens'] for r in context.evidence))
        self.assertEqual(context.usage['tokenizer'], 'cl100k_base')

    def test_exact_budget_boundary_and_safety_margin(self):
        initial = self.build([record()])
        count = initial.usage['evidence_tokens']
        self.assertEqual(self.build([record()], count).status, 'ready')
        self.assertEqual(self.build([record()], count-1).status, 'insufficient_context')
        context = self.build([record()], count, margin=.1)
        self.assertLessEqual(context.usage['evidence_tokens'], context.usage['effective_budget'])
        self.assertEqual(context.status, 'insufficient_context')

    def test_skip_whole_chunk_continue_order_no_truncation(self):
        small = self.build([record(1), record(2)])
        records = [record(0, text='very long passage ' * 2000), record(1), record(2)]
        context = self.build(records, small.usage['evidence_tokens'])
        self.assertEqual([r['chunk_id'] for r in context.evidence], ['chunk-1', 'chunk-2'])
        self.assertEqual([r['source_id'] for r in context.evidence], ['S1', 'S2'])
        self.assertEqual(context.sources['S1']['retrieved_position'], 2)
        self.assertEqual(context.skipped[0]['included_text_tokens'], 0)
        self.assertTrue(all(not r['truncated'] and r['original_text_tokens'] == r['included_text_tokens'] for r in context.evidence))

    def test_empty_evidence_and_insufficient_budget(self):
        for records, budget in (([], 100), ([record()], 0)):
            context = self.build(records, budget)
            self.assertEqual(context.status, 'insufficient_context')
            self.assertEqual(context.evidence, [])
            self.assertEqual(context.sources, {})
            self.assertEqual(context.text, '')
            self.assertEqual(context.usage['evidence_tokens'], 0)

    def test_bad_budget_metadata_and_conflicting_identity(self):
        for budget in (-1, True, 1.5):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                self.build([record()], budget)
        for margin in (-.1, 1, float('nan'), True):
            with self.subTest(margin=margin), self.assertRaises(ValueError):
                self.build([record()], margin=margin)
        bad = record(); bad['metadata']['page_end'] = 1
        with self.assertRaisesRegex(ValueError, 'page range'):
            self.build([bad])
        bad = record(); bad['chunk_id'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.build([bad])

    def test_deterministic_format_and_contiguous_label_validation(self):
        a, b = self.build([record(), record(1)]), self.build([record(), record(1)])
        self.assertEqual(a, b)
        self.assertEqual(e.format_sources(a.evidence), a.text)
        a.evidence[1]['source_id'] = 'S01'
        with self.assertRaisesRegex(ValueError, 'source IDs'):
            e.format_sources(a.evidence)

    def test_citation_ids_canonical_and_membership_only(self):
        self.assertEqual(e.citation_errors('An unsupported claim [S1]. Another [S1].', ['S1']), [])
        for reference in ('[S01]', '[S001]', '[S999]', '[S0]', '[S 1]', '[s1]', '[S1', 'S1]', '[S1, S2]', '[[S1]]', '[S١]'):
            with self.subTest(reference=reference):
                self.assertTrue(e.citation_errors(reference, ['S1']))
        self.assertIsNotNone(rag.citation_problem('Uncited claim', 1))
        self.assertIsNone(rag.citation_problem(rag.INSUFFICIENT_EVIDENCE_MESSAGE, 0, response_state='INSUFFICIENT_EVIDENCE'))
        self.assertIsNotNone(rag.citation_problem(rag.INSUFFICIENT_EVIDENCE_MESSAGE + ' Claim', 1))

    def test_history_ids_removed_without_mutating_session_messages(self):
        messages = [{'role': 'assistant', 'content': 'Old answer [S1] [S01] S9].'},
                    {'role': 'user', 'content': 'Explain the old [S2] citation.'}]
        original = deepcopy(messages)
        history = rag.format_history(messages)
        self.assertNotIn('[S1]', history)
        self.assertNotIn('[S2]', history)
        self.assertNotIn('[S01]', history)
        self.assertIn('historical source reference removed', history)
        self.assertEqual(messages, original)


class GenerationContextTests(unittest.TestCase):
    def setUp(self):
        self.configuration = config.VercelProviderConfig('verified-test/chat', 'fake-key')
        self.client = Mock()
        self.client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"state":"ANSWERED","answer":"Evidence answer [S1]."}'))])
        self.patches = [patch.object(rag, 'vercel_generation_config', return_value=self.configuration),
                        patch.object(rag, 'vercel_client', return_value=self.client),
                        patch.object(rag, 'evidence_budget_config', return_value=(12000, .1))]
        for p in self.patches:
            p.start(); self.addCleanup(p.stop)

    def test_selected_context_exactly_sent_and_returned_mapping(self):
        small = e.build_evidence_context([record(1)], safety_margin=0)
        answer, selected = rag.generate_grounded_answer('Question', [record(0, text='long ' * 3000), record(1)],
                                                       self.configuration.model, context_token_budget=small.usage['evidence_tokens'], safety_margin=0,
                                                       conversation_history=[{'role': 'assistant', 'content': 'Old [S1].'}])
        self.assertEqual(answer, 'Evidence answer [S1].')
        self.assertEqual(selected[0]['chunk_id'], 'chunk-1')
        self.assertEqual(selected[0]['source_id'], 'S1')
        prompt = self.client.chat.completions.create.call_args.kwargs['messages']
        self.assertTrue(prompt[1]['content'].endswith(small.text))
        self.assertIn('historical source reference removed', prompt[1]['content'])
        self.assertIn('Never present dissenting reasoning', prompt[0]['content'])

    def test_insufficient_context_never_constructs_provider_client(self):
        with patch.object(rag, 'vercel_client') as factory:
            answer, evidence = rag.generate_grounded_answer('Question', [record()], self.configuration.model, context_token_budget=0)
        self.assertEqual(answer, rag.INSUFFICIENT_EVIDENCE_MESSAGE)
        self.assertEqual(evidence, [])
        factory.assert_not_called()

    def test_prepared_context_tampering_rejected(self):
        context = e.build_evidence_context([record()])
        context.evidence[0]['text'] = 'Changed after selection'
        with self.assertRaisesRegex(ValueError, 'inconsistent'):
            rag.generate_grounded_answer_from_evidence('Question', context, self.configuration.model)
        self.client.chat.completions.create.assert_not_called()

    def test_legacy_source_mapping_cannot_silently_change_after_skips(self):
        evidence = rag.attach_source_ids([record(0, text='long ' * 3000), record(1)])
        count = e.build_evidence_context([record(1)], safety_margin=0).usage['evidence_tokens']
        with self.assertRaisesRegex(ValueError, 'changes source IDs'):
            rag.generate_grounded_answer_from_evidence('Question', evidence, self.configuration.model,
                                                       context_token_budget=count, safety_margin=0)
        self.client.chat.completions.create.assert_not_called()

    def test_noncanonical_answer_fails_without_correction(self):
        self.client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"state":"ANSWERED","answer":"Bad [S01]"}'))])
        answer = rag.generate_grounded_answer_from_evidence('Question', rag.attach_source_ids([record()]), self.configuration.model)
        self.assertEqual(answer.response_state, 'VALIDATION_FAILED')
        self.assertNotIn('Bad [S01]', answer)
        self.assertEqual(self.client.chat.completions.create.call_count, 1)

    def test_empty_generation_question_fails_before_provider(self):
        with self.assertRaisesRegex(ValueError, 'non-empty generation question'):
            rag.generate_grounded_answer_from_evidence(' ', rag.attach_source_ids([record()]), self.configuration.model)
        self.client.chat.completions.create.assert_not_called()

    def test_budget_settings_are_configurable_independently_of_model(self):
        settings = {'COURTLENS_EVIDENCE_TOKEN_BUDGET': '6000', 'COURTLENS_EVIDENCE_SAFETY_MARGIN': '0.2'}
        with patch.object(config, 'get_runtime_setting', side_effect=lambda name: settings.get(name, '')):
            self.assertEqual(config.evidence_budget_config(), (6000, .2))
        with patch.object(config, 'get_runtime_setting', return_value=''):
            self.assertEqual(config.evidence_budget_config(), (12000, .1))

    def test_invalid_configuration_fails_clearly(self):
        with patch.object(config, 'get_runtime_setting', side_effect=lambda name: 'nonsense' if 'TOKEN_BUDGET' in name else ''):
            with self.assertRaisesRegex(RuntimeError, 'Evidence budget'):
                config.evidence_budget_config()


if __name__ == '__main__':
    unittest.main()
