"""Offline finalization invariants; no model, embeddings or semantic verifier."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import finalize_citation_support_benchmark as f


class FinalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark=f.load_frozen()
        cls.adjudication=json.loads((f.ROOT/f.ADJUDICATION).read_text())
        cls.candidates=json.loads((f.ROOT/f.CANDIDATES).read_text())

    def test_counts_distribution_and_unique_stable_ids(self):
        self.assertEqual(len(self.benchmark['claim_examples']),32)
        self.assertEqual(len(self.benchmark['answer_examples']),6)
        self.assertEqual(Counter(r['gold_support_label'] for r in self.benchmark['claim_examples']),f.EXPECTED_DISTRIBUTION)
        ids=[r['example_id'] for r in self.benchmark['claim_examples']+self.benchmark['answer_examples']]
        self.assertEqual(len(set(ids)),38)
        self.assertEqual(ids,[r['example_id'] for r in self.candidates['claim_examples']+self.candidates['answer_examples']])

    def test_exact_authorized_revisions_and_remaining_labels(self):
        changed=[]
        for old,new in zip(self.candidates['claim_examples'],self.benchmark['claim_examples']):
            if old['gold_support_label']!=new['gold_support_label']:changed.append(new['example_id'])
        self.assertEqual(changed,['CS-012','CS-031'])
        for row in self.benchmark['claim_examples']:
            if row['example_id'] in changed:self.assertEqual(row['gold_support_label'],'CONTRADICTED')

    def test_compound_aggregation_convention(self):
        self.assertEqual(f.compound_label(['SUPPORTED','SUPPORTED']),'SUPPORTED')
        self.assertEqual(f.compound_label(['SUPPORTED','UNSUPPORTED']),'PARTIALLY_SUPPORTED')
        self.assertEqual(f.compound_label(['SUPPORTED','CONTRADICTED']),'PARTIALLY_SUPPORTED')
        self.assertEqual(f.compound_label(['UNSUPPORTED','CONTRADICTED']),'CONTRADICTED')
        self.assertEqual(f.compound_label(['UNSUPPORTED','UNSUPPORTED']),'UNSUPPORTED')
        for labels in ([],['UNKNOWN'],['PARTIALLY_SUPPORTED']):
            with self.assertRaises(ValueError):f.compound_label(labels)

    def test_five_compounds_record_contradictions_explicitly(self):
        rows=[r for r in self.benchmark['claim_examples'] if r['claim_type']=='compound_probe']
        self.assertEqual([r['example_id'] for r in rows],['CS-011','CS-014','CS-016','CS-017','CS-018'])
        for row in rows:
            self.assertEqual(row['gold_support_label'],'PARTIALLY_SUPPORTED')
            expected_second='CONTRADICTED' if row['example_id'] in ('CS-017','CS-018') else 'UNSUPPORTED'
            self.assertEqual([r['gold_support_label'] for r in row['component_adjudication']],['SUPPORTED',expected_second])
            self.assertTrue(all(r['justification'] for r in row['component_adjudication']))

    def test_answers_preserved_except_ar006_completeness(self):
        for old,new in zip(self.candidates['answer_examples'],self.benchmark['answer_examples']):
            expected=deepcopy(old['response_assessment'])
            if new['example_id']=='AR-006':expected['completeness']='NOT_APPLICABLE'
            self.assertEqual(new['response_assessment'],expected)
            self.assertNotIn('gold_support_label',new)
        self.assertEqual(self.benchmark['schema'],self.candidates['schema'])
        self.assertFalse(self.benchmark['ar006_resolution']['new_status_added'])
        self.assertIn('denominator',self.benchmark['ar006_resolution']['scoring'])

    def test_exact_sources_and_original_candidate_artifacts_unchanged(self):
        for level in ('claim_examples','answer_examples'):
            for old,new in zip(self.candidates[level],self.benchmark[level]):
                for key in (['cited_evidence_text','case_name','opinion_type','author','pdf_page_range'] if level=='claim_examples' else ['answer','context']):
                    self.assertEqual(old[key],new[key])
                self.assertEqual(old['provenance'],new['provenance'])
        for path,expected in self.benchmark['source_artifact_sha256'].items():
            self.assertEqual(f.digest((f.ROOT/path).read_bytes()),expected)
        self.assertEqual(self.candidates['status'],'PROPOSED')
        self.assertFalse(self.candidates['frozen'])

    def test_final_decisions_and_nonexpert_review_disclosure(self):
        self.assertEqual(self.benchmark['status'],'FINALIZED');self.assertTrue(self.benchmark['frozen'])
        self.assertFalse(self.benchmark['independently_human_adjudicated'])
        self.assertFalse(self.adjudication['independent_human_legal_expert_adjudication'])
        for row in self.benchmark['claim_examples']+self.benchmark['answer_examples']:
            self.assertEqual(row['review_status'],'FINALIZED')
            self.assertFalse(row['human_judgment_required'])
        for decision in self.adjudication['decisions']:
            self.assertEqual(decision['review_status'],'FINALIZED')
            self.assertEqual(decision['review_method'],'AI-assisted, user-authorized')
            self.assertIn(decision['decision'],('retained','revised'))
            self.assertTrue(decision['limitations'])

    def test_reproduction_is_deterministic_and_network_free(self):
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
            first=f.produce();second=f.produce()
        self.assertEqual(first,second)
        for name,text in first.items():self.assertEqual((f.ROOT/name).read_bytes(),text.encode())

    def test_checksum_and_canonical_serialization(self):
        raw=(f.ROOT/f.BENCHMARK).read_bytes()
        self.assertEqual(raw,f.encode(self.benchmark).encode())
        self.assertEqual((f.ROOT/f.CHECKSUM).read_text(),f'{f.digest(raw)}  {Path(f.BENCHMARK).name}\n')
        self.assertEqual(self.benchmark['adjudication_provenance']['sha256'],f.digest((f.ROOT/f.ADJUDICATION).read_bytes()))

    def test_corrupted_checksum_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/f.BENCHMARK).parent.mkdir(parents=True)
            (root/f.BENCHMARK).write_bytes((f.ROOT/f.BENCHMARK).read_bytes())
            (root/f.CHECKSUM).write_text('0'*64+'  '+Path(f.BENCHMARK).name+'\n')
            with self.assertRaisesRegex(ValueError,'checksum'):f.load_frozen(root)

    def test_invalid_label_source_decision_and_pending_status_rejected(self):
        for mutation in [lambda b:b['claim_examples'][0].update(gold_support_label='UNSUPPORTED'),
                         lambda b:b['claim_examples'][0].update(cited_evidence_text='Fabricated'),
                         lambda b:b['claim_examples'][0].update(review_status='PROPOSED'),
                         lambda b:b['answer_examples'][-1]['response_assessment'].update(completeness='INCOMPLETE')]:
            benchmark=deepcopy(self.benchmark);mutation(benchmark)
            with self.assertRaises(ValueError):f.validate_final(benchmark,self.adjudication)
        adjudication=deepcopy(self.adjudication);adjudication['decisions'][0]['final_label']='CONTRADICTED'
        with self.assertRaises(ValueError):f.validate_final(self.benchmark,adjudication)

    def test_freeze_requires_successful_prevalidation(self):
        observed=[]
        def reject(benchmark, *args, **kwargs):
            observed.append(benchmark)
            self.assertFalse(benchmark['frozen'])
            raise ValueError('Validation failed')
        with patch.object(f,'validate_final',side_effect=reject):
            with self.assertRaises(ValueError):f.produce()
        self.assertEqual(len(observed),1)
        self.assertFalse(observed[0]['frozen'])
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch.object(f,'ROOT',root),patch.object(f,'produce',side_effect=ValueError('Validation failed')):
                with self.assertRaises(ValueError):f.main()
            self.assertEqual(list(root.rglob('*')),[])


if __name__=='__main__':unittest.main()
