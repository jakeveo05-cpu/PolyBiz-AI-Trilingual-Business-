"""
Scheduled Tasks for PolyBiz AI
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


async def generate_daily_challenge(language: str = None):
    """
    Generate and store daily challenge
    Runs at 6:00 AM daily
    """
    from database import get_db, DailyChallenge
    from agents import LessonGenerator
    
    logger.info("🎯 Generating daily challenge...")
    
    try:
        db = get_db()
        lesson_gen = LessonGenerator()
        
        # Generate for each language if not specified
        languages = [language] if language else ["en", "zh"]
        
        for lang in languages:
            # Generate challenge
            challenge_content = await lesson_gen.generate_daily_challenge(
                language=lang,
                level="B1"
            )
            
            # Store in database
            with db.session_scope() as session:
                challenge = DailyChallenge(
                    date=datetime.utcnow(),
                    language=lang,
                    challenge_type="mixed",
                    title=f"Daily Challenge - {datetime.utcnow().strftime('%B %d, %Y')}",
                    content=challenge_content
                )
                session.add(challenge)
            
            logger.info(f"✅ Generated {lang.upper()} daily challenge")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate daily challenge: {e}")
        return False


async def send_daily_reminders(reminder_type: str = "morning"):
    """
    Send reminders to users
    Morning: 8:00 AM - Encourage to start learning
    Evening: 8:00 PM - Remind to complete daily goal
    """
    from database import get_db, User, LearningProgress
    
    logger.info(f"📬 Sending {reminder_type} reminders...")
    
    try:
        db = get_db()
        
        with db.session_scope() as session:
            # Get active users with reminders enabled
            users = session.query(User).filter(
                User.is_active == True,
                User.reminder_time.isnot(None)
            ).all()
            
            for user in users:
                # Get user's progress
                progress = session.query(LearningProgress).filter(
                    LearningProgress.user_id == user.id
                ).first()
                
                streak = progress.streak_days if progress else 0
                
                # Compose message based on type
                if reminder_type == "morning":
                    message = compose_morning_reminder(user.username, streak)
                else:
                    message = compose_evening_reminder(user.username, streak)
                
                # Send via appropriate platform
                if user.discord_id:
                    await send_discord_dm(user.discord_id, message)
                if user.telegram_id:
                    await send_telegram_message(user.telegram_id, message)
            
            logger.info(f"✅ Sent reminders to {len(users)} users")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send reminders: {e}")
        return False


def compose_morning_reminder(username: str, streak: int) -> str:
    """Compose morning reminder message"""
    if streak > 0:
        return f"""🌅 Good morning, {username}!

🔥 You're on a {streak}-day streak! Keep it going!

Today's goals:
• Complete the daily challenge
• Practice 1 conversation
• Review 10 vocabulary words

Let's make today count! 💪"""
    else:
        return f"""🌅 Good morning, {username}!

Ready to start your language learning journey today?

Quick wins for today:
• Try the daily challenge (5 min)
• Learn 5 new words
• Practice one phrase

Small steps lead to big progress! 🚀"""


def compose_evening_reminder(username: str, streak: int) -> str:
    """Compose evening reminder message"""
    if streak > 0:
        return f"""🌙 Evening check-in, {username}!

🔥 Your streak: {streak} days

Did you practice today? Don't break the chain!

Quick options:
• /challenge - 5-minute daily challenge
• /practice - Quick conversation
• /review - Vocabulary review

Just 5 minutes keeps your streak alive! ⏰"""
    else:
        return f"""🌙 Hey {username}!

Haven't practiced today yet? No worries!

It's not too late:
• /challenge - Quick 5-minute challenge
• /lesson - Learn something new

Even 5 minutes counts! Start your streak today 🌟"""


async def post_content_to_community():
    """
    Auto-post content to community channels
    Runs 3 times daily: 9 AM, 2 PM, 7 PM
    """
    from agents import ContentCreator
    
    logger.info("📢 Posting content to community...")
    
    try:
        content_creator = ContentCreator()
        
        # Determine content type based on time
        hour = datetime.now().hour
        
        if hour < 12:
            # Morning: Tip or phrase
            content = await content_creator.create_tip_post(
                topic="business communication",
                language="en",
                platform="discord"
            )
        elif hour < 17:
            # Afternoon: Quiz or challenge
            content = await content_creator.create_quiz_post(
                topic="business vocabulary",
                language="en",
                difficulty="medium"
            )
        else:
            # Evening: Cultural insight or discussion
            content = await content_creator.create_cultural_insight(
                topic="meeting etiquette",
                cultures=["US", "China"]
            )
        
        # Post to Discord
        await post_to_discord_channel(content)
        
        # Post to Telegram
        await post_to_telegram_channel(content)
        
        logger.info("✅ Content posted to community")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to post content: {e}")
        return False


