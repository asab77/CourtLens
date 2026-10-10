"""Prepare a human benchmark-review packet from saved Experiment 1 evidence."""

import argparse
import hashlib
import json
import textwrap
from copy import deepcopy
from pathlib import Path

from benchmark_relevance import page_range_overlaps, relevant_ranges_for_item


PROJECT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = PROJECT_DIR / "data" / "experiments" / "chunking"
DEFAULT_BENCHMARK_PATH = PROJECT_DIR / "data" / "evaluation" / "chunking_benchmark.json"
DEFAULT_RESULTS_PATH = EXPERIMENT_ROOT / "results.json"
DEFAULT_FAILURE_ANALYSIS_PATH = (
    PROJECT_DIR / "data" / "analysis" / "chunking_failure_analysis.json"
)
DEFAULT_JSON_OUTPUT = (
    PROJECT_DIR / "data" / "evaluation" / "chunking_benchmark_review.json"
)
DEFAULT_MARKDOWN_OUTPUT = (
    PROJECT_DIR / "data" / "evaluation" / "chunking_benchmark_review.md"
)
CONFIGURATION_IDS = ("600_100", "900_150", "1200_200", "1500_200")
DISPLAY_NAMES = {
    "600_100": "600/100",
    "900_150": "900/150",
    "1200_200": "1200/200",
    "1500_200": "1500/200",
}
MARKDOWN_EXCERPT_CHARACTERS = 1_600


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(path: Path) -> list[dict]:
    """Load records and verify the persisted vector-to-row invariant."""
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if any(record.get("vector_id") != index for index, record in enumerate(records)):
        raise ValueError(f"Vector IDs are not aligned with record rows in {path}")
    return records


def current_rule_relevant(candidate: dict, benchmark_item: dict) -> bool:
    """Apply the current case, source, and original-page rule."""
    if candidate["case_name"] != benchmark_item["expected_case"]:
        return False
    expected_source = benchmark_item.get("expected_source_file")
    if expected_source and expected_source not in {
        candidate["source_file"],
        candidate.get("original_source_file"),
    }:
        return False
    return page_range_overlaps(
        candidate["page_start"],
        candidate["page_end"],
        relevant_ranges_for_item(benchmark_item),
    )


def exact_candidate_key(record: dict) -> tuple:
    """Deduplicate only byte-equivalent text with the same source and page span."""
    metadata = record["metadata"]
    return (
        metadata["source_file"],
        metadata.get("original_source_file"),
        metadata["page_start"],
        metadata["page_end"],
        record["text"],
    )


def candidate_id(key: tuple) -> str:
    encoded = json.dumps(key, ensure_ascii=False, separators=(",", ":")).encode()
    return f"candidate-{hashlib.sha256(encoded).hexdigest()[:16]}"


def strong_rank_disagreement(rank_1200: int | None, rank_1500: int | None) -> bool:
    """Flag hit/miss differences or rank gaps of at least three."""
    if (rank_1200 is None) != (rank_1500 is None):
        return True
    if rank_1200 is None:
        return False
    return abs(rank_1200 - rank_1500) >= 3


def priority_tier(flags: dict) -> str:
    if flags["all_four_miss_top_5"]:
        return "highest"
    if sum(flags.values()) >= 3:
        return "high"
    if sum(flags.values()) == 2:
        return "medium"
    return "standard"


def priority_score(flags: dict) -> int:
    """Order review only; never use this score as a relevance judgment."""
    weights = {
        "all_four_miss_top_5": 8,
        "correct_case_candidate_outside_original_ranges": 4,
        "strong_1200_1500_disagreement": 2,
        "selected_in_failure_analysis": 1,
    }
    return sum(weights[name] for name, enabled in flags.items() if enabled)


def validate_saved_result(saved: dict, record: dict, benchmark_item: dict) -> None:
    """Verify every candidate came from the stated local result and record row."""
    metadata = record["metadata"]
    fields = (
        "case_name",
        "source_file",
        "original_source_file",
        "page_start",
        "page_end",
        "chunk_index",
        "token_count",
    )
    if any(saved.get(field) != metadata.get(field) for field in fields):
        raise ValueError(
            f"Saved result metadata does not match vector {saved['vector_id']}"
        )
    candidate = {field: saved.get(field) for field in fields}
    if saved["relevant"] != current_rule_relevant(candidate, benchmark_item):
        raise ValueError(
            f"Saved relevance flag disagrees with current rule for vector "
            f"{saved['vector_id']}"
        )


