"""Shared, secret-safe NYU AI Gateway configuration."""

import os


GATEWAY_BASE_URL = "https://ai-gateway.apps.cloud.rt.nyu.edu/v1"
GATEWAY_PROVIDER = "azure-openai"
EMBEDDING_MODEL = "@openai-embedding/text-embedding-3-small"
API_KEY_NAME = "NYU_AI_GATEWAY_API_KEY"
MISSING_API_KEY_MESSAGE = (
    "NYU AI Gateway API key is not configured. Add NYU_AI_GATEWAY_API_KEY to "
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
