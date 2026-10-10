"""Finalize the reviewed benchmark and rescore saved Experiment 1 rankings.

This module is intentionally local-only: it reads JSON artifacts and never loads an
embedding client, FAISS index, or network dependency.
"""

import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from benchmark_relevance import normalize_relevant_ranges, page_range_overlaps


PROJECT_DIR = Path(__file__).resolve().parent
ORIGINAL_BENCHMARK_PATH = PROJECT_DIR / "data/evaluation/chunking_benchmark.json"
REVIEW_PACKET_PATH = PROJECT_DIR / "data/evaluation/chunking_benchmark_review.json"
ORIGINAL_RESULTS_PATH = PROJECT_DIR / "data/experiments/chunking/results.json"
REVIEWED_BENCHMARK_PATH = (
    PROJECT_DIR / "data/evaluation/chunking_benchmark_reviewed.json"
)
REVIEWED_RESULTS_PATH = (
    PROJECT_DIR / "data/experiments/chunking/reviewed_results.json"
)
BREAKDOWN_PATH = PROJECT_DIR / "data/analysis/chunking_reviewed_breakdown.json"
REPORT_PATH = PROJECT_DIR / "data/analysis/chunking_reviewed_evaluation.md"

CONFIGURATION_IDS = ("600_100", "900_150", "1200_200", "1500_200")
DISPLAY_NAMES = {
    "600_100": "600/100",
    "900_150": "900/150",
    "1200_200": "1200/200",
    "1500_200": "1500/200",
}