def build_question_candidates(
    benchmark_item: dict,
    question_results: dict[str, dict],
    records_by_configuration: dict[str, list[dict]],
) -> list[dict]:
    """Join all saved Top-5 results to text and exactly deduplicate chunks."""
    candidates_by_key = {}
    for configuration_id in CONFIGURATION_IDS:
        retrieved = question_results[configuration_id]["metrics"]["retrieved"]
        for saved in retrieved:
            try:
                record = records_by_configuration[configuration_id][saved["vector_id"]]
            except IndexError as error:
                raise ValueError(
                    f"Vector {saved['vector_id']} is outside {configuration_id} records"
                ) from error
            validate_saved_result(saved, record, benchmark_item)
            key = exact_candidate_key(record)
            if key not in candidates_by_key:
                metadata = record["metadata"]
                candidate = {
                    "candidate_id": candidate_id(key),
                    "case_name": metadata["case_name"],
                    "source_file": metadata["source_file"],
                    "original_source_file": metadata.get("original_source_file"),
                    "page_start": metadata["page_start"],
                    "page_end": metadata["page_end"],
                    "currently_passes_original_relevance_rule": current_rule_relevant(
                        metadata, benchmark_item
                    ),
                    "chunk_text": record["text"],
                    "appearances": [],
                }
                candidates_by_key[key] = candidate
            candidates_by_key[key]["appearances"].append(
                {
                    "configuration": configuration_id,
                    "configuration_label": DISPLAY_NAMES[configuration_id],
                    "rank": saved["rank"],
                    "similarity": saved["similarity"],
                    "vector_id": saved["vector_id"],
                    "chunk_index": saved["chunk_index"],
                    "token_count": saved["token_count"],
                    "saved_relevant": saved["relevant"],
                }
            )

    candidates = list(candidates_by_key.values())
    for candidate in candidates:
        candidate["appearances"].sort(
            key=lambda item: (CONFIGURATION_IDS.index(item["configuration"]), item["rank"])
        )
    candidates.sort(
        key=lambda item: (
            min(appearance["rank"] for appearance in item["appearances"]),
            item["source_file"],
            item["page_start"],
            item["page_end"],
            item["candidate_id"],
        )
    )
    return candidates


