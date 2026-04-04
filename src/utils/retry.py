"""
Retry decorator with exponential backoff using tenacity.
"""

import functools
from typing import Callable, Optional, Tuple, Type

from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    after_log,
)
import logging

_log = logging.getLogger("auto-shorts-engine.retry")


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator factory that wraps a function with exponential-backoff retry logic.

    Args:
        max_attempts: Total number of attempts (including first try).
        backoff_factor: Multiplier applied to wait time after each failure.
        min_wait: Minimum wait in seconds between retries.
        max_wait: Maximum wait cap in seconds.
        exceptions: Tuple of exception types that trigger a retry.

    Returns:
        Decorated function that retries on specified exceptions.

    Example:
        @with_retry(max_attempts=3, backoff_factor=2)
        def call_api():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            decorated = retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=backoff_factor,
                    min=min_wait,
                    max=max_wait,
                ),
                retry=retry_if_exception_type(exceptions),
                before_sleep=before_sleep_log(_log, logging.WARNING),
                after=after_log(_log, logging.DEBUG),
                reraise=True,
            )(func)
            return decorated(*args, **kwargs)

        return wrapper

    return decorator
