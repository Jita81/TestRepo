"""
Retry Mechanism with Exponential Backoff.

Provides robust retry logic for handling transient failures
in pipeline operations.
"""

import asyncio
import time
import logging
from typing import Callable, Optional, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            retry_on: Tuple of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on = retry_on


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


def calculate_delay(
    attempt: int,
    config: RetryConfig
) -> float:
    """
    Calculate delay for next retry attempt.
    
    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration
    
    Returns:
        Delay in seconds
    """
    # Exponential backoff
    delay = config.initial_delay * (config.exponential_base ** attempt)
    
    # Cap at max delay
    delay = min(delay, config.max_delay)
    
    # Add jitter if enabled (randomness to prevent thundering herd)
    if config.jitter:
        import random
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_async(
    config: Optional[RetryConfig] = None
):
    """
    Decorator for async functions with retry logic.
    
    Usage:
        @retry_async(RetryConfig(max_attempts=5))
        async def risky_operation():
            ...
    
    Args:
        config: Retry configuration
    
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{config.max_attempts} failed "
                            f"for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed "
                            f"for {func.__name__}: {e}"
                        )
            
            # All attempts exhausted
            raise RetryExhaustedError(
                f"Failed after {config.max_attempts} attempts. "
                f"Last error: {last_exception}"
            ) from last_exception
        
        return wrapper
    return decorator


def retry_sync(
    config: Optional[RetryConfig] = None
):
    """
    Decorator for sync functions with retry logic.
    
    Usage:
        @retry_sync(RetryConfig(max_attempts=5))
        def risky_operation():
            ...
    
    Args:
        config: Retry configuration
    
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{config.max_attempts} failed "
                            f"for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed "
                            f"for {func.__name__}: {e}"
                        )
            
            # All attempts exhausted
            raise RetryExhaustedError(
                f"Failed after {config.max_attempts} attempts. "
                f"Last error: {last_exception}"
            ) from last_exception
        
        return wrapper
    return decorator


class RetryableOperation:
    """
    Context manager for retryable operations.
    
    Usage:
        async with RetryableOperation(config) as retry:
            result = await retry.execute(some_async_function, arg1, arg2)
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ):
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            RetryExhaustedError: If all attempts fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except self.config.retry_on as e:
                last_exception = e
                
                if attempt < self.config.max_attempts - 1:
                    delay = calculate_delay(attempt, self.config)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    await asyncio.sleep(delay)
        
        raise RetryExhaustedError(
            f"Failed after {self.config.max_attempts} attempts. "
            f"Last error: {last_exception}"
        ) from last_exception
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
