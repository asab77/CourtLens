"""Embed all case chunks and build a local FAISS cosine-similarity index."""

import json
import time
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
from embedding_retry import call_with_rate_limit_retry


PROJECT_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = PROJECT_DIR / "data" / "chunks"
VECTOR_STORE_DIR = PROJECT_DIR / "data" / "vector_store"
INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
RECORDS_PATH = VECTOR_STORE_DIR / "records.jsonl"
MANIFEST_PATH = VECTOR_STORE_DIR / "manifest.json"

BATCH_SIZE = 100
SUCCESSFUL_BATCH_DELAY_SECONDS = 10


def load_chunk_records(chunks_dir: Path = CHUNKS_DIR) -> tuple[list[dict], list[str]]:
    """Load each JSONL chunk file exactly once in deterministic order."""
    chunk_paths = sorted(chunks_dir.glob("*.jsonl"))
    resolved_paths = [path.resolve() for path in chunk_paths]

    if not chunk_paths:
        raise ValueError(f"No chunk files found in {chunks_dir}")
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


def create_embeddings(
    client: OpenAI, texts: list[str], model: str = EMBEDDING_MODEL
) -> np.ndarray:
    """Embed texts in batches while preserving their original order."""
    embeddings = []
    batch_count = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        batch_number = start // BATCH_SIZE + 1
        chunk_start = start + 1
        chunk_end = min(start + BATCH_SIZE, len(texts))
        response = call_with_rate_limit_retry(
            lambda: client.embeddings.create(model=model, input=batch),
            (
                f"document embedding batch {batch_number}/{batch_count} "
                f"(chunks {chunk_start}-{chunk_end})"
            ),
        )
        ordered_data = sorted(response.data, key=lambda item: item.index)
        embeddings.extend(item.embedding for item in ordered_data)
        print(f"Embedded {chunk_end}/{len(texts)} chunks")
        if batch_number < batch_count:
            time.sleep(SUCCESSFUL_BATCH_DELAY_SECONDS)

    matrix = np.asarray(embeddings, dtype="float32")
    if matrix.ndim != 2 or matrix.shape[0] != len(texts):
        raise ValueError("Embedding response count does not match chunk count")
    return matrix


def save_vector_store(
    records: list[dict],
    embeddings: np.ndarray,
    chunk_files: list[str],
    vector_store_dir: Path = VECTOR_STORE_DIR,
    build_metadata: dict | None = None,
    gateway_base_url: str = GATEWAY_BASE_URL,
    gateway_provider: str = GATEWAY_PROVIDER,
    embedding_model: str = EMBEDDING_MODEL,
) -> None:
    """Save the FAISS index, aligned records, and a small build manifest."""
    vector_store_dir.mkdir(parents=True, exist_ok=True)
    index_path = vector_store_dir / "index.faiss"
    records_path = vector_store_dir / "records.jsonl"
    manifest_path = vector_store_dir / "manifest.json"

    # Unit-length vectors make inner product equivalent to cosine similarity.
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    if index.ntotal != len(records):
        raise ValueError("FAISS vector count does not match record count")

    temporary_index = index_path.with_suffix(".faiss.tmp")
    temporary_records = records_path.with_suffix(".jsonl.tmp")

    faiss.write_index(index, str(temporary_index))
    with temporary_records.open("w", encoding="utf-8") as records_file:
        for vector_id, record in enumerate(records):
            stored_record = {
                "vector_id": vector_id,
                "text": record["text"],
                "metadata": record["metadata"],
            }
            records_file.write(json.dumps(stored_record, ensure_ascii=False) + "\n")

    temporary_index.replace(index_path)
    temporary_records.replace(records_path)

    manifest = {
        "gateway_base_url": gateway_base_url,
        "provider": gateway_provider,
        "embedding_model": embedding_model,
        "similarity": "cosine",
        "dimension": index.d,
        "vector_count": index.ntotal,
        "record_count": len(records),
        "chunk_file_count": len(chunk_files),
        "chunk_files": chunk_files,
        **(build_metadata or {}),
    }
    manifest_path.write_text(
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
