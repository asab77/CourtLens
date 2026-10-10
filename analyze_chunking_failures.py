"""Build a local, evidence-only report from saved chunking experiment results."""

import argparse
import json
import textwrap
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = PROJECT_DIR / "data" / "experiments" / "chunking"
DEFAULT_RESULTS_PATH = EXPERIMENT_ROOT / "results.json"
DEFAULT_BENCHMARK_PATH = PROJECT_DIR / "data" / "evaluation" / "chunking_benchmark.json"
DEFAULT_REPORT_PATH = PROJECT_DIR / "data" / "analysis" / "chunking_failure_analysis.md"
DEFAULT_JSON_PATH = PROJECT_DIR / "data" / "analysis" / "chunking_failure_analysis.json"
CONFIGURATION_IDS = ("600_100", "900_150", "1200_200", "1500_200")
DISPLAY_NAMES = {
    "600_100": "600/100",
    "900_150": "900/150",
    "1200_200": "1200/200",
    "1500_200": "1500/200",
}
SELECTION_LIMITS = {"1500_wins": 4, "1200_wins": 3}
EXCERPT_CHARACTERS = 700


def load_json(path: Path) -> dict:
    """Load one UTF-8 JSON object."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(path: Path) -> list[dict]:
    """Load stored records and verify that vector IDs match row positions."""
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if any(record.get("vector_id") != position for position, record in enumerate(records)):
        raise ValueError(f"Vector IDs are not aligned with record rows in {path}")
    return records


def locally_relevant(result: dict, benchmark_item: dict) -> bool:
    """Reproduce the experiment's case, source, and page-intersection rule."""
    if result.get("case_name") != benchmark_item["expected_case"]:
        return False
    expected_source = benchmark_item.get("expected_source_file")
    if expected_source and expected_source not in {
        result.get("source_file"),
        result.get("original_source_file"),
    }:
        return False
    page_start = result.get("page_start")
    page_end = result.get("page_end")
    if page_start is None or page_end is None:
        return False
    return any(
        page_start <= relevant_end and page_end >= relevant_start
        for relevant_start, relevant_end in benchmark_item["relevant_pages"]
    )


def compare_questions(results: dict, benchmark: dict) -> tuple[list[dict], dict, dict]:
    """Compare saved first-relevant ranks without rerunning retrieval."""
    configurations = {item["id"]: item for item in results["configurations"]}
    missing_configurations = set(CONFIGURATION_IDS) - configurations.keys()
    if missing_configurations:
        raise ValueError(f"Missing configurations: {sorted(missing_configurations)}")

    question_maps = {
        configuration_id: {
            item["id"]: item
            for item in configurations[configuration_id]["questions"]
        }
        for configuration_id in CONFIGURATION_IDS
    }
    benchmark_map = {item["id"]: item for item in benchmark["questions"]}
    if len(benchmark_map) != len(benchmark["questions"]):
        raise ValueError("Benchmark question IDs are not unique")
    expected_ids = set(benchmark_map)
    for configuration_id, question_map in question_maps.items():
        if set(question_map) != expected_ids:
            raise ValueError(
                f"Question IDs for {configuration_id} do not match the benchmark"
            )

    comparison_counts = Counter()
    rank_distributions = {
        configuration_id: Counter() for configuration_id in CONFIGURATION_IDS
    }
    comparisons = []
    miss_rank = int(results.get("ranking_depth", 5)) + 1
    for question_id in benchmark_map:
        benchmark_item = benchmark_map[question_id]
        ranks = {}
        for configuration_id in CONFIGURATION_IDS:
            result_item = question_maps[configuration_id][question_id]
            for field in ("question", "expected_case", "relevant_pages"):
                if result_item[field] != benchmark_item[field]:
                    raise ValueError(
                        f"Saved result {question_id} disagrees with benchmark field {field}"
                    )
            rank = result_item["metrics"]["first_relevant_rank"]
            ranks[configuration_id] = rank
            rank_distributions[configuration_id][
                str(rank) if rank is not None else "miss"
            ] += 1

        rank_1200 = ranks["1200_200"] or miss_rank
        rank_1500 = ranks["1500_200"] or miss_rank
        if rank_1500 < rank_1200:
            category = "1500_wins"
            comparison_counts["1500_wins"] += 1
        elif rank_1200 < rank_1500:
            category = "1200_wins"
            comparison_counts["1200_wins"] += 1
        else:
            category = "tie"
            comparison_counts["tie"] += 1
        all_miss = all(rank is None for rank in ranks.values())
        if all_miss:
            comparison_counts["all_four_miss"] += 1

        comparisons.append(
            {
                "id": question_id,
                "case_name": benchmark_item["expected_case"],
                "question": benchmark_item["question"],
                "relevant_pages": benchmark_item["relevant_pages"],
                "ranks": ranks,
                "pairwise_category": category,
                "all_four_miss": all_miss,
                "rank_improvement": abs(rank_1200 - rank_1500),
            }
        )

    counts = {
        key: comparison_counts[key]
        for key in ("1500_wins", "1200_wins", "tie", "all_four_miss")
    }
    distributions = {
        configuration_id: {
            rank: rank_distributions[configuration_id][rank]
            for rank in ("1", "2", "3", "4", "5", "miss")
        }
        for configuration_id in CONFIGURATION_IDS
    }
    return comparisons, counts, distributions


