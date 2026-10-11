"""Local synthetic and saved-artifact checks for fixed Top-5 rank-only RRF."""
from copy import deepcopy
import json
import math
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from hybrid_retrieval import ChunkCatalog, fuse
from finalize_chunking_benchmark import score_retrieved, saved_result_is_relevant
import run_hybrid_experiment as h


def corpus(n=12):
    return [{'text':f'frozen text {i}', 'metadata':{'source_file':'case.pdf','case_name':'Case',
             'chunk_index':i,'chunk_id':f'chunk:{i}','page_start':i+1,'page_end':i+1,
             'token_count':10,'opinion_type':'majority','author':'Author'}} for i in range(n)]


def rows(records, indexes, method='dense'):
    return [{**deepcopy(records[i]['metadata']), 'rank':rank,
             'similarity' if method=='dense' else 'bm25_score':10.-rank}
            for rank,i in enumerate(indexes,1)]


class FusionTests(unittest.TestCase):
    def setUp(self):
        self.records=corpus()
        self.catalog=ChunkCatalog('fixture',self.records)

    def test_formula_one_based_and_missing_list_contribution(self):
        fused=fuse(self.catalog,rows(self.records,[0,1]),rows(self.records,[1,2],'bm25'))
        found={r['chunk_index']:r for r in fused}
        self.assertEqual(found[0]['rrf_score'],1/61)
        self.assertEqual(found[1]['rrf_score'],1/62+1/61)
        self.assertEqual(found[2]['rrf_score'],1/62)
        self.assertIsNone(found[0]['bm25_rank'])
        self.assertIsNone(found[2]['dense_rank'])

    def test_duplicate_cross_list_identity_deduplicated(self):
        fused=fuse(self.catalog,rows(self.records,[0]),rows(self.records,[0],'bm25'))
        self.assertEqual(len(fused),1)
        self.assertEqual(fused[0]['rrf_score'],2/61)

    def test_duplicate_within_list_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate candidate'):
            fuse(self.catalog,rows(self.records,[0,0]),[])
        with self.assertRaisesRegex(ValueError,'Duplicate frozen'):
            ChunkCatalog('fixture',[self.records[0],self.records[0]])

    def test_non_one_based_ranks_rejected(self):
        for value in (0,2,True):
            candidates=rows(self.records,[0]);candidates[0]['rank']=value
            with self.assertRaisesRegex(ValueError,'one-based'):
                fuse(self.catalog,candidates,[])

    def test_ties_use_original_corpus_order(self):
        fused=fuse(self.catalog,rows(self.records,[5,6]),rows(self.records,[0,1],'bm25'))
        self.assertEqual([r['chunk_index'] for r in fused],[0,5,1,6])

    def test_depth5_is_fixed_even_with_deeper_lists(self):
        fused=fuse(self.catalog,rows(self.records,[0,1,2,3,4,10]),rows(self.records,[5,6,7,8,9,11],'bm25'))
        self.assertEqual(len(fused),10)
        self.assertNotIn(10,[r['chunk_index'] for r in fused])
        self.assertNotIn(11,[r['chunk_index'] for r in fused])
        self.assertEqual([r['rank'] for r in fused],list(range(1,11)))

    def test_raw_scores_do_not_influence_fusion(self):
        d=rows(self.records,[5,6]);b=rows(self.records,[0,6],'bm25')
        original=fuse(self.catalog,d,b)
        for row in d: row['similarity']=-1e200
        for row in b: row['bm25_score']=1e200
        changed=fuse(self.catalog,d,b)
        self.assertEqual([(r['chunk_index'],r['rrf_score']) for r in original],[(r['chunk_index'],r['rrf_score']) for r in changed])

    def test_metadata_and_relevance_do_not_influence_fusion(self):
        d=rows(self.records,[5,6]);b=rows(self.records,[0,6],'bm25')
        original=fuse(self.catalog,d,b)
        changed=deepcopy(self.records)
        for r in changed:
            r['metadata'].update(opinion_type='dissent',author='Other',case_name='OtherCase')
        d2=rows(changed,[5,6]);b2=rows(changed,[0,6],'bm25')
        for r in d2+b2:r['relevant']=True
        alternate=fuse(ChunkCatalog('fixture',changed),d2,b2)
        self.assertEqual([(r['chunk_index'],r['rrf_score']) for r in original],[(r['chunk_index'],r['rrf_score']) for r in alternate])

    def test_no_cross_corpus_mixing(self):
        candidates=rows(self.records,[0]);candidates[0]['collection']='different'
        with self.assertRaisesRegex(ValueError,'Cross-corpus'):
            fuse(self.catalog,candidates,[])
        candidates=rows(self.records,[0]);candidates[0]['chunk_id']='other-corpus:0'
        with self.assertRaisesRegex(ValueError,'mismatch'):
            fuse(self.catalog,candidates,[])

    def test_page_overlap_never_merges_distinct_ids(self):
        records=corpus(2);records[1]['metadata'].update(page_start=1,page_end=1)
        fused=fuse(ChunkCatalog('fixture',records),rows(records,[0]),rows(records,[1],'bm25'))
        self.assertEqual(len(fused),2)

    def test_stable_identity_mapping_and_mismatch_rejection(self):
        candidate=rows(self.records,[7])[0]
        self.assertEqual(self.catalog.verify(candidate),7)
        for field,value in [('page_start',1),('source_file','other.pdf'),('chunk_index',99),('corpus_index',0),('text','altered'),('chunk_reference',{})]:
            changed=deepcopy(candidate);changed[field]=value
            with self.assertRaises(ValueError): self.catalog.verify(changed)

    def test_empty_rankings_and_nonfinite_diagnostics(self):
        self.assertEqual(fuse(self.catalog,[],[]),[])
        for value in (float('nan'),float('inf')):
            d=rows(self.records,[0]);d[0]['similarity']=value
            with self.assertRaisesRegex(ValueError,'Non-finite'):
                fuse(self.catalog,d,[])

    def test_union_hit_can_be_lost_below_top5(self):
        fused=fuse(self.catalog,rows(self.records,[0,1,2,3,4]),rows(self.records,[5,6,7,8,9],'bm25'))
        q={'expected_case':'Case','expected_source_file':'case.pdf','relevant_ranges':[[5,5]]}
        relevant=[r for r in fused if saved_result_is_relevant(r,q)]
        self.assertEqual(relevant[0]['rank'],9)
        metrics=score_retrieved(fused,q)
        self.assertIsNone(metrics['first_relevant_rank'])
        self.assertEqual(metrics['reciprocal_rank'],0.)
        self.assertEqual(metrics['hit_at_5'],0.)

    def test_hit_at_k_and_mrr(self):
        fused=fuse(self.catalog,rows(self.records,[0,1,2,3,4]),[])
        q={'expected_case':'Case','expected_source_file':'case.pdf','relevant_ranges':[[3,3]]}
        m=score_retrieved(fused,q)
        self.assertEqual((m['hit_at_1'],m['hit_at_3'],m['hit_at_5'],m['reciprocal_rank']),(0.,1.,1.,1/3))

    def test_inputs_and_original_chunk_ids_unchanged(self):
        d=rows(self.records,[5,6]);b=rows(self.records,[0,6],'bm25')
        before=deepcopy((self.records,d,b))
        result=fuse(self.catalog,d,b)
        self.assertEqual((self.records,d,b),before)
        self.assertEqual([r['chunk_id'] for r in result],['chunk:6','chunk:0','chunk:5'])


