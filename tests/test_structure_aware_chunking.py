"""Local tests for locked Phase 4B.1 chunk rules; no embedding/vector code."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_structure_aware_chunks as chunker
import local_tokenizer


def sentence(n=100, word='word'):
    return (' ' .join([word] * n)) + '.'


def unit(index, kind, texts, sections=(), author=None, pages=None):
    pages = pages or [(1, 1)] * len(texts)
    return {'unit_index': index, 'unit_type': 'foreign_or_unassigned_source_material' if kind == 'foreign' else 'major_legal_component',
            'opinion_type': kind, 'author': author, 'text': '\n'.join(texts),
            'page_start': min(a for a, b in pages), 'page_end': max(b for a, b in pages),
            'token_count': chunker.tokens('\n'.join(texts)),
            'sentences': [{'sentence_index': i, 'text': text, 'token_count': chunker.tokens(text),
                           'page_start': pages[i][0], 'page_end': pages[i][1]} for i, text in enumerate(texts)],
            'sections': [{'section_index': i, 'relative_line_index': line, 'marker': marker, 'title': None}
                         for i, (line, marker) in enumerate(sections)]}


def preview(*units):
    return {'documents': [{'source_file': 'example.pdf', 'original_source_file': 'original.pdf',
                           'case_name': 'Example v. Sample', 'major_units': list(units)}]}


class ChunkingRulesTests(unittest.TestCase):
    def make(self, *units):
        return chunker.generate(preview(*units))

    def test_foreign_material_excluded(self):
        records, stats, _ = self.make(unit(0, 'foreign', ['FOREIGN STURGIS.']), unit(1, 'majority', ['Case text.']))
        self.assertEqual(len(records), 1)
        self.assertNotIn('STURGIS', records[0]['text'])
        self.assertEqual(stats['excluded_foreign_units'], 1)
        self.assertEqual(stats['excluded_foreign_tokens'], chunker.tokens('FOREIGN STURGIS.'))

    def test_unknown_front_matter_retained(self):
        records, stats, _ = self.make(unit(0, 'unknown', ['Legitimate front matter.']))
        self.assertEqual(records[0]['text'], 'Legitimate front matter.')
        self.assertEqual(stats['validation']['coverage_percentage'], 100)

    def test_hard_major_unit_boundaries_never_crossed(self):
        records, stats, _ = self.make(unit(0, 'majority', [sentence(20)]), unit(1, 'majority', [sentence(20)]))
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0]['metadata']['major_unit_id'], records[1]['metadata']['major_unit_id'])
        self.assertEqual(stats['validation']['MIXED_MAJOR_UNIT_CHUNKS'], 0)

    def test_majority_dissent_never_mixed(self):
        records, stats, _ = self.make(unit(0, 'majority', [sentence(30)]), unit(1, 'dissent', [sentence(30)]))
        self.assertEqual([r['metadata']['opinion_type'] for r in records], ['majority', 'dissent'])
        self.assertEqual(stats['validation']['MIXED_OPINION_CHUNKS'], 0)

    def test_concurrence_dissent_never_mixed(self):
        records, _, _ = self.make(unit(0, 'concurrence', [sentence(30)]), unit(1, 'dissent', [sentence(30)]))
        self.assertEqual(len(records), 2)

    def test_small_opinion_remains_isolated(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(700)]), unit(1, 'concurrence', [sentence(100)], author='White'), unit(2, 'dissent', [sentence(700)]))
        self.assertEqual(records[1]['metadata']['author'], 'White')
        self.assertLess(records[1]['metadata']['token_count'], 300)
        self.assertEqual(len(records[1]['metadata']['provenance']), 1)

    def test_section_boundary_flushes_above_soft_minimum(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(400), sentence(400)], [(0, 'I'), (1, 'II')]))
        self.assertEqual(len(records), 2)
        self.assertEqual([r['metadata']['sections'][0]['marker'] for r in records], ['I', 'II'])

    def test_small_section_continues_inside_same_unit(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(100), sentence(400)], [(0, 'I'), (1, 'II')]))
        self.assertEqual(len(records), 1)
        self.assertEqual([s['marker'] for s in records[0]['metadata']['sections']], ['I', 'II'])

    def test_sentence_packing_preserves_whole_sentences(self):
        texts = [sentence(400), sentence(400), sentence(200)]
        records, _, _ = self.make(unit(0, 'majority', texts))
        self.assertEqual(records[0]['text'], ' '.join(texts[:2]))
        for r in records:
            self.assertTrue(all(p['complete_sentence'] for p in r['metadata']['provenance']))

    def test_one_sentence_overlap_inside_section(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(400), sentence(400), sentence(200)], [(0, 'I')]))
        self.assertEqual(records[1]['metadata']['overlap_sentence_count'], 1)
        self.assertEqual(records[0]['metadata']['provenance'][-1]['piece_id'], records[1]['metadata']['provenance'][0]['piece_id'])

    def test_no_overlap_at_section_boundary(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(500), sentence(500)], [(0, 'I'), (1, 'II')]))
        self.assertTrue(all(not r['metadata']['overlap_piece_ids'] for r in records))

    def test_no_overlap_at_opinion_boundary(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(500)]), unit(1, 'concurrence', [sentence(500)]))
        self.assertTrue(all(not r['metadata']['overlap_piece_ids'] for r in records))

    def test_hard_max_and_overlap_omitted_when_it_cannot_fit(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(700), sentence(700)]))
        self.assertTrue(all(r['metadata']['token_count'] <= 1100 for r in records))
        self.assertEqual(records[1]['metadata']['overlap_sentence_count'], 0)

    def test_oversized_sentence_fallback(self):
        records, stats, _ = self.make(unit(0, 'majority', [sentence(2600)]))
        self.assertEqual(stats['oversized_sentence_fallback_count'], 1)
        self.assertGreater(stats['fallback_pieces_generated'], 1)
        self.assertTrue(all(r['metadata']['token_count'] <= 1100 for r in records))
        self.assertTrue(all(r['metadata']['oversized_sentence_fallback'] for r in records))
        self.assertTrue(all(r['metadata']['overlap_sentence_count'] == 0 for r in records))

    def test_fallback_text_preservation_unicode_and_no_separator(self):
        for text in ('αβ🙂' * 800, 'Z' * 12000, ('word ' * 800) + '; ' + ('other ' * 900) + ': ' + ('tail ' * 800)):
            with self.subTest(text=text[:15]):
                ranges = chunker.oversized_ranges(text)
                self.assertEqual(''.join(text[a:b] for a, b in ranges), text)
                self.assertTrue(all(chunker.tokens(text[a:b].strip()) <= 1100 for a, b in ranges))

    def test_fallback_prefers_near_target_semicolon(self):
        text = ('word ' * 800) + '; ' + ('tail ' * 1700)
        ranges = chunker.oversized_ranges(text)
        self.assertTrue(text[ranges[0][0]:ranges[0][1]].endswith('; '))
        self.assertEqual(''.join(text[a:b] for a, b in ranges), text)

    def test_soft_minimum_never_overrides_hard_max(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(250), sentence(1000)], [(0, 'I'), (1, 'II')]))
        self.assertEqual(len(records), 2)
        self.assertTrue(all(r['metadata']['token_count'] <= 1100 for r in records))
        self.assertTrue(all(r['metadata']['overlap_sentence_count'] == 0 for r in records))

    def test_target_is_soft_and_normal_sentence_is_not_split(self):
        records, _, _ = self.make(unit(0, 'majority', [sentence(150), sentence(850)]))
        self.assertEqual(len(records), 1)
        self.assertGreater(records[0]['metadata']['token_count'], 900)
        self.assertLessEqual(records[0]['metadata']['token_count'], 1100)
        self.assertTrue(all(p['complete_sentence'] for p in records[0]['metadata']['provenance']))

    def test_fallback_provenance(self):
        records, stats, pieces = self.make(unit(0, 'dissent', [sentence(2500)], pages=[(3, 5)]))
        self.assertTrue(all(p['page_start'] == 3 and p['page_end'] == 5 for p in pieces.values()))
        self.assertEqual(stats['validation']['eligible_source_sentences'], 1)
        self.assertEqual(stats['validation']['covered_source_sentences'], 1)
        self.assertEqual({r['metadata']['major_unit_id'] for r in records}, {'example.pdf:u0'})

    def test_deterministic_ids_and_source_order(self):
        p = preview(unit(0, 'majority', [sentence(400)] * 6))
        self.assertEqual(chunker.generate(p), chunker.generate(p))
        records = chunker.generate(p)[0]
        self.assertEqual([r['metadata']['chunk_index'] for r in records], list(range(len(records))))
        self.assertEqual(len({r['metadata']['chunk_id'] for r in records}), len(records))

    def test_coverage_rejects_missing_and_reordered_source(self):
        p = preview(unit(0, 'unknown', [sentence(400)] * 5))
        records, _, pieces = chunker.generate(p)
        for bad in (records[:-1], records[::-1]):
            with self.assertRaises(ValueError):
                chunker.validate(p, bad, pieces)

    def test_page_provenance(self):
        records, _, _ = self.make(unit(0, 'majority', ['First page.', 'Second page.'], pages=[(1, 2), (2, 3)]))
        self.assertEqual((records[0]['metadata']['page_start'], records[0]['metadata']['page_end']), (1, 3))

    def test_jsonl_and_manifest_serialization(self):
        # Run the actual writer against temporary paths and the real preview.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(chunker, 'OUTPUT', root / 'chunks'), patch.object(chunker, 'ANALYSIS', root / 'analysis/report'), patch('builtins.print'):
                chunker.main()
            rows = [json.loads(line) for line in (root / 'chunks/chunks.jsonl').read_text().splitlines()]
            manifest = json.loads((root / 'chunks/manifest.json').read_text())
            self.assertEqual(len(rows), manifest['number_of_chunks'])
            self.assertEqual(manifest['validation']['missing_source_sentences'], 0)
            self.assertNotIn('embedding_model', manifest)
            self.assertFalse((root / 'chunks/vector_store').exists())

    def test_marker_inside_sentence_has_exact_fragment_coverage(self):
        u = unit(0, 'majority', ['Before marker. I\nAfter marker text.'])
        u['text'] = 'Before marker.\nI\nAfter marker text.'
        u['sentences'][0]['text'] = chunker.canonical(u['text'])
        u['sections'] = [{'section_index': 0, 'relative_line_index': 1, 'marker': 'I', 'title': None}]
        records, stats, pieces = self.make(u)
        self.assertEqual(len(pieces), 2)
        self.assertEqual(''.join(p['text'] for p in pieces.values()), u['sentences'][0]['text'])
        self.assertEqual(stats['validation']['missing_source_sentences'], 0)
        self.assertTrue(all(not p['complete_sentence'] for p in pieces.values()))

    def test_validation_rejects_cross_unit_and_modified_text(self):
        p = preview(unit(0, 'majority', [sentence(300)]), unit(1, 'dissent', [sentence(300)]))
        records, _, pieces = chunker.generate(p)
        bad = copy.deepcopy(records)
        bad[0]['metadata']['provenance'] += bad[1]['metadata']['provenance']
        with self.assertRaises(ValueError):
            chunker.validate(p, bad, pieces)
        bad = copy.deepcopy(records)
        bad[0]['text'] += ' Changed.'
        with self.assertRaises(ValueError):
            chunker.validate(p, bad, pieces)

    def test_actual_corpus_foreign_white_and_coverage(self):
        p = json.loads(chunker.SOURCE.read_text())
        records, stats, _ = chunker.generate(p)
        white = [r for r in records if 'Tinker' in r['metadata']['case_name'] and r['metadata']['author'] == 'White']
        self.assertEqual(len(white), 1)
        self.assertLess(white[0]['metadata']['token_count'], 300)
        self.assertEqual(stats['excluded_foreign_units'], 1)
        self.assertEqual(stats['validation']['missing_source_sentences'], 0)
        self.assertEqual(stats['validation']['MIXED_MAJOR_UNIT_CHUNKS'], 0)
        self.assertFalse(any(r['metadata']['opinion_type'] == 'foreign' for r in records))


class LocalTokenizerTests(unittest.TestCase):
    def test_missing_vocabulary_fails_without_network(self):
        with patch.object(Path, 'is_file', return_value=False), patch.object(Path, 'glob', return_value=[]):
            with self.assertRaisesRegex(RuntimeError, 'no download attempted'):
                local_tokenizer.load_local_encoding()

    def test_exact_tokenizer_matches_cached_tiktoken(self):
        import tiktoken
        actual = tiktoken.get_encoding('cl100k_base')
        for text in ('CourtLens legal text.', 'αβ🙂 text; colon: more.', 'I.\nSection text.'):
            self.assertEqual(chunker.ENCODING.encode(text), actual.encode(text))


if __name__ == '__main__':
    unittest.main()
