"""Conservatively parse CourtLens opinions into reviewable legal structure.

Phase 4A is local analysis only. This module does not import retrieval, embedding,
or vector-store code and does not create chunks.
"""

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

import tiktoken

from chunk_text import ENCODING_NAME, PROCESSED_DIR


PROJECT_DIR = Path(__file__).resolve().parent
JSON_PATH = PROJECT_DIR / "data/analysis/structure_aware_preview.json"
REPORT_PATH = PROJECT_DIR / "data/analysis/structure_aware_preview.md"

PAGE_MARKER = re.compile(r"^===== PAGE (\d+) =====\s*$", re.MULTILINE)
SYLLABUS = re.compile(r"^syllabus\.?$", re.IGNORECASE)
PER_CURIAM = re.compile(r"^per\s+curiam\.?$", re.IGNORECASE)
MAJORITY_DELIVERY = re.compile(
    r"^(?:(?:mr\.\s+)?(?:chief\s+)?justice\s+([a-z][a-z.'’\-]+)\s+)?"
    r"(?:delivered\s+the\s+(?:opinion|oninion)\s+of\s+the\s+court|"
    r"opinion\s+of\s+the\s+court\s+was\s+delivered\s+by\s+the\s+chief\s+ju(?:s|f)tice)\.?.*$",
    re.IGNORECASE,
)
EXPLICIT_JUDICIAL_START = re.compile(
    r"^(?:mr\.\s+)?(?:(?:chief\s+)?justice)\s+([a-z][a-z.'’\-]+)\b",
    re.IGNORECASE,
)
OCR_JUDICIAL_START = re.compile(
    r"^(?:mr\.|[A-Z]{2,4}\.)\s+j[a-z\"' .]{2,12}\s+([A-Z][A-Z.'’\-]{2,})\b",
    re.IGNORECASE,
)
STANDALONE_JUSTICE = re.compile(
    r"^(?:mr\.\s+)?(?:(?:chief\s+)?justice)\s+([a-z][a-z.'’\-]+)\.\s*$",
    re.IGNORECASE,
)
ROMAN_SECTION = re.compile(r"^([IVXLCDM]{1,8})\.?$")
ROMAN_TITLED_SECTION = re.compile(r"^([IVXLCDM]{1,8})\.\s+(.{3,70})$")
SENTENCE_END = re.compile(r"[.!?](?:[\"”’']|\])?(?=\s+[\"“‘'(]?[A-Z0-9])")
ABBREVIATION = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|No|Nos|J|JJ|C|U|S|v|vs|e\.g|i\.e|cf|id|ibid|"
    r"Inc|Co|Dept|Rev|Stat|Supp|Ann|Art|Amdt|ch|pp)\.(?=\s|$)",
    re.IGNORECASE,
)
REPORTER_CITATION = re.compile(r"\b(\d+)\s+U\.\s*S\.")
RUNNING_OPINION_HEADER = re.compile(
    r"^(?:\d+\s+)?(?:opinion of the court|"
    r"[A-Z][A-Z.'’ \-]+,\s*(?:C\.\s*J\.|J\.),\s*(?:concurring|dissenting)|"
    r"dissenting opinion:)\b",
    re.IGNORECASE,
)


def canonical_text(text: str) -> str:
    """Normalize whitespace only, for defensible text-coverage comparison."""
    return " ".join(text.split())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_extracted_pages(text: str) -> dict:
    """Read extraction metadata and retain every page line with page identity."""
    lines = text.splitlines(keepends=True)
    headers = (
        "Case name: ",
        "Source file: ",
        "Descriptive source file: ",
        "Total PDF pages: ",
    )
    if len(lines) < 4 or any(
        not lines[index].startswith(header) for index, header in enumerate(headers)
    ):
        raise ValueError("missing expected extraction metadata headers")
    try:
        declared_pages = int(lines[3].removeprefix(headers[3]).strip())
    except ValueError as error:
        raise ValueError("invalid Total PDF pages header") from error
    body = "".join(lines[4:])
    markers = list(PAGE_MARKER.finditer(body))
    page_numbers = [int(marker.group(1)) for marker in markers]
    if not markers or page_numbers != list(range(1, declared_pages + 1)):
        raise ValueError("page markers must represent every declared page in order")

    pages = []
    flat_lines = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(body)
        page_text = body[marker.end() : end].strip()
        page = page_numbers[index]
        page_lines = page_text.splitlines()
        pages.append({"page": page, "text": page_text})
        for line_on_page, raw in enumerate(page_lines, start=1):
            flat_lines.append(
                {
                    "page": page,
                    "line_on_page": line_on_page,
                    "text": raw,
                    "normalized": " ".join(raw.split()),
                }
            )
    return {
        "case_name": lines[0].removeprefix(headers[0]).strip(),
        "original_source_file": lines[1].removeprefix(headers[1]).strip(),
        "source_file": lines[2].removeprefix(headers[2]).strip(),
        "declared_pdf_pages": declared_pages,
        "pages": pages,
        "lines": flat_lines,
    }


