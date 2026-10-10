"""Unit tests for local document-structure analysis heuristics."""

import unittest

import tiktoken

from analyze_document_structure import (
    analyze_text,
    heading_like_lines,
    paragraph_units,
    parse_extracted_text,
    roman_section_value,
    sentence_units,
)
from chunk_text import ENCODING_NAME


def extracted(body: str, pages: int = 1) -> str:
    return (
        "Case name: Example v. Sample\n"
        "Source file: original.pdf\n"
        "Descriptive source file: example_v_sample.pdf\n"
        f"Total PDF pages: {pages}\n\n"
        f"===== PAGE 1 =====\n\n{body}"
    )


class ParsingTests(unittest.TestCase):
    def test_page_boundaries_do_not_create_blank_line_paragraphs(self):
        text = extracted("First page text.", pages=2) + (
            "\n\n===== PAGE 2 =====\n\nSecond page text."
        )
        parsed = parse_extracted_text(text)
        paragraphs, boundaries = paragraph_units(parsed["content"])
        self.assertEqual(parsed["page_numbers"], [1, 2])
        self.assertEqual(boundaries, 0)
        self.assertEqual(paragraphs, ["First page text.\nSecond page text."])

    def test_empty_content_has_zero_statistics(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        result = analyze_text(extracted(""), encoding)
        self.assertEqual(result["total_characters"], 0)
        self.assertEqual(result["total_words"], 0)
        self.assertEqual(result["paragraph_statistics"]["count"], 0)
        self.assertEqual(result["sentence_statistics"]["count"], 0)

    def test_malformed_headers_and_missing_pages_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "metadata headers"):
            parse_extracted_text("not an extracted CourtLens file")
        malformed = (
            "Case name: Example\nSource file: x.pdf\n"
            "Descriptive source file: x.pdf\nTotal PDF pages: 1\nNo marker"
        )
        with self.assertRaisesRegex(ValueError, "no PDF page markers"):
            parse_extracted_text(malformed)


class UnitHeuristicTests(unittest.TestCase):
    def test_paragraph_statistics_use_retained_blank_lines(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        result = analyze_text(extracted("Short.\n\nA longer second paragraph."), encoding)
        expected_lengths = [
            len(encoding.encode("Short.")),
            len(encoding.encode("A longer second paragraph.")),
        ]
        stats = result["paragraph_statistics"]
        self.assertEqual(stats["count"], 2)
        self.assertEqual(result["blank_line_paragraph_boundaries"], 1)
        self.assertEqual(stats["max_tokens"], max(expected_lengths))
        self.assertEqual(stats["median_tokens"], sum(expected_lengths) / 2)

    def test_sentence_statistics_and_common_abbreviations(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        paragraphs = ["Mr. Smith cited the U. S. Reports. Then he stopped! Final question?"]
        sentences = sentence_units(paragraphs)
        self.assertEqual(
            sentences,
            ["Mr. Smith cited the U. S. Reports.", "Then he stopped!", "Final question?"],
        )
        result = analyze_text(extracted(paragraphs[0]), encoding)
        self.assertEqual(result["sentence_statistics"]["count"], 3)
        self.assertGreater(result["sentence_statistics"]["max_tokens"], 0)

    def test_heading_and_opinion_marker_detection(self):
        headings = heading_like_lines(
            [
                "Syllabus\nOPINION OF THE COURT\nII.\n"
                "JUSTICE SAMPLE, dissenting.\nORDINARY MIXED CASE TEXT"
            ]
        )
        self.assertEqual(headings["opinion_marker_counts"]["syllabus"], 1)
        self.assertEqual(headings["opinion_marker_counts"]["majority_opinion"], 1)
        self.assertEqual(headings["opinion_marker_counts"]["dissent"], 1)
        self.assertEqual(headings["roman_section_marker_frequencies"], {"II": 1})
        self.assertGreaterEqual(headings["heading_type_counts"]["short_all_caps"], 2)

    def test_roman_numeral_detection_is_standalone_and_conservative(self):
        self.assertEqual(roman_section_value("IV."), "IV")
        self.assertEqual(roman_section_value("  XII  "), "XII")
        self.assertIsNone(roman_section_value("Part IV"))
        self.assertIsNone(roman_section_value("civil"))
        self.assertIsNone(roman_section_value("I. Introduction"))


if __name__ == "__main__":
    unittest.main()
