"""
Database services - Business logic for database operations
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .models import (
    User, LearningProgress, Conversation, VocabularyItem,
    WritingSubmission, Achievement, DailyChallenge, ChallengeCompletion, AnkiDeck
)


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(
        session: Session,
        username: str,
        discord_id: str = None,
        telegram_id: str = None,
        **kwargs
    ) -> User:
        """Create a new user"""
        user = User(
            username=username,
            discord_id=discord_id,
            telegram_id=telegram_id,
            **kwargs
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_platform(
        session: Session,
        discord_id: str = None,
        telegram_id: str = None
    ) -> Optional[User]:
        """Get user by platform ID"""
        if discord_id:
            return session.query(User).filter(User.discord_id == discord_id).first()
        elif telegram_id:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
        return None
    
    @staticmethod
    def update_last_active(session: Session, user_id: int):
        """Update user's last active timestamp"""
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.last_active = datetime.utcnow()
            session.commit()
    
    @staticmethod
    def get_user_stats(session: Session, user_id: int) -> Dict:
        """Get comprehensive user statistics"""
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Calculate stats
        total_conversations = session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).count()
        
        total_vocabulary = session.query(VocabularyItem).filter(
            VocabularyItem.user_id == user_id
        ).count()
        
        total_writing = session.query(WritingSubmission).filter(
            WritingSubmission.user_id == user_id
        ).count()
        
        # Get progress for each language
        progress = session.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()
        
        return {
            "user_id": user_id,
            "username": user.username,
            "total_conversations": total_conversations,
            "total_vocabulary": total_vocabulary,
            "total_writing_submissions": total_writing,
            "progress_by_language": {
                p.language: {
                    "level": p.current_level,
                    "sessions": p.total_sessions,
                    "minutes": p.total_minutes,
                    "streak": p.streak_days
                }
                for p in progress
            }
        }


class ProgressService:
    """Service for learning progress tracking"""
    
    @staticmethod
    def update_progress(
        session: Session,
        user_id: int,
        language: str,
        skill: str,
        session_minutes: int = 0,
        **scores
    ):
        """Update user's learning progress"""
        progress = session.query(LearningProgress).filter(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.language == language,
                LearningProgress.skill == skill
            )
        ).first()
        
        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                language=language,
                skill=skill,
                total_sessions=0,
                total_minutes=0,
                streak_days=0
            )
            session.add(progress)
        
        # Update metrics (ensure not None)
        progress.total_sessions = (progress.total_sessions or 0) + 1
        progress.total_minutes = (progress.total_minutes or 0) + session_minutes
        
        # Update scores if provided
        for key, value in scores.items():
            if hasattr(progress, key):
                setattr(progress, key, value)
        
        # Update streak
        today = datetime.utcnow().date()
        if progress.last_practice_date:
            last_date = progress.last_practice_date.date()
            if last_date == today:
                pass  # Same day, no change
            elif last_date == today - timedelta(days=1):
                progress.streak_days += 1  # Consecutive day
            else:
                progress.streak_days = 1  # Streak broken
        else:
            progress.streak_days = 1
        
        progress.last_practice_date = datetime.utcnow()
        
        session.commit()
        return progress
    
    @staticmethod
    def get_streak(session: Session, user_id: int, language: str) -> int:
        """Get current streak for a language"""
        progress = session.query(LearningProgress).filter(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.language == language
            )
        ).first()
        
        return progress.streak_days if progress else 0


class VocabularyService:
    """Service for vocabulary management"""
    
    @staticmethod
    def add_vocabulary(
        session: Session,
        user_id: int,
        word: str,
        language: str,
        translation: str,
        **kwargs
    ) -> VocabularyItem:
        """Add a new vocabulary item"""
        vocab = VocabularyItem(
            user_id=user_id,
            word=word,
            language=language,
            translation=translation,
            next_review_date=datetime.utcnow() + timedelta(days=1),
            **kwargs
        )
        session.add(vocab)
        session.commit()
        session.refresh(vocab)
        return vocab
    
    @staticmethod
    def get_due_reviews(session: Session, user_id: int, limit: int = 20) -> List[VocabularyItem]:
        """Get vocabulary items due for review"""
        return session.query(VocabularyItem).filter(
            and_(
                VocabularyItem.user_id == user_id,
                VocabularyItem.next_review_date <= datetime.utcnow()
            )
        ).limit(limit).all()
    
    @staticmethod
    def record_review(
        session: Session,
        vocab_id: int,
        is_correct: bool
    ):
        """Record a vocabulary review (SRS algorithm)"""
        vocab = session.query(VocabularyItem).filter(VocabularyItem.id == vocab_id).first()
        if not vocab:
            return
        
        vocab.times_reviewed += 1
        if is_correct:
            vocab.times_correct += 1
        
        # Simple SRS algorithm (similar to Anki)
        if is_correct:
            vocab.mastery_level = min(vocab.mastery_level + 1, 5)
            vocab.interval_days = int(vocab.interval_days * vocab.ease_factor)
            vocab.ease_factor = min(vocab.ease_factor + 0.1, 3.0)
        else:
            vocab.mastery_level = max(vocab.mastery_level - 1, 0)
            vocab.interval_days = 1
            vocab.ease_factor = max(vocab.ease_factor - 0.2, 1.3)
        
        vocab.next_review_date = datetime.utcnow() + timedelta(days=vocab.interval_days)
        vocab.last_reviewed = datetime.utcnow()
        
        session.commit()


