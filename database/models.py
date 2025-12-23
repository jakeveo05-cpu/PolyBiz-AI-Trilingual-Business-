"""
Database Models for PolyBiz AI
SQLAlchemy ORM models for user tracking, progress, and analytics
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User profile and settings"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    # Platform identifiers
    discord_id = Column(String(50), unique=True, nullable=True)
    telegram_id = Column(String(50), unique=True, nullable=True)
    
    # Profile
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    
    # Learning preferences
    native_language = Column(String(10), default="vi")  # vi, en, zh
    target_languages = Column(JSON, default=list)  # ["en", "zh"]
    current_level = Column(JSON, default=dict)  # {"en": "B1", "zh": "A2"}
    learning_goals = Column(JSON, default=list)  # ["job_interview", "email_writing"]
    
    # Settings
    daily_goal_minutes = Column(Integer, default=15)
    reminder_time = Column(String(10), nullable=True)  # "09:00"
    timezone = Column(String(50), default="Asia/Ho_Chi_Minh")
    
    # Anki preferences
    anki_sync_enabled = Column(Boolean, default=False)
    anki_deck_prefix = Column(String(100), default="PolyBiz AI")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    progress = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    vocabulary = relationship("VocabularyItem", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} ({self.id})>"


class LearningProgress(Base):
    """Track user's learning progress"""
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Progress metrics
    language = Column(String(10), nullable=False)  # en, zh, vi
    skill = Column(String(50), nullable=False)  # writing, speaking, listening, reading
    
    # Scores
    current_level = Column(String(10))  # A1-C2
    accuracy_score = Column(Float, default=0.0)  # 0-100
    fluency_score = Column(Float, default=0.0)
    vocabulary_size = Column(Integer, default=0)
    
    # Activity
    total_sessions = Column(Integer, default=0)
    total_minutes = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_practice_date = Column(DateTime)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    
    def __repr__(self):
        return f"<Progress {self.language}/{self.skill} - Level {self.current_level}>"


class Conversation(Base):
    """Store conversation practice sessions"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session info
    language = Column(String(10), nullable=False)
    scenario = Column(String(50), nullable=False)  # job_interview, negotiation, etc.
    difficulty = Column(String(20), default="intermediate")
    
    # Content
    messages = Column(JSON, default=list)  # [{"role": "user", "content": "...", "timestamp": "..."}]
    
    # Evaluation
    duration_minutes = Column(Integer)
    exchange_count = Column(Integer, default=0)
    ai_feedback = Column(Text, nullable=True)
    
    # Scores
    grammar_score = Column(Float, nullable=True)
    vocabulary_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.scenario} - {self.language}>"


class VocabularyItem(Base):
    """Track vocabulary learning"""
    __tablename__ = "vocabulary_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Word info
    word = Column(String(200), nullable=False)
    language = Column(String(10), nullable=False)
    translation = Column(String(500))
    definition = Column(Text)
    example = Column(Text)
    
    # Learning data
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    mastery_level = Column(Integer, default=0)  # 0-5 (SRS levels)
    
    # Spaced repetition
    next_review_date = Column(DateTime)
    last_reviewed = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)  # Anki algorithm
    interval_days = Column(Integer, default=1)
    
    # Source
    source = Column(String(100))  # lesson, conversation, manual
    tags = Column(JSON, default=list)
    
    # Anki sync
    anki_note_id = Column(String(50), nullable=True)
    synced_to_anki = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="vocabulary")
    
    def __repr__(self):
        return f"<Vocab {self.word} ({self.language})>"


class WritingSubmission(Base):
    """Store writing submissions and feedback"""
    __tablename__ = "writing_submissions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Submission
    language = Column(String(10), nullable=False)
    writing_type = Column(String(50))  # email, report, linkedin, etc.
    original_text = Column(Text, nullable=False)
    
    # Feedback
    corrected_text = Column(Text)
    ai_feedback = Column(Text)
    
    # Scores
    grammar_score = Column(Float)
    vocabulary_score = Column(Float)
    structure_score = Column(Float)
    tone_score = Column(Float)
    overall_score = Column(Float)
    
    # Rubric used
    rubric = Column(String(50))  # IELTS, TOEFL, HSK, Business
    
    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Writing {self.writing_type} - Score {self.overall_score}>"


class Achievement(Base):
    """User achievements and badges"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Achievement info
    achievement_type = Column(String(50), nullable=False)  # streak, vocabulary, conversations
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Progress
    current_value = Column(Integer, default=0)
    target_value = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)
    
    # Metadata
    earned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    
    def __repr__(self):
        return f"<Achievement {self.achievement_name} - {self.current_value}/{self.target_value}>"


class DailyChallenge(Base):
    """Daily challenges for users"""
    __tablename__ = "daily_challenges"
    
    id = Column(Integer, primary_key=True)
    
    # Challenge info
    date = Column(DateTime, nullable=False, unique=True)
    language = Column(String(10), nullable=False)
    challenge_type = Column(String(50))  # vocabulary, phrase, quiz, etc.
    
    # Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Challenge {self.date.date()} - {self.title}>"


class ChallengeCompletion(Base):
    """Track user completion of daily challenges"""
    __tablename__ = "challenge_completions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id"), nullable=False)
    
    # Completion
    user_answer = Column(Text)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    
    # Metadata
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Completion User {self.user_id} - Challenge {self.challenge_id}>"


class AnkiDeck(Base):
    """Track generated Anki decks"""
    __tablename__ = "anki_decks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Deck info
    deck_name = Column(String(200), nullable=False)
    language = Column(String(10), nullable=False)
    template_type = Column(String(50))  # vocabulary, phrases, etc.
    
    # Content
    card_count = Column(Integer, default=0)
    source = Column(String(100))  # lesson, conversation, manual
    
    # Files
    apkg_path = Column(String(500), nullable=True)
    
    # Sync status
    synced_to_anki = Column(Boolean, default=False)
    anki_deck_id = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnkiDeck {self.deck_name} - {self.card_count} cards>"
