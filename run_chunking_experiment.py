"""Build and evaluate fixed-size chunking variants without touching production data."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from build_index import create_embeddings, load_chunk_records, save_vector_store
from benchmark_relevance import page_range_overlaps, relevant_ranges_for_item
from chunk_text import PROCESSED_DIR
from gateway_config import (
    EXPERIMENT_EMBEDDING_MODEL,
    EXPERIMENT_GATEWAY_BASE_URL,
    EXPERIMENT_GATEWAY_PROVIDER,
)
from retrieve import (
    embed_question,
    experiment_embedding_client,
    load_vector_store,
    search_vector_store,
)


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_PATH = PROJECT_DIR / "data" / "evaluation" / "chunking_benchmark.json"
EXPERIMENT_ROOT = PROJECT_DIR / "data" / "experiments" / "chunking"
RESULTS_PATH = EXPERIMENT_ROOT / "results.json"
MAX_RANK = 5
CONFIGURATIONS = (
    {"id": "600_100", "chunk_size": 600, "chunk_overlap": 100},
    {"id": "900_150", "chunk_size": 900, "chunk_overlap": 150},
    {"id": "1200_200", "chunk_size": 1200, "chunk_overlap": 200},
    {"id": "1500_200", "chunk_size": 1500, "chunk_overlap": 200},
)


def load_existing_configuration_chunks(
    configuration: dict,
    chunks_dir: Path,
    processed_dir: Path = PROCESSED_DIR,
) -> tuple[list[dict], list[str]]:
    """Validate and reuse one complete chunk set without regenerating it."""
    expected_id = f"{configuration['chunk_size']}_{configuration['chunk_overlap']}"
    if configuration["id"] != expected_id:
        raise ValueError(
            f"Configuration id {configuration['id']} does not match {expected_id}"
        )

    processed_paths = sorted(processed_dir.glob("*.txt"))
    if not processed_paths:
        raise ValueError(f"No canonical processed files found in {processed_dir}")
    expected_files = {f"{path.stem}.jsonl" for path in processed_paths}
    actual_paths = sorted(chunks_dir.glob("*.jsonl"))
    actual_files = {path.name for path in actual_paths}
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        raise ValueError(
            f"Chunk set for {configuration['id']} is incomplete or unexpected; "
            f"missing={missing}, extra={extra}"
        )

    try:
        records, chunk_files = load_chunk_records(chunks_dir)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(
            f"Chunk set for {configuration['id']} is malformed: {error}"
        ) from error

    expected_sources = {f"{path.stem}.pdf" for path in processed_paths}
    records_by_source = {source: [] for source in expected_sources}
    required_metadata = {
        "case_name",
        "source_file",
        "page_start",
        "page_end",
        "chunk_index",
        "token_count",
    }
    for record in records:
        metadata = record["metadata"]
        missing_metadata = required_metadata - metadata.keys()
        if missing_metadata:
            raise ValueError(
                f"Chunk set for {configuration['id']} is missing metadata: "
                f"{sorted(missing_metadata)}"
            )
        source_file = metadata["source_file"]
        if source_file not in records_by_source:
            raise ValueError(
                f"Chunk set for {configuration['id']} has unexpected source {source_file}"
            )
        token_count = metadata["token_count"]
        if (
            not isinstance(token_count, int)
            or token_count < 1
            or token_count > configuration["chunk_size"]
        ):
            raise ValueError(
                f"Chunk set for {configuration['id']} has invalid token_count "
                f"{token_count!r} for {source_file}"
            )
        page_start = metadata["page_start"]
        page_end = metadata["page_end"]
        if (
            not isinstance(page_start, int)
            or not isinstance(page_end, int)
            or page_start < 1
            or page_start > page_end
        ):
            raise ValueError(
                f"Chunk set for {configuration['id']} has invalid page range"
            )
        records_by_source[source_file].append(metadata["chunk_index"])

    for source_file, chunk_indexes in records_by_source.items():
        if not chunk_indexes:
            raise ValueError(
                f"Chunk set for {configuration['id']} has no records for {source_file}"
            )
        if chunk_indexes != list(range(len(chunk_indexes))):
            raise ValueError(
                f"Chunk indexes for {source_file} are not sequential from zero"
            )

    return records, chunk_files


def result_is_relevant(result: dict, benchmark_item: dict) -> bool:
    """Require both the labeled source and an overlapping labeled page range."""
    metadata = result["metadata"]
    if metadata.get("case_name") != benchmark_item["expected_case"]:
        return False

    expected_source = benchmark_item.get("expected_source_file")
    if expected_source and expected_source not in {
        metadata.get("source_file"),
        metadata.get("original_source_file"),
    }:
        return False

    return page_range_overlaps(
        metadata.get("page_start"),
        metadata.get("page_end"),
        relevant_ranges_for_item(benchmark_item),
    )


def evaluate_ranked_results(
    results: list[dict], benchmark_item: dict, max_rank: int = MAX_RANK
) -> dict:
    """Annotate ranked results and calculate Hit@K plus reciprocal rank."""
    details = []
    first_relevant_rank = None
    for rank, result in enumerate(results[:max_rank], start=1):
        relevant = result_is_relevant(result, benchmark_item)
        if relevant and first_relevant_rank is None:
            first_relevant_rank = rank
        metadata = result["metadata"]
        details.append(
            {
                "rank": rank,
                "vector_id": result["vector_id"],
                "case_name": metadata["case_name"],
                "source_file": metadata["source_file"],
                "original_source_file": metadata.get("original_source_file"),
                "page_start": metadata["page_start"],
                "page_end": metadata["page_end"],
                "chunk_index": metadata["chunk_index"],
                "token_count": metadata["token_count"],
                "similarity": result["similarity"],
                "relevant": relevant,
            }
        )

    return {
        "hit_at_1": float(first_relevant_rank is not None and first_relevant_rank <= 1),
        "hit_at_3": float(first_relevant_rank is not None and first_relevant_rank <= 3),
        "hit_at_5": float(first_relevant_rank is not None and first_relevant_rank <= 5),
        "reciprocal_rank": 1.0 / first_relevant_rank if first_relevant_rank else 0.0,
        "first_relevant_rank": first_relevant_rank,
        "retrieved": details,
    }


def aggregate_metrics(question_results: list[dict]) -> dict:
    """Average binary Hit@K and reciprocal rank over benchmark questions."""
    if not question_results:
        raise ValueError("Cannot aggregate an empty evaluation")
    count = len(question_results)
    return {
        "question_count": count,
        "hit_at_1": sum(item["metrics"]["hit_at_1"] for item in question_results) / count,
        "hit_at_3": sum(item["metrics"]["hit_at_3"] for item in question_results) / count,
        "hit_at_5": sum(item["metrics"]["hit_at_5"] for item in question_results) / count,
        "mrr": sum(item["metrics"]["reciprocal_rank"] for item in question_results) / count,
    }


def load_benchmark(path: Path, allow_unvalidated: bool = False) -> list[dict]:
    """Validate the stable page-based benchmark and require manual approval."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    if not questions:
        raise ValueError("The benchmark contains no questions")

    required = {"id", "question", "expected_case", "validated"}
    seen_ids = set()
    for item in questions:
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Benchmark item is missing fields: {sorted(missing)}")
        if item["id"] in seen_ids:
            raise ValueError(f"Duplicate benchmark id: {item['id']}")
        seen_ids.add(item["id"])
        try:
            relevant_ranges_for_item(item)
        except ValueError as error:
            raise ValueError(
                f"Benchmark item {item['id']} has invalid relevant ranges: {error}"
            ) from error

    unvalidated = [item["id"] for item in questions if not item["validated"]]
    if unvalidated and not allow_unvalidated:
        raise ValueError(
            "Manual benchmark review is required. Validate page labels and set "
            f"validated=true for: {', '.join(unvalidated)}"
        )
    return questions


