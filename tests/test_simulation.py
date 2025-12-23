"""
Simulation Tests - Giả lập nhiều user và các tình huống thực tế
Chạy: python -m tests.test_simulation
"""
import asyncio
import random
import time
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def log_test(name: str, passed: bool, error: str = None):
    """Log test result"""
    if passed:
        test_results["passed"] += 1
        print(f"  ✅ {name}")
    else:
        test_results["failed"] += 1
        test_results["errors"].append({"test": name, "error": error})
        print(f"  ❌ {name}: {error}")


@dataclass
class SimulatedUser:
    """Giả lập một user"""
    user_id: str
    username: str
    platform: str  # 'discord' or 'telegram'
    native_language: str = "vi"
    target_languages: List[str] = field(default_factory=lambda: ["en"])
    behavior: str = "normal"  # normal, aggressive, slow, abandoner


class SimulationEngine:
    """Engine để chạy các simulation tests"""
    
    def __init__(self):
        self.users: List[SimulatedUser] = []
        self.errors: List[Dict] = []
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited": 0,
            "timeouts": 0,
            "avg_response_time": 0,
            "response_times": []
        }
    
    def create_users(self, count: int, behaviors: Dict[str, float] = None):
        """Tạo nhiều user với các behavior khác nhau"""
        behaviors = behaviors or {
            "normal": 0.6,
            "aggressive": 0.2,  # Spam requests
            "slow": 0.1,        # Slow responses
            "abandoner": 0.1    # Bỏ giữa chừng
        }
        
        for i in range(count):
            behavior = random.choices(
                list(behaviors.keys()),
                weights=list(behaviors.values())
            )[0]
            
            user = SimulatedUser(
                user_id=f"sim_user_{i}_{int(time.time())}",
                username=f"TestUser{i}",
                platform=random.choice(["discord", "telegram"]),
                behavior=behavior
            )
            self.users.append(user)
        
        return self.users
    
    def record_request(self, success: bool, response_time: float, error: str = None):
        """Ghi nhận kết quả request"""
        self.metrics["total_requests"] += 1
        self.metrics["response_times"].append(response_time)
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            if error:
                if "rate limit" in error.lower():
                    self.metrics["rate_limited"] += 1
                elif "timeout" in error.lower():
                    self.metrics["timeouts"] += 1
                self.errors.append({"error": error, "time": datetime.now()})
    
    def get_report(self) -> Dict:
        """Tạo báo cáo kết quả"""
        times = self.metrics["response_times"]
        return {
            "total_users": len(self.users),
            "total_requests": self.metrics["total_requests"],
            "success_rate": self.metrics["successful_requests"] / max(self.metrics["total_requests"], 1) * 100,
            "rate_limited": self.metrics["rate_limited"],
            "timeouts": self.metrics["timeouts"],
            "avg_response_time": sum(times) / len(times) if times else 0,
            "max_response_time": max(times) if times else 0,
            "errors": self.errors[:10]  # First 10 errors
        }


# ============ TEST CASES ============

async def test_rate_limiter():
    """Test 1: Rate limiter với nhiều requests liên tục"""
    print("\n🧪 Test 1: Rate Limiter")
    
    from utils.rate_limiter import RateLimiter, RateLimitConfig
    
    # Config: 5 requests/minute để test nhanh
    config = RateLimitConfig(requests_per_minute=5, requests_per_hour=100)
    limiter = RateLimiter(config)
    
    user_id = "test_user_rate"
    allowed_count = 0
    blocked_count = 0
    
    # Gửi 10 requests liên tục
    for i in range(10):
        allowed, retry_after = await limiter.check_rate_limit(user_id)
        if allowed:
            await limiter.record_request(user_id)
            allowed_count += 1
        else:
            blocked_count += 1
    
    # Expect: 5 allowed, 5 blocked
    log_test(
        "Rate limiter blocks after limit",
        allowed_count == 5 and blocked_count == 5,
        f"Expected 5 allowed, 5 blocked. Got {allowed_count} allowed, {blocked_count} blocked"
    )
    
    # Test stats
    stats = limiter.get_user_stats(user_id)
    log_test(
        "Rate limiter tracks stats correctly",
        stats["requests_this_minute"] == 5,
        f"Expected 5 requests, got {stats['requests_this_minute']}"
    )


