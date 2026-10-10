"""Unit tests for stable page-based chunking experiment metrics."""

import json
import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from run_chunking_experiment import (
    aggregate_metrics,
    DEFAULT_BENCHMARK_PATH,
    evaluate_ranked_results,
    load_benchmark,
    page_range_overlaps,
    print_comparison,
    result_is_relevant,
)


def result(case: str, page_start: int, page_end: int, rank_id: int = 0) -> dict:
    return {
        "vector_id": rank_id,
        "similarity": 0.5,
        "text": "test",
        "metadata": {
            "case_name": case,
            "source_file": "expected.pdf",
            "original_source_file": "opaque.pdf",
            "page_start": page_start,
            "page_end": page_end,
            "chunk_index": rank_id,
            "token_count": 10,
        },
    }


BENCHMARK_ITEM = {
    "expected_case": "Expected v. Case",
    "expected_source_file": "expected.pdf",
    "relevant_pages": [[10, 12], [20, 21]],
}


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = load_benchmark(DEFAULT_BENCHMARK_PATH)
        records_path = Path(__file__).resolve().parents[1] / "data/vector_store/records.jsonl"
        cls.corpus = [json.loads(line)["metadata"] for line in records_path.read_text().splitlines()]

    def test_counts_and_unique_ids(self):
        self.assertEqual(len(self.questions), 40)
        counts = Counter(item["expected_case"] for item in self.questions)
        self.assertEqual(len(counts), 8)
        self.assertEqual(set(counts.values()), {5})
        self.assertEqual(len({item["id"] for item in self.questions}), 40)

    def test_questions_are_nonempty_and_validated(self):
        for item in self.questions:
            with self.subTest(id=item["id"]):
                self.assertTrue(item["question"].strip())
                self.assertTrue(item["type"].strip())
                self.assertIs(item["validated"], True)

    def test_case_source_pairs_and_page_ranges_exist_in_corpus(self):
        for item in self.questions:
            with self.subTest(id=item["id"]):
                records = [m for m in self.corpus if
                           (m["case_name"], m["source_file"]) ==
                           (item["expected_case"], item["expected_source_file"])]
                self.assertTrue(records)
                self.assertTrue(item["relevant_pages"])
                for interval in item["relevant_pages"]:
                    self.assertEqual(len(interval), 2)
                    start, end = interval
                    self.assertIs(type(start), int)
                    self.assertIs(type(end), int)
                    self.assertGreaterEqual(start, 1)
                    self.assertLessEqual(start, end)
                    self.assertLessEqual(end, max(m["page_end"] for m in records))

    def test_obergefell_multiple_ranges(self):
        item = next(q for q in self.questions if q["id"] == "OBE-04")
        self.assertEqual(item["relevant_pages"], [[4, 4], [28, 32]])
        for start, end, relevant in [(4, 4, True), (3, 4, True), (28, 28, True),
                                      (32, 33, True), (5, 27, False), (33, 34, False)]:
            with self.subTest(start=start, end=end):
                chunk = result(item["expected_case"], start, end)
                chunk["metadata"]["source_file"] = item["expected_source_file"]
                self.assertEqual(result_is_relevant(chunk, item), relevant)
                chunk["metadata"]["case_name"] = "Wrong v. Case"
                self.assertFalse(result_is_relevant(chunk, item))


class PageRangeTests(unittest.TestCase):
    def test_inclusive_overlap(self):
        self.assertTrue(page_range_overlaps(8, 10, [[10, 12]]))
        self.assertTrue(page_range_overlaps(12, 15, [[10, 12]]))
        self.assertTrue(page_range_overlaps(11, 11, [[10, 12]]))

    def test_non_overlap_and_missing_pages(self):
        self.assertFalse(page_range_overlaps(1, 9, [[10, 12]]))
        self.assertFalse(page_range_overlaps(13, 20, [[10, 12]]))
        self.assertFalse(page_range_overlaps(None, None, [[10, 12]]))

    def test_relevance_requires_case_source_and_pages(self):
        self.assertTrue(result_is_relevant(result("Expected v. Case", 11, 13), BENCHMARK_ITEM))
        self.assertFalse(result_is_relevant(result("Wrong v. Case", 11, 13), BENCHMARK_ITEM))
        wrong_source = result("Expected v. Case", 11, 13)
        wrong_source["metadata"]["source_file"] = "wrong.pdf"
        self.assertFalse(result_is_relevant(wrong_source, BENCHMARK_ITEM))
        self.assertFalse(result_is_relevant(result("Expected v. Case", 1, 2), BENCHMARK_ITEM))

    def test_proposed_relevant_ranges_field_is_supported(self):
        item = {
            "expected_case": "Expected v. Case",
            "expected_source_file": "expected.pdf",
            "relevant_ranges": [[2, 2], [19, 21]],
        }
        self.assertTrue(result_is_relevant(result("Expected v. Case", 2, 2), item))
        self.assertTrue(result_is_relevant(result("Expected v. Case", 20, 22), item))
        self.assertFalse(result_is_relevant(result("Expected v. Case", 3, 18), item))


