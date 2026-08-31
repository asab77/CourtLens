"""Validation and append-only local storage for human model evaluations."""

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
EVALUATIONS_PATH = PROJECT_DIR / "data" / "evaluations.jsonl"
SCORE_NAMES = ("correctness", "faithfulness", "clarity", "citation_quality")
WINNER_OPTIONS = ("Model A", "Model B", "Tie")


def validate_scores(scores: dict) -> None:
    """Require every human rating to be an integer from 1 through 5."""
    if set(scores) != set(SCORE_NAMES):
        raise ValueError("Complete every rating before saving.")
    if any(not isinstance(value, int) or not 1 <= value <= 5 for value in scores.values()):
        raise ValueError("Every rating must be an integer from 1 to 5.")


def build_evaluation_record(
    comparison: dict,
    model_a_scores: dict,
    model_b_scores: dict,
    winner: str | None,
) -> dict:
    """Validate the comparison and create one JSON-serializable evaluation record."""
    validate_scores(model_a_scores)
    validate_scores(model_b_scores)
    if winner not in WINNER_OPTIONS:
        raise ValueError("Choose Model A, Model B, or Tie before saving.")

    evidence = comparison["evidence"]
    model_a_chunk_ids = comparison["model_a_chunk_ids"]
    model_b_chunk_ids = comparison["model_b_chunk_ids"]
    if model_a_chunk_ids != model_b_chunk_ids:
        raise ValueError("Model A and Model B did not receive identical chunk IDs.")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": comparison["question"],
        "model_a": {
            "display_name": comparison["model_a_name"],
            "gateway_id": comparison["model_a_id"],
        },
        "model_b": {
            "display_name": comparison["model_b_name"],
            "gateway_id": comparison["model_b_id"],
        },
        "top_k": comparison["top_k"],
        "case_filter": comparison["case_filter"] or "All cases",
        "retrieved_chunk_ids": model_a_chunk_ids,
        "retrieved_source_metadata": [
            {
                "source_id": item["source_id"],
                "vector_id": item["vector_id"],
                "similarity": item["similarity"],
                **item["metadata"],
            }
            for item in evidence
        ],
        "model_a_answer": comparison["model_a_answer"],
        "model_b_answer": comparison["model_b_answer"],
        "model_a_scores": model_a_scores,
        "model_b_scores": model_b_scores,
        "winner": winner,
    }


def append_evaluation(record: dict, path: Path = EVALUATIONS_PATH) -> None:
    """Append one evaluation record without overwriting prior records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