async def test_session_manager():
    """Test 2: Session manager với timeout và cleanup"""
    print("\n🧪 Test 2: Session Manager")
    
    from utils.session_manager import SessionManager
    
    manager = SessionManager(cleanup_interval_minutes=1)
    
    # Test 1: Create session
    session = manager.create_session(
        user_id="user1",
        session_type="conversation",
        data={"scenario": "interview"},
        timeout_minutes=1  # 1 minute timeout for testing
    )
    log_test("Create session", session is not None)
    
    # Test 2: Get session
    retrieved = manager.get_session("user1")
    log_test("Get session", retrieved is not None and retrieved.data["scenario"] == "interview")
    
    # Test 3: Session not found
    not_found = manager.get_session("nonexistent")
    log_test("Non-existent session returns None", not_found is None)
    
    # Test 4: End session
    ended = manager.end_session("user1")
    log_test("End session", ended is not None)
    
    after_end = manager.get_session("user1")
    log_test("Session removed after end", after_end is None)
    
    # Test 5: Multiple sessions
    for i in range(5):
        manager.create_session(f"multi_user_{i}", "test", timeout_minutes=1)
    
    stats = manager.get_stats()
    log_test("Multiple sessions tracked", stats["total_sessions"] == 5)


async def test_validators():
    """Test 3: Input validators"""
    print("\n🧪 Test 3: Input Validators")
    
    from utils.validators import (
        validate_text_input, validate_language, validate_level,
        sanitize_text, detect_language, check_content_safety,
        ValidationError
    )
    
    # Test 1: Valid text
    try:
        result = validate_text_input("Hello world, this is a test.", "text", min_length=5)
        log_test("Valid text passes", result == "Hello world, this is a test.")
    except Exception as e:
        log_test("Valid text passes", False, str(e))
    
    # Test 2: Text too short
    try:
        validate_text_input("Hi", "text", min_length=5)
        log_test("Short text rejected", False, "Should have raised ValidationError")
    except ValidationError:
        log_test("Short text rejected", True)
    except Exception as e:
        log_test("Short text rejected", False, str(e))
    
    # Test 3: Text too long
    try:
        validate_text_input("x" * 10001, "text", max_length=10000)
        log_test("Long text rejected", False, "Should have raised ValidationError")
    except ValidationError:
        log_test("Long text rejected", True)
    except Exception as e:
        log_test("Long text rejected", False, str(e))
    
    # Test 4: Language validation
    try:
        result = validate_language("en")
        log_test("Valid language passes", result == "en")
    except Exception as e:
        log_test("Valid language passes", False, str(e))
    
    try:
        validate_language("invalid")
        log_test("Invalid language rejected", False)
    except ValidationError:
        log_test("Invalid language rejected", True)
    
    # Test 5: Sanitize text
    dirty = "Hello\x00World\x1f"
    clean = sanitize_text(dirty)
    log_test("Sanitize removes control chars", "\x00" not in clean and "\x1f" not in clean)
    
    # Test 6: Language detection
    log_test("Detect English", detect_language("Hello world") == "en")
    log_test("Detect Vietnamese", detect_language("Xin chào các bạn") == "vi")
    log_test("Detect Chinese", detect_language("你好世界") == "zh")
    
    # Test 7: Content safety
    safe, _ = check_content_safety("Normal business text")
    log_test("Safe content passes", safe)
    
    unsafe, reason = check_content_safety("<script>alert('xss')</script>")
    log_test("Unsafe content blocked", not unsafe)


async def test_retry_logic():
    """Test 4: Retry logic với failures"""
    print("\n🧪 Test 4: Retry Logic")
    
    from utils.retry import async_retry, RetryConfig
    
    # Counter for attempts
    attempt_count = 0
    
    @async_retry(RetryConfig(max_retries=3, base_delay=0.1))
    async def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Simulated failure")
        return "success"
    
    # Test: Function succeeds after retries
    attempt_count = 0
    try:
        result = await flaky_function()
        log_test("Retry succeeds after failures", result == "success" and attempt_count == 3)
    except Exception as e:
        log_test("Retry succeeds after failures", False, str(e))
    
    # Test: Function fails after max retries
    @async_retry(RetryConfig(max_retries=2, base_delay=0.1))
    async def always_fails():
        raise ConnectionError("Always fails")
    
    try:
        await always_fails()
        log_test("Max retries then fail", False, "Should have raised exception")
    except ConnectionError:
        log_test("Max retries then fail", True)


