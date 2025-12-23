"""
Rate Limiter - Prevent API abuse and manage quotas
"""
import time
import asyncio
from collections import defaultdict
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 20
    requests_per_hour: int = 100
    requests_per_day: int = 500
    cooldown_seconds: int = 60


@dataclass
class UserQuota:
    """Track user's API usage"""
    minute_requests: list = field(default_factory=list)
    hour_requests: list = field(default_factory=list)
    day_requests: list = field(default_factory=list)
    last_request: Optional[datetime] = None
    is_blocked: bool = False
    blocked_until: Optional[datetime] = None


class RateLimiter:
    """
    Rate limiter for API calls
    Prevents abuse and manages user quotas
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.user_quotas: Dict[str, UserQuota] = defaultdict(UserQuota)
        self._lock = asyncio.Lock()
    
    def _clean_old_requests(self, quota: UserQuota):
        """Remove expired request timestamps"""
        now = datetime.utcnow()
        
        # Clean minute requests (older than 1 minute)
        quota.minute_requests = [
            t for t in quota.minute_requests 
            if now - t < timedelta(minutes=1)
        ]
        
        # Clean hour requests (older than 1 hour)
        quota.hour_requests = [
            t for t in quota.hour_requests 
            if now - t < timedelta(hours=1)
        ]
        
        # Clean day requests (older than 24 hours)
        quota.day_requests = [
            t for t in quota.day_requests 
            if now - t < timedelta(days=1)
        ]
    
    async def check_rate_limit(self, user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if user can make a request
        
        Returns:
            (allowed: bool, retry_after_seconds: Optional[int])
        """
        async with self._lock:
            quota = self.user_quotas[user_id]
            now = datetime.utcnow()
            
            # Check if user is blocked
            if quota.is_blocked:
                if quota.blocked_until and now < quota.blocked_until:
                    retry_after = int((quota.blocked_until - now).total_seconds())
                    return False, retry_after
                else:
                    quota.is_blocked = False
                    quota.blocked_until = None
            
            # Clean old requests
            self._clean_old_requests(quota)
            
            # Check limits
            if len(quota.minute_requests) >= self.config.requests_per_minute:
                return False, 60
            
            if len(quota.hour_requests) >= self.config.requests_per_hour:
                return False, 3600
            
            if len(quota.day_requests) >= self.config.requests_per_day:
                return False, 86400
            
            return True, None
    
    async def record_request(self, user_id: str):
        """Record a successful request"""
        async with self._lock:
            quota = self.user_quotas[user_id]
            now = datetime.utcnow()
            
            quota.minute_requests.append(now)
            quota.hour_requests.append(now)
            quota.day_requests.append(now)
            quota.last_request = now
    
    async def block_user(self, user_id: str, duration_seconds: int = 3600):
        """Temporarily block a user"""
        async with self._lock:
            quota = self.user_quotas[user_id]
            quota.is_blocked = True
            quota.blocked_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user's current usage stats"""
        quota = self.user_quotas[user_id]
        self._clean_old_requests(quota)
        
        return {
            "requests_this_minute": len(quota.minute_requests),
            "requests_this_hour": len(quota.hour_requests),
            "requests_today": len(quota.day_requests),
            "limits": {
                "per_minute": self.config.requests_per_minute,
                "per_hour": self.config.requests_per_hour,
                "per_day": self.config.requests_per_day
            },
            "is_blocked": quota.is_blocked,
            "blocked_until": quota.blocked_until.isoformat() if quota.blocked_until else None
        }


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def check_and_record(user_id: str) -> tuple[bool, Optional[int]]:
    """
    Convenience function to check rate limit and record if allowed
    
    Usage:
        allowed, retry_after = await check_and_record(user_id)
        if not allowed:
            return f"Rate limited. Try again in {retry_after} seconds"
    """
    limiter = get_rate_limiter()
    allowed, retry_after = await limiter.check_rate_limit(user_id)
    
    if allowed:
        await limiter.record_request(user_id)
    
    return allowed, retry_after
