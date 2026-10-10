"""Tests for the complete Phase 4A.1 oversized-sentence review."""

import json
import unittest

from analyze_long_sentences import REVIEWS, build_analysis, load_preview


class LongSentenceAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview = load_preview()
        cls.analysis = build_analysis(cls.preview)

    def test_all_28_segments_are_reviewed_once(self):
        self.assertEqual(len(REVIEWS), 28)
        self.assertEqual(self.analysis["segment_count"], 28)
        keys = {
            (item["case_name"], item["unit_index"], item["sentence_index"])
            for item in self.analysis["segments"]
        }
        self.assertEqual(keys, set(REVIEWS))

    def test_cause_counts_cover_every_segment(self):
        self.assertEqual(sum(self.analysis["counts_by_likely_cause"].values()), 28)
        self.assertEqual(
            self.analysis["counts_by_likely_cause"],
            {
                "citation_or_statutory_enumeration": 6,
                "extraction_layout_or_footnote_interleaving": 5,
                "genuinely_long_historical_sentence": 7,
                "ocr_punctuation_loss": 8,
                "page_boundary_artifact": 2,
            },
        )

    def test_every_record_has_requested_evidence_and_fallback_decision(self):
        for item in self.analysis["segments"]:
            self.assertGreater(item["token_count"], 200)
            self.assertLessEqual(item["page_start"], item["page_end"])
            self.assertTrue(item["beginning_excerpt"])
            self.assertTrue(item["ending_excerpt"])
            self.assertTrue(item["cause_explanation"])
            self.assertIs(item["needs_phase_4b_fallback"], True)

    def test_analysis_is_deterministic_and_json_serializable(self):
        self.assertEqual(build_analysis(self.preview), self.analysis)
        json.dumps(self.analysis)


if __name__ == "__main__":
    unittest.main()