async def test_database_operations():
    """Test 5: Database operations với concurrent access"""
    print("\n🧪 Test 5: Database Operations")
    
    import tempfile
    import os as os_module
    from database.database import Database
    from database.services import UserService, VocabularyService, ProgressService
    
    # Use a unique temp database for this test
    tmpdir = tempfile.mkdtemp()
    test_db_path = os_module.path.join(tmpdir, "test_db.db")
    test_db_url = f"sqlite:///{test_db_path}"
    
    db = Database(url=test_db_url)
    db.create_tables()
    
    # Test 1: Create multiple users sequentially
    user_ids = []
    try:
        for i in range(5):
            with db.session_scope() as session:
                user = UserService.create_user(
                    session=session,
                    username=f"TestUser{i}_{int(time.time())}",
                    discord_id=f"discord_{i}_{int(time.time())}"
                )
                user_ids.append(user.id)
        log_test("Create multiple users", len(user_ids) == 5)
    except Exception as e:
        log_test("Create multiple users", False, str(e))
    
    # Test 2: Add vocabulary for user
    try:
        with db.session_scope() as session:
            vocab = VocabularyService.add_vocabulary(
                session=session,
                user_id=user_ids[0],
                word="test_word",
                language="en",
                translation="từ test"
            )
        log_test("Add vocabulary", vocab is not None)
    except Exception as e:
        log_test("Add vocabulary", False, str(e))
    
    # Test 3: Update progress
    try:
        with db.session_scope() as session:
            progress = ProgressService.update_progress(
                session=session,
                user_id=user_ids[0],
                language="en",
                skill="writing",
                session_minutes=10
            )
        log_test("Update progress", progress is not None)
    except Exception as e:
        log_test("Update progress", False, str(e))
    
    # Test 4: Get user stats
    try:
        with db.session_scope() as session:
            stats = UserService.get_user_stats(session, user_ids[0])
        log_test("Get user stats", stats["total_vocabulary"] >= 1)
    except Exception as e:
        log_test("Get user stats", False, str(e))


async def test_concurrent_sessions():
    """Test 6: Nhiều user cùng lúc với sessions"""
    print("\n🧪 Test 6: Concurrent Sessions")
    
    from utils.session_manager import SessionManager
    
    manager = SessionManager()
    num_users = 20
    
    # Create sessions for many users
    async def user_session(user_id: str):
        session = manager.create_session(
            user_id=user_id,
            session_type="conversation",
            data={"start_time": time.time()}
        )
        
        # Simulate some activity
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Update session
        manager.update_session_data(user_id, "messages", random.randint(1, 10))
        
        # Some users abandon (don't end session)
        if random.random() > 0.3:  # 70% end properly
            manager.end_session(user_id)
            return "completed"
        return "abandoned"
    
    # Run concurrent sessions
    tasks = [user_session(f"concurrent_user_{i}") for i in range(num_users)]
    results = await asyncio.gather(*tasks)
    
    completed = results.count("completed")
    abandoned = results.count("abandoned")
    
    log_test(
        f"Concurrent sessions handled ({completed} completed, {abandoned} abandoned)",
        completed + abandoned == num_users
    )
    
    # Check abandoned sessions still exist
    stats = manager.get_stats()
    log_test(
        "Abandoned sessions tracked",
        stats["total_sessions"] == abandoned
    )


async def test_error_handling():
    """Test 7: Error handling và user-friendly messages"""
    print("\n🧪 Test 7: Error Handling")
    
    from utils.error_handler import (
        PolyBizError, AIAPIError, RateLimitError, ValidationError,
        format_error_for_user
    )
    
    # Test custom exceptions
    try:
        raise AIAPIError("API connection failed", "OpenAI")
    except AIAPIError as e:
        log_test("AIAPIError has user message", "API" in e.user_message)
    
    try:
        raise RateLimitError(60)
    except RateLimitError as e:
        log_test("RateLimitError has retry_after", e.retry_after == 60)
    
    try:
        raise ValidationError("Invalid input", "text")
    except ValidationError as e:
        log_test("ValidationError has user message", "không hợp lệ" in e.user_message)
    
    # Test format_error_for_user
    generic_error = Exception("Something went wrong")
    user_msg = format_error_for_user(generic_error)
    log_test("Generic error formatted", "❌" in user_msg or "lỗi" in user_msg.lower())
    
    rate_error = Exception("rate limit exceeded 429")
    user_msg = format_error_for_user(rate_error)
    log_test("Rate limit error formatted", "đợi" in user_msg.lower() or "bận" in user_msg.lower())


async def test_backup_system():
    """Test 8: Backup system"""
    print("\n🧪 Test 8: Backup System")
    
    from utils.backup import DatabaseBackup
    import tempfile
    import os
    
    # Create temp directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        backup_dir = os.path.join(tmpdir, "backups")
        
        # Create a dummy database file
        with open(db_path, "w") as f:
            f.write("test database content")
        
        backup = DatabaseBackup(
            db_path=db_path,
            backup_dir=backup_dir,
            max_backups=3,
            compress=True
        )
        
        # Test 1: Create backup
        backup_path = backup.create_backup()
        log_test("Create backup", backup_path is not None and os.path.exists(backup_path))
        
        # Test 2: List backups
        backups = backup.list_backups()
        log_test("List backups", len(backups) == 1)
        
        # Test 3: Create multiple backups
        for i in range(4):
            backup.create_backup(suffix=f"_test{i}")
            await asyncio.sleep(0.1)  # Small delay for different timestamps
        
        # Should only keep 3 (max_backups)
        backups = backup.list_backups()
        log_test("Backup retention (max 3)", len(backups) <= 3)
        
        # Test 4: Get latest backup
        latest = backup.get_latest_backup()
        log_test("Get latest backup", latest is not None)