def priority_key(item: dict, winning_id: str, losing_id: str) -> tuple:
    """Prioritize rank gain, using miss transitions and rank one as tie-breakers."""
    winner_rank = item["ranks"][winning_id]
    loser_rank = item["ranks"][losing_id]
    return (
        -item["rank_improvement"],
        loser_rank is not None,
        winner_rank != 1,
        winner_rank,
        item["id"],
    )


def rank_reason(item: dict, winning_id: str, losing_id: str) -> str:
    """Describe only the observed rank difference."""
    winner_name = DISPLAY_NAMES[winning_id]
    loser_name = DISPLAY_NAMES[losing_id]
    winner_rank = item["ranks"][winning_id]
    loser_rank = item["ranks"][losing_id]
    if loser_rank is None:
        return (
            f"{winner_name} found the first relevant result at rank {winner_rank}; "
            f"{loser_name} missed the Top-5."
        )
    return (
        f"{winner_name} found the first relevant result at rank {winner_rank}, "
        f"compared with rank {loser_rank} for {loser_name}."
    )


def select_questions(comparisons: list[dict]) -> list[dict]:
    """Select a small deterministic set of high-information comparisons."""
    selected = []
    category_specs = (
        ("1500_wins", "1500_200", "1200_200"),
        ("1200_wins", "1200_200", "1500_200"),
    )
    for category, winning_id, losing_id in category_specs:
        candidates = [
            item for item in comparisons if item["pairwise_category"] == category
        ]
        limit = SELECTION_LIMITS[category]
        transitions = [
            item for item in candidates if item["ranks"][losing_id] is None
        ]
        transitions.sort(
            key=lambda item: (
                item["ranks"][winning_id],
                -item["rank_improvement"],
                item["id"],
            )
        )
        chosen = transitions[: min(2, limit)]
        remaining = [item for item in candidates if item not in chosen]
        remaining.sort(key=lambda item: priority_key(item, winning_id, losing_id))
        chosen.extend(remaining[: limit - len(chosen)])
        for item in chosen:
            selected.append(
                {
                    **item,
                    "selection_category": category,
                    "selection_reason": rank_reason(item, winning_id, losing_id),
                }
            )

    for item in comparisons:
        if item["all_four_miss"]:
            selected.append(
                {
                    **item,
                    "selection_category": "all_four_miss",
                    "selection_reason": (
                        "No fixed-size configuration retrieved a relevant result "
                        "within the Top-5."
                    ),
                }
            )
    return selected


def excerpt(text: str, limit: int = EXCERPT_CHARACTERS) -> str:
    """Collapse extraction whitespace and retain a bounded inspection excerpt."""
    return textwrap.shorten(" ".join(text.split()), width=limit, placeholder=" …")


