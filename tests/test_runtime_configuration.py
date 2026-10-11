"""Phase 7A.2A provider and asset tests: synthetic data, no API calls."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import faiss
import numpy as np

import gateway_config as config
import runtime_assets as assets


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.secrets = {}
        self.streamlit = patch.dict(sys.modules, {"streamlit": SimpleNamespace(secrets=self.secrets)})
        self.streamlit.start()
        self.addCleanup(self.streamlit.stop)

    def test_embedding_configuration_and_client(self):
        os.environ['AI_GATEWAY_API_KEY'] = 'fake-key'
        embedding = config.vercel_embedding_config()
        self.assertEqual(embedding.model, 'openai/text-embedding-3-small')
        self.assertEqual(embedding.provider, 'vercel-ai-gateway')
        self.assertEqual(embedding.base_url, 'https://ai-gateway.vercel.sh/v1')
        self.assertNotIn('fake-key', repr(embedding))
        with patch('openai.OpenAI') as client:
            config.vercel_client(embedding)
        client.assert_called_once_with(api_key='fake-key', base_url=embedding.base_url)

    def test_generation_model_is_independent(self):
        os.environ.update(AI_GATEWAY_API_KEY='fake-key', VERCEL_GENERATION_MODEL='test/chat-model')
        generation = config.vercel_generation_config()
        self.assertEqual(generation.model, 'test/chat-model')
        self.assertEqual(generation.base_url, config.VERCEL_BASE_URL)
        self.assertEqual(generation.provider, config.VERCEL_PROVIDER)
        self.assertEqual(config.vercel_embedding_config().model, config.VERCEL_EMBEDDING_MODEL)

    def test_secrets_precede_environment(self):
        os.environ.update(AI_GATEWAY_API_KEY='env-key', VERCEL_GENERATION_MODEL='env/model')
        self.secrets.update(AI_GATEWAY_API_KEY='secret-key', VERCEL_GENERATION_MODEL='secret/model')
        self.assertEqual(config.vercel_generation_config().model, 'secret/model')
        self.assertEqual(config.vercel_embedding_config().api_key, 'secret-key')

    def test_missing_credentials_never_fall_back_to_nyu(self):
        os.environ['NYU_AI_GATEWAY_API_KEY'] = 'legacy-key'
        for factory in (config.vercel_embedding_config, config.vercel_generation_config):
            with self.subTest(factory=factory.__name__), self.assertRaisesRegex(RuntimeError, 'AI_GATEWAY_API_KEY'):
                factory()

    def test_missing_generation_model_has_no_default(self):
        os.environ['AI_GATEWAY_API_KEY'] = 'fake-key'
        with self.assertRaisesRegex(RuntimeError, 'VERCEL_GENERATION_MODEL'):
            config.vercel_generation_config()
        self.assertEqual(config.vercel_embedding_config().model, config.VERCEL_EMBEDDING_MODEL)

    def test_default_and_configurable_runtime_path(self):
        self.assertEqual(config.runtime_vector_store_path(), config.DEFAULT_RUNTIME_VECTOR_STORE.resolve())
        os.environ['COURTLENS_VECTOR_STORE_PATH'] = 'alternate/vector_store'
        self.assertEqual(config.runtime_vector_store_path(), config.PROJECT_DIR / 'alternate/vector_store')
        self.secrets['COURTLENS_VECTOR_STORE_PATH'] = '/tmp/local-runtime/vector_store'
        self.assertEqual(config.runtime_vector_store_path(), Path('/tmp/local-runtime/vector_store').resolve())

    def test_supported_defaults_are_vercel(self):
        self.assertEqual(config.EMBEDDING_MODEL, 'openai/text-embedding-3-small')
        self.assertEqual(config.GATEWAY_PROVIDER, 'vercel-ai-gateway')
        self.assertEqual(config.API_KEY_NAME, 'AI_GATEWAY_API_KEY')
        self.assertFalse(hasattr(config, 'require_nyu_api_gateway_api_key'))


class RuntimeAssetTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.bundle = self.root / 'bundle'
        self.store = self.bundle / 'vector_store'
        self.store.mkdir(parents=True)
        for target, name, value in ((assets, 'PROJECT_DIR', self.root),
                                    (assets, 'EXPECTED_RECORDS', 2),
                                    (assets, 'EXPECTED_DIMENSION', 3)):
            patched = patch.object(target, name, value)
            patched.start()
            self.addCleanup(patched.stop)
        (self.root / 'preview.json').write_text('{"synthetic": true}')
        self.frozen = [self.record(i) for i in range(2)]
        self.stored = [dict(item, vector_id=i) for i, item in enumerate(self.frozen)]
        self.chunk_manifest = dict(strategy=assets.STRATEGY, logic_version=assets.LOGIC_VERSION,
                                   number_of_chunks=2, number_of_cases=1,
                                   source_structural_artifact='preview.json',
                                   source_structural_artifact_sha256=self.digest(self.root / 'preview.json'))
        self.manifest = dict(vector_count=2, record_count=2, dimension=3,
                             faiss_index_type='IndexFlatIP', normalization='L2_unit_length',
                             similarity='cosine', embedding_model=config.VERCEL_EMBEDDING_MODEL,
                             gateway_base_url=config.VERCEL_BASE_URL, provider=config.VERCEL_PROVIDER,
                             strategy=assets.STRATEGY, logic_version=assets.LOGIC_VERSION,
                             chunk_file_count=1, chunk_files=['chunks.jsonl'])
        self.write_inputs()
        self.write_index()

    def record(self, i):
        return {'text': f'Full synthetic evidence {i}.', 'metadata': {
            'chunk_id': f'case-{i}', 'chunk_index': i, 'source_file': 'case.pdf',
            'original_source_file': 'case.pdf', 'case_name': 'Case', 'page_start': 1,
            'page_end': 2, 'token_count': 10, 'chunking_strategy': assets.STRATEGY,
            'major_unit_id': 'opinion-1', 'opinion_type': 'majority',
            'provenance': [{'major_unit_id': 'opinion-1', 'sentence_id': str(i)}]}}

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_inputs(self):
        (self.bundle / 'chunks.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in self.frozen))
        (self.bundle / 'manifest.json').write_text(json.dumps(self.chunk_manifest))
        self.manifest['chunks_sha256'] = self.digest(self.bundle / 'chunks.jsonl')
        self.manifest['chunk_manifest_sha256'] = self.digest(self.bundle / 'manifest.json')
        (self.store / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in self.stored))
        (self.store / 'manifest.json').write_text(json.dumps(self.manifest))

    def write_index(self, vectors=None, dimension=3, index_type=faiss.IndexFlatIP):
        index = index_type(dimension)
        if vectors is None:
            vectors = np.eye(dimension, dtype='float32')[:2]
        index.add(np.asarray(vectors, dtype='float32'))
        faiss.write_index(index, str(self.store / 'index.faiss'))

    def test_validated_loading_is_read_only_and_uses_configured_path(self):
        before = {str(p): self.digest(p) for p in self.root.rglob('*') if p.is_file()}
        with patch.object(assets, 'runtime_vector_store_path', return_value=self.store) as setting:
            index, records, manifest = assets.load_runtime_vector_store()
        setting.assert_called_once_with()
        self.assertEqual((index.ntotal, index.d), (2, 3))
        self.assertEqual(records, self.stored)
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(before, {str(p): self.digest(p) for p in self.root.rglob('*') if p.is_file()})

    def test_missing_assets(self):
        for path in (self.store / 'index.faiss', self.store / 'records.jsonl',
                     self.store / 'manifest.json', self.bundle / 'chunks.jsonl',
                     self.bundle / 'manifest.json', self.root / 'preview.json'):
            with self.subTest(path=path):
                contents = path.read_bytes()
                path.unlink()
                with self.assertRaisesRegex(ValueError, 'missing'):
                    assets.load_runtime_vector_store(self.store)
                path.write_bytes(contents)

    def test_actual_dimension_mismatch(self):
        self.write_index(dimension=4)
        with self.assertRaisesRegex(ValueError, 'dimension'):
            assets.load_runtime_vector_store(self.store)

    def test_vector_record_count_mismatch(self):
        self.write_index(vectors=[[1, 0, 0]])
        with self.assertRaisesRegex(ValueError, 'counts'):
            assets.load_runtime_vector_store(self.store)

    def test_non_normalized_zero_and_nonfinite_vectors(self):
        for first in ([2, 0, 0], [0, 0, 0], [float('nan'), 0, 0], [float('inf'), 0, 0]):
            with self.subTest(vector=first):
                self.write_index(vectors=[first, [0, 1, 0]])
                with self.assertRaisesRegex(ValueError, 'finite|unit-length'):
                    assets.load_runtime_vector_store(self.store)

    def test_manifest_compatibility(self):
        for field, wrong in (('embedding_model', 'wrong/model'), ('dimension', 4),
                             ('provider', 'azure-openai'), ('gateway_base_url', config.LEGACY_NYU_BASE_URL),
                             ('record_count', 1), ('normalization', 'none'), ('strategy', 'other')):
            with self.subTest(field=field):
                original = self.manifest[field]
                self.manifest[field] = wrong
                self.write_inputs()
                with self.assertRaisesRegex(ValueError, field):
                    assets.load_runtime_vector_store(self.store)
                self.manifest[field] = original

    def test_wrong_actual_index_type(self):
        self.write_index(index_type=faiss.IndexFlatL2)
        with self.assertRaisesRegex(ValueError, 'IndexFlatIP'):
            assets.load_runtime_vector_store(self.store)

    def test_vector_record_alignment(self):
        self.stored[1]['vector_id'] = 0
        self.write_inputs()
        with self.assertRaisesRegex(ValueError, 'aligned'):
            assets.load_runtime_vector_store(self.store)

    def test_text_metadata_and_order_provenance(self):
        for field in ('text', 'metadata', 'order'):
            with self.subTest(field=field):
                original = json.loads(json.dumps(self.stored))
                if field == 'text':
                    self.stored[0]['text'] = 'Changed text'
                elif field == 'metadata':
                    self.stored[0]['metadata'] = dict(self.stored[0]['metadata'], page_end=3)
                else:
                    self.stored.reverse()
                    for i, r in enumerate(self.stored):
                        r['vector_id'] = i
                self.write_inputs()
                with self.assertRaisesRegex(ValueError, 'provenance'):
                    assets.load_runtime_vector_store(self.store)
                self.stored = original

    def test_duplicate_chunk_identity(self):
        self.frozen[1]['metadata']['chunk_id'] = self.frozen[0]['metadata']['chunk_id']
        self.write_inputs()
        with self.assertRaisesRegex(ValueError, 'identity'):
            assets.load_runtime_vector_store(self.store)

    def test_hash_mismatches(self):
        for path in (self.bundle / 'chunks.jsonl', self.bundle / 'manifest.json', self.root / 'preview.json'):
            with self.subTest(path=path):
                contents = path.read_bytes()
                path.write_bytes(contents + b'\n')
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    assets.load_runtime_vector_store(self.store)
                path.write_bytes(contents)

    def test_malformed_records_and_corrupt_index(self):
        (self.store / 'records.jsonl').write_text('{broken')
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            assets.load_runtime_vector_store(self.store)
        self.write_inputs()
        (self.store / 'index.faiss').write_bytes(b'not a FAISS index')
        with self.assertRaisesRegex(ValueError, 'Cannot read'):
            assets.load_runtime_vector_store(self.store)


if __name__ == '__main__':
    unittest.main()
