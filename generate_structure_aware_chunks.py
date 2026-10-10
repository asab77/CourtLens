"""Phase 4B.1: deterministic local chunking of the validated structural preview.

Only tiktoken and the standard library are used. No benchmark, embedding,
retrieval, or vector-store code is imported. See generated report for rules.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
from collections import Counter
from pathlib import Path

from local_tokenizer import load_local_encoding

PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR / 'data/analysis/structure_aware_preview.json'
OUTPUT = PROJECT_DIR / 'data/experiments/chunking/structure_aware_v1'
ANALYSIS = PROJECT_DIR / 'data/analysis/structure_aware_chunking'
STRATEGY = 'structure_aware_v1'
LOGIC_VERSION = 'phase4b1-v1'
TOKENIZER = 'cl100k_base'
TARGET_TOKENS = 900
HARD_MAX_TOKENS = 1100
SOFT_MIN_TOKENS = 300
OVERLAP_SENTENCES = 1
ENCODING = load_local_encoding()


def tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def canonical(text: str) -> str:
    return ' '.join(text.split())


def oversized_ranges(text: str) -> list[tuple[int, int]]:
    """Partition by character offsets; never decode partial UTF-8 token bytes.

    Prefer semicolon, colon, comma, then whitespace cuts in a 700–900 token
    window. Otherwise use a verified character boundary near 900 tokens. Every
    prefix is measured directly; final pieces are checked against the hard max.
    Ranges retain every original character, including separator whitespace.
    """
    ranges = []
    start = 0
    while tokens(text[start:].strip()) > HARD_MAX_TOKENS:
        tail = text[start:]
        low, high = 1, len(tail)
        while low < high:
            middle = (low + high + 1) // 2
            if tokens(tail[:middle].strip()) <= TARGET_TOKENS:
                low = middle
            else:
                high = middle - 1
        end = low
        # BPE counts need not be monotone: verify the selected boundary explicitly.
        while end > 1 and tokens(tail[:end].strip()) > TARGET_TOKENS:
            end -= 1
        for pattern in (r';\s*', r':\s*', r',\s*', r'\s+'):
            candidates = [m.end() for m in re.finditer(pattern, tail[:end])]
            chosen = next((c for c in reversed(candidates)
                           if 700 <= tokens(tail[:c].strip()) <= TARGET_TOKENS), None)
            if chosen is not None:
                end = chosen
                break
        if not tail[:end].strip():
            raise ValueError('Oversized fallback could not make nonempty progress')
        ranges.append((start, start + end))
        start += end
    if start < len(text):
        ranges.append((start, len(text)))
    if any(tokens(text[a:b].strip()) > HARD_MAX_TOKENS for a, b in ranges):
        raise ValueError('Fallback exceeds hard maximum')
    if ''.join(text[a:b] for a, b in ranges) != text:
        raise ValueError('Fallback changed source text')
    return ranges


def unit_pieces(document: dict, unit: dict) -> list[dict]:
    """Align sentences and known sections in the canonical unit text.

    A section marker inside an approximate sentence creates source fragments,
    not a new sentence or an invented section. Fragment page ranges retain the
    entire original sentence range conservatively.
    """
    normalized = canonical(unit['text'])
    sentences = unit['sentences']
    if canonical(' '.join(s['text'] for s in sentences)) != normalized:
        raise ValueError('Preview sentences do not cover canonical major-unit text')
    lines = unit['text'].split('\n')
    sections = []
    for section in unit['sections']:
        line = section['relative_line_index']
        if not 0 <= line < len(lines):
            raise ValueError('Section line offset outside unit')
        prefix = canonical('\n'.join(lines[:line]))
        offset = len(prefix) + bool(prefix)
        sections.append((offset, {
            'section_id': f"{document['source_file']}:u{unit['unit_index']}:s{section['section_index']}",
            'section_index': section['section_index'], 'marker': section['marker'],
            'title': section['title'],
        }))
    if sections != sorted(sections, key=lambda item: item[0]):
        raise ValueError('Section offsets out of order')
    unit_id = f"{document['source_file']}:u{unit['unit_index']}"
    pieces = []
    cursor = 0
    for sentence in sentences:
        value = sentence['text']
        if normalized[cursor:cursor + len(value)] != value:
            raise ValueError('Sentence/source alignment failed')
        end = cursor + len(value)
        cuts = [cursor] + [p for p, _ in sections if cursor < p < end] + [end]
        for left, right in zip(cuts, cuts[1:]):
            raw = value[left - cursor:right - cursor]
            if not raw.strip():
                raise ValueError('Empty section fragment')
            active = [metadata for offset, metadata in sections if offset <= left]
            section = active[-1] if active else None
            ranges = oversized_ranges(raw) if tokens(raw.strip()) > HARD_MAX_TOKENS else [(0, len(raw))]
            fallback = len(ranges) > 1
            for a, b in ranges:
                start_offset, end_offset = left - cursor + a, left - cursor + b
                pieces.append({
                    'piece_id': f"{unit_id}:n{sentence['sentence_index']}:{start_offset}-{end_offset}",
                    'major_unit_id': unit_id, 'opinion_type': unit['opinion_type'],
                    'sentence_id': f"{unit_id}:n{sentence['sentence_index']}",
                    'sentence_index': sentence['sentence_index'],
                    'char_start': start_offset, 'char_end': end_offset,
                    'page_start': sentence['page_start'], 'page_end': sentence['page_end'],
                    'section': section, 'oversized_sentence_fallback': fallback,
                    'section_boundary_fragment': len(cuts) > 2,
                    'complete_sentence': start_offset == 0 and end_offset == len(value),
                    'text': value[start_offset:end_offset],
                })
        cursor = end + 1
    return pieces


def joined(pieces: list[dict]) -> str:
    # Contiguous fragments of one sentence concatenate directly. Adding a
    # separator there would alter source text when a fallback has no whitespace.
    values = []
    previous = None
    for piece in pieces:
        if previous is not None and not (
            previous['sentence_id'] == piece['sentence_id']
            and previous['char_end'] == piece['char_start']
        ):
            values.append(' ')
        values.append(piece['text'])
        previous = piece
    return canonical(''.join(values))


def pack_unit(document: dict, unit: dict, pieces: list[dict], first_index: int) -> list[dict]:
    records, current = [], []
    overlap_ids = []

    def emit():
        nonlocal current, overlap_ids
        if not current:
            return
        sections = []
        for piece in current:
            if piece['section'] is not None and piece['section'] not in sections:
                sections.append(piece['section'])
        index = first_index + len(records)
        text = joined(current)
        metadata = {
            'chunk_id': f"{Path(document['source_file']).stem}:{STRATEGY}:{index:05d}",
            'chunk_index': index, 'case_name': document['case_name'],
            'source_file': document['source_file'],
            'original_source_file': document.get('original_source_file'),
            'chunking_strategy': STRATEGY,
            'page_start': min(p['page_start'] for p in current),
            'page_end': max(p['page_end'] for p in current), 'token_count': tokens(text),
            'major_unit_id': current[0]['major_unit_id'],
            'major_unit_index': unit['unit_index'], 'major_unit_type': unit['unit_type'],
            'opinion_type': unit['opinion_type'], 'author': unit.get('author'),
            'sections': sections,
            'sentence_ids': list(dict.fromkeys(p['sentence_id'] for p in current)),
            'sentence_range': [min(p['sentence_index'] for p in current), max(p['sentence_index'] for p in current)],
            'overlap_sentence_count': len(overlap_ids),
            'overlap_piece_ids': overlap_ids[:],
            'overlap_token_count': tokens(joined([p for p in current if p['piece_id'] in overlap_ids])) if overlap_ids else 0,
            'oversized_sentence_fallback': any(p['oversized_sentence_fallback'] for p in current),
            'provenance': [{k: v for k, v in p.items() if k != 'text'} for p in current],
        }
        records.append({'text': text, 'metadata': metadata})
        current, overlap_ids = [], []

    for piece in pieces:
        if current:
            section_change = current[-1]['section'] != piece['section']
            # Explicit sections end coherent chunks >= soft min; small sections
            # continue only inside this unit. No overlap at a section transition.
            if section_change and tokens(joined(current)) >= SOFT_MIN_TOKENS:
                emit()
            elif tokens(joined(current + [piece])) > HARD_MAX_TOKENS or (
                tokens(joined(current + [piece])) > TARGET_TOKENS
                and tokens(joined(current)) >= SOFT_MIN_TOKENS
            ):
                trailing = current[-1]
                emit()
                if (not section_change and trailing['complete_sentence']
                        and not trailing['oversized_sentence_fallback']
                        and tokens(joined([trailing, piece])) <= HARD_MAX_TOKENS):
                    current = [trailing]
                    overlap_ids = [trailing['piece_id']]
        current.append(piece)
        if tokens(joined(current)) > HARD_MAX_TOKENS:
            raise ValueError('Packing exceeded hard maximum')
    emit()
    return records


def validate(preview: dict, records: list[dict], source_pieces: dict[str, dict]) -> dict:
    """Fail before writing on identity, text, ordering, coverage, or size errors."""
    unit_map = {f"{d['source_file']}:u{u['unit_index']}": (d, u)
                for d in preview['documents'] for u in d['major_units']}
    primary_ids = []
    covered = set()
    mixed_units = mixed_opinions = 0
    indexes = Counter()
    previous = None
    for record in records:
        m = record['metadata']
        refs = m['provenance']
        if not refs or m['major_unit_id'] not in unit_map:
            raise ValueError('Missing major-unit provenance')
        d, u = unit_map[m['major_unit_id']]
        if u['opinion_type'] == 'foreign':
            raise ValueError('Foreign material became a retrieval chunk')
        pieces = []
        for ref in refs:
            source = source_pieces.get(ref['piece_id'])
            if source is None or ref != {k: v for k, v in source.items() if k != 'text'}:
                raise ValueError('Changed or missing source-piece provenance')
            pieces.append(source)
            covered.add(source['sentence_id'])
        mixed_units += len(set(p['major_unit_id'] for p in pieces)) != 1
        mixed_opinions += len(set(p['opinion_type'] for p in pieces)) != 1
        if any(p['major_unit_id'] != m['major_unit_id'] for p in pieces):
            raise ValueError('Crossed major-unit boundary')
        if (m['case_name'] != d['case_name'] or m['source_file'] != d['source_file']
                or m['opinion_type'] != u['opinion_type'] or m['author'] != u.get('author')):
            raise ValueError('Lost source identity')
        if m['chunk_index'] != indexes[d['source_file']]:
            raise ValueError('Nonconsecutive chunk indexes')
        indexes[d['source_file']] += 1
        if record['text'] != joined(pieces) or m['token_count'] != tokens(record['text']):
            raise ValueError('Chunk text/token count differs from source')
        if m['token_count'] > HARD_MAX_TOKENS:
            raise ValueError('Hard maximum exceeded')
        if (m['page_start'], m['page_end']) != (min(p['page_start'] for p in pieces), max(p['page_end'] for p in pieces)):
            raise ValueError('Invalid page provenance')
        for p in pieces:
            if not u['page_start'] <= p['page_start'] <= p['page_end'] <= u['page_end']:
                raise ValueError('Piece page provenance outside major unit')
        overlap = m['overlap_piece_ids']
        if overlap:
            if (len(overlap) != 1 or pieces[0]['piece_id'] != overlap[0] or previous is None
                    or previous['metadata']['major_unit_id'] != m['major_unit_id']):
                raise ValueError('Invalid overlap')
            prev_refs = previous['metadata']['provenance']
            if (prev_refs[-1]['piece_id'] != overlap[0] or not pieces[0]['complete_sentence']
                    or len(pieces) < 2 or pieces[0]['section'] != pieces[1]['section']):
                raise ValueError('Overlap crossed section or used a fragment')
        primary_ids.extend(p['piece_id'] for p in pieces if p['piece_id'] not in overlap)
        previous = record
    if mixed_units or mixed_opinions:
        raise ValueError('Mixed structural units/opinions')
    if primary_ids != list(source_pieces):
        raise ValueError('Missing, duplicated, or reordered primary source pieces')
    expected_sentences = {}
    for d in preview['documents']:
        for u in d['major_units']:
            if u['opinion_type'] == 'foreign':
                continue
            uid = f"{d['source_file']}:u{u['unit_index']}"
            for s in u['sentences']:
                sid = f"{uid}:n{s['sentence_index']}"
                fragments = [p for p in source_pieces.values() if p['sentence_id'] == sid]
                cursor = 0
                for p in fragments:
                    if p['char_start'] != cursor:
                        raise ValueError('Gap/overlap in source sentence fragments')
                    cursor = p['char_end']
                if cursor != len(s['text']) or ''.join(p['text'] for p in fragments) != s['text']:
                    raise ValueError('Source sentence not preserved exactly')
                expected_sentences[sid] = s
    missing = set(expected_sentences) - covered
    if missing:
        raise ValueError('Missing eligible source sentences')
    return {'MIXED_MAJOR_UNIT_CHUNKS': mixed_units, 'MIXED_OPINION_CHUNKS': mixed_opinions,
            'eligible_source_sentences': len(expected_sentences), 'covered_source_sentences': len(covered),
            'missing_source_sentences': len(missing), 'coverage_percentage': 100.0,
            'eligible_source_fragments': len(source_pieces),
            'covered_source_fragments': len(primary_ids), 'source_order_recoverable': True,
            'fallback_text_preserved': True, 'foreign_material_in_chunks': 0}


def distribution(values: list[int]) -> dict:
    ordered = sorted(values)
    def percentile(p):
        position = (len(ordered) - 1) * p
        lo = int(position)
        return round(ordered[lo] + (ordered[min(lo + 1, len(ordered) - 1)] - ordered[lo]) * (position - lo), 2)
    if not values:
        raise ValueError('Empty chunk distribution')
    return {'total_chunks': len(values), 'total_chunk_tokens': sum(values),
            'mean': round(statistics.mean(values), 2), 'median': statistics.median(values),
            'min': min(values), 'max': max(values),
            **{f'p{p}': percentile(p / 100) for p in (10, 25, 75, 90)},
            'buckets': {'<300': sum(v < 300 for v in values),
                        '300–599': sum(300 <= v <= 599 for v in values),
                        '600–900': sum(600 <= v <= 900 for v in values),
                        '901–1100': sum(900 < v <= 1100 for v in values),
                        '>1100': sum(v > 1100 for v in values)},
            'below_300_count': sum(v < 300 for v in values),
            'below_300_percentage': round(100 * sum(v < 300 for v in values) / len(values), 2),
            'above_900_count': sum(v > 900 for v in values),
            'above_900_percentage': round(100 * sum(v > 900 for v in values) / len(values), 2)}


def generate(preview: dict) -> tuple[list[dict], dict, dict]:
    records, pieces, excluded = [], {}, []
    documents = sorted(preview['documents'], key=lambda d: d['source_file'])
    if len({d['source_file'] for d in documents}) != len(documents):
        raise ValueError('Duplicate source documents')
    for document in documents:
        index = 0
        for unit in document['major_units']:
            if unit['opinion_type'] == 'foreign':
                excluded.append({'case_name': document['case_name'], 'unit_index': unit['unit_index'],
                                 'token_count': unit['token_count']})
                continue
            parts = unit_pieces(document, unit)
            for part in parts:
                if part['piece_id'] in pieces:
                    raise ValueError('Duplicate piece identity')
                pieces[part['piece_id']] = part
            packed = pack_unit(document, unit, parts, index)
            records.extend(packed)
            index += len(packed)
    validation = validate(preview, records, pieces)
    fallback = [p for p in pieces.values() if p['oversized_sentence_fallback']]
    overlap = [r['metadata']['overlap_token_count'] for r in records if r['metadata']['overlap_sentence_count']]
    summary = {
        **distribution([r['metadata']['token_count'] for r in records]),
        'total_unique_cases': len(documents),
        'chunks_by_case': dict(sorted(Counter(r['metadata']['case_name'] for r in records).items())),
        'chunks_by_major_unit_type': dict(sorted(Counter(r['metadata']['major_unit_type'] for r in records).items())),
        'chunks_by_opinion_type': dict(sorted(Counter(r['metadata']['opinion_type'] for r in records).items())),
        'chunks_with_author': sum(r['metadata']['author'] is not None for r in records),
        'chunks_without_author': sum(r['metadata']['author'] is None for r in records),
        'chunks_spanning_multiple_sections': sum(len(r['metadata']['sections']) > 1 for r in records),
        'chunks_using_overlap': len(overlap),
        'average_overlap_tokens': round(statistics.mean(overlap), 2) if overlap else 0,
        'maximum_overlap_tokens': max(overlap, default=0),
        'total_overlap_tokens': sum(overlap),
        'chunks_using_oversized_sentence_fallback': sum(r['metadata']['oversized_sentence_fallback'] for r in records),
        'oversized_sentence_fallback_count': len({p['sentence_id'] for p in fallback}),
        'fallback_pieces_generated': len(fallback),
        'fallback_examples': fallback[:3],
        'section_boundary_sentence_fragments': sum(p['section_boundary_fragment'] for p in pieces.values()),
        'excluded_foreign_units': len(excluded), 'excluded_foreign_tokens': sum(u['token_count'] for u in excluded),
        'excluded_foreign_details': excluded,
        'validation': validation,
    }
    return records, summary, pieces


def compare_fixed() -> dict:
    """Read fixed chunk records only; no benchmark, results, or index loading."""
    records = []
    for path in sorted((PROJECT_DIR / 'data/experiments/chunking/900_150/chunks').glob('*.jsonl')):
        records.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
    if not records:
        raise ValueError('Fixed 900/150 chunks unavailable')
    result = distribution([r['metadata']['token_count'] for r in records])
    result['overlap_behavior'] = 'Configured 150-token recursive splitter overlap; actual shared sentence/token overlap was not stored and is not inferred.'
    return result


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def render_report(preview: dict, records: list[dict], summary: dict, fixed: dict) -> str:
    lines = ['# CourtLens Phase 4B.1 — structure-aware chunk inspection', '',
             'Local descriptive validation only. Retrieval quality has not been evaluated.', '',
             '## Algorithm and schema', '',
             'Documents are sorted by source filename; units, sections and sentences retain source order. Foreign units are excluded. Every other unit is packed separately. Target 900; hard maximum 1100; soft minimum 300; tokenizer cl100k_base.', '',
             'A section ending flushes a chunk at 300 or more tokens. Smaller sections may continue inside the same unit. Adding a sentence beyond 900 flushes a coherent chunk at or above 300; otherwise packing may approach the strict 1100 maximum. A complete trailing sentence is repeated only on an internal context break and only when it fits with the next source piece. Explicit sections and opinions never receive cross-boundary overlap.', '',
             'Existing approximate sentences can contain a section marker internally. We align the validated marker by relative line offset in unit text and divide that sentence into exact character-range fragments at the marker. This does not change the parser or invent labels. Such fragments are ineligible for sentence overlap. Pages for every fragment conservatively retain the entire original sentence page range.', '',
             'Oversized fragments prefer semicolons, colons, commas, then whitespace in a 700–900 token window; otherwise a measured character boundary gives a token-aware split near 900 without breaking Unicode characters. Original source character ranges concatenate exactly; no fallback fragment overlap is introduced.', '',
             'The tokenizer is loaded only from a locally installed vocabulary whose reconstructed standard data matches the official SHA-256. Missing vocabulary fails without downloading.\n\nRecords follow the existing {text, metadata} schema. Metadata includes stable document-local IDs/indexes, one major-unit ID/type, opinion, raw parser author, known section IDs/markers/titles, original sentence IDs/range, overlap IDs/token count, and character-range provenance for each source piece. Whitespace joining follows Phase 4A canonical normalization.', '',
             'Coverage validation checks exact sentence reconstruction from character ranges, all primary fragments in source order, every emitted text against its source pieces, pages, unit identity, and overlap eligibility before writing any output.', '',
             '## Local quality measurements', '', '```json', json.dumps(summary, indent=2, ensure_ascii=False), '```', '',
             '## Fixed 900/150 descriptive comparison', '',
             '| Measurement | Fixed 900/150 | Structure-aware v1 |', '|---|---:|---:|']
    for key in ('total_chunks', 'mean', 'median', 'min', 'max', 'below_300_count', 'below_300_percentage', 'above_900_count', 'above_900_percentage'):
        lines.append(f'| {key} | {fixed[key]} | {summary[key]} |')
    lines += ['', fixed['overlap_behavior'], '',
              f"Structure-aware overlap: {summary['chunks_using_overlap']} chunks; mean {summary['average_overlap_tokens']} tokens; maximum {summary['maximum_overlap_tokens']} tokens. Distribution does not establish retrieval superiority.", '',
              '## Boundary inspection', '']
    # First/last chunks of every unit in the requested cases expose all boundaries.
    for needle in ('Dred Scott', 'New York Times', 'Obergefell', 'Marbury', 'Tinker'):
        document = next(d for d in preview['documents'] if needle in d['case_name'])
        lines += [f"### {document['case_name']}", '']
        for unit in document['major_units']:
            matching = [r for r in records if r['metadata']['source_file'] == document['source_file']
                        and r['metadata']['major_unit_index'] == unit['unit_index']]
            label = f"Unit {unit['unit_index']}: {unit['opinion_type']} / {unit.get('author') or 'unassigned'}"
            if not matching:
                lines += [f'**{label} — excluded foreign material; no retrieval chunk.**', '']
                continue
            lines += [f'**{label} — {len(matching)} chunk(s).**', '']
            for record in [matching[0]] + ([matching[-1]] if len(matching) > 1 else []):
                m = record['metadata']
                lines += [f"- `{m['chunk_id']}`; pp. {m['page_start']}–{m['page_end']}; {m['token_count']} tokens; overlap {m['overlap_sentence_count']}; sections {[s['marker'] for s in m['sections']]}",
                          f"  - Beginning: {record['text'][:180]}", f"  - Ending: {record['text'][-180:]}", '']
    lines += ['## Edge cases and readiness', '',
              'Short legitimate units and final residual chunks remain below 300; the minimum never overrides opinion structure. Front matter and syllabus remain eligible. Raw OCR names and running headers remain as in Phase 4A. Section-marker sentence fragments retain conservative pages and may be smaller than normal sentences. No actual sentence in this corpus exceeds 1100; fallback is exercised by synthetic tests.', '',
              'The actual fixed baseline averages 602.51 tokens versus 805.48 for this packing policy. Matching the configured target does not match realized granularity; later evaluation should acknowledge this size-distribution difference when interpreting structural effects. No parameter was adjusted using benchmark questions, labels or results.\n\nREADY for Phase 4B.2 once separately authorized. This phase creates no embeddings or vector store and makes no retrieval-quality claim.', '']
    return '\n'.join(lines)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    preview = json.loads(source_bytes)
    records, summary, _ = generate(preview)
    fixed = compare_fixed()
    manifest = {
        'strategy': STRATEGY, 'logic_version': LOGIC_VERSION,
        'logic_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'local_tokenizer_logic_sha256': hashlib.sha256((PROJECT_DIR / 'local_tokenizer.py').read_bytes()).hexdigest(),
        'tokenizer': TOKENIZER, 'target_tokens': TARGET_TOKENS,
        'hard_max_tokens': HARD_MAX_TOKENS, 'soft_min_tokens': SOFT_MIN_TOKENS,
        'overlap_sentences': OVERLAP_SENTENCES,
        'overlap_behavior': 'One complete trailing sentence within context, only if it fits; none at explicit section/opinion boundaries or between fallback fragments.',
        'source_structural_artifact': str(SOURCE.relative_to(PROJECT_DIR)),
        'source_structural_artifact_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'number_of_cases': summary['total_unique_cases'], 'number_of_chunks': len(records),
        'total_chunk_tokens_including_overlap': summary['total_chunk_tokens'],
        'excluded_foreign_units': summary['excluded_foreign_units'],
        'excluded_foreign_tokens': summary['excluded_foreign_tokens'],
        'oversized_sentence_fallback_count': summary['oversized_sentence_fallback_count'],
        'fallback_pieces_generated': summary['fallback_pieces_generated'],
        'validation': summary['validation'],
    }
    report = render_report(preview, records, summary, fixed)
    # Only these four new Phase 4B.1 artifact paths are writable.
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ANALYSIS.parent.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'chunks.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    write_json(OUTPUT / 'manifest.json', manifest)
    write_json(ANALYSIS.with_suffix('.json'), {'manifest': manifest, 'summary': summary, 'fixed_900_150': fixed})
    ANALYSIS.with_suffix('.md').write_text(report, encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
