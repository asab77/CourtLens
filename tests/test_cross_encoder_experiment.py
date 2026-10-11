"""Fake encoder/tokenizer tests: never import a neural model or download weights."""
from copy import deepcopy
import json
import re
import socket
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_cross_encoder_experiment as e
from hybrid_retrieval import ChunkCatalog
from finalize_chunking_benchmark import score_retrieved


def rows():
    return [{'rank':i+1,'hybrid_rank':i+1,'corpus_index':i,'source_file':'case.pdf','case_name':'Case',
             'chunk_index':i,'chunk_id':f'C:{i}','page_start':i+1,'page_end':i+1,'relevant':True} for i in range(8)]


class Encoding(dict):
    def __init__(self,ids,seq,offsets):
        super().__init__(input_ids=ids,offset_mapping=offsets)
        self.seq=seq
    def sequence_ids(self):return self.seq


class FakeTokenizer:
    def __call__(self,q,p=None,add_special_tokens=True,truncation=False,max_length=None,return_offsets_mapping=False):
        tokens=lambda s:list(re.finditer(r'\S+',s))
        a=tokens(q)
        if p is None:return {'input_ids':list(range(len(a)))}
        b=tokens(p)
        if truncation:
            while len(a)+len(b)+3>max_length:
                (a if len(a)>len(b) else b).pop()
        seq=[None]+[0]*len(a)+[None]+[1]*len(b)+[None]
        offsets=[(0,0)]+[m.span() for m in a]+[(0,0)]+[m.span() for m in b]+[(0,0)]
        return Encoding(list(range(len(seq))),seq,offsets)


class FakeEncoder:
    def __init__(self):self.pairs=[]
    def score(self,pairs):
        assert all(isinstance(p,tuple) and len(p)==2 and all(isinstance(t,str) for t in p) for p in pairs)
        self.pairs.extend(deepcopy(pairs))
        return [float(i%7) for i in range(len(pairs))],e.token_accounting(FakeTokenizer(),pairs)


class RerankingTests(unittest.TestCase):
    def setUp(self):
        self.rows=rows();self.stats=e.token_accounting(FakeTokenizer(),[('question','text')]*8)

    def test_scores_descending_stable_original_order_ties(self):
        ranked=e.rerank(list(reversed(self.rows)),[2.]*8,self.stats)
        self.assertEqual([r['corpus_index'] for r in ranked],list(range(8)))
        self.assertEqual([r['rank'] for r in ranked],list(range(1,9)))
        self.assertEqual([r['hybrid_rank'] for r in ranked],list(range(1,9)))

    def test_complete_union_rank7_can_reach_top5(self):
        ranked=e.rerank(self.rows,[0.,0.,0.,0.,0.,0.,10.,0.],self.stats)
        self.assertEqual(len(ranked),8)
        self.assertEqual(ranked[0]['hybrid_rank'],7)
        self.assertEqual(ranked[0]['cross_encoder_rank'],1)

    def test_no_label_metadata_or_raw_score_ranking_influence(self):
        scores=list(range(8));a=e.rerank(self.rows,scores,self.stats)
        changed=deepcopy(self.rows)
        for r in changed:r.update(relevant=False,author='Dissent',opinion_type='dissent',dense_similarity=1e20,bm25_score=1e30,rrf_score=-1e10)
        b=e.rerank(changed,scores,self.stats)
        self.assertEqual([(r['corpus_index'],r['cross_encoder_score']) for r in a],[(r['corpus_index'],r['cross_encoder_score']) for r in b])
        self.assertTrue(all('relevant' not in r for r in a+b))

    def test_oracle_isolation_and_top5_mrr(self):
        ranked=e.rerank(self.rows,[float(-i) for i in range(8)],self.stats)
        before=deepcopy(ranked)
        q={'expected_case':'Case','expected_source_file':'case.pdf','relevant_ranges':[[7,7]]}
        self.assertTrue(e.oracle(ranked,q))
        m=score_retrieved(ranked,q)
        self.assertIsNone(m['first_relevant_rank']);self.assertEqual(m['reciprocal_rank'],0.)
        q['relevant_ranges']=[[1,1]];m=score_retrieved(ranked,q)
        self.assertEqual((m['hit_at_1'],m['hit_at_3'],m['hit_at_5'],m['reciprocal_rank']),(1.,1.,1.,1.))
        q['expected_case']='Wrong';self.assertFalse(e.oracle(ranked,q))
        self.assertEqual(ranked,before)

    def test_invalid_scores_counts_and_truncation_rejected(self):
        with self.assertRaises(ValueError):e.rerank(self.rows,[1.],self.stats)
        for score in (float('nan'),float('inf')):
            with self.assertRaises(ValueError):e.rerank(self.rows,[score]*8,self.stats)
        stats=deepcopy(self.stats);stats[0]['processed_pair_tokens']=513
        with self.assertRaises(ValueError):e.rerank(self.rows,[0.]*8,stats)

    def test_source_rows_immutable(self):
        before=deepcopy(self.rows);e.rerank(self.rows,list(range(8)),self.stats)
        self.assertEqual(self.rows,before)

    def test_wrong_corpus_identity_rejected(self):
        records=[{'metadata':{k:v for k,v in r.items() if k in ('source_file','case_name','chunk_index','chunk_id','page_start','page_end')},'text':'text'} for r in self.rows]
        catalog=ChunkCatalog('fixture',records)
        self.assertEqual(catalog.verify(self.rows[0]),0)
        r=deepcopy(self.rows[0]);r['collection']='other'
        with self.assertRaises(ValueError):catalog.verify(r)
        r=deepcopy(self.rows[0]);r['chunk_id']='other'
        with self.assertRaises(ValueError):catalog.verify(r)


