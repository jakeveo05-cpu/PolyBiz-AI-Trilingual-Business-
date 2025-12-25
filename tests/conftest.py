"""
Pytest Configuration and Fixtures
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ============ ASYNC SUPPORT ============
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============ DATABASE FIXTURES ============
@pytest.fixture
def test_db():
    """Create in-memory test database"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from database.models import Base
    
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = scoped_session(sessionmaker(bind=engine))
    
    yield Session
    
    Session.remove()
    engine.dispose()


@pytest.fixture
def db_session(test_db):
    """Get a database session for testing"""
    session = test_db()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    from database.models import User
    
    user = User(
        username="test_user",
        discord_id="123456789",
        telegram_id="987654321",
        native_language="vi",
        target_languages=["en", "zh"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============ MOCK FIXTURES ============
@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API"""
    with patch("anthropic.Anthropic") as mock:
        instance = mock.return_value
        instance.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Mock AI response")]
        )
        yield instance


@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    with patch("openai.OpenAI") as mock:
        instance = mock.return_value
        instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mock AI response"))]
        )
        yield instance


# ============ RATE LIMITER FIXTURES ============
@pytest.fixture
def rate_limiter():
    """Create fresh rate limiter for testing"""
    from utils.rate_limiter import RateLimiter, RateLimitConfig
    
    config = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        requests_per_day=100
    )
    return RateLimiter(config)


# ============ SESSION MANAGER FIXTURES ============
@pytest.fixture
def session_manager():
    """Create fresh session manager for testing"""
    from utils.session_manager import SessionManager
    return SessionManager()
