"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .models import Base

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///polybiz.db")


class Database:
    """Database manager"""
    
    def __init__(self, url: str = DATABASE_URL):
        self.engine = create_engine(
            url,
            echo=False,  # Set to True for SQL logging
            connect_args={"check_same_thread": False} if "sqlite" in url else {}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
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


# Global database instance
_db = None

def get_db() -> Database:
    """Get or create global database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db


# Initialize database on import
def init_db():
    """Initialize database (create tables if they don't exist)"""
    db = get_db()
    db.create_tables()


if __name__ == "__main__":
    # Run this to initialize database
    init_db()
    print("Database initialized successfully!")
