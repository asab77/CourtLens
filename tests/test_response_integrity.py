"""Phase 7B.1 deterministic contract/generation regressions; no paid calls."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import rag
import assistant_integration as integration
import gateway_config as config
from evidence_context import build_evidence_context
from response_contract import (parse_response, ResponseText, ANSWERED,
                               INSUFFICIENT_EVIDENCE, VALIDATION_FAILED,
                               INSUFFICIENT_EVIDENCE_MESSAGE)
from test_evidence_context import record


def envelope(state, answer=''):
    return json.dumps({'state': state, 'answer': answer})


class ContractTests(unittest.TestCase):
    def test_dobbs_abstention_needs_no_citation(self):
        result = parse_response(envelope(INSUFFICIENT_EVIDENCE), ['S1', 'S2', 'S3'])
        self.assertEqual(result.response_state, INSUFFICIENT_EVIDENCE)
        self.assertEqual(result, INSUFFICIENT_EVIDENCE_MESSAGE)
        self.assertIsNone(rag.citation_problem(result, 3))

    def test_unsafe_abstention_citations_and_claims_fail_closed(self):
        for text in ['Insufficient evidence [S1]-[S3].', 'Insufficient evidence. Dobbs held X.', INSUFFICIENT_EVIDENCE_MESSAGE]:
            result = parse_response(envelope(INSUFFICIENT_EVIDENCE, text), ['S1','S2','S3'])
            self.assertEqual(result.response_state, VALIDATION_FAILED)
            self.assertNotEqual(result, text)

    def test_invalid_identifiers_never_repaired(self):
        for ref in ['[S01]', '[S999]', '[S2]', '[S 1]', '[s1]', '[S1', 'S1]', '[[S1]]', '[S1, S2]']:
            with self.subTest(ref=ref):
                result = parse_response(envelope(ANSWERED, 'Claim '+ref), ['S1'])
                self.assertEqual(result.response_state, VALIDATION_FAILED)
                self.assertTrue(result.validation_errors)
                self.assertNotIn('Claim', result)

    def test_phrase_presence_does_not_establish_abstention(self):
        result = parse_response(envelope(ANSWERED, INSUFFICIENT_EVIDENCE_MESSAGE+' Claim [S1].'), ['S1'])
        self.assertEqual(result.response_state, ANSWERED)  # No semantic classification.
        self.assertEqual(parse_response(INSUFFICIENT_EVIDENCE_MESSAGE, ['S1']).response_state, VALIDATION_FAILED)

    def test_envelope_strictness(self):
        for raw in ['[]','null','{"state":"UNKNOWN","answer":""}', '{"state":"ANSWERED","answer":3}',
                    '{"state":"ANSWERED","answer":""}', '{"state":"ANSWERED","answer":"Claim [S1]","extra":1}',
                    '{"state":"ANSWERED","state":"INSUFFICIENT_EVIDENCE","answer":""}',
                    '```json\n'+envelope(INSUFFICIENT_EVIDENCE)+'\n```']:
            with self.subTest(raw=raw):
                self.assertEqual(parse_response(raw, ['S1']).response_state, VALIDATION_FAILED)
        self.assertEqual(parse_response(envelope(VALIDATION_FAILED), ['S1']).response_state, VALIDATION_FAILED)

    def test_miranda_and_obergefell_valid_ids_are_not_semantic_verification(self):
        saved=json.loads((config.PROJECT_DIR/'data/analysis/phase7a3_smoke_test.json').read_text())
        for case in saved['cases'][:2]:
            answer=case['result']['content']
            result=parse_response(envelope(ANSWERED,answer),case['result']['source_mapping'])
            self.assertEqual(result.response_state,ANSWERED)
            self.assertEqual(result,answer)
            # These exact answers have manually documented support/completeness
            # weaknesses. An ID validator intentionally does not detect them.
            self.assertIn('Limitation' if case['id']=='B' else 'qualification',case['manual_grounding'])



class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.configuration = config.VercelProviderConfig('verified-test/chat','fake-key')
        self.patches = [patch.object(rag,'vercel_generation_config',return_value=self.configuration),
                        patch.object(rag,'vercel_client',return_value=self.client),
                        patch.object(rag,'evidence_budget_config',return_value=(12000,.1))]
        for p in self.patches: p.start();self.addCleanup(p.stop)

    def generate(self, raw, records=None, history=None):
        self.client.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=raw))])
        context=build_evidence_context([record()] if records is None else records)
        return rag.generate_grounded_answer_from_evidence('Dobbs question',context,self.configuration.model,history)

    def test_dobbs_draft_and_unsafe_correction_replay(self):
        saved=json.loads((config.PROJECT_DIR/'data/analysis/phase7a3_smoke_test.json').read_text())
        calls=[r for r in saved['requests'] if r['kind']=='generation' and r['case_id']=='C']
        self.assertEqual(len(calls),2)
        self.client.chat.completions.create.side_effect=[
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=envelope(INSUFFICIENT_EVIDENCE)))]),
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=calls[1]['answer']))])]
        result=self.generate('unused')
        self.assertEqual(result.response_state,INSUFFICIENT_EVIDENCE)
        self.assertEqual(self.client.chat.completions.create.call_count,1)
        self.assertNotIn('[S',result)

    def test_old_unstructured_dobbs_draft_is_not_repaired(self):
        saved=json.loads((config.PROJECT_DIR/'data/analysis/phase7a3_smoke_test.json').read_text())
        draft=next(r['answer'] for r in saved['requests'] if r['kind']=='generation' and r['case_id']=='C')
        result=self.generate(draft)
        self.assertEqual(result.response_state,VALIDATION_FAILED)
        self.assertEqual(result.raw_draft,draft)
        self.assertEqual(self.client.chat.completions.create.call_count,1)

    def test_unknown_id_failure_preserves_diagnostic_without_retry(self):
        raw=envelope(ANSWERED,'Claim [S999]')
        result=self.generate(raw)
        self.assertEqual(result.response_state,VALIDATION_FAILED)
        self.assertEqual(result.raw_draft,raw)
        self.assertNotIn('Claim',result)
        self.assertEqual(self.client.chat.completions.create.call_count,1)

    def test_empty_evidence_returns_explicit_abstention_without_client(self):
        result=self.generate('unused',records=[])
        self.assertEqual(result.response_state,INSUFFICIENT_EVIDENCE)
        self.client.chat.completions.create.assert_not_called()
        rag.vercel_client.assert_not_called()

    def test_history_ids_cannot_authorize_current_unknown_id(self):
        result=self.generate(envelope(ANSWERED,'Claim [S2]'), history=[{'role':'assistant','content':'Old [S2].'}])
        self.assertEqual(result.response_state,VALIDATION_FAILED)
        messages=self.client.chat.completions.create.call_args.kwargs['messages']
        self.assertNotIn('Old [S2]',messages[1]['content'])
        self.assertIn('historical source reference removed',messages[1]['content'])

    def test_current_s1_collision_maps_to_current_turn_not_history(self):
        current=record(5,'majority','Current Author')
        result=self.generate(envelope(ANSWERED,'Current claim [S1]'),[current],[{'role':'assistant','content':'Old claim [S1].'}])
        self.assertEqual(result.response_state,ANSWERED)
        messages=self.client.chat.completions.create.call_args.kwargs['messages']
        self.assertIn('Chunk ID: chunk-5',messages[1]['content'])
        self.assertNotIn('Old claim [S1]',messages[1]['content'])

    def test_mixed_opinions_and_exact_context_preserved(self):
        records=[record(0,'majority','Warren'),record(1,'dissent','Roberts')]
        result=self.generate(envelope(ANSWERED,'Majority claim [S1]. Dissent [S2].'),records)
        self.assertEqual(result.response_state,ANSWERED)
        request=self.client.chat.completions.create.call_args.kwargs
        self.assertTrue(request['messages'][1]['content'].endswith(build_evidence_context(records).text))
        self.assertNotIn('response_format',request)
        self.assertIn('Never present dissenting reasoning',request['messages'][0]['content'])

    def test_empty_model_output_is_validation_failure_without_retry(self):
        result=self.generate('')
        self.assertEqual(result.response_state,VALIDATION_FAILED)
        self.assertEqual(self.client.chat.completions.create.call_count,1)

    def test_public_string_and_tuple_shapes_retained(self):
        self.generate(envelope(ANSWERED,'Claim [S1].'))
        answer,evidence=rag.generate_grounded_answer('Question',[record()],self.configuration.model)
        self.assertIsInstance(answer,str)
        self.assertEqual(answer.response_state,ANSWERED)
        self.assertIsInstance(evidence,list)


class IntegrationStateTests(unittest.TestCase):
    def test_states_stored_without_raw_diagnostics_and_context_mapping_retained(self):
        configuration=config.VercelProviderConfig('verified-test/chat','fake-key')
        evidence=[record()]
        with patch.object(integration,'get_gateway_api_key',return_value='fake-key'), \
                patch.object(integration,'get_runtime_setting',side_effect=lambda n: configuration.model if n=='VERCEL_GENERATION_MODEL' else ''), \
                patch.object(integration,'vercel_generation_config',return_value=configuration), \
                patch.object(integration,'retrieve_hybrid',return_value=evidence), \
                patch.object(integration,'evidence_budget_config',return_value=(12000,.1)):
            for raw in [envelope(INSUFFICIENT_EVIDENCE),envelope(ANSWERED,'Claim [S999]'),envelope(ANSWERED,'Claim [S1]')]:
                response=parse_response(raw,['S1'])
                with patch.object(integration,'generate_grounded_answer_from_evidence',return_value=response):
                    result=integration.answer_question('Question',SimpleNamespace(vector_store=()),configuration.model,[])
                self.assertEqual(result['response_state'],response.response_state)
                self.assertIs(type(result['content']),str)
                self.assertNotIn('raw_draft',result)
                self.assertEqual(result['source_mapping']['S1']['chunk_id'],'chunk-0')
                self.assertEqual(result['context_status'],'ready')
                self.assertIn('membership only',result['citation_validation_scope'])

    def test_empty_context_state_does_not_invoke_generation(self):
        configuration=config.VercelProviderConfig('verified-test/chat','fake-key')
        with patch.object(integration,'get_gateway_api_key',return_value='fake-key'), \
                patch.object(integration,'get_runtime_setting',side_effect=lambda n: configuration.model if n=='VERCEL_GENERATION_MODEL' else ''), \
                patch.object(integration,'vercel_generation_config',return_value=configuration), \
                patch.object(integration,'retrieve_hybrid',return_value=[]), \
                patch.object(integration,'evidence_budget_config',return_value=(12000,.1)), \
                patch.object(integration,'generate_grounded_answer_from_evidence') as generate:
            result=integration.answer_question('Question',SimpleNamespace(vector_store=()),configuration.model,[])
        self.assertEqual(result['response_state'],INSUFFICIENT_EVIDENCE)
        self.assertEqual(result['content'],INSUFFICIENT_EVIDENCE_MESSAGE)
        generate.assert_not_called()


if __name__=='__main__':unittest.main()
