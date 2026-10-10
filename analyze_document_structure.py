"""Describe structural signals in CourtLens extracted Supreme Court opinions."""

import argparse
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

import tiktoken

from chunk_text import ENCODING_NAME, PROCESSED_DIR


PROJECT_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = PROJECT_DIR / "data" / "analysis"
JSON_PATH = ANALYSIS_DIR / "document_structure.json"
REPORT_PATH = ANALYSIS_DIR / "document_structure_report.md"

PAGE_MARKER = re.compile(r"^===== PAGE (\d+) =====\s*$", re.MULTILINE)
BLANK_LINE_BOUNDARY = re.compile(r"\n[ \t]*\n+")
WORD = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b", re.UNICODE)
ROMAN_SECTION = re.compile(r"^[IVXLCDM]{1,8}\.?$")
NUMBERED_SECTION = re.compile(r"^\d{1,3}\.$")
SENTENCE_END = re.compile(r"[.!?](?:[\"”’']|\])?(?=\s+[\"“‘'(]?[A-Z0-9])")
ABBREVIATION = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|No|Nos|J|JJ|C|U|S|v)\.(?=\s|$)", re.IGNORECASE
)


def parse_extracted_text(text: str) -> dict:
    """Parse extraction metadata and remove artificial page-marker boundaries."""
    lines = text.splitlines(keepends=True)
    expected_headers = (
        "Case name: ",
        "Source file: ",
        "Descriptive source file: ",
        "Total PDF pages: ",
    )
    if len(lines) < 4 or any(
        not lines[index].startswith(header)
        for index, header in enumerate(expected_headers)
    ):
        raise ValueError("missing expected extraction metadata headers")

    try:
        declared_pages = int(lines[3].removeprefix(expected_headers[3]).strip())
    except ValueError as error:
        raise ValueError("invalid Total PDF pages header") from error
    if declared_pages < 1:
        raise ValueError("Total PDF pages must be positive")

    body = "".join(lines[4:])
    markers = list(PAGE_MARKER.finditer(body))
    if not markers:
        raise ValueError("no PDF page markers found")

    page_numbers = [int(marker.group(1)) for marker in markers]
    if page_numbers != sorted(set(page_numbers)):
        raise ValueError("PDF page markers must be unique and increasing")

    page_texts = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(body)
        page_texts.append(body[marker.end() : end].strip())

    # Join pages with one newline so extraction-inserted blank lines do not masquerade
    # as paragraph boundaries. Blank lines found inside each page remain intact.
    content = "\n".join(page_texts).strip()
    return {
        "case_name": lines[0].removeprefix(expected_headers[0]).strip(),
        "original_source_file": lines[1].removeprefix(expected_headers[1]).strip(),
        "source_file": lines[2].removeprefix(expected_headers[2]).strip(),
        "declared_pdf_pages": declared_pages,
        "page_numbers": page_numbers,
        "page_texts": page_texts,
        "content": content,
    }