class TruncationTests(unittest.TestCase):
    def test_short_pair_counts_special_tokens(self):
        t=e.token_accounting(FakeTokenizer(),[('query words','some passage words')])[0]
        self.assertEqual(t['full_pair_tokens'],8);self.assertEqual(t['processed_pair_tokens'],8)
        self.assertFalse(t['truncated']);self.assertEqual(t['passage_tokens_retained'],3)

    def test_long_passage_deterministic_right_truncation(self):
        passage=' '.join(['word']*600)
        t=e.token_accounting(FakeTokenizer(),[('two words',passage)])[0]
        self.assertTrue(t['truncated']);self.assertEqual(t['processed_pair_tokens'],512)
        self.assertEqual(t['query_tokens_retained'],2);self.assertEqual(t['passage_tokens_retained'],507)
        self.assertEqual(t['passage_tokens_removed'],93)
        self.assertLess(t['passage_retained_end_character'],len(passage))
        self.assertEqual(t,e.token_accounting(FakeTokenizer(),[('two words',passage)])[0])

    def test_long_query_uses_frozen_longest_first(self):
        t=e.token_accounting(FakeTokenizer(),[(' '.join(['q']*600),'short passage')])[0]
        self.assertEqual(t['processed_pair_tokens'],512)
        self.assertGreater(t['query_tokens_removed'],0)
        self.assertEqual(t['passage_tokens_removed'],0)

    def test_exact_window_boundary_not_truncated(self):
        t=e.token_accounting(FakeTokenizer(),[('q',' '.join(['p']*508))])[0]
        self.assertEqual(t['full_pair_tokens'],512);self.assertFalse(t['truncated'])


class ExperimentTests(unittest.TestCase):
    def test_frozen_environment_and_revision_validation(self):
        config=e.load(e.ROOT/e.ENVIRONMENT);e.validate_environment(config)
        for field,value in [('revision','main'),('batch_size',16),('max_length',1024),('device','cuda'),('truncation','only_second')]:
            changed=deepcopy(config);changed[field]=value
            with self.assertRaises(ValueError):e.validate_environment(changed)

    def test_saved_candidates_pair_construction_and_frozen_sources(self):
        before=e.protected_snapshot();qs=e.load(e.ROOT/e.BENCHMARK)['questions']
        for c in e.COLLECTIONS:
            records,raw,baseline,pairs,hashes=e.load_inputs(c,qs)
            self.assertEqual(len(pairs),e.PAIR_COUNTS[c]);self.assertEqual(len(raw['questions']),40)
            i=0
            for q,saved in zip(qs,raw['questions']):
                for r in saved['retrieved']:
                    self.assertEqual(pairs[i],(q['question'],records[r['corpus_index']]['text']));i+=1
        self.assertEqual(before,e.protected_snapshot())

    def test_fake_inference_outputs_deterministic_and_no_network(self):
        before=e.protected_snapshot()
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
            a=FakeEncoder();first=e.build_outputs(a);second=e.build_outputs(FakeEncoder())
        self.assertEqual(len(a.pairs),612);self.assertEqual(first,second)
        self.assertEqual(before,e.protected_snapshot())
        self.assertEqual(set(first),e.output_paths())
        analysis=json.loads(first[e.ANALYSIS])
        self.assertEqual([c['oracle']['maximum_possible_mrr'] for c in analysis['comparisons']],[1.,.975])

    def test_saved_score_replay_without_model_loading(self):
        if not (e.ROOT/e.ANALYSIS).exists():self.skipTest('Real scores not generated yet')
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(e,'LocalScorer',side_effect=AssertionError('No model loading in replay')):
            outputs=e.build_outputs(e.ReplayScorer())
        self.assertTrue(all((e.ROOT/p).read_bytes()==text.encode() for p,text in outputs.items()))

    def test_writer_new_paths_only(self):
        outputs={p:'test fixture\n' for p in e.output_paths()}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);e.write_outputs(outputs,root);e.write_outputs(outputs,root)
            self.assertEqual({p.relative_to(root) for p in root.rglob('*') if p.is_file()},e.output_paths())
            (root/e.REPORT).write_text('preserve')
            with self.assertRaises(FileExistsError):e.write_outputs(outputs,root)
            self.assertEqual((root/e.REPORT).read_text(),'preserve')


if __name__=='__main__':unittest.main()
