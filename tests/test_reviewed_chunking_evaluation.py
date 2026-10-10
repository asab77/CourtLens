"""Tests for human-reviewed benchmark finalization and local rescoring."""

import json
import unittest
from copy import deepcopy

from finalize_chunking_benchmark import (
    CONFIGURATION_IDS,
    ORIGINAL_BENCHMARK_PATH,
    ORIGINAL_RESULTS_PATH,
    REVIEW_PACKET_PATH,
    aggregate,
    aggregate_by_field,
    build_all,
    build_reviewed_benchmark,
    load_json,
    rescore_saved_results,
    saved_result_is_relevant,
    score_retrieved,
)


class ReviewedBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = load_json(ORIGINAL_BENCHMARK_PATH)
        cls.review = load_json(REVIEW_PACKET_PATH)
        cls.reviewed = build_reviewed_benchmark(cls.original, cls.review)

    def test_all_40_ids_and_metadata_are_unchanged(self):
        originals = {item["id"]: item for item in self.original["questions"]}
        reviewed = {item["id"]: item for item in self.reviewed["questions"]}
        self.assertEqual(len(reviewed), 40)
        self.assertEqual(set(reviewed), set(originals))
        for question_id, item in reviewed.items():
            with self.subTest(question_id=question_id):
                source = originals[question_id]
                for field in ("type", "question", "expected_case", "expected_source_file"):
                    self.assertEqual(item[field], source[field])
                self.assertEqual(item["original_relevant_ranges"], source["relevant_pages"])

    def test_ranges_are_valid_unique_inclusive_integer_pairs(self):
        for item in self.reviewed["questions"]:
            ranges = item["relevant_ranges"]
            self.assertEqual(len(ranges), len({tuple(interval) for interval in ranges}))
            for start, end in ranges:
                self.assertIs(type(start), int)
                self.assertIs(type(end), int)
                self.assertGreaterEqual(start, 1)
                self.assertLessEqual(start, end)

    def test_established_manual_decisions_are_preserved(self):
        questions = {item["id"]: item for item in self.reviewed["questions"]}
        self.assertEqual(questions["DRE-04"]["relevant_ranges"], [[3, 4]])
        self.assertEqual(
            questions["NYT-02"]["relevant_ranges"],
            [[1, 2], [13, 15], [19, 22]],
        )
        self.assertEqual(
            questions["NYT-03"]["relevant_ranges"],
            [[2, 2], [13, 15], [19, 20]],
        )


class LocalRescoringTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "expected_case": "Case",
            "expected_source_file": "case.pdf",
            "relevant_ranges": [[5, 7], [20, 20]],
        }

    def saved(self, rank, start, end, case="Case", source="case.pdf"):
        return {
            "rank": rank,
            "vector_id": rank - 1,
            "similarity": 0.9 - rank / 10,
            "case_name": case,
            "source_file": source,
            "original_source_file": "original.pdf",
            "page_start": start,
            "page_end": end,
            "chunk_index": rank - 1,
            "token_count": 10,
            "relevant": False,
        }

    def test_multi_range_page_intersection_and_source_case_requirements(self):
        self.assertTrue(saved_result_is_relevant(self.saved(1, 4, 5), self.item))
        self.assertTrue(saved_result_is_relevant(self.saved(1, 20, 21), self.item))
        self.assertFalse(saved_result_is_relevant(self.saved(1, 8, 19), self.item))
        self.assertFalse(saved_result_is_relevant(self.saved(1, 5, 7, case="Other"), self.item))
        self.assertFalse(saved_result_is_relevant(self.saved(1, 5, 7, source="other.pdf"), self.item))

    def test_metric_recomputation(self):
        scored = score_retrieved(
            [self.saved(1, 1, 2), self.saved(2, 19, 20), self.saved(3, 5, 7)],
            self.item,
        )
        self.assertEqual(scored["first_relevant_rank"], 2)
        self.assertEqual(scored["hit_at_1"], 0.0)
        self.assertEqual(scored["hit_at_3"], 1.0)
        self.assertEqual(scored["hit_at_5"], 1.0)
        self.assertEqual(scored["reciprocal_rank"], 0.5)

    def test_aggregation_by_question_type_and_case(self):
        questions = [
            {"type": "facts", "expected_case": "A", "metrics": {"hit_at_1": 1.0, "hit_at_3": 1.0, "hit_at_5": 1.0, "reciprocal_rank": 1.0}},
            {"type": "facts", "expected_case": "B", "metrics": {"hit_at_1": 0.0, "hit_at_3": 1.0, "hit_at_5": 1.0, "reciprocal_rank": 0.5}},
        ]
        configuration = {"questions": questions}
        self.assertEqual(aggregate(questions)["mrr"], 0.75)
        self.assertEqual(aggregate_by_field(configuration, "type")["facts"]["question_count"], 2)
        self.assertEqual(aggregate_by_field(configuration, "expected_case")["A"]["mrr"], 1.0)

    def test_rescoring_does_not_mutate_original_results(self):
        original = load_json(ORIGINAL_RESULTS_PATH)
        before = deepcopy(original)
        benchmark = build_reviewed_benchmark(
            load_json(ORIGINAL_BENCHMARK_PATH), load_json(REVIEW_PACKET_PATH)
        )
        rescore_saved_results(original, benchmark)
        self.assertEqual(original, before)

    def test_output_is_deterministic(self):
        first = build_all()
        second = build_all()
        self.assertEqual(first, second)
        self.assertEqual(
            tuple(item["id"] for item in first[1]["configurations"]),
            CONFIGURATION_IDS,
        )


if __name__ == "__main__":
    unittest.main()