def build_or_load_configuration(configuration: dict, rebuild: bool = False):
    """Reuse a matching experiment index or build it in an isolated directory."""
    configuration_dir = EXPERIMENT_ROOT / configuration["id"]
    chunks_dir = configuration_dir / "chunks"
    vector_store_dir = configuration_dir / "vector_store"
    required_paths = [
        vector_store_dir / "index.faiss",
        vector_store_dir / "records.jsonl",
        vector_store_dir / "manifest.json",
    ]

    existing_store_paths = [path for path in required_paths if path.exists()]
    if existing_store_paths and len(existing_store_paths) != len(required_paths):
        raise ValueError(
            f"Experimental vector store for {configuration['id']} is incomplete"
        )

    if not rebuild and len(existing_store_paths) == len(required_paths):
        store = load_vector_store(
            vector_store_dir,
            expected_embedding_model=EXPERIMENT_EMBEDDING_MODEL,
            expected_gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
        )
        manifest = store[2]
        if (
            manifest.get("chunk_size") != configuration["chunk_size"]
            or manifest.get("chunk_overlap") != configuration["chunk_overlap"]
        ):
            raise ValueError(f"Stored manifest does not match {configuration['id']}")
        print(f"Reusing {configuration['id']} ({store[0].ntotal} vectors)")
        return store

    records, chunk_files = load_existing_configuration_chunks(
        configuration, chunks_dir
    )
    client = experiment_embedding_client()
    embeddings = create_embeddings(
        client,
        [record["text"] for record in records],
        model=EXPERIMENT_EMBEDDING_MODEL,
    )
    save_vector_store(
        records,
        embeddings,
        chunk_files,
        vector_store_dir=vector_store_dir,
        gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
        gateway_provider=EXPERIMENT_GATEWAY_PROVIDER,
        embedding_model=EXPERIMENT_EMBEDDING_MODEL,
        build_metadata={
            "experiment": "fixed_chunk_size_overlap",
            "chunk_size": configuration["chunk_size"],
            "chunk_overlap": configuration["chunk_overlap"],
        },
    )
    store = load_vector_store(
        vector_store_dir,
        expected_embedding_model=EXPERIMENT_EMBEDDING_MODEL,
        expected_gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
    )
    print(
        f"Built {configuration['id']}: {len(records)} chunks / "
        f"{store[0].ntotal} vectors"
    )
    return store


