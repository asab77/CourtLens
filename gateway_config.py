"""Secret-safe gateway configuration for production and experiments."""

import os


GATEWAY_BASE_URL = "https://ai-gateway.apps.cloud.rt.nyu.edu/v1"
GATEWAY_PROVIDER = "azure-openai"
EMBEDDING_MODEL = "@openai-embedding/text-embedding-3-small"
API_KEY_NAME = "NYU_AI_GATEWAY_API_KEY"
MISSING_API_KEY_MESSAGE = (
    "NYU AI Gateway API key is not configured. Add NYU_AI_GATEWAY_API_KEY to "
    "Streamlit secrets or your local environment."
)

# Experiment 1 uses Vercel without changing the legacy production/RAG gateway.
EXPERIMENT_GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
EXPERIMENT_GATEWAY_PROVIDER = "vercel-ai-gateway"
EXPERIMENT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
EXPERIMENT_API_KEY_NAME = "AI_GATEWAY_API_KEY"
EXPERIMENT_MISSING_API_KEY_MESSAGE = (
    "Vercel AI Gateway API key is not configured. Add AI_GATEWAY_API_KEY to "
    "Streamlit secrets or your local environment."
)


def get_nyu_api_gateway_api_key() -> str:
    """Read the key from Streamlit secrets, with an environment fallback."""
    try:
        import streamlit as st

        value = st.secrets.get(API_KEY_NAME, "")
    except (FileNotFoundError, KeyError):
        value = ""

    return str(value or os.getenv(API_KEY_NAME, "")).strip()


def require_nyu_api_gateway_api_key() -> str:
    """Return the configured key or raise a safe, actionable error."""
    api_key = get_nyu_api_gateway_api_key()
    if not api_key:
        raise RuntimeError(MISSING_API_KEY_MESSAGE)
    return api_key


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
