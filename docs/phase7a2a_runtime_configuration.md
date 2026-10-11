# Phase 7A.2A: Vercel configuration and runtime assets

This document records the prerequisite phase. Its asset validation and packaging
contract remains current; the later [Phase 7A.2A.1 migration](phase7a2a1_gateway_migration.md)
supersedes its descriptions of NYU defaults and unchanged application wiring.

This phase supplies configuration and read-only validation only. It does not
wire the Assistant, change retrieval or answer generation, modify prompts or
citations, or run an experiment. Legacy NYU configuration, experiment factories,
and existing retrieval defaults remain unchanged. No provider is selected by
fallback: missing Vercel credentials fail explicitly.

## Provider configuration

`gateway_config.vercel_embedding_config()` returns an immutable configuration
for provider `vercel-ai-gateway`, base URL `https://ai-gateway.vercel.sh/v1`, and
model `openai/text-embedding-3-small`. This embedding model deliberately remains
fixed to match the existing 1536-dimensional document vectors.

`gateway_config.vercel_generation_config()` independently reads
`VERCEL_GENERATION_MODEL`. No verified Vercel chat model was found in project
configuration; the existing `rag.ANSWER_MODELS` are NYU identifiers, not evidence
of Vercel compatibility. There is no default generation model. An absent model
produces an actionable configuration error. Supplying an ID does not verify its
availability; the operator must supply a verified Vercel chat model before live
generation integration. This phase makes no chat request or model trial.

Both configurations require `AI_GATEWAY_API_KEY` via the existing safe
experiment credential loader. Streamlit secrets take precedence over environment
variables; absent/empty settings fall back to the environment. Neither consults
`NYU_AI_GATEWAY_API_KEY`. `vercel_client(config)` constructs an OpenAI-compatible
client without sending requests or adding Portkey/NYU headers. It does not select
the request model automatically: future callers must pass `config.model` explicitly.
The credential is excluded from configuration repr; configuration objects must
never be serialized to manifests or logged. Existing secret files are unchanged.

## Single runtime path setting

`COURTLENS_VECTOR_STORE_PATH` selects the structure-aware store, via Streamlit
secrets or the environment using the same precedence. The default is:

```text
data/experiments/chunking/structure_aware_v1/vector_store/
```

Relative settings are resolved against the project directory, independent of
working directory; absolute paths and home-directory expansion are supported.
`runtime_assets.load_runtime_vector_store()` reads this setting and returns the
existing `(index, records, manifest)` tuple only after validation. It can also
accept an explicit Path for local callers/tests. Loading assets does not require
a credential or create an API client.

The setting is not yet consumed by `app.py`: the live workflow remains unchanged
until separately authorized Phase 7A.2B integration.

## Validation contract

The loader requires `index.faiss`, `records.jsonl`, and `manifest.json` in the
selected directory, with sibling `../chunks.jsonl` and `../manifest.json`.
It verifies:

- Exactly 433 index vectors, stored records, and frozen chunks, with matching
  manifest counts; dimension 1536 in both manifest and actual index.
- Actual FAISS IndexFlatIP with inner-product metric; manifest cosine similarity,
  L2 unit normalization, Vercel provider/base URL/model, structure_aware_v1 strategy,
  phase4b1-v1 logic version, and single chunks.jsonl input.
- Finite document vectors with norm 1 (absolute tolerance 1e-5, zero relative
  tolerance). Vectors are reconstructed for validation only, never normalized or
  rewritten by the loader.
- Stored vector IDs equal their row positions; full text and complete metadata
  equal the frozen chunk records in the same order.
- Nonempty unique chunk IDs, source-local contiguous chunk indices, source order
  and case count, nonempty text, source/case names, page/token ranges, strategy,
  opinion metadata, and consistent major-unit provenance.
- SHA-256 of the frozen chunks and chunk manifest matches the store manifest;
  SHA-256 of the source structural preview matches the chunk manifest. The
  preview path is project-relative and cannot escape the project directory.

Missing, incompatible or corrupt assets raise clear validation errors. There
is no regeneration, rebuild, write, silent fallback, or partial-store acceptance.
Hashes establish consistency with declared provenance, not cryptographic
identity/authenticity. Neither hashes nor row IDs independently prove that every
embedding was computed from its declared text. As with the existing experiment,
the original builder's ordering contract supplies that association.

## Fresh deployment packaging

The structure-aware experiment directory is Git-ignored and untracked. A fresh
Git checkout does not supply the runtime store. Existing ignore rules remain
unchanged; nothing is uploaded or moved by this phase.

An operator must provide the existing frozen bundle through their deployment's
normal local asset packaging or mounted directory, maintaining this layout:

```text
<bundle>/
  chunks.jsonl
  manifest.json
  vector_store/
    index.faiss
    records.jsonl
    manifest.json
```

Set `COURTLENS_VECTOR_STORE_PATH` to `<bundle>/vector_store` when using a
nondefault location. Also retain the project-relative provenance file
`data/analysis/structure_aware_preview.json` (already tracked in Git), with its
original contents. A relocated bundle still uses that canonical preview path.
Supply the secret through deployment secrets/environment, never the bundle.
Supply `VERCEL_GENERATION_MODEL` separately once a Vercel chat model is verified.
Do not replace the frozen files or their hashes to bypass a validation failure.
No external storage, upload mechanism, asset download or duplicate index is
implemented here.

## Local verification and remaining prerequisites

Run the focused local tests:

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_runtime_configuration.py'
```

The repository's `run_phase4c2_tests.py` runs the full suite with DNS, socket
connections and requests HTTP dispatch blocked, using a verified local tokenizer
vocabulary and a temporary cache. Tests use synthetic assets and mock SDK clients.
A read-only load of the actual default store is an additional local check.

The source and asset prerequisites can support Phase 7A.2B implementation. Live
Vercel generation remains blocked until a verified chat model ID is supplied;
fresh deployment remains blocked until the ignored frozen bundle is supplied.
This phase intentionally performs neither live integration nor provider checks.

## Phase completion evidence

Local validation of the actual default store passed: 433 vectors and records,
1536 dimensions, IndexFlatIP, finite unit-length vectors, matching frozen text,
metadata, identity/order, and all three provenance hashes.

- Focused Phase 7A.2A tests: 19 passed.
- Existing Phase 4C.2 tests: 14 passed; relevant existing group: 37 passed.
- Full repository suite: 218 passed under the offline runner.
- Before/after SHA-256 comparison: all 131 existing data files unchanged, with
  no new or missing data files. This covers production and experimental stores,
  frozen chunks, benchmarks, saved results, and prior analysis reports.
- No provider requests, index rebuilds, chunk regeneration, dependency installs,
  secret-file changes, commits, or pushes occurred.

**READY for Phase 7A.2B implementation.** This readiness does not establish live
provider availability. A verified Vercel generation model remains a prerequisite
for live generation; ignored runtime assets must be packaged for a fresh deployment.
