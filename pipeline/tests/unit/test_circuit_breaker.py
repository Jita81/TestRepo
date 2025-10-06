"""
Tests for Circuit Breaker Pattern.
"""

import pytest
import asyncio
from src.core.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerError,
    MultiCircuitBreaker
)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_initial_state_is_closed(self):
        """Circuit should start in closed state."""
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open
    
    @pytest.mark.asyncio
    async def test_successful_calls_keep_circuit_closed(self):
        """Successful calls should keep circuit closed."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        @breaker.call
        async def successful_operation():
            return "success"
        
        for _ in range(5):
            result = await successful_operation()
            assert result == "success"
            assert breaker.is_closed
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Circuit should open after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3, timeout=10)
        
        @breaker.call
        async def failing_operation():
            raise ValueError("Test failure")
        
        # First 3 failures should open circuit
        for i in range(3):
            with pytest.raises(ValueError):
                await failing_operation()
        
        assert breaker.is_open
        assert breaker._failure_count == 3
    
    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self):
        """Open circuit should reject calls immediately."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker.call
        async def failing_operation():
            raise ValueError("Test failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await failing_operation()
        
        assert breaker.is_open
        
        # Next call should be rejected immediately
        with pytest.raises(CircuitBreakerError):
            await failing_operation()
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self):
        """Circuit should enter half-open state after timeout."""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        @breaker.call
        async def failing_operation():
            raise ValueError("Test failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await failing_operation()
        
        assert breaker.is_open
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Circuit should be half-open now
        assert breaker._should_attempt_reset()
    
    @pytest.mark.asyncio
    async def test_circuit_closes_after_successful_recovery(self):
        """Circuit should close after successful calls in half-open state."""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        call_count = {"count": 0}
        
        @breaker.call
        async def conditionally_failing_operation():
            call_count["count"] += 1
            if call_count["count"] <= 2:
                raise ValueError("Initial failures")
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await conditionally_failing_operation()
        
        assert breaker.is_open
        
        # Wait for timeout to enter half-open
        await asyncio.sleep(0.2)
        
        # Successful calls should close circuit
        result = await conditionally_failing_operation()
        assert result == "success"
        # Need 2 successful calls
        result = await conditionally_failing_operation()
        assert breaker.is_closed
    
    def test_sync_function_support(self):
        """Circuit breaker should work with sync functions."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker.call
        def sync_operation():
            return "sync result"
        
        result = sync_operation()
        assert result == "sync result"
        assert breaker.is_closed
    
    def test_sync_function_opens_circuit(self):
        """Sync functions should open circuit on failures."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker.call
        def failing_sync_operation():
            raise ValueError("Sync failure")
        
        for _ in range(2):
            with pytest.raises(ValueError):
                failing_sync_operation()
        
        assert breaker.is_open
    
    def test_reset_circuit_manually(self):
        """Should be able to manually reset circuit."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        @breaker.call
        def failing_operation():
            raise ValueError("Failure")
        
        # Open circuit
        with pytest.raises(ValueError):
            failing_operation()
        
        assert breaker.is_open
        
        # Manual reset
        breaker.reset()
        assert breaker.is_closed
        assert breaker._failure_count == 0
    
    def test_get_stats(self):
        """Should provide circuit statistics."""
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        stats = breaker.get_stats()
        
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["failure_count"] == 0
        assert stats["failure_threshold"] == 5


class TestMultiCircuitBreaker:
    """Test multi-circuit breaker manager."""
    
    def test_get_or_create_breaker(self):
        """Should create circuit breaker on first access."""
        manager = MultiCircuitBreaker()
        
        breaker1 = manager.get("service1")
        assert isinstance(breaker1, CircuitBreaker)
        
        # Same instance on second access
        breaker2 = manager.get("service1")
        assert breaker1 is breaker2
    
    def test_separate_breakers_for_different_services(self):
        """Different services should have separate breakers."""
        manager = MultiCircuitBreaker()
        
        breaker1 = manager.get("service1")
        breaker2 = manager.get("service2")
        
        assert breaker1 is not breaker2
    
    def test_reset_all_breakers(self):
        """Should reset all circuit breakers."""
        manager = MultiCircuitBreaker(default_config={"failure_threshold": 1})
        
        # Create and open multiple breakers
        for service in ["service1", "service2", "service3"]:
            breaker = manager.get(service)
            
            @breaker.call
            def failing_op():
                raise ValueError("Failure")
            
            with pytest.raises(ValueError):
                failing_op()
            
            assert breaker.is_open
        
        # Reset all
        manager.reset_all()
        
        # All should be closed now
        for service in ["service1", "service2", "service3"]:
            assert manager.get(service).is_closed
    
    def test_get_all_stats(self):
        """Should get statistics for all breakers."""
        manager = MultiCircuitBreaker()
        
        manager.get("service1")
        manager.get("service2")
        
        stats = manager.get_all_stats()
        
        assert "service1" in stats
        assert "service2" in stats
        assert stats["service1"]["state"] == CircuitState.CLOSED.value
        assert stats["service2"]["state"] == CircuitState.CLOSED.value
