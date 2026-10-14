"""Offline harness invariants and synthetic scoring fixtures; no gold-aware candidate."""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import citation_verifier_evaluation as e


WHO={'id':'fixture','name':'Fixture','version':'1'}


def row(i,gold,predicted=None,status='VALID_PREDICTION'):
    result=e.VerificationResult(predicted,'Fixture','1') if status=='VALID_PREDICTION' else e.failure_result(status,WHO)
    return {'example_id':str(i),'gold_label':gold,'result':asdict(result)}


class MetricTests(unittest.TestCase):
    def test_perfect_synthetic_predictions(self):
        metrics=e.score_predictions([row(i,label,label) for i,label in enumerate(e.LABELS)])
        self.assertEqual(metrics['accuracy'],1);self.assertEqual(metrics['macro_f1'],1)
        self.assertEqual(metrics['false_support_rate'],0);self.assertEqual(metrics['prediction_coverage'],1)
        self.assertEqual(metrics['supported_class_precision'],1);self.assertEqual(metrics['supported_class_recall'],1)
        for label in e.LABELS:self.assertEqual(metrics['confusion_matrix']['counts'][label][label],1)

    def test_confusion_matrix_precision_recall_f1_and_fsr(self):
        rows=[row(0,'SUPPORTED','SUPPORTED'),row(1,'SUPPORTED','UNSUPPORTED'),
              row(2,'PARTIALLY_SUPPORTED','SUPPORTED'),row(3,'UNSUPPORTED','UNSUPPORTED'),row(4,'CONTRADICTED','CONTRADICTED')]
        m=e.score_predictions(rows)
        self.assertAlmostEqual(m['accuracy'],3/5)
        self.assertAlmostEqual(m['supported_class_precision'],.5);self.assertAlmostEqual(m['supported_class_recall'],.5)
        self.assertAlmostEqual(m['per_class']['UNSUPPORTED']['precision'],.5)
        self.assertAlmostEqual(m['per_class']['UNSUPPORTED']['recall'],1)
        self.assertAlmostEqual(m['macro_f1'],(.5+0+2/3+1)/4)
        self.assertAlmostEqual(m['false_support_rate'],1/3)
        self.assertEqual(m['confusion_matrix']['counts']['SUPPORTED']['UNSUPPORTED'],1)

    def test_all_supported_does_not_get_high_precision(self):
        m=e.score_predictions([row(i,g,'SUPPORTED') for i,g in enumerate(e.LABELS)])
        self.assertEqual(m['accuracy'],.25);self.assertEqual(m['false_support_rate'],1)
        self.assertEqual(m['supported_class_precision'],.25);self.assertEqual(m['supported_class_recall'],1)
        self.assertAlmostEqual(m['macro_f1'],.1)

    def test_all_unsupported_low_macro_f1_despite_zero_fsr(self):
        m=e.score_predictions([row(i,g,'UNSUPPORTED') for i,g in enumerate(e.LABELS)])
        self.assertEqual(m['accuracy'],.25);self.assertEqual(m['false_support_rate'],0)
        self.assertEqual(m['supported_class_precision'],0);self.assertEqual(m['supported_class_recall'],0)
        self.assertAlmostEqual(m['macro_f1'],.1)

    def test_zero_coverage_is_not_success(self):
        m=e.score_predictions([row(i,g,status='MISSING_PREDICTION') for i,g in enumerate(e.LABELS)])
        self.assertEqual(m['prediction_coverage'],0)
        for key in ('accuracy','macro_f1','false_support_rate','supported_class_precision','supported_class_recall'):self.assertIsNone(m[key])
        self.assertEqual(m['failure_counts']['MISSING_PREDICTION'],4)

    def test_failures_excluded_from_confusion_and_fsr_denominator(self):
        rows=[row(0,'UNSUPPORTED','SUPPORTED'),row(1,'CONTRADICTED',status='PROVIDER_ERROR'),row(2,'SUPPORTED','SUPPORTED')]
        m=e.score_predictions(rows)
        self.assertEqual(m['prediction_coverage'],2/3);self.assertEqual(m['accuracy'],.5)
        self.assertEqual(m['false_support_rate'],1);self.assertEqual(m['false_support_denominator_valid'],1)
        self.assertEqual(m['non_supported_gold_count_all'],2);self.assertEqual(m['failure_counts']['PROVIDER_ERROR'],1)

    def test_no_non_supported_valid_gold_has_undefined_fsr(self):
        self.assertIsNone(e.score_predictions([row(1,'SUPPORTED','SUPPORTED')])['false_support_rate'])

    def test_invalid_labels_duplicates_and_failed_predictions_cannot_be_scored(self):
        for rows in [[row(1,'SUPPORTED','INVALID')],[row(1,'SUPPORTED','SUPPORTED'),row(1,'SUPPORTED','SUPPORTED')]]:
            with self.assertRaises(ValueError):e.score_predictions(rows)
        r=row(1,'SUPPORTED',status='TIMEOUT');r['result']['predicted_label']='UNSUPPORTED'
        with self.assertRaises(ValueError):e.score_predictions([r])


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.benchmark=e.load_benchmark()

    def test_loader_hash_counts_version_and_distribution(self):
        b=self.benchmark;self.assertEqual(b['benchmark_version'],'1.0')
        self.assertEqual(len(b['claim_examples']),32);self.assertEqual(len(b['answer_examples']),6)
        self.assertEqual(Counter(r['gold_support_label'] for r in b['claim_examples']),{'SUPPORTED':10,'PARTIALLY_SUPPORTED':7,'UNSUPPORTED':7,'CONTRADICTED':8})
        self.assertEqual(e.sha((e.ROOT/e.BENCHMARK).read_bytes()),e.BENCHMARK_SHA256)

    def test_missing_and_modified_benchmark_fail_before_loading(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaisesRegex(ValueError,'missing'):e.load_benchmark(root)
            p=root/e.BENCHMARK;p.parent.mkdir(parents=True);p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'SHA-256'):e.load_benchmark(root)

    def test_claim_answer_separation_input_isolation_and_no_mutation(self):
        baseline=e.LexicalOverlapBaseline();before=e.serialize(self.benchmark);seen=[]
        class Spy(e.LexicalOverlapBaseline):
            def verify(self,claim,evidence,citation_metadata):
                seen.append((claim,evidence,deepcopy(citation_metadata)))
                citation_metadata['pdf_page_range'][0]=999
                return super().verify(claim,evidence,{})
        run=e.build_run(Spy(),self.benchmark,'2026-10-12T00:00:00+00:00')
        self.assertEqual(len(seen),32);self.assertEqual(run['execution']['answer_examples_excluded'],6)
        for example,(claim,evidence,metadata) in zip(self.benchmark['claim_examples'],seen):
            self.assertEqual(claim,example['claim']);self.assertEqual(evidence,example['cited_evidence_text'])
            self.assertEqual(set(metadata),{'citation_identifier','case_name','opinion_type','author','pdf_page_range','source_file','attribution_is_raw'})
            for forbidden in ('example_id','gold_support_label','example_kind','coverage_categories','justification','component_adjudication','source_question'):self.assertNotIn(forbidden,metadata)
        self.assertEqual(before,e.serialize(self.benchmark))
        self.assertNotEqual(run['predictions'][0]['input']['citation_metadata']['pdf_page_range'][0],999)

    def test_baseline_fixed_thresholds_metadata_independence_and_tokenization(self):
        b=e.LexicalOverlapBaseline()
        self.assertEqual(b.verify('a b c d e','a b c d',{}).predicted_label,'SUPPORTED')
        self.assertEqual(b.verify('a b c d','a b',{}).predicted_label,'PARTIALLY_SUPPORTED')
        self.assertEqual(b.verify('a b c d','a',{}).predicted_label,'UNSUPPORTED')
        self.assertEqual(b.verify('ＡＢＣ','abc',{}).predicted_label,'SUPPORTED')
        self.assertEqual(b.verify('a b','a b',{}),b.verify('a b','a b',{'opinion_type':'dissent','author':'Anything'}))

    def test_all_execution_failure_categories_no_retries_and_safe_errors(self):
        who=e.identity(e.LexicalOverlapBaseline());payload=e.verifier_input(self.benchmark['claim_examples'][0])
        cases=[('INVALID_LABEL',e.VerificationResult('bad',who['name'],who['version'])),
               ('INVALID_RESPONSE_SCHEMA',{}),('MISSING_PREDICTION',None),
               ('TIMEOUT',TimeoutError('private body')),('PROVIDER_ERROR',e.ProviderFailure('private body')),
               ('EXECUTION_FAILURE',RuntimeError('private body'))]
        for expected,value in cases:
            class Fake(e.LexicalOverlapBaseline):
                calls=0
                def verify(self,**kw):
                    self.calls+=1
                    if isinstance(value,Exception):raise value
                    return value
            fake=Fake();result=e.execute(fake,payload,who)
            self.assertEqual(result.execution_status,expected);self.assertEqual(fake.calls,1)
            self.assertIsNone(result.predicted_label);self.assertNotIn('private body',e.serialize(asdict(result)))

    def test_optional_accounting_validation(self):
        who=e.identity(e.LexicalOverlapBaseline())
        valid=e.VerificationResult('SUPPORTED',who['name'],who['version'],latency_seconds=.1,token_usage={'input':3,'output':2},cost_usd=.001)
        self.assertIsNone(e.result_problem(valid,who))
        for kwargs in ({'latency_seconds':-1},{'cost_usd':float('nan')},{'token_usage':{'input':True}}):
            self.assertEqual(e.result_problem(e.VerificationResult('SUPPORTED',who['name'],who['version'],**kwargs),who),'INVALID_RESPONSE_SCHEMA')

    def test_credentials_rejected(self):
        with self.assertRaises(ValueError):e.reject_credentials({'api_key':'not-to-be-stored'})
        with self.assertRaises(ValueError):e.reject_credentials({'nested':{'headers':{}}})

    def test_timestamp_does_not_change_metrics_deterministic_serialization(self):
        b=e.LexicalOverlapBaseline();a=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        same=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        later=e.build_run(b,self.benchmark,'2026-10-13T00:00:00+00:00')
        self.assertEqual(e.serialize(a),e.serialize(same));self.assertEqual(a['metrics'],later['metrics'])

    def test_output_is_new_only_with_replay_and_manifests(self):
        b=e.LexicalOverlapBaseline();run=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'run';e.write_run(run,b.configuration,output)
            self.assertEqual({p.name for p in output.iterdir()},{'results.json','configuration.json','predictions.json','report.md','manifest.json'})
            manifest=json.loads((output/'manifest.json').read_text())
            for name,h in manifest['files_sha256'].items():self.assertEqual(e.sha((output/name).read_bytes()),h)
            with self.assertRaises(FileExistsError):e.write_run(run,b.configuration,output)

    def test_replay_roundtrip_alignment_and_failures(self):
        b=e.LexicalOverlapBaseline();run=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        document=e.replay_document(run,b.configuration)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'predictions.json';path.write_text(e.serialize(document))
            who,predictions=e.load_replay(path,self.benchmark,b.verifier_id,b.version)
            replay=e.build_run(who,self.benchmark,'2026-10-12T00:00:00+00:00',predictions)
            self.assertEqual(run['metrics'],replay['metrics'])
            changed=deepcopy(document);changed['predictions'][0]['result']=asdict(e.failure_result('PROVIDER_ERROR',run['verifier']))
            path.write_text(e.serialize(changed));who,predictions=e.load_replay(path,self.benchmark,b.verifier_id,b.version)
            replay=e.build_run(who,self.benchmark,'2026-10-12T00:00:00+00:00',predictions)
            self.assertEqual(replay['metrics']['valid_predictions'],31)
            self.assertEqual(replay['metrics']['failure_counts']['PROVIDER_ERROR'],1)

    def test_replay_rejects_invalid_missing_duplicate_unknown_and_wrong_identity(self):
        b=e.LexicalOverlapBaseline();run=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        original=e.replay_document(run,b.configuration)
        mutations=[lambda d:d['predictions'].pop(),lambda d:d['predictions'].append(deepcopy(d['predictions'][0])),
                   lambda d:d['predictions'][0].update(example_id='AR-001'),
                   lambda d:d['predictions'][0]['result'].update(predicted_label='INVALID'),
                   lambda d:d.update(benchmark_sha256='fake'),lambda d:d['verifier'].update(id='wrong'),
                   lambda d:d['predictions'][0]['result'].update(verifier_version='wrong'),
                   lambda d:d['predictions'][0]['result'].update(execution_status='TIMEOUT')]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'predictions.json'
            for mutate in mutations:
                changed=deepcopy(original);mutate(changed);path.write_text(e.serialize(changed))
                with self.assertRaises(ValueError):e.load_replay(path,self.benchmark,b.verifier_id,b.version)

    def test_mutated_benchmark_and_partial_precomputed_map_rejected(self):
        b=e.LexicalOverlapBaseline();benchmark=deepcopy(self.benchmark)
        benchmark['claim_examples'][0]['gold_support_label']='CONTRADICTED'
        with self.assertRaises(ValueError):e.build_run(b,benchmark,'2026-10-12T00:00:00+00:00')
        with self.assertRaises(ValueError):e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00',{})

    def test_optional_replay_fields_and_malformed_top_schema(self):
        b=e.LexicalOverlapBaseline();run=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        document=e.replay_document(run,b.configuration)
        for r in document['predictions']:
            for key in ('rationale','error','latency_seconds','token_usage','cost_usd'):r['result'].pop(key)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'predictions.json';path.write_text(e.serialize(document))
            who,predictions=e.load_replay(path,self.benchmark,b.verifier_id,b.version)
            self.assertEqual(len(predictions),32)
            path.write_text('[]')
            with self.assertRaises(ValueError):e.load_replay(path,self.benchmark,b.verifier_id,b.version)
            document['predictions']={};path.write_text(e.serialize(document))
            with self.assertRaises(ValueError):e.load_replay(path,self.benchmark,b.verifier_id,b.version)

    def test_configuration_change_rejected_before_output_write(self):
        b=e.LexicalOverlapBaseline();run=e.build_run(b,self.benchmark,'2026-10-12T00:00:00+00:00')
        changed=deepcopy(b.configuration);changed['supported_threshold']=.1
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'run'
            with self.assertRaises(ValueError):e.write_run(run,changed,output)
            self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
