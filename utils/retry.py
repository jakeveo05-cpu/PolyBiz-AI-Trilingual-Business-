"""
Retry Logic - Handle transient failures gracefully
"""
import asyncio
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional
import logging

logger = logging.getLogger('polybiz.retry')


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay with exponential backoff and optional jitter"""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        # Add random jitter (±25%)
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)


def async_retry(config: RetryConfig = None):
    """
    Decorator for async functions with retry logic
    
    Usage:
        @async_retry(RetryConfig(max_retries=3))
        async def call_api():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            f"Attempt {attempt + 1}/{config.max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def sync_retry(config: RetryConfig = None):
    """
    Decorator for sync functions with retry logic
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        import time
                        time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


# Pre-configured retry configs for common use cases
AI_API_RETRY = RetryConfig(
    max_retries=3,
    base_delay=2.0,
    max_delay=30.0,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        # Add specific API exceptions here
    )
)

DATABASE_RETRY = RetryConfig(
    max_retries=2,
    base_delay=0.5,
    max_delay=5.0,
)

NETWORK_RETRY = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=15.0,
)
