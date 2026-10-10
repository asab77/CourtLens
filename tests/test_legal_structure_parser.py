"""Focused tests for the Phase 4A deterministic structural parser."""

import json
import tempfile
import unittest
from pathlib import Path

import tiktoken

from chunk_text import ENCODING_NAME
from parse_legal_structure import (
    analyze_document,
    build_preview,
    canonical_text,
    detect_boundaries,
    detect_case_caption,
    detect_sections,
    parse_extracted_pages,
    segment_sentences,
)


def extracted(pages: list[str]) -> str:
    body = "".join(
        f"\n\n===== PAGE {index} =====\n\n{text}"
        for index, text in enumerate(pages, start=1)
    )
    return (
        "Case name: Example v. Sample\n"
        "Source file: original.pdf\n"
        "Descriptive source file: example_v_sample.pdf\n"
        f"Total PDF pages: {len(pages)}\n{body}"
    )


class BoundaryRuleTests(unittest.TestCase):
    def lines(self, body: str) -> list[dict]:
        return parse_extracted_pages(extracted([body]))["lines"]

    def test_explicit_majority_concurrence_and_dissent_boundaries(self):
        body = (
            "MR. CHIEF JUSTICE TANEY delivered the opinion of the Court.\nMajority.\n"
            "JUSTICE WHITE, concurring.\nConcurrence.\n"
            "MR. JUSTICE BLACK, dissenting.\nDissent."
        )
        boundaries, _ = detect_boundaries(self.lines(body))
        self.assertEqual(
            [(item["opinion_type"], item["author"]) for item in boundaries],
            [("majority", "Taney"), ("concurrence", "White"), ("dissent", "Black")],
        )

    def test_words_inside_prose_do_not_trigger_boundaries(self):
        body = (
            "The advocate described Justice White as concurring in an older case.\n"
            "A citation discussed Mr. Justice Black, dissenting in another opinion.\n"
            "Ordinary text follows."
        )
        boundaries, _ = detect_boundaries(self.lines(body))
        self.assertEqual(boundaries, [])

    def test_running_headers_do_not_trigger_boundaries(self):
        boundaries, _ = detect_boundaries(
            self.lines("BLACK, J., dissenting 403 U. S.\nReporter text.")
        )
        self.assertEqual(boundaries, [])

    def test_wrapped_modern_heading_and_unknown_heading(self):
        body = (
            "Chief Justice Roberts, with whom Justice Scalia and\n"
            "Justice Thomas join, dissenting.\nText.\n"
            "UNEXPLAINED OPINION LABEL\nMore text."
        )
        boundaries, _ = detect_boundaries(self.lines(body))
        self.assertEqual(len(boundaries), 1)
        self.assertEqual(boundaries[0]["opinion_type"], "dissent")
        self.assertEqual(boundaries[0]["author"], "Roberts")

    def test_discussion_of_a_dissenting_opinion_is_not_a_boundary(self):
        boundaries, _ = detect_boundaries(
            self.lines("Justice Holmes, dissenting in a celebrated case, observed:\nQuoted text.")
        )
        self.assertEqual(boundaries, [])

    def test_ocr_tolerant_judicial_title_still_requires_explicit_status(self):
        body = (
            "YR. JusTIoE BRowN, after stating the case, delivered the opinion of the court.\nMajority.\n"
            "MR. JbsTM \" CLARK, dissenting in Nos. 1 and 2, and concurring in No. 3.\nSeparate opinion."
        )
        boundaries, _ = detect_boundaries(self.lines(body))
        self.assertEqual([item["opinion_type"] for item in boundaries], ["majority", "other"])
        self.assertEqual([item["author"] for item in boundaries], ["Brown", "Clark"])

    def test_no_boundary_document_becomes_one_unknown_unit(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.txt"
            path.write_text(extracted(["Only undifferentiated text."]), encoding="utf-8")
            document = analyze_document(path, encoding)
        self.assertEqual(len(document["major_units"]), 1)
        self.assertEqual(document["major_units"][0]["opinion_type"], "unknown")

    def test_preceding_case_opinion_is_preserved_as_foreign_before_caption(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        source = extracted(
            [
                "OTHER v. MATTER.\n"
                "MR. JUSTICE CURTIS delivered the opinion of the Court.\n"
                "Foreign case text.\n"
                "EXAMPLE v. SAMPLE.\n"
                "Actual case front matter.\n"
                "MR. CHIEF JUSTICE TANEY delivered the opinion of the Court.\n"
                "Actual opinion."
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.txt"
            path.write_text(source, encoding="utf-8")
            document = analyze_document(path, encoding)
        self.assertTrue(document["case_identity"]["activated"])
        self.assertEqual(
            [unit["opinion_type"] for unit in document["major_units"]],
            ["foreign", "unknown", "majority"],
        )
        self.assertIn("Foreign case text", document["major_units"][0]["text"])
        self.assertIn("EXAMPLE v. SAMPLE", document["major_units"][1]["text"])

    def test_front_matter_before_majority_is_not_marked_foreign(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        source = extracted(
            [
                "EXAMPLE v. SAMPLE.\nLengthy argument and front matter.\n"
                "MR. CHIEF JUSTICE TANEY delivered the opinion of the Court.\nOpinion."
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.txt"
            path.write_text(source, encoding="utf-8")
            document = analyze_document(path, encoding)
        self.assertFalse(document["case_identity"]["activated"])
        self.assertEqual(document["major_units"][0]["opinion_type"], "unknown")


class ProvenanceAndSegmentationTests(unittest.TestCase):
    def test_page_transition_text_metadata_and_coverage_are_preserved(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        source = extracted(
            [
                "Syllabus.\nPage one text.",
                "JUSTICE WHITE, concurring.\nPage two text.",
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.txt"
            path.write_text(source, encoding="utf-8")
            document = analyze_document(path, encoding)
        self.assertTrue(document["coverage"]["matches"])
        self.assertEqual(document["source_file"], "example_v_sample.pdf")
        self.assertEqual(document["original_source_file"], "original.pdf")
        self.assertEqual(document["major_units"][0]["page_start"], 1)
        self.assertEqual(document["major_units"][-1]["page_end"], 2)
        for unit in document["major_units"]:
            self.assertEqual(unit["case_name"], "Example v. Sample")
            self.assertEqual(unit["source_file"], "example_v_sample.pdf")
            self.assertEqual(unit["original_source_file"], "original.pdf")
            self.assertEqual(unit["boundary_strength"], "hard")
        reconstructed = canonical_text("\n".join(u["text"] for u in document["major_units"]))
        self.assertIn("Page one text.", reconstructed)
        self.assertIn("Page two text.", reconstructed)

    def test_sections_are_standalone_and_conservative(self):
        lines = parse_extracted_pages(
            extracted(["I.\nText.\nII. INTRODUCTION\nPart IV is ordinary prose.\ncivil"])
        )["lines"]
        sections = detect_sections(lines)
        self.assertEqual([(item["marker"], item["title"]) for item in sections], [("I", None), ("II", "INTRODUCTION")])

    def test_sentence_segmentation_protects_legal_abbreviations_and_pages(self):
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        lines = parse_extracted_pages(
            extracted(["Mr. Smith cited 410 U. S. 113. Then he stopped."])
        )["lines"]
        sentences, diagnostics = segment_sentences(lines, encoding)
        self.assertEqual([item["text"] for item in sentences], ["Mr. Smith cited 410 U. S. 113.", "Then he stopped."])
        self.assertEqual(diagnostics["sentence_count"], 2)
        self.assertTrue(all(item["page_start"] == item["page_end"] == 1 for item in sentences))

    def test_output_is_deterministic_json_serializable_and_all_cases_present(self):
        first = build_preview()
        second = build_preview()
        self.assertEqual(first, second)
        self.assertEqual(first["case_count"], 8)
        self.assertEqual(len(first["documents"]), 8)
        self.assertTrue(all(doc["coverage"]["matches"] for doc in first["documents"]))
        for document in first["documents"]:
            units = document["major_units"]
            self.assertEqual(units[0]["line_start_index"], 0)
            for left, right in zip(units, units[1:]):
                self.assertEqual(
                    left["line_end_index_exclusive"], right["line_start_index"]
                )
        json.dumps(first)

    def test_priority_case_boundaries_and_marbury_front_matter_do_not_regress(self):
        documents = {item["case_name"]: item for item in build_preview()["documents"]}

        dred = documents["Dred Scott v. Sandford"]
        self.assertTrue(dred["case_identity"]["activated"])
        self.assertEqual(dred["major_units"][0]["opinion_type"], "foreign")
        self.assertEqual(dred["major_units"][1]["opinion_type"], "unknown")
        self.assertTrue(dred["major_units"][1]["text"].startswith("DRED SCOTT"))
        self.assertFalse(
            any(
                unit["opinion_type"] == "majority" and unit["author"] == "Curtis"
                for unit in dred["major_units"]
            )
        )

        marbury = documents["Marbury v. Madison"]
        self.assertEqual(marbury["major_units"][0]["opinion_type"], "unknown")
        self.assertEqual(marbury["major_units"][0]["token_count"], 11160)
        self.assertEqual(marbury["major_units"][0]["page_start"], 1)
        self.assertEqual(marbury["major_units"][0]["page_end"], 17)

        nyt = documents["New York Times Co. v. United States"]
        self.assertEqual(
            [(unit["opinion_type"], unit["author"]) for unit in nyt["major_units"]],
            [
                ("unknown", None), ("syllabus", None), ("majority", "Per Curiam"),
                ("concurrence", "Black"), ("concurrence", "Douglas"),
                ("concurrence", "Brennan"), ("concurrence", "Stewart"),
                ("concurrence", "White"), ("concurrence", "Marshall"),
                ("dissent", "Burger"), ("dissent", "Harlan"),
                ("dissent", "Blackmun"),
            ],
        )

        obergefell = documents["Obergefell v. Hodges"]
        self.assertEqual(
            [(unit["opinion_type"], unit["author"]) for unit in obergefell["major_units"]],
            [
                ("unknown", None), ("syllabus", None), ("majority", "Kennedy"),
                ("dissent", "Roberts"), ("dissent", "Scalia"),
                ("dissent", "Thomas"), ("dissent", "Alito"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
