"""Local evidence validation, whole-passage budgeting and citation-ID integrity.

cl100k_base is an estimate for generation models, not their exact tokenizer.
No retrieval, provider requests, OCR repair or semantic verification occurs here.
"""
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import math
import re

from local_tokenizer import load_local_encoding

CANONICAL_ID = re.compile(r'S[1-9][0-9]*', re.ASCII)
CANONICAL_CITATION = re.compile(r'\[S([1-9][0-9]*)\]', re.ASCII)
# Intentionally conservative: any source-like bracket syntax is scrutinized.
SOURCE_LIKE = re.compile(r'\[\s*[sS][^\]\n]*(?:\]|(?=\n|$))')
BARE_SOURCE = re.compile(r'(?<![\w\[])S[0-9]+(?![\w])', re.ASCII)


@lru_cache(maxsize=1)
def default_tokenizer():
    return load_local_encoding()  # Verified local vocabulary; never downloads.


def token_count(text, tokenizer):
    return len(tokenizer.encode(text, disallowed_special=()))


def validate_records(records):
    """Copy records and reject duplicated/conflicting identities before selection."""
    clean, identities, chunk_ids = [], set(), set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('text'), str) or not record['text'].strip():
            raise ValueError('Evidence requires nonempty original text')
        m = record.get('metadata')
        if not isinstance(m, dict):
            raise ValueError('Evidence metadata is required')
        for field in ('case_name', 'source_file'):
            if not isinstance(m.get(field), str) or not m[field].strip():
                raise ValueError(f'Evidence requires {field}')
        if type(m.get('chunk_index')) is not int or m['chunk_index'] < 0:
            raise ValueError('Evidence requires an original chunk index')
        if (type(m.get('page_start')) is not int or type(m.get('page_end')) is not int
                or not 1 <= m['page_start'] <= m['page_end']):
            raise ValueError('Evidence requires an accurate PDF page range')
        chunk_id = m.get('chunk_id')
        if chunk_id is not None and (not isinstance(chunk_id, str) or not chunk_id.strip()):
            raise ValueError('Invalid stable chunk ID')
        for field in ('author', 'opinion_type'):
            if m.get(field) is not None and not isinstance(m[field], str):
                raise ValueError(f'Invalid {field} metadata')
        sections = m.get('sections')
        if sections is not None and (not isinstance(sections, list) or any(
                not isinstance(s, dict) or any(s.get(k) is not None and not isinstance(s[k], str)
                                             for k in ('marker', 'title')) for s in sections)):
            raise ValueError('Invalid section metadata')
        # Detect conflicting flattened hybrid metadata rather than choosing one.
        for field, value in m.items():
            if field in record and record[field] != value:
                raise ValueError(f'Conflicting evidence metadata: {field}')
        identity = (record.get('collection'), m['source_file'], m['chunk_index'])
        if identity in identities or (chunk_id is not None and chunk_id in chunk_ids):
            raise ValueError('Duplicate retrieved chunk identity')
        identities.add(identity)
        if chunk_id is not None:
            chunk_ids.add(chunk_id)
        clean.append(deepcopy(record))
    return clean


def format_source(item):
    """Preserve raw text/metadata; labels are metadata, not verified attribution."""
    m = item['metadata']
    source_id = item.get('source_id')
    if not isinstance(source_id, str) or not CANONICAL_ID.fullmatch(source_id):
        raise ValueError('Evidence source IDs must be canonical S1, S2, ...')
    opinion = m.get('opinion_type') or 'Unknown'
    author = m.get('author') or 'Unknown'
    sections = '; '.join(' '.join(str(s.get(k) or '') for k in ('marker', 'title')).strip()
                         for s in m.get('sections') or []) or 'Unknown'
    return (f"[{source_id}]\nCase: {m['case_name']}\n"
            f"Source: {m.get('original_source_file') or m['source_file']}\n"
            f"PDF pages: {m['page_start']}-{m['page_end']}\n"
            f"Chunk ID: {m.get('chunk_id') or 'Not supplied'}\n"
            f"Original chunk index: {m['chunk_index']}\n"
            f"Opinion (source metadata): {opinion}\nAuthor (raw source metadata): {author}\n"
            f"Sections (source metadata): {sections}\nText: {item['text']}")