# Human judgments made from the saved Top-5 passage text in the review packet.
# Original labels are retained; additions are limited to passages present there.
REVIEW_DECISIONS = {
    "MAR-01": ([[2, 2], [18, 19], [37, 38]], "Added majority-opinion passages describing the withheld commission and the request for mandamus."),
    "MAR-02": ([[19, 27], [31, 33]], "Added majority passages stating that signing and sealing completed the appointment and vested the legal right."),
    "MAR-03": ([[32, 37]], "Added the immediately preceding majority analysis defining mandamus and explaining why that remedy fits."),
    "MAR-04": ([[37, 40]], "No saved passage outside the original range independently states the Court's original-jurisdiction holding."),
    "MAR-05": ([[40, 44]], "No saved outside passage independently supplies the judicial-review reasoning required by the question."),
    "DRE-01": ([[5, 6]], "Outside passages describing the residence facts came from separate opinions; the original statement-of-case range remains the defensible label."),
    "DRE-02": ([[1, 2], [31, 36]], "Added controlling-opinion passages explaining the citizenship ruling and resulting lack of federal jurisdiction."),
    "DRE-03": ([[10, 12], [24, 28]], "Added controlling-opinion passages using founding-era status and constitutional consequences to explain the citizenship conclusion."),
    "DRE-04": ([[3, 4]], "Preserved the established decision: retrieved separate-opinion passages were not added to the controlling-rule label."),
    "DRE-05": ([[1, 1], [27, 28]], "Added the saved syllabus passage that expressly discusses the 1790 naturalization law as evidence of the Court's citizenship interpretation."),
    "PLE-01": ([[2, 3]], "No saved outside passage independently improves on the original statement of the operative facts."),
    "PLE-02": ([[1, 2], [6, 17]], "Added majority passages analyzing the Thirteenth and Fourteenth Amendment challenges and affirming the statute."),
    "PLE-03": ([[8, 15]], "Added the majority's preceding police-power, social-equality, and precedent analysis supporting its conclusion."),
    "PLE-04": ([[2, 5]], "Added the syllabus passage listing the statute's penalties, enforcement authority, and nurse exemption."),
    "PLE-05": ([[19, 28]], "Added the concluding pages of Justice Harlan's dissent, which continue his constitutional objection to enforced separation."),
    "GID-01": ([[2, 3]], "No saved outside passage independently adds the requested trial facts."),
    "GID-02": ([[1, 1], [5, 11]], "Added majority passages explaining why appointed counsel is fundamental and applies to state felony prosecutions."),
    "GID-03": ([[5, 11]], "Added the continuation of the majority's Betts and Powell discussion through the decision to overrule Betts."),
    "GID-04": ([[10, 11]], "No saved outside passage independently supplies the requested majority reasoning."),
    "GID-05": ([[10, 11]], "No saved outside passage lists the specific disadvantages of an uncounseled defendant as directly as the original range."),
    "MIR-01": ([[56, 57]], "No saved outside passage independently states the Miranda-specific interrogation facts."),
    "MIR-02": ([[1, 3], [57, 57]], "Added the syllabus holding that statements obtained without warnings and waiver were inadmissible."),
    "MIR-03": ([[22, 23], [32, 44]], "Added majority passages explaining custodial pressure and the safeguards adopted to counter it."),
    "MIR-04": ([[2, 2], [34, 40]], "Added the majority's detailed statement of the warnings, counsel procedure, waiver, and cessation rules."),
    "MIR-05": ([[40, 40]], "No saved outside passage directly answers the effect of simply remaining silent."),
    "TIN-01": ([[2, 2]], "No saved outside passage independently gives both why the students wore the armbands and the school's response."),
    "TIN-02": ([[1, 1], [3, 12]], "Added majority passages treating the armbands as protected expression absent substantial disruption or invasion of others' rights."),
    "TIN-03": ([[4, 5], [9, 12]], "Added majority passages explaining the scope and limits of student speech rights in school."),
    "TIN-04": ([[6, 7], [9, 12]], "Added the majority's later applications of the disruption and rights-of-others standard."),
    "TIN-05": ([[8, 9]], "No saved outside passage independently demonstrates the requested selective-treatment comparison."),
    "NYT-01": ([[2, 2]], "No saved outside passage independently gives the requested description of the classified material."),
    "NYT-02": ([[1, 2], [13, 15], [19, 22]], "Preserved the established decision: added concurring reasoning explains why the attempted restraint failed."),
    "NYT-03": ([[2, 2], [13, 15], [19, 20]], "Preserved the established decision: added passages address the government's burden and the prior-restraint standard."),
    "NYT-04": ([[3, 7]], "No saved outside passage answers the question through Justice Black's specified reasoning."),
    "NYT-05": ([[13, 14]], "No saved outside passage answers the question through Justice Brennan's specified reasoning."),
    "OBE-01": ([[12, 13]], "No saved outside passage independently identifies both questions the Court granted review to decide."),
    "OBE-02": ([[1, 5], [35, 39]], "Added syllabus and majority-conclusion passages stating both the licensing and recognition holdings."),
    "OBE-03": ([[1, 5], [22, 30]], "Added the syllabus enumeration and majority continuation of the four principles supporting the fundamental-right conclusion."),
    "OBE-04": ([[4, 4], [28, 32]], "No saved outside majority passage independently adds to the original due-process and equal-protection explanation."),
    "OBE-05": ([[15, 15]], "Outside passages mention harm more generally but do not supply the requested terminal-illness and death-certificate facts."),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_ranges(ranges: list) -> list[list[int]]:
    normalized = normalize_relevant_ranges(ranges)
    if len({tuple(interval) for interval in normalized}) != len(normalized):
        raise ValueError(f"Duplicate relevant range: {ranges!r}")
    return normalized


def build_reviewed_benchmark(original: dict, review_packet: dict) -> dict:
    questions = original.get("questions", [])
    ids = [item["id"] for item in questions]
    if len(ids) != 40 or len(set(ids)) != 40:
        raise ValueError("Expected exactly 40 unique original benchmark questions")
    if set(ids) != set(REVIEW_DECISIONS):
        raise ValueError("Human review decisions do not exactly match the benchmark IDs")
    packet_ids = [item["id"] for item in review_packet.get("questions", [])]
    if len(packet_ids) != 40 or set(packet_ids) != set(ids):
        raise ValueError("Review packet IDs do not match the benchmark")

    reviewed_questions = []
    for item in questions:
        ranges, notes = REVIEW_DECISIONS[item["id"]]
        ranges = validate_ranges(ranges)
        original_ranges = validate_ranges(item["relevant_pages"])
        reviewed_questions.append(
            {
                "id": item["id"],
                "type": item["type"],
                "question": item["question"],
                "expected_case": item["expected_case"],
                "expected_source_file": item["expected_source_file"],
                "original_relevant_ranges": original_ranges,
                "relevant_ranges": ranges,
                "relevance_changed": ranges != original_ranges,
                "review_notes": notes,
                "validated": True,
            }
        )

    reviewed = {
        "name": "CourtLens fixed-chunking benchmark — human-reviewed relevance",
        "status": "reviewed",
        "instructions": (
            "A saved result is relevant only when case/source match and its inclusive "
            "page span intersects any relevant_ranges interval. Ranges were reviewed "
            "from the saved Top-5 passage content; absence from that packet is not "
            "evidence that no other answer-bearing passage exists."
        ),
        "provenance": {
            "original_benchmark": str(ORIGINAL_BENCHMARK_PATH.relative_to(PROJECT_DIR)),
            "review_packet": str(REVIEW_PACKET_PATH.relative_to(PROJECT_DIR)),
            "review_method": "human content review of saved Top-5 candidates",
        },
        "question_count": 40,
        "changed_question_count": sum(q["relevance_changed"] for q in reviewed_questions),
        "questions": reviewed_questions,
    }
    validate_reviewed_benchmark(reviewed, original)
    return reviewed


def validate_reviewed_benchmark(reviewed: dict, original: dict) -> None:
    questions = reviewed.get("questions", [])
    if len(questions) != 40 or len({item.get("id") for item in questions}) != 40:
        raise ValueError("Reviewed benchmark must contain exactly 40 unique questions")
    originals = {item["id"]: item for item in original["questions"]}
    if set(originals) != {item["id"] for item in questions}:
        raise ValueError("Reviewed benchmark IDs differ from the original")
    for item in questions:
        source = originals[item["id"]]
        for field in ("type", "question", "expected_case", "expected_source_file"):
            if item[field] != source[field]:
                raise ValueError(f"{item['id']} changed immutable field {field}")
        validate_ranges(item["original_relevant_ranges"])
        validate_ranges(item["relevant_ranges"])
        if item["original_relevant_ranges"] != source["relevant_pages"]:
            raise ValueError(f"{item['id']} does not preserve its original ranges")
        if item.get("validated") is not True:
            raise ValueError(f"{item['id']} is not validated")
    expected = {
        "DRE-04": [[3, 4]],
        "NYT-02": [[1, 2], [13, 15], [19, 22]],
        "NYT-03": [[2, 2], [13, 15], [19, 20]],
    }
    reviewed_by_id = {item["id"]: item for item in questions}
    for question_id, ranges in expected.items():
        if reviewed_by_id[question_id]["relevant_ranges"] != ranges:
            raise ValueError(f"Established decision changed for {question_id}")


def saved_result_is_relevant(saved: dict, benchmark_item: dict) -> bool:
    if saved.get("case_name") != benchmark_item["expected_case"]:
        return False
    expected_source = benchmark_item.get("expected_source_file")
    if expected_source and expected_source not in {
        saved.get("source_file"),
        saved.get("original_source_file"),
    }:
        return False
    return page_range_overlaps(
        saved.get("page_start"),
        saved.get("page_end"),
        benchmark_item["relevant_ranges"],
    )


def score_retrieved(retrieved: list[dict], benchmark_item: dict) -> dict:
    details = []
    first_relevant_rank = None
    for expected_rank, saved in enumerate(retrieved[:5], start=1):
        if saved.get("rank") != expected_rank:
            raise ValueError("Saved results are not in consecutive rank order")
        relevant = saved_result_is_relevant(saved, benchmark_item)
        if relevant and first_relevant_rank is None:
            first_relevant_rank = expected_rank
        detail = deepcopy(saved)
        detail["relevant"] = relevant
        details.append(detail)
    return {
        "hit_at_1": float(first_relevant_rank == 1),
        "hit_at_3": float(first_relevant_rank is not None and first_relevant_rank <= 3),
        "hit_at_5": float(first_relevant_rank is not None and first_relevant_rank <= 5),
        "reciprocal_rank": 1.0 / first_relevant_rank if first_relevant_rank else 0.0,
        "first_relevant_rank": first_relevant_rank,
        "retrieved": details,
    }


def aggregate(question_results: list[dict]) -> dict:
    if not question_results:
        raise ValueError("Cannot aggregate an empty result set")
    count = len(question_results)
    return {
        "question_count": count,
        "hit_at_1": sum(q["metrics"]["hit_at_1"] for q in question_results) / count,
        "hit_at_3": sum(q["metrics"]["hit_at_3"] for q in question_results) / count,
        "hit_at_5": sum(q["metrics"]["hit_at_5"] for q in question_results) / count,
        "mrr": sum(q["metrics"]["reciprocal_rank"] for q in question_results) / count,
    }


def rescore_saved_results(original_results: dict, reviewed: dict) -> dict:
    benchmark = {item["id"]: item for item in reviewed["questions"]}
    configurations = []
    for configuration in original_results["configurations"]:
        if configuration["id"] not in CONFIGURATION_IDS:
            raise ValueError(f"Unexpected configuration {configuration['id']}")
        rescored_questions = []
        for saved_question in configuration["questions"]:
            item = benchmark[saved_question["id"]]
            for field in ("question", "expected_case", "expected_source_file"):
                if saved_question[field] != item[field]:
                    raise ValueError(f"Saved {saved_question['id']} changed field {field}")
            rescored_questions.append(
                {
                    "id": item["id"],
                    "type": item["type"],
                    "question": item["question"],
                    "expected_case": item["expected_case"],
                    "expected_source_file": item["expected_source_file"],
                    "original_relevant_ranges": item["original_relevant_ranges"],
                    "relevant_ranges": item["relevant_ranges"],
                    "metrics": score_retrieved(
                        saved_question["metrics"]["retrieved"], item
                    ),
                }
            )
        if set(q["id"] for q in rescored_questions) != set(benchmark):
            raise ValueError(f"Question IDs mismatch for {configuration['id']}")
        configurations.append(
            {
                "id": configuration["id"],
                "chunk_size": configuration["chunk_size"],
                "chunk_overlap": configuration["chunk_overlap"],
                "vector_count": configuration["vector_count"],
                "metrics": aggregate(rescored_questions),
                "questions": rescored_questions,
            }
        )
    if tuple(item["id"] for item in configurations) != CONFIGURATION_IDS:
        raise ValueError("Saved result configurations are missing or reordered")
    return {
        "experiment": "fixed_chunking_reviewed_relevance",
        "source_experiment": original_results["experiment"],
        "ranking_source": str(ORIGINAL_RESULTS_PATH.relative_to(PROJECT_DIR)),
        "reviewed_benchmark_path": str(REVIEWED_BENCHMARK_PATH.relative_to(PROJECT_DIR)),
        "method": "local rescoring of unchanged saved Top-5 rankings",
        "embedding_model": original_results["embedding_model"],
        "gateway_base_url": original_results["gateway_base_url"],
        "similarity": original_results["similarity"],
        "ranking_depth": original_results["ranking_depth"],
        "configurations": configurations,
    }


def aggregate_by_field(configuration: dict, field: str) -> dict:
    groups = {}
    for item in configuration["questions"]:
        key = item[field]
        groups.setdefault(key, []).append(item)
    return {key: aggregate(groups[key]) for key in sorted(groups)}


def build_breakdown(original_results: dict, reviewed_results: dict) -> dict:
    original_configs = {c["id"]: c for c in original_results["configurations"]}
    reviewed_configs = {c["id"]: c for c in reviewed_results["configurations"]}
    question_maps = {
        cid: {q["id"]: q for q in reviewed_configs[cid]["questions"]}
        for cid in CONFIGURATION_IDS
    }
    questions = []
    sole_wins = Counter()
    pairwise = {
        f"{left}_vs_{right}": {"left_wins": 0, "right_wins": 0, "ties": 0}
        for index, left in enumerate(CONFIGURATION_IDS)
        for right in CONFIGURATION_IDS[index + 1 :]
    }
    all_miss_ids = []
    for question_id in question_maps[CONFIGURATION_IDS[0]]:
        ranks = {
            cid: question_maps[cid][question_id]["metrics"]["first_relevant_rank"]
            for cid in CONFIGURATION_IDS
        }
        numeric = {cid: rank if rank is not None else 6 for cid, rank in ranks.items()}
        if all(rank is None for rank in ranks.values()):
            winners = []
            all_miss_ids.append(question_id)
        else:
            best = min(numeric.values())
            winners = [cid for cid in CONFIGURATION_IDS if numeric[cid] == best]
            if len(winners) == 1:
                sole_wins[winners[0]] += 1
        for index, left in enumerate(CONFIGURATION_IDS):
            for right in CONFIGURATION_IDS[index + 1 :]:
                key = f"{left}_vs_{right}"
                if numeric[left] < numeric[right]:
                    pairwise[key]["left_wins"] += 1
                elif numeric[right] < numeric[left]:
                    pairwise[key]["right_wins"] += 1
                else:
                    pairwise[key]["ties"] += 1
        sample = question_maps[CONFIGURATION_IDS[0]][question_id]
        questions.append(
            {
                "id": question_id,
                "type": sample["type"],
                "case": sample["expected_case"],
                "first_relevant_ranks": ranks,
                "best_rank_configurations": winners,
                "all_four_miss_top_5": not winners,
            }
        )

    converted_by_config = {}
    converted_pairs = []
    for cid in CONFIGURATION_IDS:
        old_map = {q["id"]: q for q in original_configs[cid]["questions"]}
        new_map = question_maps[cid]
        converted = [
            qid
            for qid in new_map
            if old_map[qid]["metrics"]["first_relevant_rank"] is None
            and new_map[qid]["metrics"]["first_relevant_rank"] is not None
        ]
        converted_by_config[cid] = converted
        converted_pairs.extend({"configuration": cid, "question_id": qid} for qid in converted)

    return {
        "reviewed_benchmark": str(REVIEWED_BENCHMARK_PATH.relative_to(PROJECT_DIR)),
        "reviewed_results": str(REVIEWED_RESULTS_PATH.relative_to(PROJECT_DIR)),
        "question_type_metrics": {
            cid: aggregate_by_field(reviewed_configs[cid], "type")
            for cid in CONFIGURATION_IDS
        },
        "case_metrics": {
            cid: aggregate_by_field(reviewed_configs[cid], "expected_case")
            for cid in CONFIGURATION_IDS
        },
        "configuration_wins": {
            "sole_best_rank_counts": {cid: sole_wins[cid] for cid in CONFIGURATION_IDS},
            "tie_for_best_count": sum(len(q["best_rank_configurations"]) > 1 for q in questions),
            "all_four_miss_count": len(all_miss_ids),
            "all_four_miss_question_ids": all_miss_ids,
            "pairwise": pairwise,
            "questions": questions,
        },
        "apparent_misses_converted_to_hits": {
            "configuration_question_pair_count": len(converted_pairs),
            "question_count": len({item["question_id"] for item in converted_pairs}),
            "by_configuration": converted_by_config,
            "pairs": converted_pairs,
        },
    }


def metric_cells(metrics: dict) -> str:
    return " | ".join(f"{metrics[key]:.3f}" for key in ("hit_at_1", "hit_at_3", "hit_at_5", "mrr"))


def render_report(original: dict, reviewed: dict, breakdown: dict, benchmark: dict) -> str:
    old = {c["id"]: c for c in original["configurations"]}
    new = {c["id"]: c for c in reviewed["configurations"]}
    lines = [
        "# Reviewed Fixed-Chunking Evaluation",
        "",
        "This report rescored the unchanged saved Top-5 rankings against the human-reviewed page ranges. No retrieval, embedding, or index operation was run.",
        "",
        "## Old vs. reviewed metrics",
        "",
        "| Configuration | Old Hit@1 | New Hit@1 | Old Hit@3 | New Hit@3 | Old Hit@5 | New Hit@5 | Old MRR | New MRR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cid in CONFIGURATION_IDS:
        om, nm = old[cid]["metrics"], new[cid]["metrics"]
        lines.append(
            f"| {DISPLAY_NAMES[cid]} | {om['hit_at_1']:.3f} | {nm['hit_at_1']:.3f} | {om['hit_at_3']:.3f} | {nm['hit_at_3']:.3f} | {om['hit_at_5']:.3f} | {nm['hit_at_5']:.3f} | {om['mrr']:.3f} | {nm['mrr']:.3f} |"
        )
    changed = benchmark["changed_question_count"]
    converted = breakdown["apparent_misses_converted_to_hits"]
    ordered = sorted(
        CONFIGURATION_IDS,
        key=lambda cid: (
            new[cid]["metrics"]["mrr"], new[cid]["metrics"]["hit_at_1"],
            new[cid]["metrics"]["hit_at_5"], new[cid]["metrics"]["hit_at_3"],
        ),
        reverse=True,
    )
    lines += [
        "",
        f"The content review expanded relevance for **{changed} of 40 questions**. It converted **{converted['configuration_question_pair_count']} configuration-question misses** across **{converted['question_count']} distinct questions** into Top-5 hits. Metrics changed only because saved passages now intersect additional human-reviewed answer-bearing ranges.",
        "",
        f"Ordering by MRR is: {', '.join(DISPLAY_NAMES[cid] for cid in ordered)}. Among the tested configurations on the reviewed 40-question CourtLens benchmark, **{DISPLAY_NAMES[ordered[0]]}** has the highest MRR. This is evidence for this benchmark, not a universal optimum.",
        "",
        "## Breakdown by question type",
        "",
        "Many types contain very few questions, so these results are exploratory.",
        "",
        "| Question type | Configuration | N | Hit@1 | Hit@3 | Hit@5 | MRR |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    types = sorted({q["type"] for q in benchmark["questions"]})
    for qtype in types:
        for cid in CONFIGURATION_IDS:
            metrics = breakdown["question_type_metrics"][cid][qtype]
            lines.append(f"| {qtype} | {DISPLAY_NAMES[cid]} | {metrics['question_count']} | {metric_cells(metrics)} |")
    lines += [
        "",
        "## Breakdown by case",
        "",
        "Each case contributes five questions. Differences may reflect question wording, opinion structure, extraction quality, or retrieval behavior; this table cannot isolate causation.",
        "",
        "| Case | Configuration | N | Hit@1 | Hit@3 | Hit@5 | MRR |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    cases = sorted({q["expected_case"] for q in benchmark["questions"]})
    for case in cases:
        for cid in CONFIGURATION_IDS:
            metrics = breakdown["case_metrics"][cid][case]
            lines.append(f"| {case} | {DISPLAY_NAMES[cid]} | {metrics['question_count']} | {metric_cells(metrics)} |")
    wins = breakdown["configuration_wins"]
    lines += [
        "",
        "## Best first-relevant ranks",
        "",
        "A sole win means one configuration had the best first relevant rank for that question. Equal ranks are ties; an all-configuration miss is kept separate.",
        "",
        "| Configuration | Sole best-rank questions |",
        "|---|---:|",
    ]
    for cid in CONFIGURATION_IDS:
        lines.append(f"| {DISPLAY_NAMES[cid]} | {wins['sole_best_rank_counts'][cid]} |")
    lines += [
        "",
        f"Ties for best rank: **{wins['tie_for_best_count']}**. All four configurations still miss Top-5 for **{wins['all_four_miss_count']}** questions: {', '.join(wins['all_four_miss_question_ids']) or 'none'}.",
        "",
        "## Interpretation and limitations",
        "",
        "The type and case tables show that the best observed configuration varies across subsets, but most type groups are tiny and every case has only five questions. These descriptive differences can motivate later investigation of structure and multi-granularity retrieval; they do not establish that a type or document requires a particular chunk size.",
        "",
        "The review packet contains only passages retrieved in the saved Top-5 by at least one configuration. The reviewed ranges can correct false negatives visible in that pool, but they are not an exhaustive map of every answer-bearing page. Page intersection also gives full credit to a chunk that merely overlaps a labeled page, and the 40-question benchmark is too small for strong subgroup claims.",
        "",
        "No era split was added. Choosing a historical/modern boundary would add an arbitrary assumption without strengthening this local rescoring analysis.",
    ]
    return "\n".join(lines) + "\n"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_all() -> tuple[dict, dict, dict, str]:
    original_benchmark = load_json(ORIGINAL_BENCHMARK_PATH)
    review_packet = load_json(REVIEW_PACKET_PATH)
    original_results = load_json(ORIGINAL_RESULTS_PATH)
    reviewed_benchmark = build_reviewed_benchmark(original_benchmark, review_packet)
    reviewed_benchmark["provenance"]["original_benchmark_sha256"] = sha256(ORIGINAL_BENCHMARK_PATH)
    reviewed_benchmark["provenance"]["review_packet_sha256"] = sha256(REVIEW_PACKET_PATH)
    reviewed_results = rescore_saved_results(original_results, reviewed_benchmark)
    reviewed_results["source_results_sha256"] = sha256(ORIGINAL_RESULTS_PATH)
    breakdown = build_breakdown(original_results, reviewed_results)
    report = render_report(original_results, reviewed_results, breakdown, reviewed_benchmark)
    return reviewed_benchmark, reviewed_results, breakdown, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and build in memory without writing")
    args = parser.parse_args()
    benchmark, results, breakdown, report = build_all()
    if args.check:
        print("Reviewed benchmark and rescoring validation passed")
        return
    write_json(REVIEWED_BENCHMARK_PATH, benchmark)
    write_json(REVIEWED_RESULTS_PATH, results)
    write_json(BREAKDOWN_PATH, breakdown)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REVIEWED_BENCHMARK_PATH.relative_to(PROJECT_DIR)}")
    print(f"Wrote {REVIEWED_RESULTS_PATH.relative_to(PROJECT_DIR)}")
    print(f"Wrote {BREAKDOWN_PATH.relative_to(PROJECT_DIR)}")
    print(f"Wrote {REPORT_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
