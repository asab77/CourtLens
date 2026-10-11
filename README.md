# CourtLens: Supreme Court retrieval and grounded answers

The ingestion pipeline currently has two small steps:

1. `extract_text.py` reads every PDF in `data/raw/` and writes one UTF-8 text file
   per case to `data/processed/`.
2. `chunk_text.py` splits those text files and writes one JSONL file per case to
   `data/chunks/`.

The retrieval pipeline adds two more steps without generating final answers:

3. `build_index.py` embeds every chunk through CourtLens AI Gateway (Vercel) using
   `openai/text-embedding-3-small`, normalizes the vectors, and saves a
   local FAISS cosine-similarity index.
4. `retrieve.py` embeds a question with the same model and prints the five nearest
   stored chunks.

## Setup and run

From the `finalProject` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-ingestion.txt
python3 extract_text.py
python3 chunk_text.py
```

## Configure CourtLens AI Gateway

CourtLens AI Gateway is our application configuration name for Vercel AI Gateway,
not a separate server or proxy. Its OpenAI-compatible base URL is
`https://ai-gateway.vercel.sh/v1`. No NYU credential or Portkey header is used.

Set `AI_GATEWAY_API_KEY` securely in Streamlit secrets or the environment.
For AI Assistant generation, separately set `VERCEL_GENERATION_MODEL` to a
Vercel chat model ID you have verified. There is no default generation model;
NYU model IDs are not translated or assumed compatible. Never commit credentials.
Streamlit secrets take precedence over environment settings.

Query embeddings use `openai/text-embedding-3-small`, matching the validated
structure-aware store. `COURTLENS_VECTOR_STORE_PATH` optionally selects the asset
bundle; its default is
`data/experiments/chunking/structure_aware_v1/vector_store/`.
The original dense cosine retrieval, case filtering, Top-K behavior and source
citation format are preserved. The AI Assistant now defaults to structure-aware
hybrid retrieval (Dense Top-5 + BM25 Top-5, RRF k=60, final Top-5), with an explicit
Dense only option. The Retrieval tab remains dense. See
[the Streamlit integration guide](docs/phase7a2d_streamlit_integration.md) for
resource caching, evidence budgeting, attribution and smoke-test prerequisites.

Existing indexes do not need rebuilding. The production `data/vector_store/`
contains historical NYU metadata and is preserved; supported runtime loading
rejects incompatible metadata instead of silently querying it with Vercel.
`build_index.py` remains an explicit offline ingestion entry point whose future
builds would use Vercel, but it is not required for running the existing store.

The retrieval script prompts for a question. It also accepts one directly:

```bash
python3 retrieve.py "What rights does Miranda protect?"
```

Launch the CourtLens research interface with:

```bash
streamlit run app.py
```

## Streamlit Community Cloud deployment

The deployed app needs `app.py`, the Python modules it imports, `requirements.txt`,
and the frozen runtime asset bundle described in
[the asset packaging guide](docs/phase7a2a_runtime_configuration.md). The
structure-aware store is ignored/untracked, so a Git checkout alone is insufficient.
In Streamlit Community Cloud, select
Python 3.12 and add this entry under **Advanced settings → Secrets**:

```toml
AI_GATEWAY_API_KEY = "YOUR_KEY_HERE"
# Also set VERCEL_GENERATION_MODEL to your verified Vercel chat model ID.
# No unverified model example/default is supplied.
```

Use `.streamlit/secrets.toml.example` as a format reference only. A real
`.streamlit/secrets.toml` is ignored and must never be committed.

Human evaluation records are appended to `data/evaluations.jsonl`. This works during
an active deployment, but Streamlit Community Cloud storage is ephemeral, so those
records may disappear when the app restarts or redeploys. Download or copy important
evaluation results elsewhere; this project intentionally does not add a database.

CourtLens has two modes. Retrieval shows the existing FAISS evidence cards without
answer generation. AI Assistant performs a fresh FAISS search for each chat question,
sends only those labeled passages to the configured Vercel answer model, and shows
the grounded response with source mappings and its exact retrieved evidence.

Normal Chat uses the single configured generation model. Compare Models remains
visible, and saved comparison/session-state behavior is preserved, but new
comparisons are disabled: this migration supplies only one verified-model setting.
Two independently verified model configurations will be needed for future
comparison support. The previous NYU model list has been removed from active UI.