def format_sources(evidence):
    records = validate_records(evidence)
    if [r.get('source_id') for r in records] != [f'S{i}' for i in range(1, len(records) + 1)]:
        raise ValueError('Evidence source IDs must be unique and contiguous in selected order')
    return '\n\n'.join(format_source(r) for r in records)


@dataclass(frozen=True)
class EvidenceContext:
    evidence: list[dict]
    text: str
    sources: dict[str, dict]
    usage: dict
    skipped: list[dict]
    status: str


def build_evidence_context(records, token_budget=12000, *, safety_margin=.1, tokenizer=None):
    """Skip nonfitting whole chunks and continue in rank order; never truncate.

    IDs are scoped to this selected context, not inherited from caller/history.
    Count the complete joined serialization on each trial (including separators).
    """
    if type(token_budget) is not int or token_budget < 0:
        raise ValueError('Context token budget must be a nonnegative integer')
    if isinstance(safety_margin, bool) or not isinstance(safety_margin, (int, float)) or not math.isfinite(safety_margin) or not 0 <= safety_margin < 1:
        raise ValueError('Safety margin must be finite and between 0 and 1')
    records = validate_records(records)
    tokenizer = tokenizer if tokenizer is not None else default_tokenizer()
    effective = math.floor(token_budget * (1 - safety_margin))
    selected, blocks, skipped, sources = [], [], [], {}
    for ordinal, record in enumerate(records):
        record['source_id'] = f'S{len(selected) + 1}'
        record['truncated'] = False
        count = token_count(record['text'], tokenizer)
        record['original_text_tokens'] = record['included_text_tokens'] = count
        block = format_source(record)
        trial = '\n\n'.join(blocks + [block])
        if token_count(trial, tokenizer) > effective:
            skipped.append({'retrieved_position': ordinal + 1, 'chunk_id': record['metadata'].get('chunk_id'),
                            'source_file': record['metadata']['source_file'], 'chunk_index': record['metadata']['chunk_index'],
                            'reason': 'whole_chunk_exceeds_remaining_budget', 'original_text_tokens': count,
                            'included_text_tokens': 0})
            continue
        selected.append(record)
        blocks.append(block)
        sources[record['source_id']] = {'retrieved_position': ordinal + 1,
                                      'chunk_id': record['metadata'].get('chunk_id'),
                                      'collection': record.get('collection'),
                                      'metadata': deepcopy(record['metadata'])}
    text = '\n\n'.join(blocks)
    usage = {'configured_budget': token_budget, 'safety_margin': safety_margin,
             'effective_budget': effective, 'evidence_tokens': token_count(text, tokenizer),
             'tokenizer': getattr(tokenizer, 'name', type(tokenizer).__name__),
             'generation_tokenizer_is_approximate': True, 'selected_count': len(selected),
             'skipped_count': len(skipped), 'policy': 'skip_whole_chunk_continue_in_rank_order'}
    return EvidenceContext(selected, text, sources, usage, skipped,
                           'ready' if selected else 'insufficient_context')


def citation_errors(answer, source_ids):
    """Validate syntax/reference membership only, never claim support."""
    allowed = set(source_ids)
    if any(not isinstance(s, str) or not CANONICAL_ID.fullmatch(s) for s in allowed):
        raise ValueError('Allowed source IDs must be canonical')
    errors = []
    for match in SOURCE_LIKE.finditer(answer):
        citation = match.group()
        if (not CANONICAL_CITATION.fullmatch(citation)
                or (match.start() > 0 and answer[match.start()-1] == '[')
                or (match.end() < len(answer) and answer[match.end()] == ']')):
            errors.append('malformed or noncanonical source reference')
        elif citation[1:-1] not in allowed:
            errors.append('source reference not included in current context')
    # Flag missing opening brackets and bare S-number references too.
    if BARE_SOURCE.search(SOURCE_LIKE.sub('', answer)):
        errors.append('unbracketed source reference')
    return list(dict.fromkeys(errors))


def sanitize_history_citations(text):
    """Remove old source-like IDs from prompt history, not stored conversation."""
    return BARE_SOURCE.sub('(historical source reference removed)',
                           SOURCE_LIKE.sub('(historical source reference removed)', text))
