"""Run a simple top-5 semantic search against the local FAISS index."""

import json
import sys
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI

from gateway_config import (
    EMBEDDING_MODEL,
    GATEWAY_BASE_URL,
    GATEWAY_PROVIDER,
    require_nyu_api_gateway_api_key,
)


PROJECT_DIR = Path(__file__).resolve().parent
VECTOR_STORE_DIR = PROJECT_DIR / "data" / "vector_store"
INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
RECORDS_PATH = VECTOR_STORE_DIR / "records.jsonl"
MANIFEST_PATH = VECTOR_STORE_DIR / "manifest.json"
TOP_K = 5


def load_vector_store() -> tuple[faiss.Index, list[dict], dict]:
    """Load the index and verify its row-to-record mapping."""
    index = faiss.read_index(str(INDEX_PATH))
    records = [
        json.loads(line)
        for line in RECORDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if index.ntotal != len(records) or index.ntotal != manifest["vector_count"]:
        raise ValueError("FAISS vectors, records, and manifest counts do not match")
    if any(record["vector_id"] != position for position, record in enumerate(records)):
        raise ValueError("Stored vector IDs are not aligned with record positions")
    if manifest["embedding_model"] != EMBEDDING_MODEL:
        raise ValueError("The index was built with a different embedding model")
    if manifest.get("gateway_base_url") != GATEWAY_BASE_URL:
        raise ValueError("The index was built through a different embedding gateway")

    return index, records, manifest


def semantic_search(
    question: str,
    top_k: int = TOP_K,
    case_name: str | None = None,
    vector_store: tuple[faiss.Index, list[dict], dict] | None = None,
) -> list[dict]:
    """Embed a question and return ranked FAISS results with stored metadata."""
    question = question.strip()
    if not question:
        raise ValueError("Please enter a non-empty question.")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    index, records, manifest = vector_store or load_vector_store()
    client = OpenAI(
        api_key=require_nyu_api_gateway_api_key(),
        base_url=GATEWAY_BASE_URL,
        default_headers={"x-portkey-provider": GATEWAY_PROVIDER},
    )
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[question])
    query_vector = np.asarray([response.data[0].embedding], dtype="float32")
    faiss.normalize_L2(query_vector)

    # Searching every row when filtering preserves the true ranking within one case.
    search_count = index.ntotal if case_name else min(top_k, index.ntotal)
    scores, vector_ids = index.search(query_vector, search_count)

    results = []
    for score, vector_id in zip(scores[0], vector_ids[0]):
        if vector_id < 0:
            continue
        record = records[int(vector_id)]
        if case_name and record["metadata"]["case_name"] != case_name:
            continue
        results.append(
            {
                "vector_id": int(vector_id),
                "similarity": float(score),
                "text": record["text"],
                "metadata": record["metadata"],
            }
        )
        if len(results) == top_k:
            break

    return results


def main() -> None:
    if not all(path.exists() for path in (INDEX_PATH, RECORDS_PATH, MANIFEST_PATH)):
        raise SystemExit("Vector store not found. Run: python3 build_index.py")

    question = " ".join(sys.argv[1:]).strip() or input("Question: ").strip()
    if not question:
        raise SystemExit("Please enter a non-empty question.")

    try:
        results = semantic_search(question)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print(f"\nTop {len(results)} results for: {question}\n")
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(f"--- Result {rank} ---")
        print(f"case_name: {metadata['case_name']}")
        print(f"page_start: {metadata['page_start']}")
        print(f"page_end: {metadata['page_end']}")
        print(f"similarity: {result['similarity']:.4f}")
        print("chunk text:")
        print(result["text"])
        print()


if __name__ == "__main__":
    main()