def build_review(
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    results_path: Path = DEFAULT_RESULTS_PATH,
    failure_analysis_path: Path = DEFAULT_FAILURE_ANALYSIS_PATH,
    experiment_root: Path = EXPERIMENT_ROOT,
) -> dict:
    """Create an undecided human-review packet from existing local files."""
    benchmark = load_json(benchmark_path)
    results = load_json(results_path)
    failure_analysis = load_json(failure_analysis_path)
    benchmark_questions = benchmark["questions"]
    benchmark_ids = [item["id"] for item in benchmark_questions]
    if len(benchmark_ids) != 40 or len(set(benchmark_ids)) != 40:
        raise ValueError("Expected exactly 40 unique benchmark questions")

    configurations = {item["id"]: item for item in results["configurations"]}
    if set(configurations) != set(CONFIGURATION_IDS):
        raise ValueError("Saved results do not contain the four expected configurations")
    result_maps = {
        configuration_id: {
            item["id"]: item
            for item in configurations[configuration_id]["questions"]
        }
        for configuration_id in CONFIGURATION_IDS
    }
    for configuration_id, result_map in result_maps.items():
        if set(result_map) != set(benchmark_ids):
            raise ValueError(
                f"Saved questions for {configuration_id} do not match the benchmark"
            )
    records_by_configuration = {
        configuration_id: load_records(
            experiment_root / configuration_id / "vector_store" / "records.jsonl"
        )
        for configuration_id in CONFIGURATION_IDS
    }
    selected_failure_ids = {
        item["id"] for item in failure_analysis["selected_questions"]
    }

    review_questions = []
    for benchmark_item in benchmark_questions:
        question_id = benchmark_item["id"]
        question_results = {
            configuration_id: result_maps[configuration_id][question_id]
            for configuration_id in CONFIGURATION_IDS
        }
        for configuration_id, result_item in question_results.items():
            for field in ("question", "expected_case", "expected_source_file", "relevant_pages"):
                if result_item.get(field) != benchmark_item.get(field):
                    raise ValueError(
                        f"{question_id} differs between benchmark and {configuration_id}: {field}"
                    )
        candidates = build_question_candidates(
            benchmark_item, question_results, records_by_configuration
        )
        first_relevant_ranks = {
            configuration_id: question_results[configuration_id]["metrics"][
                "first_relevant_rank"
            ]
            for configuration_id in CONFIGURATION_IDS
        }
        correct_case_outside = any(
            candidate["case_name"] == benchmark_item["expected_case"]
            and benchmark_item.get("expected_source_file")
            in {candidate["source_file"], candidate.get("original_source_file")}
            and not candidate["currently_passes_original_relevance_rule"]
            for candidate in candidates
        )
        flags = {
            "all_four_miss_top_5": all(
                rank is None for rank in first_relevant_ranks.values()
            ),
            "correct_case_candidate_outside_original_ranges": correct_case_outside,
            "strong_1200_1500_disagreement": strong_rank_disagreement(
                first_relevant_ranks["1200_200"],
                first_relevant_ranks["1500_200"],
            ),
            "selected_in_failure_analysis": question_id in selected_failure_ids,
        }
        review_questions.append(
            {
                "id": question_id,
                "case_name": benchmark_item["expected_case"],
                "question": benchmark_item["question"],
                "original_relevant_ranges": deepcopy(
                    benchmark_item["relevant_pages"]
                ),
                "original_benchmark_metadata": {
                    "type": benchmark_item.get("type"),
                    "expected_source_file": benchmark_item.get("expected_source_file"),
                    "validated": benchmark_item.get("validated"),
                },
                "current_retrieval_outcomes": {
                    configuration_id: {
                        "first_relevant_rank": first_relevant_ranks[configuration_id],
                        "hit_at_1": question_results[configuration_id]["metrics"]["hit_at_1"],
                        "hit_at_3": question_results[configuration_id]["metrics"]["hit_at_3"],
                        "hit_at_5": question_results[configuration_id]["metrics"]["hit_at_5"],
                    }
                    for configuration_id in CONFIGURATION_IDS
                },
                "review_priority": {
                    "tier": priority_tier(flags),
                    "score": priority_score(flags),
                    "flags": flags,
                },
                "candidate_count": len(candidates),
                "candidates": candidates,
                "human_review": {
                    "status": "pending",
                    "accepted_relevant_ranges": [],
                    "notes": "",
                },
            }
        )

    priority_order = sorted(
        review_questions,
        key=lambda item: (-item["review_priority"]["score"], item["id"]),
    )
    return {
        "name": "CourtLens Experiment 1 benchmark human review",
        "status": "pending_human_review",
        "instructions": {
            "purpose": (
                "Inspect saved candidates and record human judgments without changing "
                "the original benchmark. Retrieval rank and similarity are evidence "
                "locations, not relevance judgments."
            ),
            "human_review_status_values": ["pending", "accepted", "needs_discussion"],
            "range_format": "Inclusive PDF page ranges: [[start, end], ...]",
            "do_not_auto_populate": "accepted_relevant_ranges",
        },
        "sources": {
            "benchmark": str(benchmark_path),
            "results": str(results_path),
            "failure_analysis": str(failure_analysis_path),
            "records": {
                configuration_id: str(
                    experiment_root
                    / configuration_id
                    / "vector_store"
                    / "records.jsonl"
                )
                for configuration_id in CONFIGURATION_IDS
            },
        },
        "question_count": len(review_questions),
        "pending_review_count": sum(
            item["human_review"]["status"] == "pending"
            for item in review_questions
        ),
        "priority_order": [
            {
                "id": item["id"],
                "tier": item["review_priority"]["tier"],
                "score": item["review_priority"]["score"],
                "flags": item["review_priority"]["flags"],
            }
            for item in priority_order
        ],
        "questions": review_questions,
    }


def rank_label(rank: int | None) -> str:
    return str(rank) if rank is not None else "Miss"


def ranges_label(ranges: list[list[int]]) -> str:
    return ", ".join(
        str(start) if start == end else f"{start}-{end}" for start, end in ranges
    )


def markdown_excerpt(text: str) -> str:
    collapsed = " ".join(text.split())
    return textwrap.shorten(
        collapsed, width=MARKDOWN_EXCERPT_CHARACTERS, placeholder=" …"
    )


def flag_labels(flags: dict) -> list[str]:
    labels = {
        "all_four_miss_top_5": "all four miss Top-5",
        "correct_case_candidate_outside_original_ranges": (
            "correct-case candidate outside original ranges"
        ),
        "strong_1200_1500_disagreement": "strong 1200/1500 disagreement",
        "selected_in_failure_analysis": "selected in failure analysis",
    }
    return [labels[name] for name, enabled in flags.items() if enabled]