async def check_streaks():
    """
    Check and update user streaks at midnight
    Reset streaks for users who didn't practice
    """
    from database import get_db, LearningProgress
    from datetime import date
    
    logger.info("🔥 Checking streaks...")
    
    try:
        db = get_db()
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        with db.session_scope() as session:
            # Get all progress records
            all_progress = session.query(LearningProgress).all()
            
            streaks_broken = 0
            streaks_maintained = 0
            
            for progress in all_progress:
                if progress.last_practice_date:
                    last_date = progress.last_practice_date.date()
                    
                    if last_date < yesterday:
                        # Streak broken
                        progress.streak_days = 0
                        streaks_broken += 1
                    else:
                        streaks_maintained += 1
            
            logger.info(f"✅ Streaks checked: {streaks_maintained} maintained, {streaks_broken} broken")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to check streaks: {e}")
        return False


async def generate_weekly_report():
    """
    Generate weekly progress report for all users
    Runs Sunday 9 PM
    """
    from database import get_db, User
    from database.services import UserService
    
    logger.info("📊 Generating weekly reports...")
    
    try:
        db = get_db()
        
        with db.session_scope() as session:
            users = session.query(User).filter(User.is_active == True).all()
            
            for user in users:
                stats = UserService.get_user_stats(session, user.id)
                report = compose_weekly_report(stats)
                
                # Send report
                if user.discord_id:
                    await send_discord_dm(user.discord_id, report)
                if user.telegram_id:
                    await send_telegram_message(user.telegram_id, report)
            
            logger.info(f"✅ Sent weekly reports to {len(users)} users")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate weekly reports: {e}")
        return False


def compose_weekly_report(stats: dict) -> str:
    """Compose weekly progress report"""
    username = stats.get('username', 'Learner')
    conversations = stats.get('total_conversations', 0)
    vocabulary = stats.get('total_vocabulary', 0)
    writing = stats.get('total_writing_submissions', 0)
    
    progress_by_lang = stats.get('progress_by_language', {})
    
    report = f"""📊 **Weekly Progress Report**

Hey {username}! Here's your week in review:

📈 **This Week's Activity**
• Conversations: {conversations}
• Vocabulary learned: {vocabulary}
• Writing submissions: {writing}

"""
    
    if progress_by_lang:
        report += "🌍 **Progress by Language**\n"
        for lang, data in progress_by_lang.items():
            report += f"• {lang.upper()}: Level {data.get('level', 'N/A')}, {data.get('streak', 0)}-day streak\n"
    
    report += """
💡 **Tips for Next Week**
• Try a new conversation scenario
• Review vocabulary daily
• Challenge yourself with harder content

Keep up the great work! 🚀"""
    
    return report


async def cleanup_old_data():
    """
    Cleanup old data to save storage
    Runs Sunday 3 AM
    """
    from database import get_db, Conversation, WritingSubmission
    from datetime import timedelta
    
    logger.info("🧹 Cleaning up old data...")
    
    try:
        db = get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=90)  # Keep 90 days
        
        with db.session_scope() as session:
            # Delete old conversations (keep summary, delete messages)
            old_conversations = session.query(Conversation).filter(
                Conversation.completed_at < cutoff_date
            ).all()
            
            for conv in old_conversations:
                conv.messages = []  # Clear messages but keep metadata
            
            logger.info(f"✅ Cleaned up {len(old_conversations)} old conversations")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup: {e}")
        return False


# Helper functions for sending messages
async def send_discord_dm(user_id: str, message: str):
    """Send Discord DM (placeholder - implement with bot)"""
    logger.info(f"📨 Discord DM to {user_id}: {message[:50]}...")
    # TODO: Implement with Discord bot
    pass


async def send_telegram_message(user_id: str, message: str):
    """Send Telegram message (placeholder - implement with bot)"""
    logger.info(f"📨 Telegram to {user_id}: {message[:50]}...")
    # TODO: Implement with Telegram bot
    pass


async def post_to_discord_channel(content: str, channel_id: str = None):
    """Post to Discord channel (placeholder)"""
    logger.info(f"📢 Discord post: {content[:50]}...")
    # TODO: Implement with Discord bot
    pass


async def post_to_telegram_channel(content: str, channel_id: str = None):
    """Post to Telegram channel (placeholder)"""
    logger.info(f"📢 Telegram post: {content[:50]}...")
    # TODO: Implement with Telegram bot
    pass


async def backup_database():
    """
    Create daily database backup
    Runs at 2:00 AM daily
    """
    logger.info("💾 Starting database backup...")
    
    try:
        from utils.backup import get_backup_manager
        
        backup_manager = get_backup_manager()
        backup_path = backup_manager.create_backup()
        
        if backup_path:
            logger.info(f"✅ Database backup created: {backup_path}")
            return True
        else:
            logger.error("❌ Database backup failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Backup error: {e}")
        return False
