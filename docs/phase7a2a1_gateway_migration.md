# Phase 7A.2A.1: CourtLens AI Gateway migration

CourtLens AI Gateway names the application's Vercel provider configuration. It
is not an additional server, wrapper service, or proxy.

## Supported configuration

Configuration is centralized in `gateway_config.py`:

| Setting | Value / behavior |
|---|---|
| Provider | Vercel AI Gateway (`vercel-ai-gateway`) |
| Base URL | `https://ai-gateway.vercel.sh/v1` |
| Credential | `AI_GATEWAY_API_KEY` |
| Embedding model | `openai/text-embedding-3-small` |
| Generation model | `VERCEL_GENERATION_MODEL`, required independently, no default |
| Runtime path | `COURTLENS_VECTOR_STORE_PATH`; defaults to the frozen structure-aware store |

Streamlit secrets take precedence over environment settings. Missing credentials
or generation model produce explicit errors. No credential is logged or stored
in manifests; the real secret file is unchanged. The sample secret file has been
updated without any real values. NYU credential getters have been removed.
Historical NYU provider/model/URL constants are explicitly named `LEGACY_NYU_*`
for reading archived metadata; no supported client uses them.

## Migrated execution paths

- `retrieve.embedding_client()` constructs the configured Vercel client, without
  Portkey headers. The default question embedding model matches the frozen store.
- `retrieve.semantic_search()` loads the existing validated runtime store when
  none is supplied, then performs the original dense FAISS retrieval. The low-level
  store loader defaults to the configured runtime path and Vercel compatibility.
- `app.py` caches the validated structure-aware store and checks the Vercel
  credential. Assistant generation configuration is checked before retrieval, so
  an unset model does not cause a needless question-embedding request.
- `rag.py` uses the independent configured Vercel generation model and client.
  A passed model ID must match `VERCEL_GENERATION_MODEL`. The existing prompts,
  labeled evidence, history handling, citation format, and correction behavior
  remain unchanged.
- `build_index.py` uses the same Vercel client/configuration for any future explicit
  ingestion execution. It was not executed in this migration.
- Existing Vercel experiment factories and explicitly configured experimental
  paths remain compatible. Historical data is not rewritten.

The original production index has legacy NYU metadata and is preserved unchanged.
It is not silently accepted as a supported Vercel runtime store, even though its
vector dimension matches. The supported default is the validated existing
433-record structure-aware store; no rebuild is needed. Dense retrieval remains
cosine via normalized inner product, with unchanged case filtering and Top-K
ranking. Hybrid retrieval has not been integrated.

## Application compatibility

Retrieval, Normal Chat and Compare Models remain visible with the existing layout
and session-state keys. Normal Chat's model selector displays only the configured
Vercel model. Without that setting, it displays a configuration placeholder and
fails clearly before provider requests.

The previous four NYU model IDs are removed from active execution. They have not
been mapped to guessed Vercel IDs. New Compare Models requests are explicitly
disabled because this phase supplies only one generation-model setting. The
workspace and saved comparison results remain available. Two independently
verified model configurations and their validation will be required in a future
phase to restore new comparisons. No extra model or provider call was introduced.

## Deployment and historical documentation

Use the current README and `.streamlit/secrets.toml.example` for provider setup.
Supply a Vercel chat model ID that you have independently verified; this phase
does not verify availability or make generation requests.

The asset packaging contract in `phase7a2a_runtime_configuration.md` still applies:
the ignored/untracked store, frozen chunks and manifest must be supplied to a
fresh deployment, along with the tracked structural preview for hash verification.
No assets were uploaded, moved, duplicated or regenerated; ignore rules are unchanged.

The earlier Phase 7A.2A document describes its historical prerequisite-only state
(when the Assistant still used NYU). This migration supersedes those statements
about current application wiring. Frozen experiment records and analysis reports
remain historical evidence, not setup instructions.

## Tests and stop boundary

Focused tests use mocked clients and Streamlit's local test harness. They check
Vercel defaults, missing credentials/model, no NYU fallback/imports, independent
model configuration, dense runtime loading, Normal Chat citations/session state,
and the explicit Compare Models limitation. Historical store fixtures still
verify archived NYU metadata can only be loaded with explicit legacy expectations.

No live provider request, embedding, index rebuild, benchmark change, hybrid
integration, query rewriting, new citation verification, dependency installation,
commit or push is part of this phase.

## Completion evidence

- Focused application migration/UI tests: 12 passed.
- Focused provider and asset tests: 19 passed.
- Full repository suite: 230 passed under the offline runner (DNS and network
  connections blocked). Existing relevant test groups also passed.
- Actual frozen runtime store passed read-only validation: 433 vectors and
  records, 1536 dimensions, IndexFlatIP, normalized vectors and matching provenance.
- All 131 existing data files retained their before/after SHA-256 hashes. No
  data files were added or removed, including production and experimental indexes,
  frozen chunks, benchmarks, results and analysis reports.
- No real provider requests, artifact rebuilds, secret-file edits, dependency
  installs, commits or pushes occurred.

**READY for Phase 7A.2B implementation.** Live generation is not yet ready: no
`VERCEL_GENERATION_MODEL` is configured locally, and its availability has not
been tested here. New model comparisons require two verified model configurations.
Fresh deployment also requires supplying the ignored frozen runtime bundle.
