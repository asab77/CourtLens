"""Deterministic dataset integrity tests, not semantic-label adjudication."""
from copy import deepcopy
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

import build_citation_support_candidates as b
from citation_support_dataset import validate_dataset


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.dataset=json.loads((b.ROOT/b.CANDIDATES).read_text())

    def test_unique_ids_counts_status_and_label_vocabularies(self):
        result=validate_dataset(self.dataset)
        self.assertEqual(result['claim_count'],32);self.assertEqual(result['answer_count'],6)
        self.assertEqual(len({r['example_id'] for r in self.dataset['claim_examples']+self.dataset['answer_examples']}),38)
        self.assertEqual({r['gold_support_label'] for r in self.dataset['claim_examples']},set(b.LABELS))
        self.assertFalse(self.dataset['frozen']);self.assertFalse(self.dataset['independently_human_adjudicated'])

    def test_duplicate_ids_and_invalid_labels_rejected(self):
        for mutate in [lambda d:d['claim_examples'][1].update(example_id=d['claim_examples'][0]['example_id']),
                       lambda d:d['claim_examples'][0].update(gold_support_label='CORRECT')]:
            data=deepcopy(self.dataset);mutate(data)
            with self.assertRaises(ValueError):validate_dataset(data)

    def test_required_provenance_and_source_hashes(self):
        data=deepcopy(self.dataset);data['claim_examples'][0].pop('provenance')
        with self.assertRaises(ValueError):validate_dataset(data)
        data=deepcopy(self.dataset);data['claim_examples'][0]['provenance']['records_sha256']='fake'
        with self.assertRaisesRegex(ValueError,'hash'):validate_dataset(data)

    def test_exact_source_text_and_no_fabricated_quotations(self):
        for mutate in [lambda r:r.update(cited_evidence_text='Invented Supreme Court passage'),
                       lambda r:r.update(exact_quotation='Invented quotation')]:
            data=deepcopy(self.dataset);mutate(data['claim_examples'][0])
            with self.assertRaises(ValueError):validate_dataset(data)

    def test_pages_opinion_author_and_chunk_row_integrity(self):
        for field,value in [('pdf_page_range',[1,999]),('opinion_type','dissent'),('author','Invented Author')]:
            data=deepcopy(self.dataset);data['claim_examples'][0][field]=value
            with self.assertRaises(ValueError):validate_dataset(data)
        data=deepcopy(self.dataset);data['claim_examples'][0]['provenance']['vector_id']=999
        with self.assertRaises(ValueError):validate_dataset(data)

    def test_citation_scoped_identity_not_just_syntax(self):
        data=deepcopy(self.dataset);data['claim_examples'][0]['citation_identifier']='S01'
        with self.assertRaises(ValueError):validate_dataset(data)
        data=deepcopy(self.dataset);row=data['claim_examples'][0]
        row['citation_identifier']='S2';row['provenance']['citation_binding']['citation_identifier']='S2'
        with self.assertRaisesRegex(ValueError,'identity'):validate_dataset(data)

    def test_required_category_coverage_and_atomicity_exceptions(self):
        all_rows=self.dataset['claim_examples']+self.dataset['answer_examples']
        self.assertEqual({k for r in all_rows for k in r['coverage_categories']},set('ABCDEFGHIJKLMNO'))
        compounds=[r for r in self.dataset['claim_examples'] if r['claim_type']=='compound_probe']
        self.assertEqual(len(compounds),5)
        self.assertTrue(all('K' in r['coverage_categories'] or 'G' in r['coverage_categories'] for r in compounds))

    def test_claim_and_response_labels_are_separate(self):
        data=deepcopy(self.dataset);data['answer_examples'][0]['gold_support_label']='SUPPORTED'
        with self.assertRaisesRegex(ValueError,'separation'):validate_dataset(data)
        data=deepcopy(self.dataset);data['answer_examples'][0]['response_assessment']['abstention']='SUPPORTED'
        with self.assertRaises(ValueError):validate_dataset(data)

    def test_authentic_synthetic_axes_and_complete_answer_contexts(self):
        data=deepcopy(self.dataset);data['answer_examples'][0]['context'].pop()
        with self.assertRaises(ValueError):validate_dataset(data)
        data=deepcopy(self.dataset);row=next(r for r in data['claim_examples'] if r['example_kind']=='authentic');row['claim']='Invented model answer'
        with self.assertRaises(ValueError):validate_dataset(data)

    def test_serialization_and_report_reproduction_no_network(self):
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
            first=b.build_dataset();second=b.build_dataset()
        self.assertEqual(b.encode(first),b.encode(second))
        self.assertEqual(b.encode(first),(b.ROOT/b.CANDIDATES).read_text())
        self.assertEqual(b.review_report(first),(b.ROOT/b.REVIEW).read_text())


if __name__=='__main__':unittest.main()