def attach_retrieval_evidence(
    selected: list[dict],
    results: dict,
    benchmark: dict,
    experiment_root: Path,
) -> list[dict]:
    """Join saved top-five vector IDs to stored chunk text."""
    configurations = {item["id"]: item for item in results["configurations"]}
    benchmark_map = {item["id"]: item for item in benchmark["questions"]}
    question_maps = {
        configuration_id: {
            item["id"]: item
            for item in configurations[configuration_id]["questions"]
        }
        for configuration_id in ("1200_200", "1500_200")
    }
    records = {
        configuration_id: load_records(
            experiment_root / configuration_id / "vector_store" / "records.jsonl"
        )
        for configuration_id in ("1200_200", "1500_200")
    }

    enriched = []
    for item in selected:
        retrievals = {}
        benchmark_item = benchmark_map[item["id"]]
        for configuration_id in ("1200_200", "1500_200"):
            saved_results = question_maps[configuration_id][item["id"]]["metrics"][
                "retrieved"
            ]
            evidence = []
            for saved_result in saved_results:
                vector_id = saved_result["vector_id"]
                try:
                    stored_record = records[configuration_id][vector_id]
                except IndexError as error:
                    raise ValueError(
                        f"Vector ID {vector_id} is outside {configuration_id} records"
                    ) from error
                metadata = stored_record["metadata"]
                comparisons = {
                    "case_name": metadata["case_name"],
                    "source_file": metadata["source_file"],
                    "page_start": metadata["page_start"],
                    "page_end": metadata["page_end"],
                    "chunk_index": metadata["chunk_index"],
                }
                if any(saved_result[key] != value for key, value in comparisons.items()):
                    raise ValueError(
                        f"Stored record metadata does not match result for "
                        f"{item['id']} / {configuration_id} / vector {vector_id}"
                    )
                if saved_result["relevant"] != locally_relevant(
                    saved_result, benchmark_item
                ):
                    raise ValueError(
                        f"Saved relevance flag disagrees with benchmark for "
                        f"{item['id']} / {configuration_id} / vector {vector_id}"
                    )
                evidence.append(
                    {
                        **saved_result,
                        "text_excerpt": excerpt(stored_record["text"]),
                    }
                )
            retrievals[configuration_id] = evidence
        enriched.append({**item, "retrievals": retrievals})
    return enriched


def pages_label(ranges: list[list[int]]) -> str:
    """Format inclusive benchmark page ranges."""
    return ", ".join(
        str(start) if start == end else f"{start}-{end}" for start, end in ranges
    )


def rank_label(rank: int | None) -> str:
    return str(rank) if rank is not None else "Miss"


