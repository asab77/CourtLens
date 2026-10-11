"""Text-free, rank-only RRF over verified identities in one frozen corpus."""
from copy import deepcopy
import math

K = 60
DEPTH = 5


class ChunkCatalog:
    """Identity is corpus + source + original chunk index, never page overlap."""
    def __init__(self, collection, records):
        self.collection = collection
        self.records = records
        self.lookup = {}
        for ordinal, record in enumerate(records):
            m = record['metadata']
            key = (m['source_file'], m['chunk_index'])
            if key in self.lookup:
                raise ValueError('Duplicate frozen chunk identity')
            self.lookup[key] = ordinal

    def verify(self, row):
        if row.get('collection', self.collection) != self.collection:
            raise ValueError('Cross-corpus candidate')
        key = (row.get('source_file'), row.get('chunk_index'))
        if key not in self.lookup:
            raise ValueError('Unmapped candidate identity')
        ordinal = self.lookup[key]
        record = self.records[ordinal]
        for field, value in record['metadata'].items():
            if field in row and row[field] != value:
                raise ValueError(f'Candidate metadata mismatch: {field}')
        for field in ('case_name', 'source_file', 'chunk_index', 'page_start', 'page_end'):
            if row.get(field) != record['metadata'][field]:
                raise ValueError(f'Missing/mismatched candidate field: {field}')
        if row.get('chunk_id') != record['metadata'].get('chunk_id'):
            raise ValueError('Candidate chunk ID mismatch')
        if 'corpus_index' in row and row['corpus_index'] != ordinal:
            raise ValueError('Candidate corpus order mismatch')
        if 'text' in row and row['text'] != record['text']:
            raise ValueError('Candidate text mismatch')
        if 'chunk_reference' in row and row['chunk_reference'] != {'source_file': key[0], 'chunk_index': key[1]}:
            raise ValueError('Candidate reference mismatch')
        return ordinal


def fuse(catalog, dense, bm25):
    """Exactly Top-5 + Top-5, k=60, one-based ranks, stable corpus-order ties.

    Diagnostic raw scores are copied but never used in score or sort keys.
    Duplicate identities within a retriever are rejected; cross-list duplicates
    contribute once per retriever and yield a single output candidate.
    """
    union = {}
    for method, rows, diagnostic in [('dense', dense, 'similarity'), ('bm25', bm25, 'bm25_score')]:
        seen = set()
        for rank, row in enumerate(rows[:DEPTH], 1):
            if type(row.get('rank')) is not int or row['rank'] != rank:
                raise ValueError('Expected contiguous one-based ranks')
            ordinal = catalog.verify(row)
            if ordinal in seen:
                raise ValueError('Duplicate candidate in one ranking')
            seen.add(ordinal)
            score = row.get(diagnostic)
            if score is not None and (not isinstance(score, (int, float)) or not math.isfinite(score)):
                raise ValueError('Non-finite diagnostic score')
            if ordinal not in union:
                m = catalog.records[ordinal]['metadata']
                fields = ('chunk_id', 'chunk_index', 'case_name', 'source_file', 'original_source_file',
                          'page_start', 'page_end', 'token_count', 'opinion_type', 'author',
                          'major_unit_id', 'major_unit_type', 'sections')
                candidate = {field: deepcopy(m.get(field)) for field in fields}
                candidate.update(collection=catalog.collection, corpus_index=ordinal,
                                 chunk_reference={'source_file': m['source_file'], 'chunk_index': m['chunk_index']},
                                 dense_rank=None, bm25_rank=None, dense_similarity=None, bm25_score=None, rrf_score=0.)
                union[ordinal] = candidate
            candidate = union[ordinal]
            candidate[method + '_rank'] = rank
            candidate['dense_similarity' if method == 'dense' else 'bm25_score'] = score
            candidate['rrf_score'] += 1 / (K + rank)
    ordered = sorted(union.values(), key=lambda r: (-r['rrf_score'], r['corpus_index']))
    for rank, row in enumerate(ordered, 1):
        row['rank'] = row['hybrid_rank'] = rank
    return ordered
