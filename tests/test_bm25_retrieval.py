"""Synthetic BM25 formula, tokenizer, ranking, serialization, and safety tests."""

from copy import deepcopy
import json
import math
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from bm25_retrieval import BM25, tokenize
from finalize_chunking_benchmark import score_retrieved, saved_result_is_relevant
import run_bm25_experiment as experiment


def records(count=30):
    return [{'text': 'shared term', 'metadata': {
        'chunk_index': i, 'chunk_id': f'original:{i}', 'case_name': 'Target', 'source_file': 'target.pdf',
        'original_source_file': 'original.pdf', 'page_start': i + 1, 'page_end': i + 1,
        'token_count': 2, 'opinion_type': 'majority', 'author': 'Author'}} for i in range(count)]


class TokenizerTests(unittest.TestCase):
    def test_unicode_casefold_numbers_and_punctuation(self):
        self.assertEqual(tokenize('RÉSUMÉ Straße ９００ 36°30 3.14 O’Connor a_b IV नमस्ते'),
                         ['résumé', 'strasse', '900', '36', '30', '3', '14', 'o', 'connor', 'a', 'b', 'iv', 'नमस्ते'])

    def test_no_stopwords_or_stemming(self):
        self.assertEqual(tokenize('The courts and court'), ['the', 'courts', 'and', 'court'])

    def test_empty_and_malformed_input(self):
        self.assertEqual(tokenize(' !!! '), [])
        with self.assertRaises(TypeError):
            tokenize(None)


class FormulaTests(unittest.TestCase):
    def test_hand_calculated_term_frequency_idf_and_length_normalization(self):
        bm = BM25(['alpha alpha beta', 'beta', 'gamma gamma'])
        idf = math.log(1 + 2.5 / 1.5)
        expected = idf * 2 * 2.5 / (2 + 1.5 * (.25 + .75 * 3 / 2))
        self.assertAlmostEqual(bm.scores('alpha')[0], expected, places=14)
        self.assertEqual(bm.scores('alpha')[1:], [0., 0.])
        self.assertAlmostEqual(bm.idf['beta'], math.log(1 + 1.5 / 2.5), places=14)
        self.assertGreater(bm.scores('beta')[1], bm.scores('beta')[0])

    def test_common_terms_have_positive_smoothed_idf(self):
        bm = BM25(['common', 'common'])
        self.assertAlmostEqual(bm.idf['common'], math.log(1 + .5 / 2.5))
        self.assertGreater(bm.scores('common')[0], 0)

    def test_repeated_query_terms_and_term_order(self):
        bm = BM25(['alpha beta beta', 'alpha'])
        self.assertEqual(bm.scores('beta beta'), [2 * x for x in bm.scores('beta')])
        self.assertEqual(bm.scores('alpha beta'), bm.scores('beta alpha'))

    def test_same_tokenizer_for_documents_and_queries(self):
        a = BM25(['RÉSUMÉ Straße ９００'])
        b = BM25(['résumé strasse 900'])
        self.assertEqual(a.scores('résumé STRASSE 900'), b.scores('RÉSUMÉ Straße ９００'))

    def test_empty_oov_and_all_empty_document_handling(self):
        bm = BM25(['alpha', 'beta'])
        for query in ('', '!!!', 'unknownword'):
            self.assertEqual(bm.scores(query), [0., 0.])
            self.assertEqual(bm.rank(query), [])
        self.assertEqual(BM25(['', '!!!']).rank('alpha'), [])
        with self.assertRaises(ValueError):
            BM25([])

    def test_parameter_and_rank_limit_validation(self):
        for args in ({'k1': 0}, {'k1': float('nan')}, {'b': 2}, {'b': float('inf')}):
            with self.assertRaises(ValueError):
                BM25(['text'], **args)
        with self.assertRaises(ValueError):
            BM25(['text']).rank('text', -1)


