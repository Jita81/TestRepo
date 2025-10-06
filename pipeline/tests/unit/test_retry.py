"""
Tests for Retry Mechanism.
"""

import pytest
import asyncio
from src.core.retry import (
    RetryConfig,
    retry_async,
    retry_sync,
    RetryExhaustedError,
    RetryableOperation,
    calculate_delay
)


class TestRetryConfig:
    """Test retry configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False


class TestCalculateDelay:
    """Test delay calculation."""
    
    def test_exponential_backoff(self):
        """Delay should increase exponentially."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )
        
        delay0 = calculate_delay(0, config)
        delay1 = calculate_delay(1, config)
        delay2 = calculate_delay(2, config)
        
        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0
    
    def test_max_delay_cap(self):
        """Delay should not exceed max_delay."""
        config = RetryConfig(
            initial_delay=10.0,
            max_delay=20.0,
            exponential_base=2.0,
            jitter=False
        )
        
        delay = calculate_delay(5, config)  # Would be 320 without cap
        assert delay == 20.0
    
    def test_jitter_adds_randomness(self):
        """Jitter should add randomness to delay."""
        config = RetryConfig(
            initial_delay=10.0,
            jitter=True
        )
        
        delays = [calculate_delay(1, config) for _ in range(10)]
        
        # Delays should vary (not all the same)
        assert len(set(delays)) > 1
        
        # All delays should be within jitter range (50%-100% of expected)
        for delay in delays:
            expected = 10.0 * 2.0  # 20.0
            assert expected * 0.5 <= delay <= expected


class TestRetryAsync:
    """Test async retry decorator."""
    
    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Successful call should not retry."""
        call_count = {"count": 0}
        
        @retry_async(RetryConfig(max_attempts=3))
        async def successful_operation():
            call_count["count"] += 1
            return "success"
        
        result = await successful_operation()
        assert result == "success"
        assert call_count["count"] == 1  # Called only once
    
    @pytest.mark.asyncio
    async def test_retries_on_failure(self):
        """Should retry on failure."""
        call_count = {"count": 0}
        
        @retry_async(RetryConfig(max_attempts=3, initial_delay=0.01))
        async def failing_operation():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise ValueError("Transient failure")
            return "success"
        
        result = await failing_operation()
        assert result == "success"
        assert call_count["count"] == 3  # Failed twice, succeeded third time
    
    @pytest.mark.asyncio
    async def test_raises_retry_exhausted(self):
        """Should raise RetryExhaustedError after max attempts."""
        @retry_async(RetryConfig(max_attempts=3, initial_delay=0.01))
        async def always_failing():
            raise ValueError("Permanent failure")
        
        with pytest.raises(RetryExhaustedError) as exc_info:
            await always_failing()
        
        assert "Failed after 3 attempts" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_respects_retry_on_exceptions(self):
        """Should only retry on specified exceptions."""
        call_count = {"count": 0}
        
        @retry_async(RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            retry_on=(ValueError,)  # Only retry on ValueError
        ))
        async def mixed_failures():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("Retryable")
            else:
                raise TypeError("Not retryable")
        
        # Should retry ValueError, then raise TypeError immediately
        with pytest.raises(TypeError):
            await mixed_failures()
        
        assert call_count["count"] == 2


class TestRetrySync:
    """Test sync retry decorator."""
    
    def test_successful_call_no_retry(self):
        """Successful call should not retry."""
        call_count = {"count": 0}
        
        @retry_sync(RetryConfig(max_attempts=3))
        def successful_operation():
            call_count["count"] += 1
            return "success"
        
        result = successful_operation()
        assert result == "success"
        assert call_count["count"] == 1
    
    def test_retries_on_failure(self):
        """Should retry on failure."""
        call_count = {"count": 0}
        
        @retry_sync(RetryConfig(max_attempts=3, initial_delay=0.01))
        def failing_operation():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise ValueError("Transient failure")
            return "success"
        
        result = failing_operation()
        assert result == "success"
        assert call_count["count"] == 3
    
    def test_raises_retry_exhausted(self):
        """Should raise RetryExhaustedError after max attempts."""
        @retry_sync(RetryConfig(max_attempts=3, initial_delay=0.01))
        def always_failing():
            raise ValueError("Permanent failure")
        
        with pytest.raises(RetryExhaustedError):
            always_failing()


class TestRetryableOperation:
    """Test retryable operation context manager."""
    
    @pytest.mark.asyncio
    async def test_execute_async_function(self):
        """Should execute async function with retry."""
        async def async_task():
            return "async result"
        
        async with RetryableOperation() as retry:
            result = await retry.execute(async_task)
            assert result == "async result"
    
    @pytest.mark.asyncio
    async def test_execute_sync_function(self):
        """Should execute sync function with retry."""
        def sync_task():
            return "sync result"
        
        async with RetryableOperation() as retry:
            result = await retry.execute(sync_task)
            assert result == "sync result"
    
    @pytest.mark.asyncio
    async def test_retries_on_failure(self):
        """Should retry failed operations."""
        call_count = {"count": 0}
        
        async def failing_task():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise ValueError("Transient error")
            return "success"
        
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        async with RetryableOperation(config) as retry:
            result = await retry.execute(failing_task)
            assert result == "success"
            assert call_count["count"] == 2
    
    @pytest.mark.asyncio
    async def test_passes_arguments(self):
        """Should pass arguments to function."""
        async def add(a, b):
            return a + b
        
        async with RetryableOperation() as retry:
            result = await retry.execute(add, 5, 10)
            assert result == 15
    
    @pytest.mark.asyncio
    async def test_passes_kwargs(self):
        """Should pass keyword arguments to function."""
        async def multiply(x, factor=2):
            return x * factor
        
        async with RetryableOperation() as retry:
            result = await retry.execute(multiply, 5, factor=3)
            assert result == 15
