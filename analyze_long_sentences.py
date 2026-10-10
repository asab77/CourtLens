"""Review every Phase 4A sentence segment longer than 200 tokens locally."""

import argparse
import json
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
PREVIEW_PATH = PROJECT_DIR / "data/analysis/structure_aware_preview.json"
JSON_PATH = PROJECT_DIR / "data/analysis/long_sentence_analysis.json"
REPORT_PATH = PROJECT_DIR / "data/analysis/long_sentence_analysis.md"
THRESHOLD = 200


# Human review of all 28 oversized segments produced by the Phase 4A parser.
# Keys deliberately include the structural position so unexpected parser drift fails.
REVIEWS = {
    ("Dred Scott v. Sandford", 1, 132): ("page_boundary_artifact", "The sentence continues across pages 6–7 and absorbs the running header because the page break has no sentence-ending punctuation."),
    ("Dred Scott v. Sandford", 2, 190): ("ocr_punctuation_loss", "OCR joins sentence-ending punctuation to the next capitalized word (`State.And`), preventing a normal split."),
    ("Dred Scott v. Sandford", 2, 214): ("genuinely_long_historical_sentence", "A single semicolon-heavy historical sentence remains grammatically continuous."),
    ("Dred Scott v. Sandford", 2, 460): ("genuinely_long_historical_sentence", "A single long constitutional-history sentence uses coordinated clauses and semicolons."),
    ("Dred Scott v. Sandford", 5, 50): ("citation_or_statutory_enumeration", "One sentence enumerates a long series of case citations before stating their common rule."),
    ("Dred Scott v. Sandford", 5, 285): ("ocr_punctuation_loss", "Several apparent sentence endings are fused to following words (`pretended.In`, `jurisdiction; that`) and a footnote line is inserted."),
    ("Dred Scott v. Sandford", 6, 111): ("genuinely_long_historical_sentence", "A lengthy statutory quotation forms one sentence with repeated clauses."),
    ("Dred Scott v. Sandford", 6, 294): ("extraction_layout_or_footnote_interleaving", "A footnote or parallel text block is inserted mid-sentence, mixing the territorial-power discussion with the Farmer's Letters quotation."),
    ("Dred Scott v. Sandford", 6, 350): ("genuinely_long_historical_sentence", "A long enumerative sentence lists many forms of territorial administration."),
    ("Dred Scott v. Sandford", 6, 363): ("ocr_punctuation_loss", "OCR punctuation and dash-prefixed continuations (`. -But`, `.Whatever`) obscure multiple likely sentence boundaries."),
    ("Dred Scott v. Sandford", 9, 12): ("ocr_punctuation_loss", "Multiple sentences are fused without spaces after periods (`jurisdiction.It`, `State.To`)."),
    ("Dred Scott v. Sandford", 9, 58): ("ocr_punctuation_loss", "A long quoted plea is followed by OCR dash-and-period sequences that hide the next sentence boundary."),
    ("Dred Scott v. Sandford", 9, 571): ("extraction_layout_or_footnote_interleaving", "Two quoted passages and a footnote marker are merged into one extracted segment."),
    ("Dred Scott v. Sandford", 9, 733): ("ocr_punctuation_loss", "Question marks and periods are followed by OCR dash-prefixed text, which the conservative splitter does not treat as a new sentence."),
    ("Dred Scott v. Sandford", 9, 786): ("citation_or_statutory_enumeration", "One sentence enumerates a series of territorial statutes and dates."),
    ("Dred Scott v. Sandford", 9, 829): ("ocr_punctuation_loss", "OCR quote marks and punctuation around `While` obscure a likely boundary before a new sentence."),
    ("Dred Scott v. Sandford", 9, 855): ("genuinely_long_historical_sentence", "A single long rhetorical question remains syntactically continuous despite OCR noise."),
    ("Dred Scott v. Sandford", 9, 899): ("ocr_punctuation_loss", "Bullet-like OCR characters after periods prevent several otherwise plausible splits."),
    ("Gideon v. Wainwright", 2, 73): ("extraction_layout_or_footnote_interleaving", "A long footnote citation list is inserted after the opening clause and ends mid-citation."),
    ("Marbury v. Madison", 0, 13): ("extraction_layout_or_footnote_interleaving", "Marginal headnotes and main text are interleaved by column-order extraction, creating a 544-token pseudo-sentence."),
    ("Marbury v. Madison", 0, 30): ("page_boundary_artifact", "A statutory quotation crosses pages 3–4 and absorbs the page header into the continuing sentence."),
    ("Miranda v. Arizona", 1, 418): ("extraction_layout_or_footnote_interleaving", "Footnote 30 is inserted inside a quotation and interrupts the main sentence sequence."),
    ("New York Times Co. v. United States", 7, 54): ("citation_or_statutory_enumeration", "The segment is a long quoted statutory subsection with four enumerated clauses."),
    ("New York Times Co. v. United States", 7, 84): ("citation_or_statutory_enumeration", "The segment quotes the long enumerative text of 18 U.S.C. § 793(e)."),
    ("Obergefell v. Hodges", 3, 206): ("citation_or_statutory_enumeration", "A single citation-dense sentence contains multiple parentheticals and nested quotations."),
    ("Plessy v. Ferguson", 1, 13): ("genuinely_long_historical_sentence", "A single fact-statement sentence uses repeated semicolon-separated clauses."),
    ("Plessy v. Ferguson", 1, 16): ("genuinely_long_historical_sentence", "A single procedural-history sentence contains many coordinated clauses."),
    ("Plessy v. Ferguson", 2, 8): ("citation_or_statutory_enumeration", "A long statutory quotation enumerates penalties, officer powers, and liability rules."),
}