class RankingAndEvaluationTests(unittest.TestCase):
    def test_ties_order_and_zero_scores_excluded(self):
        bm = BM25(['alpha', 'alpha', 'beta'])
        self.assertEqual([i for i, _ in bm.rank('alpha')], [0, 1])
        self.assertEqual(bm.rank('alpha', 1), bm.rank('alpha')[:1])
        self.assertEqual(bm.rank('alpha', 0), [])

    def test_positive_scores_descending_then_original_ordinal(self):
        ranked = BM25(['other', 'term term term', 'term', 'term']).rank('term')
        self.assertEqual(ranked, sorted(ranked, key=lambda pair: (-pair[1], pair[0])))
        self.assertNotIn(0, [i for i, _ in ranked])
        self.assertLess([i for i, _ in ranked].index(2), [i for i, _ in ranked].index(3))

    def test_top20_serialization_preserves_original_ids_and_metadata(self):
        corpus = records()
        before = deepcopy(corpus)
        _, queries = experiment.rank_queries(corpus, [('Q', 'shared')])
        output = json.loads(experiment.encode(queries))
        self.assertEqual([r['rank'] for r in output[0]['retrieved']], list(range(1, 21)))
        self.assertEqual([r['chunk_id'] for r in output[0]['retrieved']], [f'original:{i}' for i in range(20)])
        for row in output[0]['retrieved']:
            for field in experiment.ROW_FIELDS:
                self.assertEqual(row[field], corpus[row['corpus_index']]['metadata'].get(field))
            self.assertTrue(math.isfinite(row['bm25_score']))
            self.assertNotIn('relevant', row)
            self.assertNotIn('text', row)
        self.assertEqual(corpus, before)
        self.assertEqual(experiment.rank_queries(corpus, [('Q', 'shared')])[1], queries)

    def test_no_label_case_or_opinion_boosts(self):
        corpus = records()
        changed = deepcopy(corpus)
        for r in changed:
            r['metadata'].update(case_name='Different', opinion_type='dissent', author='Other', relevant=True, expected_case='Different')
        _, a = experiment.rank_queries(corpus, [('Q', 'shared')])
        _, b = experiment.rank_queries(changed, [('Q', 'shared')])
        self.assertEqual([(r['corpus_index'], r['bm25_score']) for r in a[0]['retrieved']],
                         [(r['corpus_index'], r['bm25_score']) for r in b[0]['retrieved']])

    def test_top5_mrr_does_not_credit_a_rank6_hit(self):
        _, ranked = experiment.rank_queries(records(), [('Q', 'shared')])
        q = {'expected_case': 'Target', 'expected_source_file': 'target.pdf', 'relevant_ranges': [[6, 6]]}
        metrics = score_retrieved(ranked[0]['retrieved'], q)
        self.assertTrue(saved_result_is_relevant(ranked[0]['retrieved'][5], q))
        self.assertIsNone(metrics['first_relevant_rank'])
        self.assertEqual([metrics[k] for k in ('hit_at_1', 'hit_at_3', 'hit_at_5', 'reciprocal_rank')], [0., 0., 0., 0.])

    def test_correct_multirange_case_source_relevance(self):
        _, ranked = experiment.rank_queries(records(), [('Q', 'shared')])
        q = {'expected_case': 'Target', 'expected_source_file': 'target.pdf', 'relevant_ranges': [[3, 3], [8, 9]]}
        self.assertEqual(score_retrieved(ranked[0]['retrieved'], q)['first_relevant_rank'], 3)
        q['expected_case'] = 'Other'
        self.assertIsNone(score_retrieved(ranked[0]['retrieved'], q)['first_relevant_rank'])

    def test_complementarity_all_hit_and_rank_categories(self):
        for a, b, expected in [(None, None, ('both_miss', 'shared_miss')), (1, None, ('dense_only', 'dense_win')),
                               (None, 3, ('bm25_only', 'bm25_win')), (2, 2, ('both_hit', 'tie')),
                               (2, 1, ('both_hit', 'bm25_win')), (1, 4, ('both_hit', 'dense_win'))]:
            self.assertEqual(experiment.complementarity(a, b), expected)

    def test_synthetic_serialization_is_deterministic(self):
        output = {'records': records(2), 'scores': BM25(['shared', 'term']).scores('shared')}
        self.assertEqual(experiment.encode(output), experiment.encode(deepcopy(output)))


class FrozenArtifactTests(unittest.TestCase):
    def test_existing_corpora_and_benchmark_immutable_during_ranking(self):
        before = experiment.protected_snapshot()
        with patch.object(socket, 'getaddrinfo', side_effect=AssertionError('Network forbidden')), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            for collection, count in experiment.COUNTS.items():
                corpus, _ = experiment.load_corpus(collection)
                original = deepcopy(corpus)
                _, ranked = experiment.rank_queries(corpus, [('synthetic', 'synthetic-unmatched-zzzzz')])
                self.assertEqual(len(corpus), count)
                self.assertEqual(corpus, original)
                self.assertEqual(ranked[0]['id'], 'synthetic')
        self.assertEqual(experiment.protected_snapshot(), before)

    def test_full_evaluation_reproducible_without_network_or_source_mutation(self):
        before = experiment.protected_snapshot()
        with patch.object(socket, 'getaddrinfo', side_effect=AssertionError('Network forbidden')), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            first = experiment.build_outputs()
            second = experiment.build_outputs()
        self.assertEqual(first, second)
        self.assertEqual(set(first), experiment.output_paths())
        self.assertEqual(experiment.protected_snapshot(), before)
        for collection in experiment.COLLECTIONS:
            directory = experiment.EXPERIMENT_ROOT / collection
            raw = json.loads(first[directory / 'rankings_top20.json'])
            evaluated = json.loads(first[directory / 'results.json'])
            self.assertEqual(len(raw['questions']), 40)
            self.assertEqual(len(evaluated['questions']), 40)
            for q, official in zip(raw['questions'], evaluated['questions']):
                rows = q['retrieved']
                self.assertEqual(len(rows), 20)
                self.assertEqual(rows, sorted(rows, key=lambda r: (-r['bm25_score'], r['corpus_index'])))
                self.assertEqual([r['rank'] for r in rows], list(range(1, 21)))
                self.assertTrue(all(math.isfinite(r['bm25_score']) and r['bm25_score'] > 0 for r in rows))
                self.assertEqual(official['metrics'], score_retrieved(rows, official))
        analysis = json.loads(first[experiment.ANALYSIS_JSON])
        for c in analysis['comparisons']:
            self.assertEqual(sum(c['top5_complementarity'].values()), 40)
            self.assertEqual(sum(c['first_relevant_rank_comparison'].values()), 40)
            for q in c['targeted_failures']:
                self.assertEqual(len(q['bm25_top5']), 5)
                self.assertTrue(all(r['manual_inspection'].get('status') for r in q['bm25_top5']))

    def test_writer_only_creates_new_phase5a_paths(self):
        outputs = {p: 'synthetic fixture\n' for p in experiment.output_paths()}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            experiment.write_outputs(outputs, root)
            self.assertEqual({p.relative_to(root) for p in root.rglob('*') if p.is_file()}, experiment.output_paths())
            experiment.write_outputs(outputs, root)
            p = root / experiment.ANALYSIS_MD
            p.write_text('preserve existing')
            with self.assertRaises(FileExistsError):
                experiment.write_outputs(outputs, root)
            self.assertEqual(p.read_text(), 'preserve existing')


if __name__ == '__main__':
    unittest.main()