class RetrievalMetricTests(unittest.TestCase):
    def test_hit_cutoffs_and_metric_names(self):
        for first_rank in range(1, 7):
            ranked = [result("Wrong v. Case", 10, 12, i) for i in range(6)]
            ranked[first_rank - 1] = result("Expected v. Case", 10, 12, first_rank - 1)
            metrics = evaluate_ranked_results(ranked, BENCHMARK_ITEM)
            for cutoff in (1, 3, 5):
                self.assertEqual(metrics[f"hit_at_{cutoff}"], float(first_rank <= cutoff))
            self.assertEqual(metrics["reciprocal_rank"], 1 / first_rank if first_rank <= 5 else 0)
            aggregate = aggregate_metrics([{"metrics": metrics}])
            self.assertEqual(set(aggregate), {"question_count", "hit_at_1", "hit_at_3", "hit_at_5", "mrr"})
            self.assertFalse(any(key.startswith("recall") for key in metrics))

    def test_comparison_uses_hit_labels(self):
        output = StringIO()
        metrics = aggregate_metrics([{"metrics": evaluate_ranked_results([], BENCHMARK_ITEM)}])
        with redirect_stdout(output):
            print_comparison([{"chunk_size": 600, "chunk_overlap": 100, "metrics": metrics}])
        for label in ("Hit@1", "Hit@3", "Hit@5", "MRR"):
            self.assertIn(label, output.getvalue())
        self.assertNotIn("Recall@", output.getvalue())

    def test_hit_and_reciprocal_rank_at_rank_two(self):
        ranked = [
            result("Wrong v. Case", 10, 12, 0),
            result("Expected v. Case", 10, 12, 1),
            result("Expected v. Case", 20, 21, 2),
        ]
        metrics = evaluate_ranked_results(ranked, BENCHMARK_ITEM)
        self.assertEqual(metrics["hit_at_1"], 0.0)
        self.assertEqual(metrics["hit_at_3"], 1.0)
        self.assertEqual(metrics["hit_at_5"], 1.0)
        self.assertEqual(metrics["reciprocal_rank"], 0.5)
        self.assertEqual(metrics["first_relevant_rank"], 2)

    def test_zero_when_no_relevant_result_is_retrieved(self):
        metrics = evaluate_ranked_results(
            [result("Wrong v. Case", 10, 12)], BENCHMARK_ITEM
        )
        self.assertEqual(metrics["hit_at_5"], 0.0)
        self.assertEqual(metrics["reciprocal_rank"], 0.0)
        self.assertIsNone(metrics["first_relevant_rank"])

    def test_aggregate_metrics(self):
        question_results = [
            {"metrics": {"hit_at_1": 1.0, "hit_at_3": 1.0, "hit_at_5": 1.0, "reciprocal_rank": 1.0}},
            {"metrics": {"hit_at_1": 0.0, "hit_at_3": 1.0, "hit_at_5": 1.0, "reciprocal_rank": 0.5}},
        ]
        aggregate = aggregate_metrics(question_results)
        self.assertEqual(aggregate["hit_at_1"], 0.5)
        self.assertEqual(aggregate["hit_at_3"], 1.0)
        self.assertEqual(aggregate["hit_at_5"], 1.0)
        self.assertEqual(aggregate["mrr"], 0.75)


if __name__ == "__main__":
    unittest.main()
