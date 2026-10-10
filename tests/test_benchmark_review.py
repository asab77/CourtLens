"""Tests for the local benchmark human-review workflow."""

import json
import unittest

from benchmark_relevance import (
    normalize_relevant_ranges,
    page_range_overlaps,
    relevant_ranges_for_item,
)
from prepare_benchmark_review import (
    DEFAULT_BENCHMARK_PATH,
    build_review,
)


class RelevantRangeTests(unittest.TestCase):
    def test_normalizes_legacy_single_range_and_multiple_ranges(self):
        self.assertEqual(normalize_relevant_ranges([2, 2]), [[2, 2]])
        self.assertEqual(
            normalize_relevant_ranges([[2, 2], [19, 21]]),
            [[2, 2], [19, 21]],
        )

    def test_proposed_field_precedes_backward_compatible_field(self):
        item = {
            "relevant_ranges": [[19, 21]],
            "relevant_pages": [[2, 2]],
        }
        self.assertEqual(relevant_ranges_for_item(item), [[19, 21]])
        self.assertTrue(page_range_overlaps(18, 19, [[2, 2], [19, 21]]))
        self.assertFalse(page_range_overlaps(3, 18, [[2, 2], [19, 21]]))

    def test_rejects_empty_or_malformed_ranges(self):
        for value in ([], [0, 2], [3, 2], [[1]], [[1, "2"]], "1-2"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_relevant_ranges(value)


class ActualReviewArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = json.loads(DEFAULT_BENCHMARK_PATH.read_text(encoding="utf-8"))
        cls.review = build_review()

    def test_all_questions_appear_once_with_original_text_and_labels(self):
        benchmark_by_id = {item["id"]: item for item in self.benchmark["questions"]}
        review_by_id = {item["id"]: item for item in self.review["questions"]}
        self.assertEqual(len(self.review["questions"]), 40)
        self.assertEqual(len(review_by_id), 40)
        self.assertEqual(set(review_by_id), set(benchmark_by_id))
        for question_id, item in review_by_id.items():
            original = benchmark_by_id[question_id]
            with self.subTest(question_id=question_id):
                self.assertEqual(item["question"], original["question"])
                self.assertEqual(item["case_name"], original["expected_case"])
                self.assertEqual(
                    item["original_relevant_ranges"], original["relevant_pages"]
                )
                self.assertEqual(
                    item["original_benchmark_metadata"]["expected_source_file"],
                    original["expected_source_file"],
                )

    def test_every_human_decision_is_pending_and_empty(self):
        self.assertEqual(self.review["pending_review_count"], 40)
        for item in self.review["questions"]:
            self.assertEqual(
                item["human_review"],
                {
                    "status": "pending",
                    "accepted_relevant_ranges": [],
                    "notes": "",
                },
            )

    def test_each_question_has_all_twenty_saved_appearances(self):
        for item in self.review["questions"]:
            with self.subTest(question_id=item["id"]):
                appearances = sum(
                    len(candidate["appearances"])
                    for candidate in item["candidates"]
                )
                self.assertEqual(appearances, 20)
                self.assertEqual(
                    len({candidate["candidate_id"] for candidate in item["candidates"]}),
                    item["candidate_count"],
                )
                self.assertTrue(
                    all(candidate["chunk_text"] for candidate in item["candidates"])
                )

    def test_all_four_misses_receive_highest_priority(self):
        highest = {
            item["id"]
            for item in self.review["priority_order"]
            if item["tier"] == "highest"
        }
        self.assertEqual(highest, {"DRE-04", "NYT-02", "NYT-03", "OBE-01"})


if __name__ == "__main__":
    unittest.main()
