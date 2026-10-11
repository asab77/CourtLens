"""Deterministic, text-only Okapi BM25; no dependencies or metadata inputs.

IDF(t) = ln(1 + (N - df(t) + .5) / (df(t) + .5))
score(q,d) = sum(qtf(t) * IDF(t) * tf(t,d)*(k1+1) /
                  (tf(t,d) + k1*(1-b+b*len(d)/avgdl)))

The positive smoothed Robertson IDF convention avoids negative scores for common
terms. Repeated query terms contribute linearly; no extra query saturation is
applied. Length is the count of lexical terms, not embedding-token count.
"""

from collections import Counter, defaultdict
import math
import unicodedata


K1 = 1.5
B = 0.75
TOKENIZER_VERSION = 'nfkc-casefold-unicode-letter-number-marks-v1'
TOKENIZER_DESCRIPTION = (
    'Unicode NFKC then casefold; contiguous Unicode letters/numbers form terms; '
    'combining marks continue an existing term. All other characters, including '
    'punctuation, apostrophes, hyphens, decimal points, and underscores, separate '
    'terms. Numeric strings remain terms. No stemming, stopword removal, OCR '
    'repair, synonyms, expansion, or legal normalization. Frozen text, including '
    'headers and PDF markers, is used as-is.'
)


def tokenize(text):
    if not isinstance(text, str):
        raise TypeError('BM25 text must be a string')
    terms, current = [], []
    for char in unicodedata.normalize('NFKC', text).casefold():
        category = unicodedata.category(char)[0]
        if category in ('L', 'N') or (category == 'M' and current):
            current.append(char)
        else:
            if current:
                terms.append(''.join(current))
                current = []
    if current:
        terms.append(''.join(current))
    return terms


class BM25:
    """Ranking accepts only strings; labels, cases, and opinions cannot enter."""

    def __init__(self, documents, k1=K1, b=B):
        if not documents:
            raise ValueError('BM25 requires a nonempty corpus')
        if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError('BM25 requires finite k1 > 0 and 0 <= b <= 1')
        self.k1, self.b = k1, b
        self.document_count = len(documents)
        counts = [Counter(tokenize(text)) for text in documents]
        self.lengths = [sum(count.values()) for count in counts]
        self.average_length = sum(self.lengths) / self.document_count
        self.postings = defaultdict(list)
        for index, count in enumerate(counts):
            for term, frequency in count.items():
                self.postings[term].append((index, frequency))
        self.idf = {term: math.log1p((self.document_count - len(rows) + .5) / (len(rows) + .5))
                    for term, rows in self.postings.items()}

    def scores(self, query):
        output = [0.0] * self.document_count
        query_counts = Counter(tokenize(query))
        if not self.average_length:
            return output
        # Canonical term order makes accumulation invariant to query word order.
        for term, query_frequency in sorted(query_counts.items()):
            for index, frequency in self.postings.get(term, ()):
                denominator = frequency + self.k1 * (1 - self.b + self.b * self.lengths[index] / self.average_length)
                output[index] += query_frequency * self.idf[term] * frequency * (self.k1 + 1) / denominator
        if any(not math.isfinite(value) or value < 0 for value in output):
            raise ValueError('BM25 generated an invalid score')
        return output

    def rank(self, query, limit=20):
        if type(limit) is not int or limit < 0:
            raise ValueError('Rank limit must be a nonnegative integer')
        scored = self.scores(query)
        # No zero-score padding: an empty/OOV query cannot get accidental hits.
        matches = [(index, score) for index, score in enumerate(scored) if score > 0]
        return sorted(matches, key=lambda item: (-item[1], item[0]))[:limit]
