"""Offline accounting contracts; sockets blocked, provider clients fake."""
from copy import deepcopy
from dataclasses import asdict
from decimal import Decimal
import json
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

import citation_verifier_evaluation as h
import llm_citation_verifier as v
import cumulative_verifier_accounting as c
from test_llm_citation_verifier import client

PREFLIGHT=h.ROOT/'data/analysis/citation_verifiers/gpt41mini_v1/preflight_v1'

class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.network=patch.object(socket.socket,'connect',side_effect=AssertionError('No network'));self.network.start();self.addCleanup(self.network.stop)
        self.dns=patch.object(socket,'getaddrinfo',side_effect=AssertionError('No network'));self.dns.start();self.addCleanup(self.dns.stop)
        self.benchmark=h.load_benchmark();self.prior=c.load_preflight(PREFLIGHT)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.directory=Path(self.temp.name)

    def reserve(self,budget):
        if len(budget.new_records)>=32:return budget.reserve(1,'benchmark')
        example=self.benchmark['claim_examples'][len(budget.new_records)]
        budget.current_example=example['example_id']
        tokens=v.token_estimate(v.build_messages(**h.verifier_input(example)))['reserved_input_tokens']
        return budget.reserve(tokens,'benchmark')

    def test_import_and_dry_run(self):
        report=c.benchmark_dry_run(self.prior,self.benchmark)
        self.assertEqual(report['historical_preflight_requests'],3)
        self.assertEqual(Decimal(report['historical_cost_usd']),Decimal('.000818'))
        self.assertEqual(report['pending_benchmark_examples'],32)
        self.assertEqual(report['total_planned_requests'],35)
        self.assertEqual(report['new_API_requests'],0)
        self.assertEqual(Decimal(report['cumulative_projected_cost_usd']),Decimal('.0476788'))

    def test_benchmark_only_32_and_35_exact_request_boundaries(self):
        provider=client();output=self.directory/'run'
        run=c.run_benchmark_only(provider,self.prior,self.benchmark,output,'2026-10-13T00:00:00+00:00')
        self.assertEqual(provider.chat.completions.create.call_count,32)
        self.assertEqual(run['request_accounting']['combined_requests'],35)
        self.assertEqual(run['request_accounting']['new_benchmark_requests'],32)
        calls=provider.chat.completions.create.call_args_list
        for call,example in zip(calls,self.benchmark['claim_examples']):
            payload=json.loads(call.kwargs['messages'][1]['content'])
            self.assertEqual(payload,h.verifier_input(example))
            self.assertEqual(set(payload),{'claim','evidence','citation_metadata'})
        budget=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
        with self.assertRaises(v.RequestLimitReached):self.reserve(budget)
        with self.assertRaises(FileExistsError):c.run_benchmark_only(provider,self.prior,self.benchmark,output,'2026-10-13T00:00:00+00:00')
        self.assertEqual(provider.chat.completions.create.call_count,32)

    def test_decimal_cost_boundary(self):
        budget=c.CumulativeBudget(self.prior,self.benchmark)
        example=self.benchmark['claim_examples'][0]
        tokens=v.token_estimate(v.build_messages(**h.verifier_input(example)))['reserved_input_tokens']
        reservation=c.cost(tokens,512)
        budget.charged_estimate=Decimal('.10')-reservation
        self.reserve(budget)
        self.assertEqual(budget.charged_estimate,Decimal('.10'))
        with self.assertRaises(v.RequestLimitReached):self.reserve(budget)
        budget=c.CumulativeBudget(self.prior,self.benchmark)
        budget.charged_estimate=Decimal('.10')-reservation+Decimal('.0000000001')
        with self.assertRaises(v.RequestLimitReached):self.reserve(budget)
        self.assertEqual(len(budget.records),3)

    def test_history_is_counted_and_preflight_forbidden(self):
        budget=c.CumulativeBudget(self.prior,self.benchmark)
        self.assertIsInstance(budget.charged_estimate,Decimal)
        self.assertEqual(budget.charged_estimate,Decimal('.000818'))
        with self.assertRaises(ValueError):budget.reserve(1,'preflight')
        for _ in range(32):self.reserve(budget)
        self.assertEqual(len(budget.records),35)
        with self.assertRaises(v.RequestLimitReached):self.reserve(budget)

    def test_missing_prior_fails_closed(self):
        with self.assertRaises(FileNotFoundError):c.load_preflight(self.directory)

    def tamper(self,name,edit,refresh=False):
        directory=self.directory/'prior';shutil.copytree(PREFLIGHT,directory)
        value=json.loads((directory/name).read_text());edit(value)
        (directory/name).write_text(h.serialize(value))
        if refresh:
            manifest=json.loads((directory/'manifest.json').read_text())
            manifest['files_sha256'][name]=h.sha((directory/name).read_bytes())
            (directory/'manifest.json').write_text(h.serialize(manifest))
        return directory

    def test_tampered_ledger(self):
        directory=self.tamper('request_ledger.json',lambda x:x.update(accounted_cost_usd=0))
        with self.assertRaises(ValueError):c.load_preflight(directory)

    def test_duplicate_request_ids_even_with_updated_manifest(self):
        directory=self.tamper('request_ledger.json',lambda x:x['records'][1].update(request_number=1),True)
        with self.assertRaises(ValueError):c.load_preflight(directory)

    def test_mismatched_configuration(self):
        for key,value in [('model','other'),('prompt_sha256','bad'),('benchmark_sha256','bad'),('temperature',1),('sdk_max_retries',1),('automatic_model_fallback',True)]:
            with self.subTest(key=key):
                directory=self.tamper('configuration.json',lambda x:x.update({key:value}),True)
                with self.assertRaises(ValueError):c.load_preflight(directory)
                shutil.rmtree(directory)

    def test_incomplete_or_inconsistent_accounting(self):
        for name,edit in [('request_ledger.json',lambda x:x['records'][0].update(status='dispatching')),('results.json',lambda x:x.update(input_tokens=0)),('predictions.json',lambda x:x[0]['result'].update(cost_usd=0)),('raw_responses.json',lambda x:x[0].update(returned_model='other'))]:
            with self.subTest(name=name):
                directory=self.tamper(name,edit,True)
                with self.assertRaises(ValueError):c.load_preflight(directory)
                shutil.rmtree(directory)

    def test_completed_resume_never_repeats(self):
        output=self.directory/'run';budget=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
        provider=client();verifier=v.GPT41MiniCitationVerifier(provider,budget)
        budget.current_example='CS-001';verifier.request(**h.verifier_input(self.benchmark['claim_examples'][0]),kind='benchmark')
        next_provider=client();run=c.run_benchmark_only(next_provider,self.prior,self.benchmark,output,'2026-10-13T00:00:00+00:00')
        self.assertEqual(next_provider.chat.completions.create.call_count,31)
        first=json.loads(next_provider.chat.completions.create.call_args_list[0].kwargs['messages'][1]['content'])
        self.assertEqual(first,h.verifier_input(self.benchmark['claim_examples'][1]))
        self.assertEqual(run['request_accounting']['combined_requests'],35)

    def test_uncertain_request_not_retried(self):
        output=self.directory/'run';budget=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
        self.reserve(budget)
        provider=client();run=c.run_benchmark_only(provider,self.prior,self.benchmark,output,'2026-10-13T00:00:00+00:00')
        self.assertEqual(provider.chat.completions.create.call_count,31)
        self.assertEqual(run['request_accounting']['uncertain_requests_not_retried'],['CS-001'])
        self.assertEqual(run['predictions'][0]['result']['execution_status'],'EXECUTION_FAILURE')
        c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')

    def test_duplicate_or_out_of_order_reservations(self):
        budget=c.CumulativeBudget(self.prior,self.benchmark)
        self.reserve(budget);budget.current_example='CS-001'
        with self.assertRaises(ValueError):budget.reserve(100,'benchmark')

    def test_journal_tampering_and_partial_write(self):
        directory=self.directory/'journal';budget=c.CumulativeBudget(self.prior,self.benchmark,directory);self.reserve(budget)
        path=directory/'0001.json';envelope=json.loads(path.read_text());envelope['body']['records'][-1]['request_number']=4.5
        envelope['body_sha256']=h.sha(h.serialize(envelope['body']).encode());path.write_text(h.serialize(envelope))
        with self.assertRaises(ValueError):c.CumulativeBudget(self.prior,self.benchmark,directory)
        path.unlink();(directory/'0001.tmp').write_text('partial')
        with self.assertRaises(ValueError):c.CumulativeBudget(self.prior,self.benchmark,directory)

    def test_reservation_durable_before_dispatch(self):
        output=self.directory/'run';budget=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
        provider=client();original=provider.chat.completions.create.return_value
        def dispatch(**kwargs):
            resumed=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
            self.assertEqual(resumed.records[-1]['status'],'dispatching')
            self.assertEqual(len(resumed.records),4)
            return original
        provider.chat.completions.create.side_effect=dispatch
        budget.current_example='CS-001'
        v.GPT41MiniCitationVerifier(provider,budget).request(**h.verifier_input(self.benchmark['claim_examples'][0]),kind='benchmark')
        resumed=c.CumulativeBudget(self.prior,self.benchmark,output/'request_journal')
        self.assertIsNotNone(resumed.records[-1]['result'])

    def test_dry_run_no_client_or_writes(self):
        journal=self.directory/'absent'
        with patch.object(v,'make_client',side_effect=AssertionError('No client')):
            c.benchmark_dry_run(self.prior,self.benchmark,journal)
        self.assertFalse(journal.exists())

    def test_cli_benchmark_only_dry_run_never_constructs_client(self):
        import run_llm_citation_verifier as runner
        argv=['runner','--benchmark-only','--output',str(self.directory/'run'),'--max-requests','35','--max-output-tokens','512','--estimated-cost-ceiling','.10']
        with patch.object(sys,'argv',argv),patch.object(runner,'make_client',side_effect=AssertionError('No client')),patch('builtins.print'):
            runner.main()
        self.assertFalse((self.directory/'run').exists())

    def test_legacy_live_cli_disabled(self):
        import run_llm_citation_verifier as runner
        argv=['runner','--live','--max-requests','35','--max-output-tokens','512','--estimated-cost-ceiling','.10']
        with patch.object(sys,'argv',argv),patch.object(runner,'make_client',side_effect=AssertionError('No client')):
            with self.assertRaises(ValueError):runner.main()

    def test_restart_missing_accounting_fails_closed(self):
        output=self.directory/'run';output.mkdir()
        provider=client()
        with self.assertRaises(ValueError):c.run_benchmark_only(provider,self.prior,self.benchmark,output,'2026-10-13T00:00:00+00:00')
        provider.chat.completions.create.assert_not_called()

if __name__=='__main__':unittest.main()
