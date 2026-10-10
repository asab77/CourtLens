"""Load the exact cl100k_base vocabulary locally; never download tokenizer data."""
import base64
import hashlib
import os
import tempfile
from pathlib import Path

import tiktoken

VOCABULARY_SHA256 = '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7'
CACHE_KEY = '9b5ad71b2ce5302211f9c61530b329a4922fc6a4'


def load_local_encoding() -> tiktoken.Encoding:
    """Use a verified existing tiktoken cache or installed VS Code vocabulary.

    Neither creates nor updates a cache. Missing/corrupt files fail locally.
    Regex and special tokens match tiktoken's cl100k_base constructor exactly.
    """
    cache = os.environ.get('TIKTOKEN_CACHE_DIR', os.environ.get('DATA_GYM_CACHE_DIR', str(Path(tempfile.gettempdir()) / 'data-gym-cache')))
    candidates = [Path(cache) / CACHE_KEY] if cache else []
    extensions = Path.home() / '.vscode/extensions'
    candidates += sorted(extensions.glob('*/dist/cl100k_base.tiktoken'))
    candidates += sorted(extensions.glob('*/dist/resources/cl100k_base.tiktoken.noindex'))
    for path in candidates:
        if not path.is_file():
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != VOCABULARY_SHA256:
            # Copilot Chat stores the same ranks as unsigned-varint length +
            # token bytes in rank order. Reconstruct the standard text format
            # and verify its official hash before accepting this local asset.
            if path.name != 'cl100k_base.tiktoken':
                continue
            try:
                entries, cursor = [], 0
                while cursor < len(data):
                    length, shift = 0, 0
                    while True:
                        byte = data[cursor]
                        cursor += 1
                        length |= (byte & 127) << shift
                        shift += 7
                        if shift > 35:
                            raise ValueError('Invalid local vocabulary length')
                        if not byte & 128:
                            break
                    token = data[cursor:cursor + length]
                    if len(token) != length or not token:
                        raise ValueError('Invalid local vocabulary token')
                    cursor += length
                    entries.append(base64.b64encode(token) + b' ' + str(len(entries)).encode() + b'\n')
                data = b''.join(entries)
            except (ValueError, IndexError):
                continue
            if hashlib.sha256(data).hexdigest() != VOCABULARY_SHA256:
                continue
        ranks = {base64.b64decode(token): int(rank) for token, rank in (line.split() for line in data.splitlines())}
        return tiktoken.Encoding(
            name='cl100k_base',
            pat_str=r"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s",
            mergeable_ranks=ranks,
            special_tokens={'<|endoftext|>': 100257, '<|fim_prefix|>': 100258,
                            '<|fim_middle|>': 100259, '<|fim_suffix|>': 100260,
                            '<|endofprompt|>': 100276},
        )
    raise RuntimeError('Verified local cl100k_base vocabulary unavailable; no download attempted. Provide it in TIKTOKEN_CACHE_DIR before running.')
