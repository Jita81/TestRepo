"""
Circuit Breaker Pattern Implementation.

Provides fault tolerance and resilience for pipeline operations by
preventing cascading failures and allowing systems to recover gracefully.
"""

import asyncio
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure threshold exceeded
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for resilient service calls.
    
    The circuit breaker prevents cascading failures by:
    1. Tracking failures (CLOSED state)
    2. Opening circuit after threshold (OPEN state)
    3. Testing recovery periodically (HALF_OPEN state)
    4. Closing circuit when service recovers
    
    Example:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        
        @breaker.call
        async def risky_operation():
            return await external_service.call()
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60,
        recovery_timeout: float = 30,
        expected_exceptions: tuple = (Exception,)
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery (OPEN → HALF_OPEN)
            recovery_timeout: Seconds to wait in HALF_OPEN before closing
            expected_exceptions: Tuple of exceptions to count as failures
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._opened_at: Optional[float] = None
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (operational)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)."""
        return self._state == CircuitState.HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt recovery."""
        if self._state != CircuitState.OPEN:
            return False
        
        if self._opened_at is None:
            return False
        
        return time.time() - self._opened_at >= self.timeout
    
    def _record_success(self):
        """Record successful operation."""
        self._failure_count = 0
        
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            
            # Close circuit after successful recovery test
            if self._success_count >= 2:
                self._state = CircuitState.CLOSED
                self._success_count = 0
                logger.info("Circuit breaker closed - service recovered")
    
    def _record_failure(self):
        """Record failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            # Failed during recovery test - reopen circuit
            self._state = CircuitState.OPEN
            self._opened_at = time.time()
            self._success_count = 0
            logger.warning("Circuit breaker reopened - recovery failed")
            
        elif self._failure_count >= self.failure_threshold:
            # Threshold exceeded - open circuit
            self._state = CircuitState.OPEN
            self._opened_at = time.time()
            logger.error(
                f"Circuit breaker opened after {self._failure_count} failures"
            )
    
    def call(self, func: Callable) -> Callable:
        """
        Decorator for protecting function calls with circuit breaker.
        
        Args:
            func: Function to protect
        
        Returns:
            Wrapped function
        """
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if we should attempt reset
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("Circuit breaker half-open - testing recovery")
            
            # Reject calls when circuit is open
            if self._state == CircuitState.OPEN:
                raise CircuitBreakerError(
                    f"Circuit breaker is open. "
                    f"Last failure: {self._last_failure_time}"
                )
            
            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result
                
            except self.expected_exceptions as e:
                self._record_failure()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if we should attempt reset
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("Circuit breaker half-open - testing recovery")
            
            # Reject calls when circuit is open
            if self._state == CircuitState.OPEN:
                raise CircuitBreakerError(
                    f"Circuit breaker is open. "
                    f"Last failure: {self._last_failure_time}"
                )
            
            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
                
            except self.expected_exceptions as e:
                self._record_failure()
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._opened_at = None
        logger.info("Circuit breaker manually reset")
    
    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with current state and metrics
        """
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self._last_failure_time,
            "opened_at": self._opened_at
        }


class MultiCircuitBreaker:
    """
    Manage multiple circuit breakers for different services.
    
    Example:
        breakers = MultiCircuitBreaker()
        
        @breakers.get("video_service").call
        async def generate_video():
            ...
        
        @breakers.get("3d_service").call
        async def convert_to_3d():
            ...
    """
    
    def __init__(self, default_config: Optional[dict] = None):
        """
        Initialize multi-circuit breaker.
        
        Args:
            default_config: Default configuration for new breakers
        """
        self.default_config = default_config or {
            "failure_threshold": 5,
            "timeout": 60,
            "recovery_timeout": 30
        }
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get(self, name: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker by name.
        
        Args:
            name: Circuit breaker name
        
        Returns:
            CircuitBreaker instance
        """
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(**self.default_config)
            logger.info(f"Created circuit breaker: {name}")
        
        return self._breakers[name]
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for name, breaker in self._breakers.items():
            breaker.reset()
            logger.info(f"Reset circuit breaker: {name}")
    
    def get_all_stats(self) -> dict:
        """
        Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping names to stats
        """
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
