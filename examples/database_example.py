"""
Example: How to use the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Database, get_db
from database.services import UserService, ProgressService, VocabularyService, ConversationService, AchievementService


def example_create_user():
    """Example: Create a new user"""
    db = get_db()
    
    with db.session_scope() as session:
        user = UserService.create_user(
            session=session,
            username="john_doe",
            discord_id="123456789",
            native_language="vi",
            target_languages=["en", "zh"],
            current_level={"en": "B1", "zh": "A2"},
            learning_goals=["job_interview", "email_writing"]
        )
        
        print(f"✅ Created user: {user.username} (ID: {user.id})")
        return user.id


def example_track_progress(user_id: int):
    """Example: Track learning progress"""
    db = get_db()
    
    with db.session_scope() as session:
        # Update progress after a conversation session
        progress = ProgressService.update_progress(
            session=session,
            user_id=user_id,
            language="en",
            skill="speaking",
            session_minutes=15,
            fluency_score=75.0,
            accuracy_score=80.0
        )
        
        print(f"✅ Updated progress: {progress.language}/{progress.skill}")
        print(f"   Streak: {progress.streak_days} days")
        print(f"   Total sessions: {progress.total_sessions}")


def example_add_vocabulary(user_id: int):
    """Example: Add vocabulary items"""
    db = get_db()
    
    words = [
        {"word": "leverage", "translation": "tận dụng", "example": "We leverage AI tools."},
        {"word": "synergy", "translation": "hiệu ứng cộng hưởng", "example": "Create synergy."},
        {"word": "stakeholder", "translation": "bên liên quan", "example": "Consider all stakeholders."}
    ]
    
    with db.session_scope() as session:
        for word_data in words:
            vocab = VocabularyService.add_vocabulary(
                session=session,
                user_id=user_id,
                language="en",
                **word_data,
                tags=["business", "vocabulary"],
                source="lesson"
            )
            print(f"✅ Added vocabulary: {vocab.word}")


def example_conversation_session(user_id: int):
    """Example: Track a conversation session"""
    db = get_db()
    
    with db.session_scope() as session:
        # Start conversation
        conversation = ConversationService.start_conversation(
            session=session,
            user_id=user_id,
            language="en",
            scenario="job_interview",
            difficulty="intermediate"
        )
        
        print(f"✅ Started conversation: {conversation.scenario}")
        
        # Add messages
        ConversationService.add_message(
            session=session,
            conversation_id=conversation.id,
            role="user",
            content="Tell me about yourself."
        )
        
        ConversationService.add_message(
            session=session,
            conversation_id=conversation.id,
            role="assistant",
            content="I'm a software engineer with 5 years of experience..."
        )
        
        # Complete conversation
        ConversationService.complete_conversation(
            session=session,
            conversation_id=conversation.id,
            feedback="Good job! Your responses were clear and professional.",
            grammar_score=85.0,
            vocabulary_score=80.0,
            fluency_score=75.0,
            overall_score=80.0
        )
        
        print(f"✅ Completed conversation with score: {conversation.overall_score}")


def example_check_achievements(user_id: int):
    """Example: Check and award achievements"""
    db = get_db()
    
    with db.session_scope() as session:
        newly_earned = AchievementService.check_and_award_achievements(
            session=session,
            user_id=user_id
        )
        
        if newly_earned:
            print(f"🏆 Earned {len(newly_earned)} new achievement(s):")
            for achievement in newly_earned:
                print(f"   - {achievement.achievement_name}")
        else:
            print("No new achievements yet. Keep learning!")


def example_get_stats(user_id: int):
    """Example: Get user statistics"""
    db = get_db()
    
    with db.session_scope() as session:
        stats = UserService.get_user_stats(session, user_id)
        
        print("\n📊 User Statistics:")
        print(f"   Username: {stats['username']}")
        print(f"   Total Conversations: {stats['total_conversations']}")
        print(f"   Total Vocabulary: {stats['total_vocabulary']}")
        print(f"   Total Writing: {stats['total_writing_submissions']}")
        
        print("\n   Progress by Language:")
        for lang, progress in stats['progress_by_language'].items():
            print(f"   {lang.upper()}: Level {progress['level']}, {progress['sessions']} sessions, {progress['streak']} day streak")


def example_vocabulary_review(user_id: int):
    """Example: Vocabulary review (SRS)"""
    db = get_db()
    
    with db.session_scope() as session:
        # Get due reviews
        due_items = VocabularyService.get_due_reviews(session, user_id, limit=5)
        
        print(f"\n📚 You have {len(due_items)} vocabulary items to review:")
        
        for vocab in due_items:
            print(f"\n   Word: {vocab.word}")
            print(f"   Translation: {vocab.translation}")
            
            # Simulate review (in real app, user would answer)
            is_correct = True  # User got it right
            
            VocabularyService.record_review(
                session=session,
                vocab_id=vocab.id,
                is_correct=is_correct
            )
            
            print(f"   ✅ Reviewed! Next review in {vocab.interval_days} days")


if __name__ == "__main__":
    print("=" * 60)
    print("PolyBiz AI - Database Examples")
    print("=" * 60)
    
    # Initialize database
    db = get_db()
    db.create_tables()
    
    # Run examples
    print("\n1️⃣ Creating user...")
    user_id = example_create_user()
    
    print("\n2️⃣ Tracking progress...")
    example_track_progress(user_id)
    
    print("\n3️⃣ Adding vocabulary...")
    example_add_vocabulary(user_id)
    
    print("\n4️⃣ Conversation session...")
    example_conversation_session(user_id)
    
    print("\n5️⃣ Checking achievements...")
    example_check_achievements(user_id)
    
    print("\n6️⃣ Getting user stats...")
    example_get_stats(user_id)
    
    print("\n7️⃣ Vocabulary review (SRS)...")
    example_vocabulary_review(user_id)
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)
