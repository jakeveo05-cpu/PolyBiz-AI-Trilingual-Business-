#!/usr/bin/env python
"""
Local Test Script - Test PolyBiz AI without real API keys
Simulates bot interactions and verifies all components work
"""
import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set mock environment variables for testing
os.environ.setdefault("DISCORD_BOT_TOKEN", "test_token")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test_key_for_local_testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///test_polybiz.db")


def print_header(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")


def print_result(name: str, passed: bool, message: str = ""):
    status = "✅" if passed else "❌"
    print(f"{status} {name}: {message}")


async def test_database():
    """Test database operations"""
    print_header("Testing Database")
    
    try:
        from database import get_db
        from database.models import User, VocabularyItem
        from database.services import UserService, VocabularyService
        
        db = get_db()
        db.create_tables()
        print_result("Create tables", True, "Tables created")
        
        # Test user creation
        with db.session_scope() as session:
            user = UserService.create_user(
                session=session,
                username="test_user",
                discord_id="test_discord_123"
            )
            print_result("Create user", True, f"User ID: {user.id}")
            
            # Test vocabulary
            vocab = VocabularyService.add_vocabulary(
                session=session,
                user_id=user.id,
                word="leverage",
                language="en",
                translation="tận dụng"
            )
            print_result("Add vocabulary", True, f"Vocab ID: {vocab.id}")
            
            # Test stats
            stats = UserService.get_user_stats(session, user.id)
            print_result("Get stats", True, f"Vocab count: {stats['total_vocabulary']}")
        
        return True
        
    except Exception as e:
        print_result("Database", False, str(e))
        return False


async def test_validators():
    """Test input validators"""
    print_header("Testing Validators")
    
    try:
        from utils.validators import (
            validate_text_input, validate_language, 
            validate_level, validate_scenario
        )
        from utils.error_handler import ValidationError
        
        # Valid inputs
        assert validate_text_input("Hello world", "test") == "Hello world"
        print_result("validate_text_input", True, "Valid text accepted")
        
        assert validate_language("en") == "en"
        print_result("validate_language", True, "Valid language accepted")
        
        assert validate_level("B1") == "B1"
        print_result("validate_level", True, "Valid level accepted")
        
        assert validate_scenario("job_interview") == "job_interview"
        print_result("validate_scenario", True, "Valid scenario accepted")
        
        # Invalid inputs
        try:
            validate_language("invalid")
            print_result("Invalid language rejection", False, "Should have raised")
        except ValidationError:
            print_result("Invalid language rejection", True, "Correctly rejected")
        
        return True
        
    except Exception as e:
        print_result("Validators", False, str(e))
        return False


async def test_rate_limiter():
    """Test rate limiter"""
    print_header("Testing Rate Limiter")
    
    try:
        from utils.rate_limiter import RateLimiter, RateLimitConfig
        
        config = RateLimitConfig(requests_per_minute=3)
        limiter = RateLimiter(config)
        
        # First 3 requests should pass
        for i in range(3):
            allowed, _ = await limiter.check_rate_limit("test_user")
            await limiter.record_request("test_user")
            assert allowed, f"Request {i+1} should be allowed"
        print_result("Allow within limit", True, "3 requests allowed")
        
        # 4th request should be blocked
        allowed, retry_after = await limiter.check_rate_limit("test_user")
        assert not allowed, "4th request should be blocked"
        print_result("Block over limit", True, f"Blocked, retry after {retry_after}s")
        
        return True
        
    except Exception as e:
        print_result("Rate Limiter", False, str(e))
        return False


async def test_session_manager():
    """Test session manager"""
    print_header("Testing Session Manager")
    
    try:
        from utils.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create session
        session = manager.create_session(
            user_id="test_user",
            session_type="conversation",
            data={"scenario": "interview"},
            timeout_minutes=30
        )
        print_result("Create session", True, f"Type: {session.session_type}")
        
        # Get session
        retrieved = manager.get_session("test_user")
        assert retrieved is not None
        print_result("Get session", True, "Session retrieved")
        
        # Update data
        manager.update_session_data("test_user", "step", 2)
        session = manager.get_session("test_user")
        assert session.data["step"] == 2
        print_result("Update session", True, "Data updated")
        
        # End session
        manager.end_session("test_user")
        assert not manager.has_session("test_user")
        print_result("End session", True, "Session ended")
        
        return True
        
    except Exception as e:
        print_result("Session Manager", False, str(e))
        return False


async def test_cache():
    """Test caching layer"""
    print_header("Testing Cache")
    
    try:
        from utils.cache import get_cache_manager
        
        cache = get_cache_manager()
        
        # Set value
        await cache.set("test_key", {"data": "test_value"}, ttl_seconds=60)
        print_result("Set cache", True, "Value cached")
        
        # Get value
        value = await cache.get("test_key")
        assert value == {"data": "test_value"}
        print_result("Get cache", True, f"Value: {value}")
        
        # Delete value
        await cache.delete("test_key")
        value = await cache.get("test_key")
        assert value is None
        print_result("Delete cache", True, "Value deleted")
        
        return True
        
    except Exception as e:
        print_result("Cache", False, str(e))
        return False


async def test_error_handling():
    """Test error handling"""
    print_header("Testing Error Handling")
    
    try:
        from utils.error_handler import (
            PolyBizError, AIAPIError, RateLimitError,
            format_error_for_user
        )
        
        # Custom errors
        error = AIAPIError("Connection failed", "OpenAI")
        assert "OpenAI" in error.user_message
        print_result("AIAPIError", True, "User message contains provider")
        
        error = RateLimitError(60)
        assert "60" in error.user_message
        print_result("RateLimitError", True, "User message contains retry time")
        
        # Format for user
        msg = format_error_for_user(Exception("Rate limit exceeded"))
        assert "đợi" in msg.lower() or "bận" in msg.lower()
        print_result("format_error_for_user", True, "Friendly message generated")
        
        return True
        
    except Exception as e:
        print_result("Error Handling", False, str(e))
        return False


async def test_health_check():
    """Test health check"""
    print_header("Testing Health Check")
    
    try:
        from utils.health_check import run_health_checks
        
        result = run_health_checks()
        
        print(f"  Total checks: {result['summary']['total']}")
        print(f"  Passed: {result['summary']['passed']}")
        print(f"  Failed: {result['summary']['failed']}")
        
        for check in result['checks']:
            status = "✅" if check['healthy'] else "⚠️"
            print(f"  {status} {check['name']}: {check['message']}")
        
        # At least disk and memory should pass
        assert result['summary']['passed'] >= 2
        print_result("Health check", True, "Core checks working")
        
        return True
        
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  🧪 PolyBiz AI - Local Test Suite")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Database", await test_database()))
    results.append(("Validators", await test_validators()))
    results.append(("Rate Limiter", await test_rate_limiter()))
    results.append(("Session Manager", await test_session_manager()))
    results.append(("Cache", await test_cache()))
    results.append(("Error Handling", await test_error_handling()))
    results.append(("Health Check", await test_health_check()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{len(results)} passed")
    
    if failed == 0:
        print("\n  🎉 All tests passed! Ready for deployment.")
    else:
        print(f"\n  ⚠️ {failed} test(s) failed. Please fix before deploying.")
    
    # Cleanup test database
    try:
        if os.path.exists("test_polybiz.db"):
            os.remove("test_polybiz.db")
            print("\n  🧹 Cleaned up test database")
    except PermissionError:
        print("\n  ⚠️ Could not delete test database (in use). Delete manually if needed.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
