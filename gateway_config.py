"""Secret-safe gateway configuration for production and experiments."""

import os
from dataclasses import dataclass, field
from pathlib import Path


# Historical metadata only: never used to construct a supported client.
LEGACY_NYU_BASE_URL = "https://ai-gateway.apps.cloud.rt.nyu.edu/v1"
LEGACY_NYU_EMBEDDING_MODEL = "@openai-embedding/text-embedding-3-small"
LEGACY_NYU_PROVIDER = "azure-openai"

# Experiments and the supported CourtLens runtime use the same Vercel provider.
EXPERIMENT_GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
EXPERIMENT_GATEWAY_PROVIDER = "vercel-ai-gateway"
EXPERIMENT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
EXPERIMENT_API_KEY_NAME = "AI_GATEWAY_API_KEY"
EXPERIMENT_MISSING_API_KEY_MESSAGE = (
    "Vercel AI Gateway API key is not configured. Add AI_GATEWAY_API_KEY to "
    "Streamlit secrets or your local environment."
)


def get_experiment_api_key() -> str:
    """Read the Vercel experiment key without exposing its value."""
    try:
        import streamlit as st

        value = st.secrets.get(EXPERIMENT_API_KEY_NAME, "")
    except (FileNotFoundError, KeyError):
        value = ""

    return str(value or os.getenv(EXPERIMENT_API_KEY_NAME, "")).strip()


def require_experiment_api_key() -> str:
    """Return the Vercel experiment key or raise a safe configuration error."""
    api_key = get_experiment_api_key()
    if not api_key:
        raise RuntimeError(EXPERIMENT_MISSING_API_KEY_MESSAGE)
    return api_key


# CourtLens AI Gateway is the application's configuration name, not a proxy.
GATEWAY_NAME = "CourtLens AI Gateway"
GATEWAY_BASE_URL = EXPERIMENT_GATEWAY_BASE_URL
GATEWAY_PROVIDER = EXPERIMENT_GATEWAY_PROVIDER
EMBEDDING_MODEL = EXPERIMENT_EMBEDDING_MODEL
API_KEY_NAME = EXPERIMENT_API_KEY_NAME
MISSING_API_KEY_MESSAGE = EXPERIMENT_MISSING_API_KEY_MESSAGE
get_gateway_api_key = get_experiment_api_key
require_gateway_api_key = require_experiment_api_key

# Embedding and generation models are selected independently.
VERCEL_BASE_URL = EXPERIMENT_GATEWAY_BASE_URL
VERCEL_PROVIDER = EXPERIMENT_GATEWAY_PROVIDER
VERCEL_EMBEDDING_MODEL = EXPERIMENT_EMBEDDING_MODEL
VERCEL_GENERATION_MODEL_SETTING = "VERCEL_GENERATION_MODEL"
RUNTIME_VECTOR_STORE_SETTING = "COURTLENS_VECTOR_STORE_PATH"
PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_RUNTIME_VECTOR_STORE = (
    PROJECT_DIR / "data/experiments/chunking/structure_aware_v1/vector_store"
)


def get_runtime_setting(name: str) -> str:
    """Streamlit secrets take precedence over the environment, as for keys."""
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
    except (FileNotFoundError, KeyError):
        value = ""
    return str(value or os.getenv(name, "")).strip()


@dataclass(frozen=True)
class VercelProviderConfig:
    """Explicit provider settings. Credentials are excluded from repr/logging.

    This object is client configuration, never a serializable asset manifest.
    """

    model: str
    api_key: str = field(repr=False)
    provider: str = VERCEL_PROVIDER
    base_url: str = VERCEL_BASE_URL


def vercel_embedding_config() -> VercelProviderConfig:
    """Use the model matching the frozen runtime document vectors."""
    return VercelProviderConfig(VERCEL_EMBEDDING_MODEL, require_experiment_api_key())


def vercel_generation_config() -> VercelProviderConfig:
    """Require an independently selected model; no unverified chat default."""
    api_key = require_experiment_api_key()
    model = get_runtime_setting(VERCEL_GENERATION_MODEL_SETTING)
    if not model:
        raise RuntimeError(
            "Vercel generation model is not configured. Set VERCEL_GENERATION_MODEL "
            "in Streamlit secrets or the environment to your verified Vercel chat "
            "model ID. No default model or NYU fallback is selected."
        )
    return VercelProviderConfig(model, api_key)


def vercel_client(config: VercelProviderConfig):
    """Construct an SDK client without sending a request or adding NYU headers."""
    from openai import OpenAI

    return OpenAI(api_key=config.api_key, base_url=config.base_url)


def runtime_vector_store_path() -> Path:
    """Resolve the single asset path setting relative to the project, not cwd."""
    value = get_runtime_setting(RUNTIME_VECTOR_STORE_SETTING)
    path = Path(value).expanduser() if value else DEFAULT_RUNTIME_VECTOR_STORE
    return (path if path.is_absolute() else PROJECT_DIR / path).resolve()
