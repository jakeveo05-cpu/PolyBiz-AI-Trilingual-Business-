"""
Unit Tests for Retry Logic
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.retry import (
    RetryConfig,
    calculate_delay,
    async_retry,
    sync_retry,
    AI_API_RETRY,
    DATABASE_RETRY
)


class TestRetryConfig:
    """Tests for RetryConfig"""
    
    def test_default_values(self):
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_custom_values(self):
        config = RetryConfig(
            max_retries=5,
            base_delay=0.5,
            max_delay=30.0,
            jitter=False
        )
        
        assert config.max_retries == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 30.0
        assert config.jitter is False


class TestCalculateDelay:
    """Tests for calculate_delay"""
    
    def test_first_attempt_delay(self):
        config = RetryConfig(base_delay=1.0, jitter=False)
        delay = calculate_delay(0, config)
        
        assert delay == 1.0
    
    def test_exponential_backoff(self):
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        
        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 8.0
    
    def test_max_delay_cap(self):
        config = RetryConfig(base_delay=1.0, max_delay=5.0, jitter=False)
        
        # Attempt 10 would be 1024 without cap
        delay = calculate_delay(10, config)
        assert delay == 5.0
    
    def test_jitter_adds_variance(self):
        config = RetryConfig(base_delay=10.0, jitter=True)
        
        # Run multiple times to check variance
        delays = [calculate_delay(0, config) for _ in range(10)]
        
        # Should have some variance (not all the same)
        assert len(set(delays)) > 1


class TestAsyncRetry:
    """Tests for async_retry decorator"""
    
    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        call_count = 0
        
        @async_retry(RetryConfig(max_retries=3))
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await success_func()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retries_on_failure(self):
        call_count = 0
        
        @async_retry(RetryConfig(max_retries=3, base_delay=0.01))
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await fail_then_succeed()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        call_count = 0
        
        @async_retry(RetryConfig(max_retries=2, base_delay=0.01))
        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Permanent failure")
        
        with pytest.raises(ConnectionError):
            await always_fail()
        
        assert call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_only_retries_specified_exceptions(self):
        call_count = 0
        
        @async_retry(RetryConfig(
            max_retries=3,
            base_delay=0.01,
            retryable_exceptions=(ConnectionError,)
        ))
        async def raise_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")
        
        with pytest.raises(ValueError):
            await raise_value_error()
        
        # Should not retry ValueError
        assert call_count == 1


class TestSyncRetry:
    """Tests for sync_retry decorator"""
    
    def test_success_no_retry(self):
        call_count = 0
        
        @sync_retry(RetryConfig(max_retries=3))
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = success_func()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retries_on_failure(self):
        call_count = 0
        
        @sync_retry(RetryConfig(max_retries=3, base_delay=0.01))
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = fail_then_succeed()
        
        assert result == "success"
        assert call_count == 2


class TestPreConfiguredRetryConfigs:
    """Tests for pre-configured retry configs"""
    
    def test_ai_api_retry_config(self):
        assert AI_API_RETRY.max_retries == 3
        assert AI_API_RETRY.base_delay == 2.0
        assert ConnectionError in AI_API_RETRY.retryable_exceptions
    
    def test_database_retry_config(self):
        assert DATABASE_RETRY.max_retries == 2
        assert DATABASE_RETRY.base_delay == 0.5