def print_comparison(configuration_results: list[dict]) -> None:
    """Print a compact fixed-width aggregate metric table."""
    print()
    print(f"{'Configuration':<18} {'Hit@1':>9} {'Hit@3':>9} {'Hit@5':>9} {'MRR':>9}")
    print("-" * 58)
    for result in configuration_results:
        metrics = result["metrics"]
        label = f"{result['chunk_size']} / {result['chunk_overlap']}"
        print(
            f"{label:<18} {metrics['hit_at_1']:>9.3f} "
            f"{metrics['hit_at_3']:>9.3f} {metrics['hit_at_5']:>9.3f} "
            f"{metrics['mrr']:>9.3f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK_PATH)
    parser.add_argument("--rebuild", action="store_true", help="Rebuild all experiment indexes")
    parser.add_argument(
        "--allow-unvalidated",
        action="store_true",
        help="Run unvalidated labels before manual approval (not for final reporting)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        benchmark = load_benchmark(
            args.benchmark, allow_unvalidated=args.allow_unvalidated
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Benchmark validation failed: {error}") from error
    stores = {
        configuration["id"]: build_or_load_configuration(configuration, args.rebuild)
        for configuration in CONFIGURATIONS
    }

    client = experiment_embedding_client()
    query_vectors = {
        item["id"]: embed_question(
            item["question"], client=client, model=EXPERIMENT_EMBEDDING_MODEL
        )
        for item in benchmark
    }
    configuration_results = []
    for configuration in CONFIGURATIONS:
        question_results = []
        store = stores[configuration["id"]]
        for item in benchmark:
            ranked = search_vector_store(query_vectors[item["id"]], store, top_k=MAX_RANK)
            metrics = evaluate_ranked_results(ranked, item)
            question_results.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "expected_case": item["expected_case"],
                    "expected_source_file": item.get("expected_source_file"),
                    "relevant_pages": relevant_ranges_for_item(item),
                    "metrics": metrics,
                }
            )
        configuration_results.append(
            {
                **configuration,
                "vector_count": store[0].ntotal,
                "metrics": aggregate_metrics(question_results),
                "questions": question_results,
            }
        )

    output = {
        "experiment": "fixed_chunk_size_overlap",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "embedding_model": EXPERIMENT_EMBEDDING_MODEL,
        "gateway_base_url": EXPERIMENT_GATEWAY_BASE_URL,
        "similarity": "cosine_via_normalized_inner_product",
        "ranking_depth": MAX_RANK,
        "benchmark_path": str(args.benchmark),
        "configurations": configuration_results,
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print_comparison(configuration_results)
    print(f"\nSaved detailed results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