Historical NYU references in frozen manifests, experiment records and research
reports describe past behavior; they are not supported runtime configuration.

The builder writes three files to `data/vector_store/`:

- `index.faiss`: normalized embedding vectors searched with FAISS `IndexFlatIP`.
- `records.jsonl`: chunk text and unchanged metadata, in exact FAISS vector order.
- `manifest.json`: model, vector dimension, counts, and indexed input filenames.

Each stored record also has a `vector_id`; vector ID `n` always maps to line `n`
of `records.jsonl`. The builder rejects duplicate input paths and verifies that the
FAISS vector count equals the chunk-record count before saving.

The output filenames use a filesystem-safe version of the case name. For example,
`Miranda v. Arizona` becomes `data/processed/miranda_v_arizona.txt` and
`data/chunks/miranda_v_arizona.jsonl`. Original files in `data/raw/` are not renamed.

The extractor prefers the PDF's embedded U.S. Reports title. If that is absent, it
uses a recognizable `Party v. Party` caption on page 1. It stops with an error rather
than guessing when neither source provides a reliable name.

Each text file begins with the source filename and PDF page count. Extracted text
is separated with markers such as `===== PAGE 1 =====`, preserving PDF page
boundaries for future citations.

## Chunking decisions

Chunks are measured with the `cl100k_base` tokenizer rather than by character
count. The maximum is 1,200 tokens with 200 tokens of overlap. The recursive
splitter tries boundaries in this order: blank lines, line breaks, sentence ends
(`. `), and finally spaces. This favors intact paragraphs and sentences.

Chunking runs over each complete case, not one page at a time. This allows chunks
to reach the requested size and permits overlap across page boundaries. Each JSONL
record contains the chunk text plus `case_name`, descriptive `source_file`, actual
`original_source_file`, `page_start`, `page_end`, `chunk_index`, and `token_count`
metadata. Keeping both source fields preserves the mapping to an unchanged raw PDF.

## Important limitation

`pypdf` extracts text already embedded in a PDF. It does not perform OCR. If a PDF
contains only scanned page images, the script leaves that page's section empty and
reports the number of empty pages. OCR can be added later if the collection needs it.

## Experiment 1: fixed chunk size and overlap

`run_chunking_experiment.py` compares four token-based configurations while keeping
the embedding model, normalized vectors, FAISS `IndexFlatIP`, questions, and
relevance rules fixed:

- 600 tokens / 100 overlap
- 900 tokens / 150 overlap
- 1200 tokens / 200 overlap
- 1500 tokens / 200 overlap

Experiment 1 uses the Vercel AI Gateway independently of the legacy production/RAG
configuration. Set `AI_GATEWAY_API_KEY`; the runner uses the OpenAI-compatible base
URL `https://ai-gateway.vercel.sh/v1` with `openai/text-embedding-3-small`. It does
not send the NYU/Portkey provider header. Never commit the real key.

`data/evaluation/chunking_benchmark.json` contains 40 manually reviewed questions
across 8 Supreme Court cases, with 5 questions per case. All entries are marked
`"validated": true`. This benchmark compares chunking configurations under otherwise
controlled retrieval conditions; no experimental results are claimed here. The
normal runner refuses to use unvalidated labels.

Run the validated experiment from the project directory:

```bash
export AI_GATEWAY_API_KEY="YOUR_KEY_HERE"
python run_chunking_experiment.py
```

Use `--rebuild` to regenerate all four isolated indexes. For an implementation smoke
test only, `--allow-unvalidated` bypasses the review gate; results from that mode
must not be treated as final benchmark findings.

Generated chunks, indexes, and `results.json` live below
`data/experiments/chunking/` and never overwrite `data/chunks/` or
`data/vector_store/`. The detailed results record every retrieved rank, case, source,
page span, similarity, chunk index, token count, and relevance decision.

The runner reuses each configuration's existing complete chunk set. Missing,
partial, malformed, or configuration-inconsistent chunks stop the run rather than
being regenerated silently.

A retrieved chunk is relevant only when its case matches, its expected source file
matches when one is supplied, and its inclusive page span intersects a labeled page
range. Hit@1, Hit@3, and Hit@5 indicate whether at least one relevant chunk
appears by that depth. Reciprocal rank is `1 / first_relevant_rank`, or zero when no
relevant chunk appears in the top five; MRR is its mean across questions.

Run the metric unit tests without Streamlit:

```bash
python -m unittest discover -s tests -v
```