class ExperimentTests(unittest.TestCase):
    def test_question_order_and_wording_mismatch_rejected(self):
        qs=[{'id':str(i),'question':str(i)} for i in range(40)]
        h.check_questions(qs,qs)
        with self.assertRaisesRegex(ValueError,'order/count'): h.check_questions(list(reversed(qs)),qs)
        changed=deepcopy(qs);changed[0]['question']='changed'
        with self.assertRaisesRegex(ValueError,'benchmark mismatch'): h.check_questions(changed,qs)

    def test_rank_change_all_categories(self):
        for a,b,c in [(None,None,'shared_miss'),(None,2,'improved'),(1,None,'worsened'),(2,1,'improved'),(1,2,'worsened'),(1,1,'tie')]:
            self.assertEqual(h.rank_change(a,b),c)

    def test_local_saved_outputs_deterministic_and_protected(self):
        before=h.protected_snapshot()
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')), patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
            first=h.build_outputs();second=h.build_outputs()
        self.assertEqual(first,second)
        self.assertEqual(before,h.protected_snapshot())
        self.assertEqual(set(first),h.output_paths())
        for collection in h.COLLECTIONS:
            rankings=json.loads(first[h.BASE/collection/'rankings.json'])
            results=json.loads(first[h.BASE/collection/'results.json'])
            self.assertEqual(len(rankings['questions']),40)
            self.assertEqual([q['id'] for q in rankings['questions']],[q['id'] for q in results['questions']])
            for raw,q in zip(rankings['questions'],results['questions']):
                rows=raw['retrieved']
                self.assertLessEqual(len(rows),10)
                self.assertEqual(rows,sorted(rows,key=lambda r:(-r['rrf_score'],r['corpus_index'])))
                self.assertEqual(len({r['corpus_index'] for r in rows}),len(rows))
                self.assertTrue(all(math.isfinite(r['rrf_score']) for r in rows))
                self.assertEqual(q['metrics'],score_retrieved(rows,q))
                self.assertEqual([r['relevant'] for r in rows],[saved_result_is_relevant(r,q) for r in rows])
                for r in rows:
                    self.assertEqual(r['rrf_score'],sum(1/(60+r[k]) for k in ('dense_rank','bm25_rank') if r[k] is not None))

    def test_writer_new_paths_only_and_conflicts_rejected(self):
        output={p:'fixture\n' for p in h.output_paths()}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);h.write_outputs(output,root);h.write_outputs(output,root)
            self.assertEqual({p.relative_to(root) for p in root.rglob('*') if p.is_file()},h.output_paths())
            (root/h.REPORT).write_text('preserved')
            with self.assertRaises(FileExistsError):h.write_outputs(output,root)
            self.assertEqual((root/h.REPORT).read_text(),'preserved')
            with self.assertRaises(ValueError):h.write_outputs({Path('data/existing'):'bad'},root)


if __name__=='__main__':unittest.main()
