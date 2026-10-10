"""Run new, relevant, and full CourtLens tests with verified local vocabulary.

An older test group calls tiktoken.get_encoding directly, which downloads on a
cache miss. Seed only a temporary cache from the already-installed, hash-verified
vocabulary, and block DNS/connections and requests HTTP dispatch. Existing code,
tests, data artifacts, credentials, and caches are not modified.
"""

import base64
import hashlib
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

import requests

from local_tokenizer import CACHE_KEY, VOCABULARY_SHA256, load_local_encoding


def main():
    with patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS/network forbidden in local tests')), \
            patch.object(socket, 'create_connection', side_effect=AssertionError('Network forbidden in local tests')), \
            patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden in local tests')), \
            patch.object(requests.sessions.Session, 'request', side_effect=AssertionError('Real HTTP forbidden in local tests')):
        encoding = load_local_encoding()
        entries = sorted(encoding._mergeable_ranks.items(), key=lambda item: item[1])
        vocabulary = b''.join(base64.b64encode(token) + b' ' + str(rank).encode() + b'\n' for token, rank in entries)
        if hashlib.sha256(vocabulary).hexdigest() != VOCABULARY_SHA256:
            raise RuntimeError('Local vocabulary does not match the canonical tokenizer')
        with tempfile.TemporaryDirectory(prefix='courtlens-phase4c2-tests-') as directory:
            (Path(directory) / CACHE_KEY).write_bytes(vocabulary)
            with patch.dict(os.environ, {'TIKTOKEN_CACHE_DIR': directory}):
                sys.path.insert(0, str(Path(__file__).resolve().parent / 'tests'))
                groups = [
                    ('New Phase 4C.2 tests', lambda: unittest.defaultTestLoader.loadTestsFromName('test_benchmark_v2_finalization')),
                    ('Relevant existing tests', lambda: unittest.defaultTestLoader.loadTestsFromNames(['test_benchmark_review', 'test_reviewed_chunking_evaluation', 'test_chunking_evaluation', 'test_phase4c_benchmark_audit'])),
                    ('Full repository suite', lambda: unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent / 'tests'))),
                ]
                success = True
                for label, build in groups:
                    print(label, flush=True)
                    result = unittest.TextTestRunner(verbosity=1).run(build())
                    success = success and result.wasSuccessful()
                return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