class ConversationService:
    """Service for conversation management"""
    
    @staticmethod
    def start_conversation(
        session: Session,
        user_id: int,
        language: str,
        scenario: str,
        difficulty: str = "intermediate"
    ) -> Conversation:
        """Start a new conversation session"""
        conversation = Conversation(
            user_id=user_id,
            language=language,
            scenario=scenario,
            difficulty=difficulty,
            messages=[]
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation
    
    @staticmethod
    def add_message(
        session: Session,
        conversation_id: int,
        role: str,
        content: str
    ):
        """Add a message to conversation"""
        conversation = session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation.exchange_count += 1
            session.commit()
    
    @staticmethod
    def complete_conversation(
        session: Session,
        conversation_id: int,
        feedback: str = None,
        **scores
    ):
        """Mark conversation as complete with scores"""
        conversation = session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.completed_at = datetime.utcnow()
            conversation.ai_feedback = feedback
            
            # Calculate duration
            if conversation.started_at:
                duration = (conversation.completed_at - conversation.started_at).total_seconds() / 60
                conversation.duration_minutes = int(duration)
            
            # Set scores
            for key, value in scores.items():
                if hasattr(conversation, key):
                    setattr(conversation, key, value)
            
            session.commit()


class AchievementService:
    """Service for achievement management"""
    
    ACHIEVEMENTS = {
        "first_conversation": {"name": "First Steps", "target": 1, "type": "conversations"},
        "conversation_master": {"name": "Conversation Master", "target": 50, "type": "conversations"},
        "vocabulary_100": {"name": "Word Collector", "target": 100, "type": "vocabulary"},
        "vocabulary_500": {"name": "Vocabulary Master", "target": 500, "type": "vocabulary"},
        "streak_7": {"name": "Week Warrior", "target": 7, "type": "streak"},
        "streak_30": {"name": "Monthly Champion", "target": 30, "type": "streak"},
        "writing_10": {"name": "Prolific Writer", "target": 10, "type": "writing"},
    }
    
    @staticmethod
    def check_and_award_achievements(session: Session, user_id: int):
        """Check and award new achievements"""
        stats = UserService.get_user_stats(session, user_id)
        
        newly_earned = []
        
        for achievement_id, achievement_data in AchievementService.ACHIEVEMENTS.items():
            # Check if already earned
            existing = session.query(Achievement).filter(
                and_(
                    Achievement.user_id == user_id,
                    Achievement.achievement_type == achievement_data["type"],
                    Achievement.achievement_name == achievement_data["name"]
                )
            ).first()
            
            if existing and existing.is_completed:
                continue
            
            # Check progress
            current_value = 0
            if achievement_data["type"] == "conversations":
                current_value = stats.get("total_conversations", 0)
            elif achievement_data["type"] == "vocabulary":
                current_value = stats.get("total_vocabulary", 0)
            elif achievement_data["type"] == "writing":
                current_value = stats.get("total_writing_submissions", 0)
            elif achievement_data["type"] == "streak":
                # Get max streak across all languages
                progress_data = stats.get("progress_by_language", {})
                current_value = max([p.get("streak", 0) for p in progress_data.values()], default=0)
            
            # Create or update achievement
            if not existing:
                existing = Achievement(
                    user_id=user_id,
                    achievement_type=achievement_data["type"],
                    achievement_name=achievement_data["name"],
                    target_value=achievement_data["target"],
                    current_value=current_value
                )
                session.add(existing)
            else:
                existing.current_value = current_value
            
            # Check if completed
            if current_value >= achievement_data["target"] and not existing.is_completed:
                existing.is_completed = True
                existing.earned_at = datetime.utcnow()
                newly_earned.append(existing)
        
        session.commit()
        return newly_earned
