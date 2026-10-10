# CourtLens Document Structure Analysis

This local descriptive analysis asks whether the eight extracted opinions expose different structural signals that could justify a later chunking experiment. It does not measure retrieval quality and does not claim that structure-aware chunking is better.

## Heuristics and interpretation limits

Token counts use `cl100k_base`, the tokenizer used by CourtLens. Metadata and `===== PAGE N =====` markers are excluded from content statistics. Page-marker boundaries are joined with one newline so their injected blank lines are not counted as paragraph boundaries. Paragraphs split only on blank lines retained inside extracted pages.

Sentences are approximate: normalized paragraph text is split at `.`, `?`, or `!` when followed by a likely new sentence, after protecting a small list of common legal abbreviations. OCR errors, citations, initials, hyphenation, and hard line wraps can still distort sentence measurements.

Heading-like lines are standalone Roman numerals, standalone numbered markers, conservative syllabus/opinion/concurrence/dissent marker matches, or short lines whose letters are at least 90% uppercase. These are signals, not a parsed opinion outline. Running headers repeat across pages and can inflate heading and opinion marker counts. Marker presence is more trustworthy than its raw frequency.

## Comparison

| Case | Pages | Characters | Words | Approx. tokens | Paragraphs | Para median | Para mean | Para p90 | Para max | Sentences | Sent. median | Sent. mean | Sent. p90 | Sent. max | Blank boundaries | Heading-like | Roman |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Dred Scott v. Sandford | 241 | 672,098 | 116,319 | 158,519 | 1 | 158,519.00 | 158,519.00 | 158,519.00 | 158,519 | 3,558 | 34.00 | 42.15 | 85.00 | 341 | 0 | 262 | 3 |
| Gideon v. Wainwright | 18 | 35,024 | 5,958 | 8,998 | 1 | 8,998.00 | 8,998.00 | 8,998.00 | 8,998 | 289 | 23.00 | 29.48 | 59.20 | 230 | 0 | 35 | 2 |
| Marbury v. Madison | 44 | 94,793 | 16,916 | 26,765 | 1 | 26,765.00 | 26,765.00 | 26,765.00 | 26,765 | 620 | 34.00 | 41.37 | 82.00 | 544 | 0 | 49 | 0 |
| Miranda v. Arizona | 110 | 223,040 | 37,486 | 55,508 | 1 | 55,508.00 | 55,508.00 | 55,508.00 | 55,508 | 1,956 | 21.00 | 26.72 | 57.00 | 251 | 0 | 169 | 9 |
| New York Times Co. v. United States | 51 | 101,898 | 17,034 | 23,458 | 1 | 23,458.00 | 23,458.00 | 23,458.00 | 23,458 | 665 | 26.00 | 33.09 | 64.00 | 228 | 0 | 91 | 2 |
| Obergefell v. Hodges | 99 | 213,131 | 35,032 | 53,864 | 1 | 53,864.00 | 53,864.00 | 53,864.00 | 53,864 | 2,122 | 19.50 | 23.69 | 49.00 | 257 | 0 | 108 | 18 |
| Plessy v. Ferguson | 28 | 63,669 | 10,980 | 14,685 | 1 | 14,685.00 | 14,685.00 | 14,685.00 | 14,685 | 353 | 31.00 | 39.23 | 80.80 | 267 | 0 | 54 | 0 |
| Tinker v. Des Moines School Dist. | 24 | 48,373 | 8,084 | 11,516 | 1 | 11,516.00 | 11,516.00 | 11,516.00 | 11,516 | 403 | 21.00 | 26.84 | 56.00 | 173 | 0 | 49 | 2 |

### Explicit marker summary

| Case | Syllabus | Majority | Concurrence | Dissent | Numbered | Heading-like / 10k tokens | Roman / 10k tokens | Roman sequence frequencies |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Dred Scott v. Sandford | 0 | 4 | 0 | 4 | 0 | 16.53 | 0.19 | I: 1, II: 1, V: 1 |
| Gideon v. Wainwright | 1 | 5 | 5 | 0 | 0 | 38.90 | 2.22 | I: 1, II: 1 |
| Marbury v. Madison | 0 | 2 | 0 | 0 | 0 | 18.31 | 0.00 | none |
| Miranda v. Arizona | 1 | 27 | 0 | 17 | 1 | 30.45 | 1.62 | I: 1, II: 2, III: 3, IV: 2, V: 1 |
| New York Times Co. v. United States | 1 | 0 | 19 | 13 | 1 | 38.79 | 0.85 | I: 1, II: 1 |
| Obergefell v. Hodges | 5 | 32 | 0 | 1 | 0 | 20.05 | 3.34 | I: 5, II: 5, III: 4, IV: 3, V: 1 |
| Plessy v. Ferguson | 2 | 13 | 0 | 1 | 1 | 36.77 | 0.00 | none |
| Tinker v. Des Moines School Dist. | 1 | 6 | 3 | 8 | 1 | 42.55 | 1.74 | I: 1, II: 1 |

## Per-case observations

### Dred Scott v. Sandford

The extraction contains 158,519 tokens across 241 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 3558 units with a median of 34.00 tokens and a 90th percentile of 85.00. It detects 262 heading-like line occurrences and 3 standalone Roman-numeral markers (0.19 per 10,000 tokens). Conservative opinion markers present: majority opinion, dissent.

