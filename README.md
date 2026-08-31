# Supreme Court ingestion: extraction and chunking

The ingestion pipeline currently has two small steps:

1. `extract_text.py` reads every PDF in `data/raw/` and writes one UTF-8 text file
   per case to `data/processed/`.
2. `chunk_text.py` splits those text files and writes one JSONL file per case to
   `data/chunks/`.

The retrieval pipeline adds two more steps without generating final answers:

3. `build_index.py` embeds every chunk through the NYU AI gateway using
   `@openai-embedding/text-embedding-3-small`, normalizes the vectors, and saves a
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

## Build and test the vector index

Set the NYU Gateway key in your local environment, then run:

```bash
export NYU_AI_GATEWAY_API_KEY="YOUR_KEY_HERE"
python3 build_index.py
python3 retrieve.py
```

Both embedding scripts use the OpenAI Python client with the custom OpenAI-compatible
base URL `https://ai-gateway.apps.cloud.rt.nyu.edu/v1`. The Portkey SDK is not needed.
They send the workshop provider setting as `x-portkey-provider: azure-openai`.
The key is loaded centrally from Streamlit secrets or, for local development, the
`NYU_AI_GATEWAY_API_KEY` environment variable. Never commit the real value.

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
and all three files in `data/vector_store/`. In Streamlit Community Cloud, select
Python 3.12 and add this entry under **Advanced settings → Secrets**:

```toml
NYU_AI_GATEWAY_API_KEY = "YOUR_KEY_HERE"
```

Use `.streamlit/secrets.toml.example` as a format reference only. A real
`.streamlit/secrets.toml` is ignored and must never be committed.

Human evaluation records are appended to `data/evaluations.jsonl`. This works during
an active deployment, but Streamlit Community Cloud storage is ephemeral, so those
records may disappear when the app restarts or redeploys. Download or copy important
evaluation results elsewhere; this project intentionally does not add a database.

CourtLens has two modes. Retrieval shows the existing FAISS evidence cards without
answer generation. AI Assistant performs a fresh FAISS search for each chat question,
sends only those labeled passages to the selected NYU Gateway answer model, and shows
the grounded response with source mappings and its exact retrieved evidence.

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