def render_markdown(review: dict) -> str:
    """Render an editable, human-readable review packet."""
    question_map = {item["id"]: item for item in review["questions"]}
    lines = [
        "# CourtLens Chunking Benchmark Review",
        "",
        "This packet contains only candidates already retrieved in Experiment 1. "
        "Similarity and rank help locate passages; they do not determine relevance.",
        "",
        "All human-review fields begin pending and empty. The original benchmark "
        "ranges are preserved separately.",
        "",
        "## Prioritized Review Queue",
        "",
        "| Priority | ID | Case | 1200 rank | 1500 rank | Reasons |",
        "|---|---|---|---:|---:|---|",
    ]
    for priority in review["priority_order"]:
        item = question_map[priority["id"]]
        outcomes = item["current_retrieval_outcomes"]
        reasons = "; ".join(flag_labels(priority["flags"])) or "routine review"
        lines.append(
            f"| {priority['tier']} ({priority['score']}) | {item['id']} | "
            f"{item['case_name']} | "
            f"{rank_label(outcomes['1200_200']['first_relevant_rank'])} | "
            f"{rank_label(outcomes['1500_200']['first_relevant_rank'])} | {reasons} |"
        )

    lines.extend(["", "## Question Review Forms"])
    for item in review["questions"]:
        outcomes = item["current_retrieval_outcomes"]
        lines.extend(
            [
                "",
                f"### {item['id']} — {item['case_name']}",
                "",
                f"**Question:** {item['question']}",
                "",
                f"**Original relevant PDF ranges:** {ranges_label(item['original_relevant_ranges'])}",
                "",
                f"**Original metadata:** type `{item['original_benchmark_metadata']['type']}`; "
                f"source `{item['original_benchmark_metadata']['expected_source_file']}`; "
                f"validated `{str(item['original_benchmark_metadata']['validated']).lower()}`.",
                "",
                "**Current first relevant ranks:** "
                + "; ".join(
                    f"{DISPLAY_NAMES[configuration_id]} "
                    f"{rank_label(outcomes[configuration_id]['first_relevant_rank'])}"
                    for configuration_id in CONFIGURATION_IDS
                )
                + ".",
                "",
                f"**Review priority:** {item['review_priority']['tier']} "
                f"({item['review_priority']['score']}); "
                + ("; ".join(flag_labels(item["review_priority"]["flags"])) or "routine review")
                + ".",
                "",
                "**Human review:** status `pending`; accepted relevant ranges `[]`; notes blank.",
                "",
                f"#### Saved candidates ({item['candidate_count']} unique)",
            ]
        )
        for candidate in item["candidates"]:
            lines.extend(
                [
                    "",
                    f"##### {candidate['candidate_id']} — pages "
                    f"{candidate['page_start']}-{candidate['page_end']}",
                    "",
                    f"Current rule: **{'passes' if candidate['currently_passes_original_relevance_rule'] else 'does not pass'}**. "
                    f"Case/source: `{candidate['case_name']}` / `{candidate['source_file']}`.",
                    "",
                    "| Configuration | Rank | Similarity | Vector | Chunk | Tokens |",
                    "|---|---:|---:|---:|---:|---:|",
                ]
            )
            for appearance in candidate["appearances"]:
                lines.append(
                    f"| {appearance['configuration_label']} | {appearance['rank']} | "
                    f"{appearance['similarity']:.6f} | {appearance['vector_id']} | "
                    f"{appearance['chunk_index']} | {appearance['token_count']} |"
                )
            lines.extend(
                [
                    "",
                    f"> {markdown_excerpt(candidate['chunk_text'])}",
                ]
            )

    lines.extend(
        [
            "",
            "## Review Limitations",
            "",
            "- Candidate coverage is limited to the saved Top-5 from four fixed-size configurations.",
            "- A passage absent from this packet may still be relevant elsewhere in the opinion.",
            "- The Markdown view truncates long passages; the JSON artifact retains full chunk text.",
            "- Overlapping chunks are deduplicated only when text, source, and page span are exactly equal.",
            "- Rank and similarity must not be treated as human relevance judgments.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK_PATH)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument(
        "--failure-analysis", type=Path, default=DEFAULT_FAILURE_ANALYSIS_PATH
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    review = build_review(
        args.benchmark, args.results, args.failure_analysis, EXPERIMENT_ROOT
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(review), encoding="utf-8")
    print(
        f"Prepared {review['question_count']} pending questions in "
        f"{args.json_output} and {args.markdown_output}"
    )


if __name__ == "__main__":
    main()