async def test_stress_simulation():
    """Test 9: Stress test với nhiều requests"""
    print("\n🧪 Test 9: Stress Simulation")
    
    from utils.rate_limiter import RateLimiter, RateLimitConfig
    from utils.session_manager import SessionManager
    
    engine = SimulationEngine()
    users = engine.create_users(10)
    
    # Shared resources - low limits to trigger rate limiting
    limiter = RateLimiter(RateLimitConfig(
        requests_per_minute=3,  # Very low to ensure blocking
        requests_per_hour=50
    ))
    session_manager = SessionManager()
    
    async def simulate_user_activity(user: SimulatedUser):
        """Simulate one user's activity"""
        for _ in range(5):  # Each user makes 5 requests
            start_time = time.time()
            
            try:
                # Check rate limit
                allowed, retry_after = await limiter.check_rate_limit(user.user_id)
                
                if not allowed:
                    engine.record_request(False, time.time() - start_time, "rate limited")
                    if user.behavior == "aggressive":
                        continue  # Aggressive users keep trying
                    await asyncio.sleep(0.1)
                    continue
                
                await limiter.record_request(user.user_id)
                
                # Simulate different behaviors
                if user.behavior == "slow":
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                elif user.behavior == "aggressive":
                    pass  # No delay
                else:
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                
                # Create/use session
                if not session_manager.has_session(user.user_id):
                    session_manager.create_session(
                        user.user_id, 
                        "test",
                        timeout_minutes=5
                    )
                
                # Abandoners don't end sessions
                if user.behavior != "abandoner" and random.random() > 0.5:
                    session_manager.end_session(user.user_id)
                
                engine.record_request(True, time.time() - start_time)
                
            except Exception as e:
                engine.record_request(False, time.time() - start_time, str(e))
    
    # Run all users concurrently
    tasks = [simulate_user_activity(user) for user in users]
    await asyncio.gather(*tasks)
    
    report = engine.get_report()
    
    log_test(
        f"Stress test completed ({report['total_requests']} requests)",
        report["total_requests"] > 0
    )
    log_test(
        f"Success rate > 50% ({report['success_rate']:.1f}%)",
        report["success_rate"] > 50
    )
    log_test(
        f"Rate limiting working ({report['rate_limited']} blocked)",
        report["rate_limited"] > 0  # Some should be rate limited
    )


async def test_edge_cases():
    """Test 10: Edge cases và boundary conditions"""
    print("\n🧪 Test 10: Edge Cases")
    
    from utils.validators import validate_text_input, ValidationError
    from utils.session_manager import SessionManager
    
    # Test 1: Empty string
    try:
        validate_text_input("", "text")
        log_test("Empty string rejected", False)
    except ValidationError:
        log_test("Empty string rejected", True)
    
    # Test 2: Only whitespace
    try:
        validate_text_input("   \n\t  ", "text")
        log_test("Whitespace-only rejected", False)
    except ValidationError:
        log_test("Whitespace-only rejected", True)
    
    # Test 3: Unicode text
    try:
        result = validate_text_input("Xin chào 你好 🎉", "text", min_length=3)
        log_test("Unicode text accepted", len(result) > 0)
    except Exception as e:
        log_test("Unicode text accepted", False, str(e))
    
    # Test 4: Very long text at boundary
    boundary_text = "x" * 10000
    try:
        result = validate_text_input(boundary_text, "text", max_length=10000)
        log_test("Boundary length accepted", len(result) == 10000)
    except Exception as e:
        log_test("Boundary length accepted", False, str(e))
    
    # Test 5: Session with same user_id overwrites
    manager = SessionManager()
    session1 = manager.create_session("same_user", "type1", {"data": 1})
    session2 = manager.create_session("same_user", "type2", {"data": 2})
    
    current = manager.get_session("same_user")
    log_test(
        "New session overwrites old",
        current.session_type == "type2" and current.data["data"] == 2
    )


# ============ MAIN ============

async def run_all_tests():
    """Chạy tất cả tests"""
    print("=" * 60)
    print("🧪 PolyBiz AI - Simulation Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        await test_rate_limiter()
        await test_session_manager()
        await test_validators()
        await test_retry_logic()
        await test_database_operations()
        await test_concurrent_sessions()
        await test_error_handling()
        await test_backup_system()
        await test_stress_simulation()
        await test_edge_cases()
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        traceback.print_exc()
    
    elapsed = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⏱️ Time: {elapsed:.2f}s")
    
    if test_results["errors"]:
        print("\n❌ Failed Tests:")
        for err in test_results["errors"]:
            print(f"  - {err['test']}: {err['error']}")
    
    print("=" * 60)
    
    return test_results["failed"] == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
