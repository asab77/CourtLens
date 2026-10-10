"""Bounded retry support for transient embedding rate limits."""

import time
from collections.abc import Callable
from typing import TypeVar

from openai import RateLimitError


RATE_LIMIT_BACKOFF_SECONDS = (60, 120, 240)
ResponseT = TypeVar("ResponseT")


def call_with_rate_limit_retry(
    request: Callable[[], ResponseT], operation: str
) -> ResponseT:
    """Retry one embedding request only when the gateway reports a rate limit."""
    retry_number = 0
    while True:
        try:
            return request()
        except RateLimitError:
            if retry_number == len(RATE_LIMIT_BACKOFF_SECONDS):
                raise
            wait_seconds = RATE_LIMIT_BACKOFF_SECONDS[retry_number]
            retry_number += 1
            print(
                f"Rate limited on {operation}; retry {retry_number}/"
                f"{len(RATE_LIMIT_BACKOFF_SECONDS)} in {wait_seconds} seconds."
            )
            time.sleep(wait_seconds)
