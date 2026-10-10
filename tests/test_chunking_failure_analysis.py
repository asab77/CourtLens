"""Focused tests for local fixed-chunking failure analysis."""

import unittest

from analyze_chunking_failures import (
    locally_relevant,
    select_questions,
)


class RelevanceTests(unittest.TestCase):
    benchmark = {
        "expected_case": "Example v. Case",
        "expected_source_file": "example.pdf",
        "relevant_pages": [[10, 12]],
    }

    def result(self, **overrides):
        result = {
            "case_name": "Example v. Case",
            "source_file": "example.pdf",
            "original_source_file": "original.pdf",
            "page_start": 12,
            "page_end": 14,
        }
        result.update(overrides)
        return result

    def test_relevance_requires_case_source_and_page_intersection(self):
        self.assertTrue(locally_relevant(self.result(), self.benchmark))
        self.assertFalse(
            locally_relevant(self.result(case_name="Other v. Case"), self.benchmark)
        )
        self.assertFalse(
            locally_relevant(self.result(source_file="other.pdf"), self.benchmark)
        )
        self.assertFalse(
            locally_relevant(self.result(page_start=13, page_end=14), self.benchmark)
        )


class SelectionTests(unittest.TestCase):
    def comparison(
        self,
        question_id,
        rank_1200,
        rank_1500,
        category,
        all_miss=False,
    ):
        miss_rank = 6
        return {
            "id": question_id,
            "case_name": "Example v. Case",
            "question": "Question?",
            "relevant_pages": [[1, 2]],
            "ranks": {
                "600_100": None if all_miss else 2,
                "900_150": None if all_miss else 2,
                "1200_200": rank_1200,
                "1500_200": rank_1500,
            },
            "pairwise_category": category,
            "all_four_miss": all_miss,
            "rank_improvement": abs(
                (rank_1200 or miss_rank) - (rank_1500 or miss_rank)
            ),
        }

    def test_selection_balances_miss_transitions_and_large_rank_gains(self):
        miss_to_one = self.comparison("A", None, 1, "1500_wins")
        miss_to_three = self.comparison("B", None, 3, "1500_wins")
        five_to_one = self.comparison("C", 5, 1, "1500_wins")
        four_to_one = self.comparison("D", 4, 1, "1500_wins")
        miss_to_five = self.comparison("E", None, 5, "1500_wins")

        selected = select_questions(
            [miss_to_one, miss_to_three, five_to_one, four_to_one, miss_to_five]
        )

        self.assertEqual([item["id"] for item in selected], ["A", "B", "C", "D"])

    def test_selection_includes_all_universal_misses(self):
        comparisons = [
            self.comparison(f"L{index}", 5, 1, "1500_wins")
            for index in range(5)
        ]
        comparisons.extend(
            self.comparison(f"S{index}", 1, 5, "1200_wins")
            for index in range(4)
        )
        comparisons.extend(
            self.comparison(f"M{index}", None, None, "tie", all_miss=True)
            for index in range(3)
        )

        selected = select_questions(comparisons)
        categories = [item["selection_category"] for item in selected]

        self.assertEqual(categories.count("1500_wins"), 4)
        self.assertEqual(categories.count("1200_wins"), 3)
        self.assertEqual(categories.count("all_four_miss"), 3)


if __name__ == "__main__":
    unittest.main()
