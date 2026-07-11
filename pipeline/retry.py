"""
retry.py
--------
One retry helper, used by every stage that makes an external call
(research_agent.py's LLM call, composio_client.py's HTTP call). Extracted
because both stages had independently written near-identical
attempt-count-plus-linear-backoff loops -- duplicated logic that would
drift out of sync the next time someone tuned one but not the other.

Design choice: retry on *transient* failures only. A caller decides what
counts as transient by raising `TransientError` for it; any other
exception propagates immediately on the first attempt, because retrying a
non-transient failure (a bad request, a schema mismatch) just wastes three
attempts producing the same wrong answer three times.
"""

from __future__ import annotations
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class TransientError(Exception):
    """Raise this (or a subclass) for failures worth retrying: timeouts,
    rate limits, 5xx responses, malformed-but-plausibly-truncated JSON.
    Any other exception is treated as final and re-raised immediately."""


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    backoff_seconds: float = 2.0,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T:
    """
    Calls fn() up to max_attempts times. Retries only on TransientError,
    with linear backoff (backoff_seconds * attempt_number). Any other
    exception is not retried. Raises the last TransientError if every
    attempt is exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except TransientError as exc:
            last_exc = exc
            if attempt < max_attempts:
                if on_retry:
                    on_retry(attempt, exc)
                time.sleep(backoff_seconds * attempt)
                continue
    raise last_exc  # type: ignore[misc]  # loop always sets last_exc before falling through
