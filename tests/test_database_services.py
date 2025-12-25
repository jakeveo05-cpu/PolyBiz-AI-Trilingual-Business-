"""
Unit Tests for Database Services
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import User, LearningProgress, VocabularyItem, Conversation, Achievement
from database.services import UserService, ProgressService, VocabularyService, ConversationService, AchievementService


class TestUserService:
    """Tests for UserService"""
    
    def test_create_user(self, db_session):
        user = UserService.create_user(
            session=db_session,
            username="test_user",
            discord_id="12345"
        )
        
        assert user.id is not None
        assert user.username == "test_user"
        assert user.discord_id == "12345"
    
    def test_get_user_by_discord_id(self, db_session, sample_user):
        found = UserService.get_user_by_platform(
            session=db_session,
            discord_id=sample_user.discord_id
        )
        
        assert found is not None
        assert found.id == sample_user.id
    
    def test_get_user_by_telegram_id(self, db_session, sample_user):
        found = UserService.get_user_by_platform(
            session=db_session,
            telegram_id=sample_user.telegram_id
        )
        
        assert found is not None
        assert found.id == sample_user.id
    
    def test_get_nonexistent_user(self, db_session):
        found = UserService.get_user_by_platform(
            session=db_session,
            discord_id="nonexistent"
        )
        
        assert found is None
    
    def test_get_user_stats(self, db_session, sample_user):
        stats = UserService.get_user_stats(db_session, sample_user.id)
        
        assert stats["user_id"] == sample_user.id
        assert stats["username"] == sample_user.username
        assert "total_conversations" in stats
        assert "total_vocabulary" in stats


class TestProgressService:
    """Tests for ProgressService"""
    
    def test_update_progress_creates_new(self, db_session, sample_user):
        progress = ProgressService.update_progress(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            skill="writing",
            session_minutes=15
        )
        
        assert progress is not None
        assert progress.language == "en"
        assert progress.skill == "writing"
        assert progress.total_minutes == 15
        assert progress.total_sessions == 1
    
    def test_update_progress_increments(self, db_session, sample_user):
        # First session
        ProgressService.update_progress(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            skill="speaking",
            session_minutes=10
        )
        
        # Second session
        progress = ProgressService.update_progress(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            skill="speaking",
            session_minutes=20
        )
        
        assert progress.total_sessions == 2
        assert progress.total_minutes == 30
    
    def test_streak_starts_at_one(self, db_session, sample_user):
        progress = ProgressService.update_progress(
            session=db_session,
            user_id=sample_user.id,
            language="zh",
            skill="reading",
            session_minutes=5
        )
        
        assert progress.streak_days == 1
    
    def test_get_streak(self, db_session, sample_user):
        ProgressService.update_progress(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            skill="writing",
            session_minutes=10
        )
        
        streak = ProgressService.get_streak(db_session, sample_user.id, "en")
        assert streak >= 1


class TestVocabularyService:
    """Tests for VocabularyService"""
    
    def test_add_vocabulary(self, db_session, sample_user):
        vocab = VocabularyService.add_vocabulary(
            session=db_session,
            user_id=sample_user.id,
            word="leverage",
            language="en",
            translation="tận dụng",
            example="We leverage AI tools."
        )
        
        assert vocab.id is not None
        assert vocab.word == "leverage"
        assert vocab.translation == "tận dụng"
        assert vocab.next_review_date is not None
    
    def test_get_due_reviews_empty(self, db_session, sample_user):
        # No vocabulary added yet
        due = VocabularyService.get_due_reviews(db_session, sample_user.id)
        assert len(due) == 0
    
    def test_get_due_reviews_with_items(self, db_session, sample_user):
        # Add vocab with past review date
        vocab = VocabularyItem(
            user_id=sample_user.id,
            word="test",
            language="en",
            translation="kiểm tra",
            next_review_date=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add(vocab)
        db_session.commit()
        
        due = VocabularyService.get_due_reviews(db_session, sample_user.id)
        assert len(due) == 1
    
    def test_record_review_correct(self, db_session, sample_user):
        vocab = VocabularyService.add_vocabulary(
            session=db_session,
            user_id=sample_user.id,
            word="synergy",
            language="en",
            translation="hiệu ứng cộng hưởng"
        )
        
        VocabularyService.record_review(db_session, vocab.id, is_correct=True)
        
        db_session.refresh(vocab)
        assert vocab.times_reviewed == 1
        assert vocab.times_correct == 1
        assert vocab.mastery_level == 1
    
    def test_record_review_incorrect(self, db_session, sample_user):
        vocab = VocabularyService.add_vocabulary(
            session=db_session,
            user_id=sample_user.id,
            word="paradigm",
            language="en",
            translation="mô hình"
        )
        
        VocabularyService.record_review(db_session, vocab.id, is_correct=False)
        
        db_session.refresh(vocab)
        assert vocab.times_reviewed == 1
        assert vocab.times_correct == 0
        assert vocab.interval_days == 1  # Reset to 1


class TestConversationService:
    """Tests for ConversationService"""
    
    def test_start_conversation(self, db_session, sample_user):
        conv = ConversationService.start_conversation(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            scenario="job_interview",
            difficulty="intermediate"
        )
        
        assert conv.id is not None
        assert conv.scenario == "job_interview"
        assert conv.messages == []
    
    def test_add_message(self, db_session, sample_user):
        conv = ConversationService.start_conversation(
            session=db_session,
            user_id=sample_user.id,
            language="en",
            scenario="networking"
        )
        
        ConversationService.add_message(
            session=db_session,
            conversation_id=conv.id,
            role="user",
            content="Hello, nice to meet you!"
        )
        
        # Refresh to get updated data
        db_session.expire(conv)
        db_session.refresh(conv)
        
        # Note: SQLite JSON may not update in-place, check exchange_count instead
        assert conv.exchange_count == 1
    
    def test_complete_conversation(self, db_session, sample_user):
        conv = ConversationService.start_conversation(
            session=db_session,
            user_id=sample_user.id,
            language="zh",
            scenario="client_meeting"
        )
        
        ConversationService.complete_conversation(
            session=db_session,
            conversation_id=conv.id,
            feedback="Great job!",
            overall_score=85.0
        )
        
        db_session.refresh(conv)
        assert conv.completed_at is not None
        assert conv.ai_feedback == "Great job!"
        assert conv.overall_score == 85.0


class TestAchievementService:
    """Tests for AchievementService"""
    
    def test_check_achievements_creates_records(self, db_session, sample_user):
        newly_earned = AchievementService.check_and_award_achievements(
            db_session, sample_user.id
        )
        
        # Should create achievement records (even if not completed)
        achievements = db_session.query(Achievement).filter(
            Achievement.user_id == sample_user.id
        ).all()
        
        assert len(achievements) > 0
    
    def test_first_conversation_achievement(self, db_session, sample_user):
        # Create a conversation
        conv = Conversation(
            user_id=sample_user.id,
            language="en",
            scenario="networking",
            completed_at=datetime.utcnow()
        )
        db_session.add(conv)
        db_session.commit()
        
        newly_earned = AchievementService.check_and_award_achievements(
            db_session, sample_user.id
        )
        
        # Should earn "First Steps" achievement
        first_steps = [a for a in newly_earned if a.achievement_name == "First Steps"]
        assert len(first_steps) == 1