### Gideon v. Wainwright

The extraction contains 8,998 tokens across 18 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 289 units with a median of 23.00 tokens and a 90th percentile of 59.20. It detects 35 heading-like line occurrences and 2 standalone Roman-numeral markers (2.22 per 10,000 tokens). Conservative opinion markers present: syllabus, majority opinion, concurrence.

### Marbury v. Madison

The extraction contains 26,765 tokens across 44 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 620 units with a median of 34.00 tokens and a 90th percentile of 82.00. It detects 49 heading-like line occurrences and 0 standalone Roman-numeral markers (0.00 per 10,000 tokens). Conservative opinion markers present: majority opinion.

### Miranda v. Arizona

The extraction contains 55,508 tokens across 110 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 1956 units with a median of 21.00 tokens and a 90th percentile of 57.00. It detects 169 heading-like line occurrences and 9 standalone Roman-numeral markers (1.62 per 10,000 tokens). Conservative opinion markers present: syllabus, majority opinion, dissent.

### New York Times Co. v. United States

The extraction contains 23,458 tokens across 51 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 665 units with a median of 26.00 tokens and a 90th percentile of 64.00. It detects 91 heading-like line occurrences and 2 standalone Roman-numeral markers (0.85 per 10,000 tokens). Conservative opinion markers present: syllabus, concurrence, dissent.

### Obergefell v. Hodges

The extraction contains 53,864 tokens across 99 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 2122 units with a median of 19.50 tokens and a 90th percentile of 49.00. It detects 108 heading-like line occurrences and 18 standalone Roman-numeral markers (3.34 per 10,000 tokens). Conservative opinion markers present: syllabus, majority opinion, dissent.

### Plessy v. Ferguson

The extraction contains 14,685 tokens across 28 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 353 units with a median of 31.00 tokens and a 90th percentile of 80.80. It detects 54 heading-like line occurrences and 0 standalone Roman-numeral markers (0.00 per 10,000 tokens). Conservative opinion markers present: syllabus, majority opinion, dissent.

### Tinker v. Des Moines School Dist.

The extraction contains 11,516 tokens across 24 marked pages; all declared PDF pages are represented. It has 0 retained blank-line paragraph boundaries, so the paragraph heuristic yields 1 whole-document unit and cannot recover semantic paragraphs. The sentence heuristic finds 403 units with a median of 21.00 tokens and a 90th percentile of 56.00. It detects 49 heading-like line occurrences and 2 standalone Roman-numeral markers (1.74 per 10,000 tokens). Conservative opinion markers present: syllabus, majority opinion, concurrence, dissent.

## Structural density and explicit sectioning

All eight files have zero retained blank-line boundaries after artificial page boundaries are removed. Paragraph-based density therefore cannot distinguish these documents: each becomes one whole-document unit. This is evidence about the extraction format, not evidence that the opinions lack paragraphs.

Using approximate sentence length as the remaining local density signal, the three highest 90th percentiles are Dred Scott v. Sandford (85.00 tokens; median 34.00); Marbury v. Madison (82.00 tokens; median 34.00); Plessy v. Ferguson (80.80 tokens; median 31.00). This sentence heuristic is approximate and especially sensitive to OCR and legal citations.

The strongest explicit-section signals after normalizing marker counts by document token count are Obergefell v. Hodges (18 Roman markers, 3.34 per 10,000 tokens); Gideon v. Wainwright (2 Roman markers, 2.22 per 10,000 tokens); Tinker v. Des Moines School Dist. (2 Roman markers, 1.74 per 10,000 tokens). New York Times also exposes many concurrence and dissent marker lines despite only two standalone Roman markers, illustrating that separate-opinion labels and internal section markers capture different kinds of structure. Running headers and OCR artifacts mean these comparisons should guide manual inspection rather than serve as labels.

## Extraction limitations

- PDF extraction preserves page order but not a dependable semantic hierarchy. Hard line wraps, page headers, footers, and page numbers remain in the text.
- Blank-line paragraph boundaries are sparse or inconsistent in some files. A long measured paragraph may be several visually distinct paragraphs collapsed by extraction.
- Older scans contain substantial OCR noise, including broken words and altered characters. That weakens capitalization, heading, word, and sentence heuristics.
- Syllabus and opinion labels often recur as running headers. Counts indicate available signals, not the number of distinct opinion components.
- Standalone Roman numerals can mark sections, but can also occur in syllabi, separate opinions, or other enumerations. The analyzer does not infer nesting.

## Implications for Chunking

The measured variation supports testing whether a future chunker can use observable boundaries while retaining token limits. Candidate signals include standalone Roman or numbered markers, conservative opinion-component markers, blank-line boundaries when present, and sentence boundaries as a fallback. Repeated running headers should be de-duplicated or down-weighted before they become split points.

A future experiment should preserve the same corpus, embedding model, benchmark, retrieval settings, and Hit@1/Hit@3/Hit@5/MRR calculations, changing only the chunk-boundary strategy. It should also enforce maximum token sizes because the long paragraph units show that structural boundaries alone are insufficient. These findings motivate a controlled comparison; they do not establish a retrieval improvement.
