"""Local tests for the experiment-specific Vercel embedding migration."""

import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

import chunk_text
import retrieve
import run_chunking_experiment as experiment
from build_index import save_vector_store
from gateway_config import (
    EMBEDDING_MODEL,
    EXPERIMENT_EMBEDDING_MODEL,
    EXPERIMENT_GATEWAY_BASE_URL,
    EXPERIMENT_GATEWAY_PROVIDER,
    GATEWAY_BASE_URL,
    LEGACY_NYU_BASE_URL,
    LEGACY_NYU_EMBEDDING_MODEL,
    LEGACY_NYU_PROVIDER,
    get_experiment_api_key,
    require_experiment_api_key,
)
from retrieve import load_vector_store


def record(source: str, chunk_index: int = 0, token_count: int = 4) -> dict:
    return {
        "text": f"text for {source} chunk {chunk_index}",
        "metadata": {
            "case_name": source.removesuffix(".pdf"),
            "source_file": source,
            "page_start": 1,
            "page_end": 1,
            "chunk_index": chunk_index,
            "token_count": token_count,
        },
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(item) + "\n" for item in records), encoding="utf-8"
    )


class ExperimentCredentialTests(unittest.TestCase):
    def test_environment_key_loads_without_being_exposed(self):
        secret = "test-secret-that-must-not-be-printed"
        fake_streamlit = SimpleNamespace(secrets={})
        stdout = StringIO()
        stderr = StringIO()

        with patch.dict(sys.modules, {"streamlit": fake_streamlit}):
            with patch.dict(os.environ, {"AI_GATEWAY_API_KEY": secret}, clear=True):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    value = get_experiment_api_key()

        self.assertEqual(value, secret)
        self.assertNotIn(secret, stdout.getvalue())
        self.assertNotIn(secret, stderr.getvalue())

    def test_missing_key_error_is_safe_and_actionable(self):
        fake_streamlit = SimpleNamespace(secrets={})
        with patch.dict(sys.modules, {"streamlit": fake_streamlit}):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "AI_GATEWAY_API_KEY") as raised:
                    require_experiment_api_key()

        self.assertNotIn("test-secret", str(raised.exception))

    def test_experiment_client_uses_vercel_without_portkey_header(self):
        with patch.object(retrieve, "require_experiment_api_key", return_value="secret"):
            with patch.object(retrieve, "OpenAI") as openai:
                retrieve.experiment_embedding_client()

        openai.assert_called_once_with(
            api_key="secret", base_url=EXPERIMENT_GATEWAY_BASE_URL
        )
        self.assertNotIn("default_headers", openai.call_args.kwargs)


