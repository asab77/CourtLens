"""Read-only validation of the frozen structure-aware runtime asset bundle.

No build, embedding, retrieval or generation calls occur here. The sidecar
chunks and chunk manifest must accompany a configured vector_store directory.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path

import faiss
import numpy as np

from gateway_config import (
    PROJECT_DIR, VERCEL_BASE_URL, VERCEL_EMBEDDING_MODEL, VERCEL_PROVIDER,
    runtime_vector_store_path,
)
from retrieve import load_vector_store

EXPECTED_RECORDS = 433
EXPECTED_DIMENSION = 1536
STRATEGY = "structure_aware_v1"
LOGIC_VERSION = "phase4b1-v1"


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Required runtime asset is missing: {path}. Supply the frozen bundle; no rebuild is attempted.")


def _sha256(path: Path) -> str:
    _require_file(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path):
    _require_file(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Malformed runtime JSON asset: {path}") from error


def _jsonl(path: Path) -> list[dict]:
    _require_file(path)
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Malformed runtime JSONL asset: {path}") from error


def load_runtime_vector_store(vector_store_dir: Path | None = None):
    """Validate a store and return the existing (index, records, manifest) tuple.

    The manifests declare provenance, not cryptographic authenticity. Matching
    hashes and exact frozen records establish consistency, not proof that an
    arbitrary embedding was computed from its declared text.
    """
    path = Path(vector_store_dir) if vector_store_dir is not None else runtime_vector_store_path()
    path = path.resolve()
    try:
        return _validate(path)
    except (KeyError, TypeError, AttributeError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Malformed runtime asset schema in {path}") from error


def _validate(path: Path):
    for name in ("index.faiss", "records.jsonl", "manifest.json"):
        _require_file(path / name)
    chunks_path = path.parent / "chunks.jsonl"
    chunk_manifest_path = path.parent / "manifest.json"
    manifest = _json(path / "manifest.json")
    chunk_manifest = _json(chunk_manifest_path)
    frozen = _jsonl(chunks_path)
    if not isinstance(manifest, dict) or not isinstance(chunk_manifest, dict):
        raise ValueError("Runtime manifests must be JSON objects")
    required = {
        "vector_count": EXPECTED_RECORDS, "record_count": EXPECTED_RECORDS,
        "dimension": EXPECTED_DIMENSION, "faiss_index_type": "IndexFlatIP",
        "normalization": "L2_unit_length", "similarity": "cosine",
        "embedding_model": VERCEL_EMBEDDING_MODEL, "gateway_base_url": VERCEL_BASE_URL,
        "provider": VERCEL_PROVIDER, "strategy": STRATEGY, "logic_version": LOGIC_VERSION,
        "chunk_file_count": 1, "chunk_files": ["chunks.jsonl"],
    }
    for name, expected in required.items():
        if manifest.get(name) != expected:
            raise ValueError(f"Runtime manifest {name} mismatch; expected {expected!r}")
    if (chunk_manifest.get("number_of_chunks") != EXPECTED_RECORDS
            or chunk_manifest.get("strategy") != STRATEGY
            or chunk_manifest.get("logic_version") != LOGIC_VERSION
            or len(frozen) != EXPECTED_RECORDS):
        raise ValueError("Frozen chunk manifest/count/strategy mismatch")
    for name, artifact in (("chunks_sha256", chunks_path), ("chunk_manifest_sha256", chunk_manifest_path)):
        if manifest.get(name) != _sha256(artifact):
            raise ValueError(f"Runtime source artifact hash mismatch: {name}")
    # The preview is a project-relative provenance artifact, also required in a
    # deployment. Relocating the bundle does not change that canonical path.
    source_name = chunk_manifest.get("source_structural_artifact")
    if not isinstance(source_name, str) or not source_name:
        raise ValueError("Missing source structural artifact path")
    relative_source = Path(source_name)
    source_path = (PROJECT_DIR / relative_source).resolve()
    if relative_source.is_absolute() or not source_path.is_relative_to(PROJECT_DIR.resolve()):
        raise ValueError("Source structural artifact must be a project-relative path")
    if chunk_manifest.get("source_structural_artifact_sha256") != _sha256(source_path):
        raise ValueError("Source structural artifact hash mismatch")
    try:
        store = load_vector_store(path, expected_embedding_model=VERCEL_EMBEDDING_MODEL,
                                  expected_gateway_base_url=VERCEL_BASE_URL)
    except RuntimeError as error:
        raise ValueError(f"Cannot read runtime FAISS index: {path / 'index.faiss'}") from error
    index, stored, _ = store
    if not isinstance(index, faiss.IndexFlatIP) or index.metric_type != faiss.METRIC_INNER_PRODUCT:
        raise ValueError("Runtime index must be FAISS IndexFlatIP")
    if index.d != EXPECTED_DIMENSION:
        raise ValueError("Runtime FAISS dimension mismatch")
    if index.ntotal != EXPECTED_RECORDS or len(stored) != EXPECTED_RECORDS:
        raise ValueError("Runtime vector/record count mismatch")
    seen = set()
    counts = Counter()
    sources = []
    for position, (record, original) in enumerate(zip(stored, frozen)):
        if record["text"] != original["text"] or record["metadata"] != original["metadata"]:
            raise ValueError(f"Frozen chunk text/metadata/order provenance mismatch at vector {position}")
        metadata = record["metadata"]
        source = metadata["source_file"]
        chunk_id = metadata["chunk_id"]
        if (not isinstance(chunk_id, str) or not chunk_id or chunk_id in seen
                or metadata["chunk_index"] != counts[source]):
            raise ValueError(f"Invalid chunk identity/order at vector {position}")
        if (not isinstance(record["text"], str) or not record["text"].strip()
                or metadata["chunking_strategy"] != STRATEGY
                or not isinstance(source, str) or not source
                or not metadata["case_name"] or not metadata["original_source_file"]
                or not 1 <= metadata["page_start"] <= metadata["page_end"]
                or not 1 <= metadata["token_count"] <= 1100
                or not isinstance(metadata["major_unit_id"], str)
                or metadata["opinion_type"] == "foreign"
                or not metadata["provenance"]
                or any(p["major_unit_id"] != metadata["major_unit_id"] for p in metadata["provenance"])):
            raise ValueError(f"Invalid chunk metadata/provenance at vector {position}")
        seen.add(chunk_id)
        counts[source] += 1
        sources.append(source)
    if sources != sorted(sources) or len(counts) != chunk_manifest.get("number_of_cases"):
        raise ValueError("Frozen chunk source ordering/case count mismatch")
    vectors = index.reconstruct_n(0, index.ntotal)
    if not np.isfinite(vectors).all():
        raise ValueError("Runtime document vectors must be finite")
    if not np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5, rtol=0):
        raise ValueError("Runtime document vectors must be unit-length L2-normalized")
    return store