def candidate_text(lines: list[dict], start: int, width: int) -> str | None:
    """Join up to three nonblank lines on one page for wrapped headings."""
    selected = lines[start : start + width]
    if len(selected) != width or any(not item["normalized"] for item in selected):
        return None
    if len({item["page"] for item in selected}) != 1:
        return None
    return " ".join(item["normalized"] for item in selected)


def normalize_author(author: str | None) -> str | None:
    if not author:
        return None
    return author.strip(" .,'\"").title()


def case_name_anchors(case_name: str) -> list[str]:
    """Return conservative party-name anchors for a caption identity check."""
    parts = re.split(r"\s+v\.\s+", case_name, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2:
        return []
    stopwords = {"co", "company", "inc", "et", "al", "the", "dist"}
    anchors = []
    for part in parts:
        tokens = [
            token.lower()
            for token in re.findall(r"[A-Za-z]{3,}", part)
            if token.lower() not in stopwords
        ]
        if not tokens:
            return []
        anchors.extend(tokens)
    return anchors


def detect_case_caption(lines: list[dict], case_name: str) -> dict | None:
    """Find the first one-to-three-line caption containing all party anchors."""
    anchors = case_name_anchors(case_name)
    if not anchors:
        return None
    for index in range(len(lines)):
        for width in (1, 2, 3):
            candidate = candidate_text(lines, index, width)
            if not candidate:
                continue
            normalized = " ".join(re.findall(r"[a-z]+", candidate.lower()))
            words = set(normalized.split())
            if all(anchor in words for anchor in anchors):
                matched_offsets = [
                    offset
                    for offset, item in enumerate(lines[index : index + width])
                    if set(re.findall(r"[a-z]+", item["normalized"].lower()))
                    & set(anchors)
                ]
                caption_start = index + min(matched_offsets)
                caption_end = index + max(matched_offsets) + 1
                caption_lines = lines[caption_start:caption_end]
                return {
                    "line_index": caption_start,
                    "heading_line_count": len(caption_lines),
                    "page": lines[caption_start]["page"],
                    "heading": " ".join(item["normalized"] for item in caption_lines),
                    "anchors": anchors,
                }
    return None


def classify_authored_heading(text: str) -> dict | None:
    """Recognize explicit authored headings, including wrapped headings."""
    start = EXPLICIT_JUDICIAL_START.match(text)
    ocr_start = OCR_JUDICIAL_START.match(text)
    if not start and not ocr_start:
        return None
    author = normalize_author((start or ocr_start).group(1))
    lowered = text.lower()
    # This construction introduces a quotation or discussion of another case,
    # rather than a separately authored component in the current document.
    if not text.rstrip().endswith("."):
        return None
    if re.search(r"\bdissenting(?: opinion)? in\b.*\b(?:case|observed)\b", lowered):
        return None
    author_end = (start or ocr_start).end()
    tail = text[author_end:]
    if not re.match(r"^(?:\s*,|\s+dissenting\b|\s+concurring\b)", tail, re.I):
        return None
    has_concurrence = bool(re.search(r"\bconcurr(?:ing|ence)\b", lowered))
    has_dissent = bool(re.search(r"\bdissent(?:ing|ence)\b", lowered))
    if not has_concurrence and not has_dissent:
        return None
    if has_concurrence and has_dissent:
        opinion_type = "other"
        reason = "explicit authored mixed concurrence/dissent heading"
    elif has_dissent:
        opinion_type = "dissent"
        reason = "explicit authored dissent heading"
    else:
        opinion_type = "concurrence"
        reason = "explicit authored concurrence heading"
    return {
        "opinion_type": opinion_type,
        "author": author,
        "confidence": "high" if start else "medium",
        "reason": reason + (" with OCR-tolerant judicial-title match" if ocr_start else ""),
        "pattern": "authored_separate_opinion",
    }


def detect_boundaries(lines: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return hard major-component boundaries and unresolved heading candidates."""
    boundaries = []
    ambiguous = []
    syllabus_seen = False
    index = 0
    while index < len(lines):
        line = lines[index]["normalized"]
        if not line:
            index += 1
            continue
        boundary = None
        width = 1
        if SYLLABUS.fullmatch(line) and not syllabus_seen:
            syllabus_seen = True
            boundary = {
                "opinion_type": "syllabus",
                "author": None,
                "confidence": "high",
                "reason": "first standalone Syllabus label",
                "pattern": "syllabus_label",
            }
        elif PER_CURIAM.fullmatch(line):
            boundary = {
                "opinion_type": "majority",
                "author": "Per Curiam",
                "confidence": "high",
                "reason": "standalone PER CURIAM attribution",
                "pattern": "per_curiam",
            }
        else:
            for candidate_width in (1, 2, 3):
                candidate = candidate_text(lines, index, candidate_width)
                if not candidate:
                    continue
                majority = MAJORITY_DELIVERY.match(candidate)
                ocr_majority = (
                    OCR_JUDICIAL_START.match(candidate)
                    if re.search(
                        r"\bdelivered\s+the\s+(?:opinion|oninion)\s+of\s+the\s+court\b",
                        candidate,
                        re.IGNORECASE,
                    )
                    else None
                )
                if majority:
                    boundary = {
                        "opinion_type": "majority",
                        "author": normalize_author(majority.group(1)),
                        "confidence": "high",
                        "reason": "explicit delivery of the opinion of the Court",
                        "pattern": "majority_delivery",
                    }
                    width = candidate_width
                    break
                if ocr_majority:
                    boundary = {
                        "opinion_type": "majority",
                        "author": normalize_author(ocr_majority.group(1)),
                        "confidence": "medium",
                        "reason": "explicit delivery of the opinion of the Court with OCR-tolerant judicial-title match",
                        "pattern": "majority_delivery_ocr_tolerant",
                    }
                    width = candidate_width
                    break
                authored = classify_authored_heading(candidate)
                if authored:
                    boundary = authored
                    width = candidate_width
                    break

        if boundary is None:
            standalone = STANDALONE_JUSTICE.fullmatch(line)
            if standalone:
                following = next(
                    (
                        item["normalized"]
                        for item in lines[index + 1 : index + 4]
                        if item["normalized"]
                    ),
                    "",
                )
                opinion_type = (
                    "concurrence"
                    if re.match(
                        r"^(?:While I join the opinion of the Court|Concurring as I do|I concur(?: in| with))\b",
                        following,
                        re.I,
                    )
                    else "other"
                )
                boundary = {
                    "opinion_type": opinion_type,
                    "author": normalize_author(standalone.group(1)),
                    "confidence": "medium",
                    "reason": (
                        "standalone justice attribution followed by an express statement joining the Court"
                        if opinion_type == "concurrence"
                        else "standalone justice attribution between opinion text"
                    ),
                    "pattern": "standalone_justice_attribution",
                }

        if boundary:
            heading = candidate_text(lines, index, width) or line
            boundaries.append(
                {
                    "line_index": index,
                    "heading_line_count": width,
                    "page": lines[index]["page"],
                    "heading": heading,
                    **boundary,
                }
            )
            index += width
            continue

        lowered = line.lower()
        if (
            len(line) <= 180
            and re.search(r"\b(?:concurring|dissenting|opinion of the court)\b", lowered)
            and not RUNNING_OPINION_HEADER.match(line)
        ):
            ambiguous.append(
                {"page": lines[index]["page"], "text": line, "reason": "opinion language without a high-confidence boundary form"}
            )
        index += 1

    # Remove exact duplicate boundaries at one line, preserving the first rule.
    unique = []
    seen = set()
    for item in boundaries:
        if item["line_index"] not in seen:
            unique.append(item)
            seen.add(item["line_index"])
    return unique, ambiguous


def running_header_diagnostics(lines: list[dict]) -> dict:
    matches = [
        {"page": item["page"], "text": item["normalized"]}
        for item in lines
        if item["normalized"] and RUNNING_OPINION_HEADER.match(item["normalized"])
    ]
    return {"ignored_running_header_count": len(matches), "ignored_running_header_examples": matches[:12]}


def page_range(lines: list[dict]) -> tuple[int, int]:
    pages = [item["page"] for item in lines]
    return min(pages), max(pages)


def line_char_spans(lines: list[dict]) -> tuple[str, list[tuple[int, int, int]]]:
    pieces = []
    spans = []
    cursor = 0
    for index, item in enumerate(lines):
        if index:
            pieces.append("\n")
            cursor += 1
        value = item["text"]
        start = cursor
        pieces.append(value)
        cursor += len(value)
        spans.append((start, cursor, item["page"]))
    return "".join(pieces), spans


def pages_for_span(start: int, end: int, spans: list[tuple[int, int, int]]) -> tuple[int, int]:
    pages = [page for line_start, line_end, page in spans if start <= line_end and end >= line_start]
    if not pages:
        raise ValueError("sentence span has no page provenance")
    return min(pages), max(pages)


def protect_sentence_periods(text: str) -> str:
    protected = ABBREVIATION.sub(lambda match: match.group(0).replace(".", "∯"), text)
    return REPORTER_CITATION.sub(lambda match: match.group(0).replace(".", "∯"), protected)


def segment_sentences(lines: list[dict], encoding) -> tuple[list[dict], dict]:
    """Approximate sentences while retaining page ranges and surfacing outliers."""
    text, spans = line_char_spans(lines)
    protected = protect_sentence_periods(text)
    sentences = []
    start = 0
    for match in SENTENCE_END.finditer(protected):
        end = match.end()
        raw = text[start:end]
        normalized = canonical_text(raw)
        if normalized:
            page_start, page_end = pages_for_span(start, end, spans)
            sentences.append(
                {
                    "sentence_index": len(sentences),
                    "page_start": page_start,
                    "page_end": page_end,
                    "token_count": len(encoding.encode(normalized)),
                    "text": normalized,
                }
            )
        start = end
    remainder = canonical_text(text[start:])
    if remainder:
        page_start, page_end = pages_for_span(start, len(text), spans)
        sentences.append(
            {
                "sentence_index": len(sentences),
                "page_start": page_start,
                "page_end": page_end,
                "token_count": len(encoding.encode(remainder)),
                "text": remainder,
            }
        )
    lengths = [item["token_count"] for item in sentences]
    diagnostics = {
        "sentence_count": len(sentences),
        "median_sentence_tokens": round(float(statistics.median(lengths)), 2) if lengths else 0,
        "maximum_sentence_tokens": max(lengths, default=0),
        "sentences_over_200_tokens": sum(length > 200 for length in lengths),
        "long_sentence_examples": [
            {"sentence_index": item["sentence_index"], "page_start": item["page_start"], "page_end": item["page_end"], "token_count": item["token_count"], "excerpt": item["text"][:300]}
            for item in sentences if item["token_count"] > 200
        ][:5],
    }
    return sentences, diagnostics


def detect_sections(lines: list[dict]) -> list[dict]:
    """Detect only standalone Roman markers or Roman markers with uppercase titles."""
    sections = []
    for relative_index, item in enumerate(lines):
        line = item["normalized"]
        marker = ROMAN_SECTION.fullmatch(line)
        title = None
        if not marker:
            titled = ROMAN_TITLED_SECTION.fullmatch(line)
            if titled:
                letters = [char for char in titled.group(2) if char.isalpha()]
                uppercase_ratio = (
                    sum(char.isupper() for char in letters) / len(letters) if letters else 0
                )
                if len(letters) >= 3 and uppercase_ratio >= 0.8:
                    marker = titled
                    title = titled.group(2)
        if marker:
            sections.append(
                {
                    "section_index": len(sections),
                    "marker": marker.group(1),
                    "title": title,
                    "page": item["page"],
                    "relative_line_index": relative_index,
                    "confidence": "high",
                    "reason": "standalone Roman marker" if title is None else "Roman marker with short uppercase title",
                }
            )
    return sections


def apply_case_identity_boundary(parsed: dict, boundaries: list[dict]) -> tuple[list[dict], dict]:
    """Prevent an opinion before the expected caption from inheriting case identity.

    The refinement activates only when a conservative caption match occurs after an
    already detected opinion boundary. Ordinary front matter before a majority is
    unaffected.
    """
    caption = detect_case_caption(parsed["lines"], parsed["case_name"])
    if not caption:
        return boundaries, {"activated": False, "reason": "no conservative caption match"}
    preceding = [
        item
        for item in boundaries
        if item["line_index"] < caption["line_index"]
        and item["opinion_type"] in {"majority", "concurrence", "dissent", "other"}
    ]
    if not preceding:
        return boundaries, {
            "activated": False,
            "reason": "no opinion boundary precedes the matching case caption",
            "caption": caption,
        }
    retained = [item for item in boundaries if item["line_index"] >= caption["line_index"]]
    retained.insert(
        0,
        {
            "line_index": caption["line_index"],
            "heading_line_count": caption["heading_line_count"],
            "page": caption["page"],
            "heading": caption["heading"],
            "opinion_type": "unknown",
            "author": None,
            "confidence": "high",
            "reason": "caption contains all expected case-party anchors after foreign opinion material",
            "pattern": "case_caption_identity",
        },
    )
    return retained, {
        "activated": True,
        "caption": caption,
        "suppressed_pre_caption_opinion_boundaries": [item["heading"] for item in preceding],
    }


def build_units(
    parsed: dict, boundaries: list[dict], encoding, case_identity: dict
) -> list[dict]:
    lines = parsed["lines"]
    starts = [item["line_index"] for item in boundaries]
    if not starts or starts[0] != 0:
        leading_is_foreign = case_identity.get("activated", False)
        boundaries = [
            {
                "line_index": 0,
                "heading_line_count": 0,
                "page": lines[0]["page"],
                "heading": None,
                "opinion_type": "foreign" if leading_is_foreign else "unknown",
                "author": None,
                "confidence": "low",
                "reason": (
                    "source text before the matching case caption; preserved but not attributed to the metadata case"
                    if leading_is_foreign
                    else "text before the first confidently detected major component"
                ),
                "pattern": "foreign_pre_case_text" if leading_is_foreign else "unassigned_leading_text",
            },
            *boundaries,
        ]
    units = []
    for unit_index, boundary in enumerate(boundaries):
        start = boundary["line_index"]
        end = boundaries[unit_index + 1]["line_index"] if unit_index + 1 < len(boundaries) else len(lines)
        unit_lines = lines[start:end]
        if not unit_lines:
            continue
        text, _ = line_char_spans(unit_lines)
        page_start, page_end = page_range(unit_lines)
        sentences, sentence_diagnostics = segment_sentences(unit_lines, encoding)
        sections = detect_sections(unit_lines)
        token_count = len(encoding.encode(text))
        units.append(
            {
                "unit_index": len(units),
                "unit_type": (
                    "foreign_or_unassigned_source_material"
                    if boundary["opinion_type"] == "foreign"
                    else "major_legal_component"
                ),
                "boundary_strength": "hard",
                "case_name": parsed["case_name"],
                "source_file": parsed["source_file"],
                "original_source_file": parsed["original_source_file"],
                "opinion_type": boundary["opinion_type"],
                "author": boundary["author"],
                "line_start_index": start,
                "line_end_index_exclusive": end,
                "page_start": page_start,
                "page_end": page_end,
                "token_count": token_count,
                "boundary": {
                    "heading": boundary["heading"],
                    "page": boundary["page"],
                    "pattern": boundary["pattern"],
                    "confidence": boundary["confidence"],
                    "reason": boundary["reason"],
                },
                "sections": sections,
                "sentences": sentences,
                "sentence_diagnostics": sentence_diagnostics,
                "beginning_excerpt": canonical_text(text)[:350],
                "ending_excerpt": canonical_text(text)[-350:],
                "text": text,
            }
        )
    return units


def validate_document_structure(document: dict, expected_line_count: int) -> None:
    """Validate source identity, ordering, page provenance, and hard boundaries."""
    units = document["major_units"]
    if not units:
        raise ValueError("A structural document must contain at least one major unit")
    expected_start = 0
    for expected_index, unit in enumerate(units):
        if unit["unit_index"] != expected_index:
            raise ValueError("Major unit indexes are not consecutive")
        if unit["line_start_index"] != expected_start:
            raise ValueError("Major units overlap or leave a gap in document order")
        if unit["line_end_index_exclusive"] <= unit["line_start_index"]:
            raise ValueError("Major unit has an empty or reversed line interval")
        expected_start = unit["line_end_index_exclusive"]
        if unit["page_start"] < 1 or unit["page_start"] > unit["page_end"]:
            raise ValueError("Major unit has an invalid page range")
        if unit["page_end"] > document["document_pages"]:
            raise ValueError("Major unit exceeds the declared document pages")
        if unit["case_name"] != document["case_name"] or unit["source_file"] != document["source_file"]:
            raise ValueError("Major unit lost its document source identity")
        if unit["original_source_file"] != document["original_source_file"]:
            raise ValueError("Major unit lost its original source identity")
        if unit["boundary_strength"] != "hard":
            raise ValueError("Major opinion/component boundaries must be explicit hard boundaries")
        if any(
            sentence["page_start"] < unit["page_start"]
            or sentence["page_end"] > unit["page_end"]
            or sentence["page_start"] > sentence["page_end"]
            for sentence in unit["sentences"]
        ):
            raise ValueError("Sentence page provenance falls outside its major unit")
    if expected_start != expected_line_count:
        raise ValueError("Major units do not cover the complete extracted document")


def analyze_document(path: Path, encoding) -> dict:
    parsed = parse_extracted_pages(path.read_text(encoding="utf-8"))
    boundaries, ambiguous = detect_boundaries(parsed["lines"])
    boundaries, case_identity = apply_case_identity_boundary(parsed, boundaries)
    units = build_units(parsed, boundaries, encoding, case_identity)
    original = canonical_text("\n".join(page["text"] for page in parsed["pages"]))
    reconstructed = canonical_text("\n".join(unit["text"] for unit in units))
    coverage_matches = original == reconstructed
    if not coverage_matches:
        raise ValueError(f"Structural parsing dropped or changed text in {path}")
    unit_tokens = [unit["token_count"] for unit in units]
    unknown_tokens = sum(unit["token_count"] for unit in units if unit["opinion_type"] == "unknown")
    diagnostics = {
        "major_unit_count": len(units),
        "opinion_boundary_match_count": sum(unit["boundary"]["pattern"] != "unassigned_leading_text" for unit in units),
        "section_boundary_match_count": sum(len(unit["sections"]) for unit in units),
        "opinion_types_detected": sorted({unit["opinion_type"] for unit in units}),
        "authors_detected": [unit["author"] for unit in units if unit["author"]],
        "unknown_unit_count": sum(unit["opinion_type"] == "unknown" for unit in units),
        "unknown_token_count": unknown_tokens,
        "suspiciously_small_units_under_200_tokens": [unit["unit_index"] for unit in units if unit["token_count"] < 200],
        "suspiciously_large_units_over_25000_tokens": [unit["unit_index"] for unit in units if unit["token_count"] > 25_000],
        "ambiguous_heading_candidate_count": len(ambiguous),
        "ambiguous_heading_candidates": ambiguous[:30],
        **running_header_diagnostics(parsed["lines"]),
        "sentence_count": sum(len(unit["sentences"]) for unit in units),
        "sentences_over_200_tokens": sum(unit["sentence_diagnostics"]["sentences_over_200_tokens"] for unit in units),
        "possible_false_positive_risks": (
            (["Standalone justice attributions without an express opinion type are treated as boundaries at medium confidence."]
             if any(unit["boundary"]["pattern"] == "standalone_justice_attribution" for unit in units) else [])
            + (["More than one majority-delivery heading was detected; the source may contain a preceding-case fragment or another embedded opinion."]
               if sum(unit["opinion_type"] == "majority" for unit in units) > 1 else [])
        ),
        "possible_false_negative_risks": [
            "OCR-corrupted or implicit opinion headings may remain inside another or unknown unit.",
            "Repeated reporter running headers are intentionally ignored even when they name an opinion type."
        ],
    }
    document = {
        "case_name": parsed["case_name"],
        "source_file": parsed["source_file"],
        "original_source_file": parsed["original_source_file"],
        "processed_file": path.name,
        "document_pages": parsed["declared_pdf_pages"],
        "document_token_count": len(encoding.encode(original)),
        "major_units": units,
        "diagnostics": diagnostics,
        "case_identity": case_identity,
        "coverage": {
            "method": "SHA-256 of page-marker-free text after whitespace-only canonicalization",
            "normalization": "metadata headers and page-marker lines excluded; all remaining whitespace collapsed",
            "original_sha256": digest(original),
            "reconstructed_sha256": digest(reconstructed),
            "matches": coverage_matches,
        },
    }
    validate_document_structure(document, len(parsed["lines"]))
    return document


def build_preview(processed_dir: Path = PROCESSED_DIR) -> dict:
    paths = sorted(processed_dir.glob("*.txt"))
    if len(paths) != 8:
        raise ValueError(f"Expected 8 processed cases, found {len(paths)}")
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    documents = [analyze_document(path, encoding) for path in paths]
    return {
        "analysis": "CourtLens Phase 4A structure-aware parsing preview",
        "phase": "4A",
        "purpose": "human review before any structure-aware chunk construction",
        "tokenizer": ENCODING_NAME,
        "case_count": len(documents),
        "rules": {
            "hard_boundaries": "First Syllabus label; standalone PER CURIAM; explicit delivery of the opinion of the Court; explicit authored concurrence/dissent; medium-confidence standalone justice attribution.",
            "ignored_as_boundaries": "Reporter running headers such as 'BLACK, J., dissenting 403 U. S.' and prose/citations mentioning concurrence or dissent.",
            "sections": "Standalone Roman numerals, optionally followed by a short >=80% uppercase title; section markers do not create major units.",
            "sentences": "Terminal punctuation with protection for common legal abbreviations and U.S. reporter citations; page spans retained; long segments surfaced as diagnostics.",
        },
        "documents": documents,
    }


def escape(value: str | None) -> str:
    return (value or "—").replace("|", "\\|").replace("\n", " ")


def render_report(preview: dict) -> str:
    priority_review_notes = {
        "Dred Scott v. Sandford": (
            "A caption-identity conflict rule now preserves the opening Sturgis/Honold material as foreign source text and begins Dred Scott front matter at the `DRED SCOTT ... v. ... SANDFORD` caption. The Taney boundary and both express dissents are strong; the intervening standalone justice attributions are intentionally medium confidence, and several raw author names remain visibly OCR-corrupted."
        ),
        "New York Times Co. v. United States": (
            "The parser finds the short per curiam disposition, six separately authored concurrences, and three dissents. All authored splits use explicit headings; 49 repeated reporter headers were ignored rather than treated as new opinions."
        ),
        "Obergefell v. Hodges": (
            "The parser finds the syllabus, Kennedy majority, and four separately authored dissents by Roberts, Scalia, Thomas, and Alito. These boundaries are explicit and high confidence; the many reporter headers and syllabus filing summaries are retained without becoming splits."
        ),
    }
    lines = [
        "# CourtLens Phase 4A: Structure-Aware Parsing Preview",
        "",
        "This is a deterministic local parsing preview for human review. It does not contain final chunks and makes no retrieval-performance claim.",
        "",
        "## Parser rules",
        "",
        "- **Hard major-component boundaries:** the first standalone `Syllabus` label, standalone `PER CURIAM`, an explicit delivery of the opinion of the Court, explicit authored concurrence/dissent headings, and medium-confidence standalone justice attributions.",
        "- **Case identity:** when a confidently detected opinion occurs before a later caption containing every expected party-name anchor, the pre-caption text is preserved as `foreign` and cannot inherit the metadata case's opinion type.",
        "- **Ignored as hard boundaries:** repeated reporter headers, citations, and ordinary prose mentioning concurrences or dissents.",
        "- **Sections:** standalone Roman numerals or Roman numerals followed by a short predominantly uppercase title. Sections are preferred boundaries for a future phase, not opinion boundaries.",
        "- **Sentences:** terminal punctuation after protecting common legal abbreviations and `U. S.` reporter citations. Long segments are reported because OCR and citations still defeat the heuristic.",
        "- **Text preservation:** metadata and artificial page-marker lines are excluded. All page text is retained in order; coverage is checked after whitespace-only canonicalization.",
        "",
        "## Corpus summary",
        "",
        "| Case | Pages | Tokens | Major units | Opinion boundaries | Sections | Unknown units | Ambiguous candidates |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for doc in preview["documents"]:
        d = doc["diagnostics"]
        lines.append(
            f"| {doc['case_name']} | {doc['document_pages']} | {doc['document_token_count']:,} | {d['major_unit_count']} | {d['opinion_boundary_match_count']} | {d['section_boundary_match_count']} | {d['unknown_unit_count']} | {d['ambiguous_heading_candidate_count']} |"
        )
    lines += ["", "## Per-case structural preview", ""]
    detail_cases = {
        "Dred Scott v. Sandford",
        "New York Times Co. v. United States",
        "Obergefell v. Hodges",
    }
    for doc in preview["documents"]:
        d = doc["diagnostics"]
        lines += [
            f"### {doc['case_name']}",
            "",
            f"Pages: **{doc['document_pages']}** · Tokens: **{doc['document_token_count']:,}** · Major units: **{len(doc['major_units'])}** · Coverage: **{'pass' if doc['coverage']['matches'] else 'fail'}**",
            "",
            "| Unit | Opinion type | Author | Pages | Tokens | Boundary confidence | Trigger | Sections |",
            "|---:|---|---|---:|---:|---|---|---:|",
        ]
        for unit in doc["major_units"]:
            boundary = unit["boundary"]
            lines.append(
                f"| {unit['unit_index']} | {unit['opinion_type']} | {escape(unit['author'])} | {unit['page_start']}–{unit['page_end']} | {unit['token_count']:,} | {boundary['confidence']} | {escape(boundary['heading'])} | {len(unit['sections'])} |"
            )
        lines += [
            "",
            f"Detected types: {', '.join(d['opinion_types_detected'])}. Detected authors: {', '.join(d['authors_detected']) or 'none'}. Sentences over 200 tokens: {d['sentences_over_200_tokens']}. Repeated reporter headers ignored: {d['ignored_running_header_count']}.",
            "",
        ]
        if doc["case_name"] in detail_cases:
            lines += [
                "#### Priority review note",
                "",
                priority_review_notes[doc["case_name"]],
                "",
                "#### Boundary inspection details",
                "",
            ]
            for unit in doc["major_units"]:
                boundary = unit["boundary"]
                section_text = ", ".join(
                    f"{section['marker']}{('. ' + section['title']) if section['title'] else ''} (p. {section['page']})"
                    for section in unit["sections"]
                ) or "none"
                lines += [
                    f"**Unit {unit['unit_index']} — {unit['opinion_type']} / {unit['author'] or 'author unknown'} / pp. {unit['page_start']}–{unit['page_end']}**",
                    "",
                    f"Trigger: `{boundary['heading'] or 'leading unassigned text'}` ({boundary['confidence']}; {boundary['reason']}).",
                    "",
                    f"Sections: {section_text}.",
                    "",
                    f"Beginning: “{unit['beginning_excerpt']}”",
                    "",
                    f"Ending: “{unit['ending_excerpt']}”",
                    "",
                ]
        if d["ambiguous_heading_candidates"]:
            lines += ["Ambiguous candidate examples:", ""]
            for candidate in d["ambiguous_heading_candidates"][:8]:
                lines.append(f"- p. {candidate['page']}: `{candidate['text']}`")
            lines.append("")
        if d["suspiciously_small_units_under_200_tokens"] or d["suspiciously_large_units_over_25000_tokens"]:
            lines += [
                f"Size diagnostics: units under 200 tokens: {d['suspiciously_small_units_under_200_tokens'] or 'none'}; units over 25,000 tokens: {d['suspiciously_large_units_over_25000_tokens'] or 'none'}.",
                "",
            ]
        if d["possible_false_positive_risks"] or d["possible_false_negative_risks"]:
            lines += ["Boundary risks:", ""]
            for risk in d["possible_false_positive_risks"]:
                lines.append(f"- Possible false positive: {risk}")
            for risk in d["possible_false_negative_risks"]:
                lines.append(f"- Possible false negative: {risk}")
            lines.append("")
    lines += [
        "## Uncertainty and human-review priorities",
        "",
        "- OCR corruption can hide a true heading or distort an author name. The parser keeps such text even when it cannot classify it.",
        "- Medium-confidence standalone justice attributions are useful for older reports, but they deserve manual review because the line may introduce commentary rather than a new opinion.",
        "- Repeated running headers are excluded from boundary detection. This prevents many false splits but can miss a boundary when the true heading was lost in extraction.",
        "- Sentence segmentation is an approximation. Long reported segments identify places where abbreviations, citations, OCR, or unusual punctuation prevented a clean split.",
        "- An `unknown` leading unit means the parser could not confidently assign front matter, argument, an earlier case fragment, or a syllabus-like component to an opinion.",
        "",
        "The three priority cases should be reviewed unit by unit before Phase 4B. Questionable boundaries are intentionally surfaced here rather than silently corrected.",
    ]
    return "\n".join(lines) + "\n"


def write_preview(preview: dict) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(preview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(preview), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="analyze and validate without writing")
    args = parser.parse_args()
    preview = build_preview()
    if not args.check:
        write_preview(preview)
        print(f"Wrote {JSON_PATH.relative_to(PROJECT_DIR)}")
        print(f"Wrote {REPORT_PATH.relative_to(PROJECT_DIR)}")
    else:
        print(f"Validated {preview['case_count']} cases with complete text coverage")


if __name__ == "__main__":
    main()