FALLBACK = {
    "genuinely_long_historical_sentence": "yes — a future maximum-size guard must split an indivisible oversized sentence without crossing the enclosing opinion",
    "ocr_punctuation_loss": "yes — token-aware fallback is safer than guessing missing punctuation during parsing",
    "page_boundary_artifact": "yes — preserve provenance, then use a maximum-size fallback if the reconstructed sentence remains oversized",
    "citation_or_statutory_enumeration": "yes — keep the quotation or citation sequence when possible, but enforce the future hard token maximum",
    "extraction_layout_or_footnote_interleaving": "yes — retain source order and use a bounded fallback; automatic text repair would be speculative",
}


def load_preview(path: Path = PREVIEW_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_analysis(preview: dict) -> dict:
    segments = []
    seen = set()
    for document in preview["documents"]:
        for unit in document["major_units"]:
            for sentence in unit["sentences"]:
                if sentence["token_count"] <= THRESHOLD:
                    continue
                key = (document["case_name"], unit["unit_index"], sentence["sentence_index"])
                if key not in REVIEWS:
                    raise ValueError(f"Oversized sentence has no human review: {key}")
                cause, explanation = REVIEWS[key]
                seen.add(key)
                text = sentence["text"]
                segments.append(
                    {
                        "case_name": document["case_name"],
                        "source_file": document["source_file"],
                        "unit_index": unit["unit_index"],
                        "opinion_type": unit["opinion_type"],
                        "author_raw": unit["author"],
                        "sentence_index": sentence["sentence_index"],
                        "page_start": sentence["page_start"],
                        "page_end": sentence["page_end"],
                        "token_count": sentence["token_count"],
                        "beginning_excerpt": text[:350],
                        "ending_excerpt": text[-350:],
                        "likely_cause": cause,
                        "cause_explanation": explanation,
                        "needs_phase_4b_fallback": True,
                        "phase_4b_fallback_reason": FALLBACK[cause],
                    }
                )
    missing = set(REVIEWS) - seen
    if missing:
        raise ValueError(f"Reviewed sentence keys no longer exceed {THRESHOLD} tokens: {sorted(missing)}")
    if len(segments) != 28:
        raise ValueError(f"Expected 28 oversized sentence segments, found {len(segments)}")
    counts = Counter(item["likely_cause"] for item in segments)
    return {
        "analysis": "CourtLens Phase 4A.1 oversized sentence review",
        "source_preview": str(PREVIEW_PATH.relative_to(PROJECT_DIR)),
        "threshold_tokens_exclusive": THRESHOLD,
        "segment_count": len(segments),
        "counts_by_likely_cause": dict(sorted(counts.items())),
        "sentence_segmentation_changed": False,
        "decision": (
            "No parser-level sentence change: the failures are heterogeneous, and "
            "repairing OCR punctuation or page layout would require speculative text rewriting."
        ),
        "phase_4b_recommendation": (
            "Preserve normal sentence packing, but when one sentence exceeds the future "
            "hard token maximum, apply a secondary token-aware split contained within the "
            "same opinion and retain the original page provenance."
        ),
        "segments": segments,
    }


def render_report(analysis: dict) -> str:
    lines = [
        "# CourtLens Phase 4A.1: Long Sentence Analysis",
        "",
        "This report reviews every sentence segment above 200 tokens in the Phase 4A structural preview. No source text was rewritten.",
        "",
        "## Cause summary",
        "",
        "| Likely cause | Count |",
        "|---|---:|",
    ]
    for cause, count in analysis["counts_by_likely_cause"].items():
        lines.append(f"| {cause.replace('_', ' ')} | {count} |")
    lines += [
        "",
        "## Decision",
        "",
        analysis["decision"],
        "",
        analysis["phase_4b_recommendation"],
        "",
        "## All oversized segments",
        "",
    ]
    for index, item in enumerate(analysis["segments"], start=1):
        lines += [
            f"### {index}. {item['case_name']} — pp. {item['page_start']}–{item['page_end']} — {item['token_count']} tokens",
            "",
            f"Unit: {item['unit_index']} ({item['opinion_type']}, author raw: {item['author_raw'] or 'unknown'}).",
            "",
            f"Likely cause: **{item['likely_cause'].replace('_', ' ')}**. {item['cause_explanation']}",
            "",
            f"Phase 4B fallback: {item['phase_4b_fallback_reason']}",
            "",
            f"Beginning: “{item['beginning_excerpt']}”",
            "",
            f"Ending: “{item['ending_excerpt']}”",
            "",
        ]
    return "\n".join(lines)


def write_outputs(analysis: dict) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(analysis) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args()
    analysis = build_analysis(load_preview())
    if args.check:
        print(f"Validated {analysis['segment_count']} oversized sentence reviews")
    else:
        write_outputs(analysis)
        print(f"Wrote {JSON_PATH.relative_to(PROJECT_DIR)}")
        print(f"Wrote {REPORT_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
