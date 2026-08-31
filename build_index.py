"""Embed all case chunks and build a local FAISS cosine-similarity index."""

import json
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
CHUNKS_DIR = PROJECT_DIR / "data" / "chunks"
VECTOR_STORE_DIR = PROJECT_DIR / "data" / "vector_store"
INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
RECORDS_PATH = VECTOR_STORE_DIR / "records.jsonl"
MANIFEST_PATH = VECTOR_STORE_DIR / "manifest.json"

BATCH_SIZE = 100


def load_chunk_records() -> tuple[list[dict], list[str]]:
    """Load each JSONL chunk file exactly once in deterministic order."""
    chunk_paths = sorted(CHUNKS_DIR.glob("*.jsonl"))
    resolved_paths = [path.resolve() for path in chunk_paths]

    if not chunk_paths:
        raise ValueError(f"No chunk files found in {CHUNKS_DIR}")
    if len(resolved_paths) != len(set(resolved_paths)):
        raise ValueError("Duplicate chunk files were discovered")

    records = []
    for chunk_path in chunk_paths:
        with chunk_path.open(encoding="utf-8") as chunk_file:
            for line_number, line in enumerate(chunk_file, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not record.get("text"):
                    raise ValueError(f"Empty chunk text in {chunk_path.name}:{line_number}")
                if not isinstance(record.get("metadata"), dict):
                    raise ValueError(f"Missing metadata in {chunk_path.name}:{line_number}")
                records.append(record)

    return records, [path.name for path in chunk_paths]


def create_embeddings(client: OpenAI, texts: list[str]) -> np.ndarray:
    """Embed texts in batches while preserving their original order."""
    embeddings = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        ordered_data = sorted(response.data, key=lambda item: item.index)
        embeddings.extend(item.embedding for item in ordered_data)
        print(f"Embedded {min(start + BATCH_SIZE, len(texts))}/{len(texts)} chunks")

    matrix = np.asarray(embeddings, dtype="float32")
    if matrix.ndim != 2 or matrix.shape[0] != len(texts):
        raise ValueError("Embedding response count does not match chunk count")
    return matrix


def save_vector_store(
    records: list[dict], embeddings: np.ndarray, chunk_files: list[str]
) -> None:
    """Save the FAISS index, aligned records, and a small build manifest."""
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Unit-length vectors make inner product equivalent to cosine similarity.
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    if index.ntotal != len(records):
        raise ValueError("FAISS vector count does not match record count")

    temporary_index = INDEX_PATH.with_suffix(".faiss.tmp")
    temporary_records = RECORDS_PATH.with_suffix(".jsonl.tmp")

    faiss.write_index(index, str(temporary_index))
    with temporary_records.open("w", encoding="utf-8") as records_file:
        for vector_id, record in enumerate(records):
            stored_record = {
                "vector_id": vector_id,
                "text": record["text"],
                "metadata": record["metadata"],
            }
            records_file.write(json.dumps(stored_record, ensure_ascii=False) + "\n")

    temporary_index.replace(INDEX_PATH)
    temporary_records.replace(RECORDS_PATH)

    manifest = {
        "gateway_base_url": GATEWAY_BASE_URL,
        "provider": GATEWAY_PROVIDER,
        "embedding_model": EMBEDDING_MODEL,
        "similarity": "cosine",
        "dimension": index.d,
        "vector_count": index.ntotal,
        "record_count": len(records),
        "chunk_file_count": len(chunk_files),
        "chunk_files": chunk_files,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> None:
    records, chunk_files = load_chunk_records()
    print(f"Loaded {len(records)} chunks from {len(chunk_files)} unique files.")

    client = OpenAI(
        api_key=require_nyu_api_gateway_api_key(),
        base_url=GATEWAY_BASE_URL,
        default_headers={"x-portkey-provider": GATEWAY_PROVIDER},
    )
    embeddings = create_embeddings(client, [record["text"] for record in records])
    save_vector_store(records, embeddings, chunk_files)
    print(f"Saved {len(records)} vectors to {INDEX_PATH}")
    print(f"Saved aligned chunk records to {RECORDS_PATH}")


if __name__ == "__main__":
    main()
