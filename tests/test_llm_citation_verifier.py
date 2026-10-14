"""Fake provider clients only. No inference, embeddings or real networking."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import socket
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import httpx
from openai import AuthenticationError

import citation_verifier_evaluation as h
import llm_citation_verifier as v
import run_llm_citation_verifier as r


def fake_response(content='{"label":"SUPPORTED","rationale":"The passage states the claim."}',cost=None):
    usage={'prompt_tokens':100,'completion_tokens':20,'cost':cost}
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content),finish_reason='stop')],
                           usage=SimpleNamespace(model_dump=lambda:usage))


def client(response=None):
    dispatch=Mock(return_value=response or fake_response())
    return SimpleNamespace(max_retries=0,base_url=v.VERCEL_BASE_URL,chat=SimpleNamespace(completions=SimpleNamespace(create=dispatch)))


class LLMVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.benchmark=h.load_benchmark();cls.payload=h.verifier_input(cls.benchmark['claim_examples'][0])

    def verifier(self,provider=None,requests=35,ceiling=.10):
        return v.GPT41MiniCitationVerifier(provider or client(),v.RequestBudget(v.RequestLimits(requests,512,ceiling)),clock=Mock(side_effect=[0.,1.]*100))

    def test_gateway_factory_pins_model_and_disables_retries(self):
        base=Mock();base.with_options.return_value=client()
        with patch.object(v,'require_gateway_api_key',return_value='fake-key'),patch.object(v,'vercel_client',return_value=base) as factory:
            result=v.make_client()
        config=factory.call_args.args[0]
        self.assertEqual(config.model,'openai/gpt-4.1-mini');self.assertEqual(config.base_url,'https://ai-gateway.vercel.sh/v1')
        self.assertNotIn('fake-key',repr(config));base.with_options.assert_called_once_with(max_retries=0,timeout=60)
        self.assertEqual(result.max_retries,0)

    def test_prompt_and_payload_exact_preservation_and_isolation(self):
        messages=v.build_messages(**self.payload);self.assertEqual(json.loads(messages[1]['content']),self.payload)
        for word in ('compound claims','independently meaningful','quotation','endorsement','exceptions','untrusted','outside legal knowledge'):
            self.assertIn(word,v.SYSTEM_PROMPT)
        self.assertEqual(v.PROMPT_SHA256,h.sha(v.SYSTEM_PROMPT.encode()))
        bad=deepcopy(self.payload);bad['citation_metadata']['gold_support_label']='SUPPORTED'
        with self.assertRaises(ValueError):v.build_messages(**bad)
        self.assertNotIn('example_id',json.loads(messages[1]['content']))

    def test_mixed_opinions_and_unknown_author_preserved(self):
        for example in self.benchmark['claim_examples']:
            payload=h.verifier_input(example);parsed=json.loads(v.build_messages(**payload)[1]['content'])
            self.assertEqual(parsed['evidence'],example['cited_evidence_text'])
            self.assertEqual(parsed['citation_metadata']['opinion_type'],example['opinion_type'])
            self.assertEqual(parsed['citation_metadata']['author'],example['author'])

    def test_all_four_labels_and_strict_json(self):
        for label in h.LABELS:
            result=v.parse_output(json.dumps({'label':label,'rationale':'Evidence reason'}));self.assertEqual(result.predicted_label,label)
        invalid=['not json','[]','{"label":"SUPPORTED"}','{"label":1,"rationale":"reason"}',
                 '{"label":"SUPPORTED","rationale":""}','{"label":"SUPPORTED","rationale":"  "}',
                 '{"label":"SUPPORTED","rationale":"reason","extra":1}',
                 '{"label":"SUPPORTED","label":"CONTRADICTED","rationale":"reason"}',
                 '```json\n{"label":"SUPPORTED","rationale":"reason"}\n```']
        for text in invalid:self.assertEqual(v.parse_output(text).execution_status,'INVALID_RESPONSE_SCHEMA')
        self.assertEqual(v.parse_output('{"label":"WRONG","rationale":"reason"}').execution_status,'INVALID_LABEL')

    def test_fixed_parameters_output_limit_and_usage(self):
        provider=client();verifier=self.verifier(provider);result=verifier.verify(**self.payload)
        kwargs=provider.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs['model'],v.MODEL);self.assertEqual(kwargs['temperature'],0);self.assertEqual(kwargs['max_tokens'],512)
        self.assertNotIn('response_format',kwargs);self.assertEqual(result.latency_seconds,1.)
        self.assertEqual(result.token_usage,{'input':100,'output':20});self.assertAlmostEqual(result.cost_usd,.000072)
        self.assertIsNone(h.result_problem(result,h.identity(verifier)))

    def test_invalid_response_no_repair_request(self):
        provider=client(fake_response('bad'));verifier=self.verifier(provider);result=verifier.verify(**self.payload)
        self.assertEqual(result.execution_status,'INVALID_RESPONSE_SCHEMA');self.assertEqual(provider.chat.completions.create.call_count,1)
        self.assertIsNotNone(result.token_usage)

    def test_timeouts_provider_and_unexpected_errors_no_retries(self):
        auth=AuthenticationError('private payload',response=httpx.Response(401,request=httpx.Request('POST','https://example.invalid')),body=None)
        for error,status in [(TimeoutError('private'),'TIMEOUT'),(auth,'PROVIDER_ERROR'),(RuntimeError('private'),'EXECUTION_FAILURE')]:
            provider=client();provider.chat.completions.create.side_effect=error
            verifier=self.verifier(provider);result=verifier.verify(**self.payload)
            self.assertEqual(result.execution_status,status);self.assertEqual(provider.chat.completions.create.call_count,1)
            self.assertNotIn('private',h.serialize(asdict(result)))
            self.assertEqual(verifier.budget.records[0]['accounting_method'],'conservative_reservation')

    def test_request_count_enforcement_before_dispatch(self):
        provider=client();verifier=self.verifier(provider,requests=1)
        verifier.verify(**self.payload)
        with self.assertRaises(v.RequestLimitReached):verifier.verify(**self.payload)
        self.assertEqual(provider.chat.completions.create.call_count,1)

    def test_cost_ceiling_prevents_dispatch(self):
        provider=client();verifier=self.verifier(provider,ceiling=.000001)
        with self.assertRaises(v.RequestLimitReached):verifier.verify(**self.payload)
        provider.chat.completions.create.assert_not_called()

    def test_reported_cost_reconciles_and_stops_after_overspend(self):
        provider=client(fake_response(cost=.20));verifier=self.verifier(provider)
        result=verifier.verify(**self.payload);self.assertEqual(result.cost_usd,.20);self.assertTrue(verifier.budget.stopped)
        with self.assertRaises(v.RequestLimitReached):verifier.verify(**self.payload)
        self.assertEqual(provider.chat.completions.create.call_count,1)

    def test_complete_input_budget_rejection_no_truncation(self):
        provider=client();verifier=self.verifier(provider);payload=deepcopy(self.payload);payload['evidence']='long evidence '*10000
        with self.assertRaises(v.RequestLimitReached):verifier.verify(**payload)
        provider.chat.completions.create.assert_not_called()

    def test_bad_caps_and_retry_enabled_clients_rejected(self):
        for args in [(36,512,.1),(35,513,.1),(0,512,.1),(35,512,0)]:
            with self.assertRaises(ValueError):v.RequestLimits(*args)
        provider=client();provider.max_retries=2
        with self.assertRaises(ValueError):self.verifier(provider)

    def test_dry_run_no_network_no_credentials_and_immutability(self):
        before=h.serialize(self.benchmark)
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(r,'make_client',side_effect=AssertionError('No client in dry run')):
            report=r.dry_run(self.benchmark,v.RequestLimits(35,512,.10))
        self.assertEqual(report['provider_requests_made'],0);self.assertEqual(len(report['inputs']),32)
        self.assertFalse(report['blockers']);self.assertFalse(report['evidence_truncated'])
        self.assertEqual(before,h.serialize(self.benchmark));self.assertLess(report['max_reserved_input_tokens'],8192)
        self.assertEqual(report,r.dry_run(self.benchmark,v.RequestLimits(35,512,.10)))
        blocked=r.dry_run(self.benchmark,v.RequestLimits(1,512,.0001));self.assertTrue(blocked['blockers'])

    def test_prepare_refuses_overwrite_and_saves_prompt(self):
        report=r.dry_run(self.benchmark,v.RequestLimits(35,512,.10))
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'prepared';r.prepare(report,output)
            self.assertEqual((output/'system_prompt.txt').read_text(),v.SYSTEM_PROMPT)
            with self.assertRaises(FileExistsError):r.prepare(report,output)

    def test_harness_compatibility_deterministic_fake_run_and_stop(self):
        provider=client();verifier=self.verifier(provider);run=h.build_run(verifier,self.benchmark,'2026-10-13T00:00:00+00:00')
        self.assertEqual(run['metrics']['prediction_coverage'],1);self.assertEqual(len(run['predictions']),32)
        repeat=h.build_run(self.verifier(),self.benchmark,'2026-10-13T00:00:00+00:00')
        self.assertEqual(h.serialize(run),h.serialize(repeat))
        with tempfile.TemporaryDirectory() as d:
            provider=client();result=r.run_authorized(provider,self.benchmark,v.RequestLimits(1,512,.1),Path(d)/'fake_run','2026-10-13T00:00:00+00:00')
            self.assertEqual(provider.chat.completions.create.call_count,1)
            self.assertEqual(result['metrics']['prediction_coverage'],0)
            self.assertEqual(result['metrics']['failure_counts']['MISSING_PREDICTION'],32)
            self.assertEqual(result['request_accounting']['stop_reason'],'request_or_cost_limit')

    def test_preflight_and_benchmark_caps_are_independent(self):
        budget=v.RequestBudget(v.RequestLimits(35,512,.1))
        for _ in range(3):budget.reserve(1,'preflight')
        for _ in range(32):budget.reserve(1,'benchmark')
        self.assertEqual(len(budget.records),35)
        with self.assertRaises(v.RequestLimitReached):budget.reserve(1,'benchmark')
        budget=v.RequestBudget(v.RequestLimits(35,512,.1))
        for _ in range(3):budget.reserve(1,'preflight')
        with self.assertRaises(v.RequestLimitReached):budget.reserve(1,'preflight')

    def test_durable_ledger_written_before_dispatch_and_blocks_restart(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'fake_run';provider=client();observed=[]
            def dispatch(**kwargs):
                ledger=json.loads((Path(d)/'fake_run_request_ledger.json').read_text())
                observed.append(ledger['records'][-1]['status'])
                raise TimeoutError('private')
            provider.chat.completions.create.side_effect=dispatch
            result=r.run_authorized(provider,self.benchmark,v.RequestLimits(35,512,.1),output,'2026-10-13T00:00:00+00:00')
            self.assertEqual(observed,['dispatching'])
            self.assertEqual(result['request_accounting']['attempted_requests'],1)
            self.assertEqual(result['metrics']['valid_predictions'],0)
            with self.assertRaises(FileExistsError):r.run_authorized(provider,self.benchmark,v.RequestLimits(35,512,.1),output,'2026-10-13T00:00:00+00:00')
            self.assertNotIn('private',(Path(d)/'fake_run_request_ledger.json').read_text())

    def test_provider_output_over_limit_stops_further_requests(self):
        response=fake_response();response.usage=SimpleNamespace(model_dump=lambda:{'prompt_tokens':100,'completion_tokens':513})
        provider=client(response);verifier=self.verifier(provider);result=verifier.verify(**self.payload)
        self.assertEqual(result.execution_status,'INVALID_RESPONSE_SCHEMA');self.assertTrue(verifier.budget.stopped)
        with self.assertRaises(v.RequestLimitReached):verifier.verify(**self.payload)
        self.assertEqual(provider.chat.completions.create.call_count,1)


if __name__=='__main__':unittest.main()
