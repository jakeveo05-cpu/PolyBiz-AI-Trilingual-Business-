"""
Unit Tests for Rate Limiter
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.rate_limiter import RateLimiter, RateLimitConfig, check_and_record


class TestRateLimitConfig:
    """Tests for RateLimitConfig"""
    
    def test_default_values(self):
        config = RateLimitConfig()
        assert config.requests_per_minute == 20
        assert config.requests_per_hour == 100
        assert config.requests_per_day == 500
    
    def test_custom_values(self):
        config = RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=50,
            requests_per_day=200
        )
        assert config.requests_per_minute == 10
        assert config.requests_per_hour == 50
        assert config.requests_per_day == 200


class TestRateLimiter:
    """Tests for RateLimiter"""
    
    @pytest.fixture
    def limiter(self):
        config = RateLimitConfig(
            requests_per_minute=3,
            requests_per_hour=10,
            requests_per_day=50
        )
        return RateLimiter(config)
    
    @pytest.mark.asyncio
    async def test_allows_first_request(self, limiter):
        allowed, retry_after = await limiter.check_rate_limit("user1")
        assert allowed is True
        assert retry_after is None
    
    @pytest.mark.asyncio
    async def test_records_request(self, limiter):
        await limiter.record_request("user1")
        stats = limiter.get_user_stats("user1")
        assert stats["requests_this_minute"] == 1
    
    @pytest.mark.asyncio
    async def test_blocks_after_minute_limit(self, limiter):
        user_id = "user2"
        
        # Make 3 requests (the limit)
        for _ in range(3):
            await limiter.record_request(user_id)
        
        # 4th request should be blocked
        allowed, retry_after = await limiter.check_rate_limit(user_id)
        assert allowed is False
        assert retry_after == 60  # 1 minute
    
    @pytest.mark.asyncio
    async def test_different_users_independent(self, limiter):
        # Fill up user1's quota
        for _ in range(3):
            await limiter.record_request("user1")
        
        # user2 should still be allowed
        allowed, _ = await limiter.check_rate_limit("user2")
        assert allowed is True
    
    @pytest.mark.asyncio
    async def test_block_user(self, limiter):
        await limiter.block_user("user3", duration_seconds=3600)
        
        allowed, retry_after = await limiter.check_rate_limit("user3")
        assert allowed is False
        assert retry_after > 0
    
    def test_get_user_stats(self, limiter):
        stats = limiter.get_user_stats("new_user")
        
        assert "requests_this_minute" in stats
        assert "requests_this_hour" in stats
        assert "requests_today" in stats
        assert "limits" in stats
        assert stats["requests_this_minute"] == 0


class TestCheckAndRecord:
    """Tests for check_and_record convenience function"""
    
    @pytest.mark.asyncio
    async def test_allows_and_records(self):
        # Use unique user ID to avoid conflicts
        user_id = f"test_user_{datetime.now().timestamp()}"
        
        allowed, retry_after = await check_and_record(user_id)
        assert allowed is True
        assert retry_after is None