class ExperimentalStoreTests(unittest.TestCase):
    def setUp(self):
        self.records = [record("case.pdf", 0), record("case.pdf", 1)]
        self.embeddings = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype="float32")

    def test_vercel_manifest_and_experiment_compatibility(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store_dir = Path(temp_dir)
            save_vector_store(
                self.records,
                self.embeddings.copy(),
                ["case.jsonl"],
                vector_store_dir=store_dir,
                gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
                gateway_provider=EXPERIMENT_GATEWAY_PROVIDER,
                embedding_model=EXPERIMENT_EMBEDDING_MODEL,
            )

            manifest = json.loads(
                (store_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["gateway_base_url"], EXPERIMENT_GATEWAY_BASE_URL)
            self.assertEqual(manifest["embedding_model"], EXPERIMENT_EMBEDDING_MODEL)
            self.assertEqual(manifest["provider"], EXPERIMENT_GATEWAY_PROVIDER)

            index, records, _ = load_vector_store(
                store_dir,
                expected_embedding_model=EXPERIMENT_EMBEDDING_MODEL,
                expected_gateway_base_url=EXPERIMENT_GATEWAY_BASE_URL,
            )
            self.assertEqual(index.ntotal, len(records))
            # Supported defaults now match Vercel.
            load_vector_store(store_dir)

    def test_historical_store_requires_explicit_legacy_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store_dir = Path(temp_dir)
            save_vector_store(
                self.records,
                self.embeddings.copy(),
                ["case.jsonl"],
                vector_store_dir=store_dir,
                gateway_base_url=LEGACY_NYU_BASE_URL,
                gateway_provider=LEGACY_NYU_PROVIDER,
                embedding_model=LEGACY_NYU_EMBEDDING_MODEL,
            )

            with self.assertRaisesRegex(ValueError, "different embedding model"):
                load_vector_store(store_dir)
            index, records, manifest = load_vector_store(
                store_dir, expected_embedding_model=LEGACY_NYU_EMBEDDING_MODEL,
                expected_gateway_base_url=LEGACY_NYU_BASE_URL)

        self.assertEqual(index.ntotal, len(records))
        self.assertEqual(manifest["embedding_model"], LEGACY_NYU_EMBEDDING_MODEL)
        self.assertEqual(manifest["gateway_base_url"], LEGACY_NYU_BASE_URL)


class ExistingChunkValidationTests(unittest.TestCase):
    configuration = {"id": "10_2", "chunk_size": 10, "chunk_overlap": 2}

    def make_fixture(self, root: Path) -> tuple[Path, Path]:
        processed_dir = root / "processed"
        chunks_dir = root / "chunks"
        processed_dir.mkdir()
        chunks_dir.mkdir()
        for stem in ("alpha", "beta"):
            (processed_dir / f"{stem}.txt").write_text("source", encoding="utf-8")
            write_jsonl(chunks_dir / f"{stem}.jsonl", [record(f"{stem}.pdf")])
        return processed_dir, chunks_dir

    def test_complete_chunks_are_loaded_without_regeneration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir, chunks_dir = self.make_fixture(Path(temp_dir))
            with patch.object(chunk_text, "chunk_cases") as chunk_cases:
                records, files = experiment.load_existing_configuration_chunks(
                    self.configuration, chunks_dir, processed_dir
                )

        self.assertEqual(len(records), 2)
        self.assertEqual(files, ["alpha.jsonl", "beta.jsonl"])
        chunk_cases.assert_not_called()

    def test_partial_chunk_set_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir, chunks_dir = self.make_fixture(Path(temp_dir))
            (chunks_dir / "beta.jsonl").unlink()
            with self.assertRaisesRegex(ValueError, "incomplete or unexpected"):
                experiment.load_existing_configuration_chunks(
                    self.configuration, chunks_dir, processed_dir
                )

    def test_malformed_chunk_set_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir, chunks_dir = self.make_fixture(Path(temp_dir))
            (chunks_dir / "beta.jsonl").write_text("{bad json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed"):
                experiment.load_existing_configuration_chunks(
                    self.configuration, chunks_dir, processed_dir
                )

    def test_configuration_inconsistent_chunk_set_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir, chunks_dir = self.make_fixture(Path(temp_dir))
            write_jsonl(chunks_dir / "beta.jsonl", [record("beta.pdf", token_count=11)])
            with self.assertRaisesRegex(ValueError, "invalid token_count"):
                experiment.load_existing_configuration_chunks(
                    self.configuration, chunks_dir, processed_dir
                )

    def test_all_existing_experiment_chunks_validate_with_expected_counts(self):
        expected_counts = {
            "600_100": 1163,
            "900_150": 598,
            "1200_200": 447,
            "1500_200": 287,
        }
        for configuration in experiment.CONFIGURATIONS:
            with self.subTest(configuration=configuration["id"]):
                chunks_dir = (
                    experiment.EXPERIMENT_ROOT / configuration["id"] / "chunks"
                )
                records, files = experiment.load_existing_configuration_chunks(
                    configuration, chunks_dir
                )
                self.assertEqual(len(files), 8)
                self.assertEqual(len(records), expected_counts[configuration["id"]])


class BuildPathTests(unittest.TestCase):
    def test_missing_store_reuses_chunks_and_uses_vercel_metadata(self):
        fake_index = SimpleNamespace(ntotal=1)
        fake_store = (fake_index, [record("case.pdf")], {})
        configuration = {"id": "10_2", "chunk_size": 10, "chunk_overlap": 2}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(experiment, "EXPERIMENT_ROOT", Path(temp_dir)):
                with patch.object(
                    experiment,
                    "load_existing_configuration_chunks",
                    return_value=([record("case.pdf")], ["case.jsonl"]),
                ) as load_chunks:
                    with patch.object(experiment, "experiment_embedding_client"):
                        with patch.object(
                            experiment,
                            "create_embeddings",
                            return_value=np.asarray([[1.0, 0.0]], dtype="float32"),
                        ) as create_embeddings:
                            with patch.object(experiment, "save_vector_store") as save_store:
                                with patch.object(
                                    experiment, "load_vector_store", return_value=fake_store
                                ) as load_store:
                                    with patch.object(chunk_text, "chunk_cases") as chunk_cases:
                                        experiment.build_or_load_configuration(configuration)

        load_chunks.assert_called_once()
        chunk_cases.assert_not_called()
        self.assertEqual(
            create_embeddings.call_args.kwargs["model"], EXPERIMENT_EMBEDDING_MODEL
        )
        self.assertEqual(
            save_store.call_args.kwargs["gateway_base_url"],
            EXPERIMENT_GATEWAY_BASE_URL,
        )
        self.assertEqual(
            save_store.call_args.kwargs["embedding_model"],
            EXPERIMENT_EMBEDDING_MODEL,
        )
        self.assertEqual(
            load_store.call_args.kwargs["expected_gateway_base_url"],
            EXPERIMENT_GATEWAY_BASE_URL,
        )


if __name__ == "__main__":
    unittest.main()
