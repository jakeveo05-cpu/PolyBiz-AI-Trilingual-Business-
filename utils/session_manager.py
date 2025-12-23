"""
Session Manager - Handle conversation sessions with auto-cleanup
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger('polybiz.session')


@dataclass
class Session:
    """User session data"""
    user_id: str
    session_type: str  # 'conversation', 'review', 'vocab'
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    timeout_minutes: int = 30
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() - self.last_activity > timedelta(minutes=self.timeout_minutes)
    
    def touch(self):
        """Update last activity time"""
        self.last_activity = datetime.utcnow()


class SessionManager:
    """
    Manage user sessions with automatic cleanup
    Prevents memory leaks from abandoned sessions
    """
    
    def __init__(self, cleanup_interval_minutes: int = 5):
        self._sessions: Dict[str, Session] = {}
        self._cleanup_interval = cleanup_interval_minutes * 60
        self._cleanup_task: Optional[asyncio.Task] = None
        self._on_session_expire: Optional[Callable] = None
    
    def set_expire_callback(self, callback: Callable):
        """Set callback to run when session expires"""
        self._on_session_expire = callback
    
    def create_session(
        self,
        user_id: str,
        session_type: str,
        data: Dict[str, Any] = None,
        timeout_minutes: int = 30
    ) -> Session:
        """Create a new session for user"""
        # End existing session if any
        if user_id in self._sessions:
            self.end_session(user_id)
        
        session = Session(
            user_id=user_id,
            session_type=session_type,
            data=data or {},
            timeout_minutes=timeout_minutes
        )
        self._sessions[user_id] = session
        
        logger.info(f"Session created: user={user_id}, type={session_type}")
        return session
    
    def get_session(self, user_id: str) -> Optional[Session]:
        """Get user's active session"""
        session = self._sessions.get(user_id)
        
        if session:
            if session.is_expired():
                logger.info(f"Session expired: user={user_id}")
                self.end_session(user_id)
                return None
            session.touch()
        
        return session
    
    def has_session(self, user_id: str) -> bool:
        """Check if user has active session"""
        return self.get_session(user_id) is not None
    
    def update_session_data(self, user_id: str, key: str, value: Any):
        """Update session data"""
        session = self.get_session(user_id)
        if session:
            session.data[key] = value
            session.touch()
    
    def end_session(self, user_id: str) -> Optional[Session]:
        """End and remove user's session"""
        session = self._sessions.pop(user_id, None)
        if session:
            logger.info(f"Session ended: user={user_id}, type={session.session_type}")
        return session
    
    async def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        expired_users = [
            user_id for user_id, session in self._sessions.items()
            if session.is_expired()
        ]
        
        for user_id in expired_users:
            session = self._sessions.pop(user_id, None)
            if session and self._on_session_expire:
                try:
                    await self._on_session_expire(user_id, session)
                except Exception as e:
                    logger.error(f"Error in session expire callback: {e}")
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Session cleanup task started")
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Session cleanup task stopped")
    
    async def _cleanup_loop(self):
        """Background loop for cleaning up expired sessions"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        now = datetime.utcnow()
        sessions_by_type = {}
        
        for session in self._sessions.values():
            sessions_by_type[session.session_type] = sessions_by_type.get(session.session_type, 0) + 1
        
        return {
            "total_sessions": len(self._sessions),
            "sessions_by_type": sessions_by_type,
            "oldest_session_minutes": max(
                [(now - s.created_at).total_seconds() / 60 for s in self._sessions.values()],
                default=0
            )
        }


# Global session manager
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
