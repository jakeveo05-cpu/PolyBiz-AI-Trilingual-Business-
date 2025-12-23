"""
Database connection and session management
"""
import os
import threading
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from contextlib import contextmanager
from .models import Base

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///polybiz.db")


class Database:
    """Database manager with SQLite concurrency handling"""
    
    _lock = threading.Lock()
    
    def __init__(self, url: str = DATABASE_URL):
        self.url = url
        self.is_sqlite = "sqlite" in url
        
        # SQLite-specific settings for better concurrency
        connect_args = {}
        if self.is_sqlite:
            connect_args = {
                "check_same_thread": False,
                "timeout": 30  # Wait up to 30 seconds for lock
            }
        
        self.engine = create_engine(
            url,
            echo=False,
            connect_args=connect_args,
            pool_pre_ping=True,  # Check connection health
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        # Enable WAL mode for SQLite (better concurrency)
        if self.is_sqlite:
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
                cursor.close()
        
        # Use scoped_session for thread safety
        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        self.SessionLocal = scoped_session(session_factory)
    
    def create_tables(self):
        """Create all tables"""
        with self._lock:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        with self._lock:
            Base.metadata.drop_all(bind=self.engine)
            print("⚠️ Database tables dropped")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            self.SessionLocal.remove()  # Important for scoped_session


# Global database instance
_db = None
_db_lock = threading.Lock()

def get_db() -> Database:
    """Get or create global database instance (thread-safe)"""
    global _db
    if _db is None:
        with _db_lock:
            if _db is None:  # Double-check locking
                _db = Database()
    return _db


def reset_db():
    """Reset database instance (for testing)"""
    global _db
    with _db_lock:
        if _db is not None:
            _db.SessionLocal.remove()
        _db = None


# Initialize database on import
def init_db():
    """Initialize database (create tables if they don't exist)"""
    db = get_db()
    db.create_tables()


if __name__ == "__main__":
    # Run this to initialize database
    init_db()
    print("Database initialized successfully!")