def percentile(values: list[int], percent: float) -> float:
    """Return a linearly interpolated percentile, or zero for no observations."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def distribution(values: list[int]) -> dict:
    """Summarize a sequence of token lengths."""
    return {
        "count": len(values),
        "median_tokens": round(float(statistics.median(values)), 2) if values else 0.0,
        "mean_tokens": round(statistics.fmean(values), 2) if values else 0.0,
        "p90_tokens": round(percentile(values, 90), 2),
        "max_tokens": max(values, default=0),
    }


def paragraph_units(content: str) -> tuple[list[str], int]:
    """Split only at blank lines retained within extracted PDF page text."""
    if not content.strip():
        return [], 0
    boundaries = len(BLANK_LINE_BOUNDARY.findall(content))
    paragraphs = [part.strip() for part in BLANK_LINE_BOUNDARY.split(content) if part.strip()]
    return paragraphs, boundaries


def _protect_abbreviation_periods(text: str) -> str:
    return ABBREVIATION.sub(lambda match: match.group(0).replace(".", "∯"), text)


def sentence_units(paragraphs: list[str]) -> list[str]:
    """Approximate sentences using terminal punctuation after common abbreviations."""
    sentences = []
    for paragraph in paragraphs:
        normalized = " ".join(paragraph.split())
        if not normalized:
            continue
        protected = _protect_abbreviation_periods(normalized)
        start = 0
        for match in SENTENCE_END.finditer(protected):
            end = match.end()
            sentence = normalized[start:end].strip()
            if sentence:
                sentences.append(sentence)
            start = end
        remainder = normalized[start:].strip()
        if remainder:
            sentences.append(remainder)
    return sentences


def roman_section_value(line: str) -> str | None:
    """Return a normalized standalone Roman-numeral marker when present."""
    stripped = line.strip()
    if not ROMAN_SECTION.fullmatch(stripped):
        return None
    return stripped.removesuffix(".")


def opinion_marker_type(line: str) -> str | None:
    """Conservatively label lines that look like opinion-component markers."""
    stripped = " ".join(line.split())
    lowered = stripped.lower()
    if re.fullmatch(r"syllabus\.?(?:\s+\d+\s+u\.\s*s\.?)?", lowered):
        return "syllabus"
    if "delivered the opinion of the court" in lowered or re.match(
        r"^opinion of the court(?:\.|\s|$)", lowered
    ):
        return "majority_opinion"
    if len(stripped) <= 120 and "(" not in stripped:
        judicial_label = bool(
            re.search(r"\b(?:justice|chief|j\.|jj\.)\b", lowered)
            or re.match(r"^[A-Z][A-Z .'-]{2,},", stripped)
        )
        if judicial_label and re.search(r"\bconcurring\b", lowered):
            return "concurrence"
        if judicial_label and re.search(r"\bdissenting\b", lowered):
            return "dissent"
    return None


def heading_like_lines(page_texts: list[str]) -> dict:
    """Detect explicit marker lines and conservative short all-caps headings."""
    detections = []
    type_counts = Counter()
    roman_counts = Counter()
    opinion_counts = Counter()
    numbered_count = 0

    for page_number, page_text in enumerate(page_texts, start=1):
        for raw_line in page_text.splitlines():
            line = " ".join(raw_line.split())
            if not line:
                continue
            kinds = []
            roman = roman_section_value(line)
            if roman:
                kinds.append("roman_section")
                roman_counts[roman] += 1
            if NUMBERED_SECTION.fullmatch(line):
                kinds.append("numbered_section")
                numbered_count += 1
            opinion_type = opinion_marker_type(line)
            if opinion_type:
                kinds.append(opinion_type)
                opinion_counts[opinion_type] += 1

            letters = [character for character in line if character.isalpha()]
            uppercase_ratio = (
                sum(character.isupper() for character in letters) / len(letters)
                if letters
                else 0
            )
            if (
                3 <= len(line) <= 120
                and len(letters) >= 3
                and uppercase_ratio >= 0.9
                and not line.endswith((";", ",", ":"))
            ):
                kinds.append("short_all_caps")

            if kinds:
                unique_kinds = list(dict.fromkeys(kinds))
                type_counts.update(unique_kinds)
                detections.append(
                    {"page": page_number, "text": line, "types": unique_kinds}
                )

    return {
        "heading_like_line_count": len(detections),
        "heading_type_counts": dict(sorted(type_counts.items())),
        "heading_examples": detections[:20],
        "roman_section_marker_count": sum(roman_counts.values()),
        "roman_section_marker_frequencies": dict(sorted(roman_counts.items())),
        "numbered_section_marker_count": numbered_count,
        "opinion_marker_counts": {
            marker: opinion_counts.get(marker, 0)
            for marker in ("syllabus", "majority_opinion", "concurrence", "dissent")
        },
    }


def analyze_text(text: str, encoding) -> dict:
    """Analyze one extracted case without external services."""
    parsed = parse_extracted_text(text)
    content = parsed["content"]
    paragraphs, boundary_count = paragraph_units(content)
    sentences = sentence_units(paragraphs)
    paragraph_lengths = [len(encoding.encode(item)) for item in paragraphs]
    sentence_lengths = [len(encoding.encode(item)) for item in sentences]
    headings = heading_like_lines(parsed["page_texts"])
    page_numbers = parsed["page_numbers"]
    token_count = len(encoding.encode(content))
    rate_denominator = max(token_count, 1) / 10_000

    return {
        "case_name": parsed["case_name"],
        "source_file": parsed["source_file"],
        "original_source_file": parsed["original_source_file"],
        "total_characters": len(content),
        "total_words": len(WORD.findall(content)),
        "approximate_tokens": token_count,
        "declared_pdf_pages": parsed["declared_pdf_pages"],
        "pdf_pages_represented": len(page_numbers),
        "page_number_min": min(page_numbers),
        "page_number_max": max(page_numbers),
        "page_sequence_complete": page_numbers
        == list(range(1, parsed["declared_pdf_pages"] + 1)),
        "blank_line_paragraph_boundaries": boundary_count,
        "paragraph_statistics": distribution(paragraph_lengths),
        "sentence_statistics": distribution(sentence_lengths),
        **headings,
        "heading_like_lines_per_10k_tokens": round(
            headings["heading_like_line_count"] / rate_denominator, 2
        ),
        "roman_markers_per_10k_tokens": round(
            headings["roman_section_marker_count"] / rate_denominator, 2
        ),
    }


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _marker_summary(case: dict) -> str:
    markers = case["opinion_marker_counts"]
    present = [
        name.replace("_", " ")
        for name, count in markers.items()
        if count
    ]
    return ", ".join(present) if present else "none detected"


def build_report(cases: list[dict]) -> str:
    """Render measured results and restrained interpretations as Markdown."""
    lines = [
        "# CourtLens Document Structure Analysis",
        "",
        "This local descriptive analysis asks whether the eight extracted opinions expose "
        "different structural signals that could justify a later chunking experiment. It "
        "does not measure retrieval quality and does not claim that structure-aware "
        "chunking is better.",
        "",
        "## Heuristics and interpretation limits",
        "",
        f"Token counts use `{ENCODING_NAME}`, the tokenizer used by CourtLens. Metadata and "
        "`===== PAGE N =====` markers are excluded from content statistics. Page-marker "
        "boundaries are joined with one newline so their injected blank lines are not "
        "counted as paragraph boundaries. Paragraphs split only on blank lines retained "
        "inside extracted pages.",
        "",
        "Sentences are approximate: normalized paragraph text is split at `.`, `?`, or `!` "
        "when followed by a likely new sentence, after protecting a small list of common "
        "legal abbreviations. OCR errors, citations, initials, hyphenation, and hard line "
        "wraps can still distort sentence measurements.",
        "",
        "Heading-like lines are standalone Roman numerals, standalone numbered markers, "
        "conservative syllabus/opinion/concurrence/dissent marker matches, or short lines "
        "whose letters are at least 90% uppercase. These are signals, not a parsed opinion "
        "outline. Running headers repeat across pages and can inflate heading and opinion "
        "marker counts. Marker presence is more trustworthy than its raw frequency.",
        "",
        "## Comparison",
        "",
        "| Case | Pages | Characters | Words | Approx. tokens | Paragraphs | Para median | Para mean | Para p90 | Para max | Sentences | Sent. median | Sent. mean | Sent. p90 | Sent. max | Blank boundaries | Heading-like | Roman |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for case in cases:
        paragraph = case["paragraph_statistics"]
        sentence = case["sentence_statistics"]
        row = [
            case["case_name"],
            case["pdf_pages_represented"],
            case["total_characters"],
            case["total_words"],
            case["approximate_tokens"],
            paragraph["count"],
            paragraph["median_tokens"],
            paragraph["mean_tokens"],
            paragraph["p90_tokens"],
            paragraph["max_tokens"],
            sentence["count"],
            sentence["median_tokens"],
            sentence["mean_tokens"],
            sentence["p90_tokens"],
            sentence["max_tokens"],
            case["blank_line_paragraph_boundaries"],
            case["heading_like_line_count"],
            case["roman_section_marker_count"],
        ]
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")

    lines.extend(
        [
            "",
            "### Explicit marker summary",
            "",
            "| Case | Syllabus | Majority | Concurrence | Dissent | Numbered | Heading-like / 10k tokens | Roman / 10k tokens | Roman sequence frequencies |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for case in cases:
        markers = case["opinion_marker_counts"]
        roman = case["roman_section_marker_frequencies"]
        roman_text = ", ".join(f"{key}: {value}" for key, value in roman.items()) or "none"
        lines.append(
            f"| {case['case_name']} | {markers['syllabus']} | "
            f"{markers['majority_opinion']} | {markers['concurrence']} | "
            f"{markers['dissent']} | {case['numbered_section_marker_count']} | "
            f"{case['heading_like_lines_per_10k_tokens']:.2f} | "
            f"{case['roman_markers_per_10k_tokens']:.2f} | "
            f"{roman_text} |"
        )

    lines.extend(["", "## Per-case observations", ""])
    for case in cases:
        paragraph = case["paragraph_statistics"]
        sentence = case["sentence_statistics"]
        sequence_note = (
            "all declared PDF pages are represented"
            if case["page_sequence_complete"]
            else "the represented page sequence differs from the declared page count"
        )
        lines.extend(
            [
                f"### {case['case_name']}",
                "",
                f"The extraction contains {_fmt(case['approximate_tokens'])} tokens across "
                f"{case['pdf_pages_represented']} marked pages; {sequence_note}. It has "
                f"{case['blank_line_paragraph_boundaries']} retained blank-line paragraph "
                f"boundaries, so the paragraph heuristic yields {paragraph['count']} "
                f"whole-document unit and cannot recover semantic paragraphs. The sentence "
                f"heuristic finds "
                f"{sentence['count']} units with a median of "
                f"{_fmt(sentence['median_tokens'])} tokens and a 90th percentile of "
                f"{_fmt(sentence['p90_tokens'])}. It detects "
                f"{case['heading_like_line_count']} heading-like line occurrences and "
                f"{case['roman_section_marker_count']} standalone Roman-numeral markers "
                f"({case['roman_markers_per_10k_tokens']:.2f} per 10,000 tokens). "
                f"Conservative opinion markers present: {_marker_summary(case)}.",
                "",
            ]
        )

    sentence_density_rank = sorted(
        cases,
        key=lambda item: (
            item["sentence_statistics"]["p90_tokens"],
            item["sentence_statistics"]["median_tokens"],
        ),
        reverse=True,
    )
    section_rank = sorted(
        cases,
        key=lambda item: (
            item["roman_section_marker_count"] / max(item["approximate_tokens"], 1),
            item["heading_like_line_count"] / max(item["approximate_tokens"], 1),
        ),
        reverse=True,
    )
    dense = sentence_density_rank[:3]
    sectioned = section_rank[:3]
    lines.extend(
        [
            "## Structural density and explicit sectioning",
            "",
            "All eight files have zero retained blank-line boundaries after artificial page "
            "boundaries are removed. Paragraph-based density therefore cannot distinguish "
            "these documents: each becomes one whole-document unit. This is evidence about "
            "the extraction format, not evidence that the opinions lack paragraphs.",
            "",
            "Using approximate sentence length as the remaining local density signal, the "
            "three highest 90th percentiles are "
            + "; ".join(
                f"{item['case_name']} ({_fmt(item['sentence_statistics']['p90_tokens'])} "
                f"tokens; median {_fmt(item['sentence_statistics']['median_tokens'])})"
                for item in dense
            )
            + ". This sentence heuristic is approximate and especially sensitive to OCR and "
            "legal citations.",
            "",
            "The strongest explicit-section signals after normalizing marker counts by "
            "document token count are "
            + "; ".join(
                f"{item['case_name']} ({item['roman_section_marker_count']} Roman markers, "
                f"{item['roman_markers_per_10k_tokens']:.2f} per 10,000 tokens)"
                for item in sectioned
            )
            + ". New York Times also exposes many concurrence and dissent marker lines despite "
            "only two standalone Roman markers, illustrating that separate-opinion labels and "
            "internal section markers capture different kinds of structure. Running headers "
            "and OCR artifacts mean these comparisons should guide manual inspection rather "
            "than serve as labels.",
            "",
            "## Extraction limitations",
            "",
            "- PDF extraction preserves page order but not a dependable semantic hierarchy. "
            "Hard line wraps, page headers, footers, and page numbers remain in the text.",
            "- Blank-line paragraph boundaries are sparse or inconsistent in some files. A "
            "long measured paragraph may be several visually distinct paragraphs collapsed "
            "by extraction.",
            "- Older scans contain substantial OCR noise, including broken words and altered "
            "characters. That weakens capitalization, heading, word, and sentence heuristics.",
            "- Syllabus and opinion labels often recur as running headers. Counts indicate "
            "available signals, not the number of distinct opinion components.",
            "- Standalone Roman numerals can mark sections, but can also occur in syllabi, "
            "separate opinions, or other enumerations. The analyzer does not infer nesting.",
            "",
            "## Implications for Chunking",
            "",
            "The measured variation supports testing whether a future chunker can use "
            "observable boundaries while retaining token limits. Candidate signals include "
            "standalone Roman or numbered markers, conservative opinion-component markers, "
            "blank-line boundaries when present, and sentence boundaries as a fallback. "
            "Repeated running headers should be de-duplicated or down-weighted before they "
            "become split points.",
            "",
            "A future experiment should preserve the same corpus, embedding model, benchmark, "
            "retrieval settings, and Hit@1/Hit@3/Hit@5/MRR calculations, changing only the "
            "chunk-boundary strategy. It should also enforce maximum token sizes because the "
            "long paragraph units show that structural boundaries alone are insufficient. "
            "These findings motivate a controlled comparison; they do not establish a "
            "retrieval improvement.",
            "",
        ]
    )
    return "\n".join(lines)


def run_analysis(processed_dir: Path = PROCESSED_DIR) -> dict:
    """Analyze every canonical processed case in deterministic filename order."""
    text_paths = sorted(processed_dir.glob("*.txt"))
    if not text_paths:
        raise ValueError(f"No extracted text files found in {processed_dir}")
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    cases = []
    for text_path in text_paths:
        case = analyze_text(text_path.read_text(encoding="utf-8"), encoding)
        case["processed_file"] = text_path.name
        cases.append(case)
    return {
        "analysis": "CourtLens document structure description",
        "case_count": len(cases),
        "tokenizer": ENCODING_NAME,
        "heuristics": {
            "content": "Exclude four metadata headers and page-marker lines; join pages with one newline.",
            "paragraphs": "Split on blank lines retained inside extracted page text.",
            "sentences": "Split approximately at terminal punctuation after protecting common legal abbreviations.",
            "headings": "Standalone Roman/numbered markers, conservative opinion markers, and short >=90% uppercase lines.",
            "warning": "Signals are descriptive heuristics, not a reliable document-outline classifier.",
        },
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--json-output", type=Path, default=JSON_PATH)
    parser.add_argument("--report-output", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_analysis(args.processed_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.report_output.write_text(build_report(result["cases"]), encoding="utf-8")
    print(f"Analyzed {result['case_count']} cases.")
    print(f"Saved machine-readable results to {args.json_output}")
    print(f"Saved report to {args.report_output}")


if __name__ == "__main__":
    main()