def render_report(analysis: dict) -> str:
    """Render the structured evidence as readable Markdown."""
    counts = analysis["summary_counts"]
    lines = [
        "# Fixed-Chunking Failure Analysis",
        "",
        "This report uses only the saved Experiment 1 rankings and local vector-store "
        "records. It does not rerun retrieval or infer explanations for the observed "
        "rank differences.",
        "",
        "## Summary",
        "",
        "| Comparison | Questions |",
        "|---|---:|",
        f"| 1500/200 beats 1200/200 | {counts['1500_wins']} |",
        f"| 1200/200 beats 1500/200 | {counts['1200_wins']} |",
        f"| Tie | {counts['tie']} |",
        f"| All four miss Top-5 | {counts['all_four_miss']} |",
        "",
        "A miss is ordered immediately after rank 5 for pairwise comparison. The "
        "manual-review set includes up to two strong miss-to-hit transitions per win "
        "category, then fills the category quota with the largest remaining rank "
        "improvements. All universal misses are included.",
        "",
        "## First Relevant Rank Distribution",
        "",
        "| Configuration | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Miss |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for configuration_id in CONFIGURATION_IDS:
        distribution = analysis["first_relevant_rank_distribution"][configuration_id]
        lines.append(
            f"| {DISPLAY_NAMES[configuration_id]} | {distribution['1']} | "
            f"{distribution['2']} | {distribution['3']} | {distribution['4']} | "
            f"{distribution['5']} | {distribution['miss']} |"
        )

    lines.extend(
        [
            "",
            "## Selected Questions",
            "",
            "| Category | ID | Case | Relevant pages | 600/100 | 900/150 | 1200/200 | 1500/200 |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    category_labels = {
        "1500_wins": "1500/200 wins",
        "1200_wins": "1200/200 wins",
        "all_four_miss": "All configurations struggle",
    }
    for item in analysis["selected_questions"]:
        ranks = item["ranks"]
        lines.append(
            f"| {category_labels[item['selection_category']]} | {item['id']} | "
            f"{item['case_name']} | {pages_label(item['relevant_pages'])} | "
            f"{rank_label(ranks['600_100'])} | {rank_label(ranks['900_150'])} | "
            f"{rank_label(ranks['1200_200'])} | {rank_label(ranks['1500_200'])} |"
        )

    for category in ("1500_wins", "1200_wins", "all_four_miss"):
        lines.extend(["", f"## {category_labels[category]}"])
        for item in analysis["selected_questions"]:
            if item["selection_category"] != category:
                continue
            ranks = item["ranks"]
            lines.extend(
                [
                    "",
                    f"### {item['id']} — {item['case_name']}",
                    "",
                    f"**Question:** {item['question']}",
                    "",
                    f"**Expected pages:** {pages_label(item['relevant_pages'])}",
                    "",
                    f"**First relevant ranks:** 600/100 {rank_label(ranks['600_100'])}; "
                    f"900/150 {rank_label(ranks['900_150'])}; "
                    f"1200/200 {rank_label(ranks['1200_200'])}; "
                    f"1500/200 {rank_label(ranks['1500_200'])}.",
                    "",
                    f"**Selection evidence:** {item['selection_reason']}",
                ]
            )
            for configuration_id in ("1200_200", "1500_200"):
                lines.extend(["", f"#### {DISPLAY_NAMES[configuration_id]} Top-5", ""])
                for result in item["retrievals"][configuration_id]:
                    lines.extend(
                        [
                            f"**Rank {result['rank']} — similarity "
                            f"{result['similarity']:.6f} — "
                            f"{'relevant' if result['relevant'] else 'not relevant'}**",
                            "",
                            f"Source: `{result['case_name']}` / `{result['source_file']}`; "
                            f"pages {result['page_start']}-{result['page_end']}; "
                            f"vector `{result['vector_id']}`; chunk `{result['chunk_index']}`.",
                            "",
                            f"> {result['text_excerpt']}",
                            "",
                        ]
                    )

    lines.extend(
        [
            "## Limitations",
            "",
            "- The report shows the stored Top-5 only. It cannot determine where a "
            "relevant chunk ranked below five.",
            "- Similarity scores are comparable within a configuration's ranking, but "
            "chunk boundaries and candidate sets differ across configurations.",
            "- Excerpts collapse extraction whitespace and are truncated for manual "
            "inspection; the structured source records remain unchanged.",
            "- Selection reasons describe rank evidence only. Determining why a chunk "
            "succeeded or failed requires human review of the included excerpts.",
            "",
        ]
    )
    return "\n".join(lines)


def build_analysis(
    results_path: Path = DEFAULT_RESULTS_PATH,
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    experiment_root: Path = EXPERIMENT_ROOT,
) -> dict:
    """Create the complete structured analysis from existing local artifacts."""
    results = load_json(results_path)
    benchmark = load_json(benchmark_path)
    comparisons, counts, distributions = compare_questions(results, benchmark)
    selected = select_questions(comparisons)
    selected = attach_retrieval_evidence(
        selected, results, benchmark, experiment_root
    )
    return {
        "analysis": "fixed_chunking_failure_analysis",
        "sources": {
            "results": str(results_path),
            "benchmark": str(benchmark_path),
            "records": [
                str(experiment_root / configuration_id / "vector_store" / "records.jsonl")
                for configuration_id in ("1200_200", "1500_200")
            ],
        },
        "selection_policy": {
            "1500_wins_selected": SELECTION_LIMITS["1500_wins"],
            "1200_wins_selected": SELECTION_LIMITS["1200_wins"],
            "all_four_misses_selected": "all",
            "priority": [
                "up to two strongest miss-to-Top-5 transitions per win category",
                "largest remaining rank improvements",
                "miss transitions and rank-one results break equal-gain ties",
            ],
        },
        "summary_counts": counts,
        "first_relevant_rank_distribution": distributions,
        "selected_questions": selected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = build_analysis(args.results, args.benchmark, EXPERIMENT_ROOT)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(analysis), encoding="utf-8")
    args.json_output.write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(analysis['selected_questions'])} questions to {args.report}")
    print(f"Wrote structured evidence to {args.json_output}")


if __name__ == "__main__":
    main()
