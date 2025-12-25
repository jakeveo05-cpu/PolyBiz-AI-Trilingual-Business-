"""
Unit Tests for Session Manager
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.session_manager import Session, SessionManager, get_session_manager


class TestSession:
    """Tests for Session dataclass"""
    
    def test_session_creation(self):
        session = Session(
            user_id="user1",
            session_type="conversation",
            data={"partner": "mock"},
            timeout_minutes=30
        )
        
        assert session.user_id == "user1"
        assert session.session_type == "conversation"
        assert session.data["partner"] == "mock"
    
    def test_session_not_expired(self):
        session = Session(
            user_id="user1",
            session_type="test",
            data={},
            timeout_minutes=30
        )
        
        assert session.is_expired() is False
    
    def test_session_expired(self):
        session = Session(
            user_id="user1",
            session_type="test",
            data={},
            timeout_minutes=1  # 1 minute timeout
        )
        # Manually set last_activity to past
        session.last_activity = datetime.utcnow() - timedelta(minutes=5)
        
        assert session.is_expired() is True
    
    def test_session_touch(self):
        session = Session(
            user_id="user1",
            session_type="test",
            data={},
            timeout_minutes=30
        )
        old_activity = session.last_activity
        
        # Small delay
        import time
        time.sleep(0.01)
        
        session.touch()
        assert session.last_activity >= old_activity


class TestSessionManager:
    """Tests for SessionManager"""
    
    def test_create_session(self, session_manager):
        session = session_manager.create_session(
            user_id="user1",
            session_type="conversation",
            data={"scenario": "interview"},
            timeout_minutes=30
        )
        
        assert session is not None
        assert session.user_id == "user1"
        assert session.session_type == "conversation"
    
    def test_get_session(self, session_manager):
        session_manager.create_session(
            user_id="user2",
            session_type="review",
            data={},
            timeout_minutes=15
        )
        
        retrieved = session_manager.get_session("user2")
        assert retrieved is not None
        assert retrieved.session_type == "review"
    
    def test_get_nonexistent_session(self, session_manager):
        retrieved = session_manager.get_session("nonexistent")
        assert retrieved is None
    
    def test_has_session(self, session_manager):
        assert session_manager.has_session("user3") is False
        
        session_manager.create_session(
            user_id="user3",
            session_type="test",
            data={},
            timeout_minutes=10
        )
        
        assert session_manager.has_session("user3") is True
    
    def test_end_session(self, session_manager):
        session_manager.create_session(
            user_id="user4",
            session_type="test",
            data={},
            timeout_minutes=10
        )
        
        assert session_manager.has_session("user4") is True
        
        session_manager.end_session("user4")
        
        assert session_manager.has_session("user4") is False
    
    def test_update_session_data(self, session_manager):
        session_manager.create_session(
            user_id="user5",
            session_type="conversation",
            data={"step": 1},
            timeout_minutes=10
        )
        
        session_manager.update_session_data("user5", "step", 2)
        session_manager.update_session_data("user5", "new_key", "value")
        
        session = session_manager.get_session("user5")
        assert session.data["step"] == 2
        assert session.data["new_key"] == "value"
    
    def test_get_expired_session_returns_none(self, session_manager):
        # Create session with short timeout
        session = Session(
            user_id="user6",
            session_type="test",
            data={},
            timeout_minutes=1
        )
        # Manually expire it
        session.last_activity = datetime.utcnow() - timedelta(minutes=5)
        session_manager._sessions["user6"] = session
        
        # Should return None for expired session
        retrieved = session_manager.get_session("user6")
        assert retrieved is None
    
    def test_cleanup_expired_sessions(self, session_manager):
        # Create expired session
        expired_session = Session(
            user_id="expired_user",
            session_type="test",
            data={},
            timeout_minutes=1
        )
        expired_session.last_activity = datetime.utcnow() - timedelta(minutes=5)
        session_manager._sessions["expired_user"] = expired_session
        
        # Create valid session
        session_manager.create_session(
            user_id="valid_user",
            session_type="test",
            data={},
            timeout_minutes=30
        )
        
        # Get stats before cleanup
        stats = session_manager.get_stats()
        assert stats["total_sessions"] == 2
        
        # Access expired session (triggers cleanup)
        session_manager.get_session("expired_user")
        
        assert "expired_user" not in session_manager._sessions
        assert "valid_user" in session_manager._sessions
    
    def test_get_stats(self, session_manager):
        session_manager.create_session("u1", "test", {}, 10)
        session_manager.create_session("u2", "test", {}, 10)
        session_manager.create_session("u3", "conversation", {}, 10)
        
        stats = session_manager.get_stats()
        assert stats["total_sessions"] == 3
        assert stats["sessions_by_type"]["test"] == 2
        assert stats["sessions_by_type"]["conversation"] == 1


class TestGetSessionManager:
    """Tests for get_session_manager singleton"""
    
    def test_returns_same_instance(self):
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        
        assert manager1 is manager2
