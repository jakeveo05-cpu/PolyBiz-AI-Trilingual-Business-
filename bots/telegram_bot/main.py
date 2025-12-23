"""
PolyBiz AI - Telegram Bot (Enhanced)
Full integration with database, automation, and all AI agents
"""
import sys
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import TELEGRAM_BOT_TOKEN
from agents import (
    WritingCoach, ConversationPartner, LessonGenerator,
    ContentCreator, AnkiGenerator, AnkiCard
)
from database import get_db
from database.services import UserService, ProgressService, VocabularyService, ConversationService, AchievementService

# Initialize
writing_coach = WritingCoach()
lesson_generator = LessonGenerator()
content_creator = ContentCreator()
anki_generator = AnkiGenerator()

# Active sessions
active_conversations = {}
active_conversation_ids = {}

# Database
db = get_db()

# Conversation states
REVIEW_TEXT, VOCAB_WORD, VOCAB_TRANSLATION, VOCAB_EXAMPLE = range(4)


# ============ START & HELP ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - welcome and create user"""
    user = update.effective_user
    
    # Create user in database
    with db.session_scope() as session:
        db_user = UserService.get_user_by_platform(session, telegram_id=str(user.id))
        
        if not db_user:
            db_user = UserService.create_user(
                session=session,
                username=user.first_name or user.username,
                telegram_id=str(user.id)
            )
    
    keyboard = [
        [InlineKeyboardButton("🎯 Daily Challenge", callback_data="challenge")],
        [InlineKeyboardButton("🗣️ Practice Conversation", callback_data="practice_menu")],
        [InlineKeyboardButton("📝 Review Writing", callback_data="review")],
        [InlineKeyboardButton("📚 Get Lesson", callback_data="lesson_menu")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌏 *Welcome to PolyBiz AI, {user.first_name}!*\n\n"
        "I'm your AI-powered business language learning assistant.\n\n"
        "*Quick Commands:*\n"
        "• /challenge - Daily challenge\n"
        "• /practice - Conversation practice\n"
        "• /review - Writing feedback\n"
        "• /lesson - Personalized lesson\n"
        "• /vocab - Add vocabulary\n"
        "• /stats - Your statistics\n"
        "• /help - All commands\n\n"
        "Choose an option below to get started! 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🌏 *PolyBiz AI - Commands*

*👤 Profile*
/profile - View your profile
/setlang - Set your languages
/stats - View statistics

*📝 Writing*
/review - Submit writing for feedback

*🗣️ Conversation*
/practice - Start conversation practice
/stop - End practice session

*📚 Learning*
/lesson [topic] - Generate a lesson
/challenge - Daily challenge

*📇 Vocabulary*
/vocab - Add new vocabulary
/review\\_vocab - SRS review
/ankideck - Generate Anki deck

*Languages:* en, zh, vi
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ============ PROFILE & STATS ============
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View user profile"""
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
        
        if not user:
            await update.message.reply_text("Please use /start first to create your profile.")
            return
        
        stats = UserService.get_user_stats(session, user.id)
        
        profile_text = f"""
📊 *{user.username}'s Profile*

🌍 *Languages*
Native: {user.native_language.upper()}
Learning: {', '.join([l.upper() for l in user.target_languages]) if user.target_languages else 'Not set'}

📈 *Activity*
• Conversations: {stats['total_conversations']}
• Vocabulary: {stats['total_vocabulary']}
• Writing: {stats['total_writing_submissions']}
"""
        
        if stats['progress_by_language']:
            profile_text += "\n📚 *Progress*\n"
            for lang, data in stats['progress_by_language'].items():
                profile_text += f"• {lang.upper()}: Level {data['level'] or 'N/A'}, 🔥 {data['streak']} day streak\n"
        
        await update.message.reply_text(profile_text, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View statistics"""
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
        
        if not user:
            await update.message.reply_text("Please use /start first.")
            return
        
        stats = UserService.get_user_stats(session, user.id)
        
        # Get max streak
        max_streak = 0
        if stats['progress_by_language']:
            max_streak = max([p.get('streak', 0) for p in stats['progress_by_language'].values()])
        
        stats_text = f"""
📊 *Your Statistics*

💬 Conversations: {stats['total_conversations']}
📚 Vocabulary: {stats['total_vocabulary']}
✍️ Writing: {stats['total_writing_submissions']}
🔥 Best Streak: {max_streak} days
"""
        await update.message.reply_text(stats_text, parse_mode="Markdown")


# ============ WRITING REVIEW ============
async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start writing review"""
    context.user_data["mode"] = "review"
    await update.message.reply_text(
        "📝 *Writing Review Mode*\n\n"
        "Send me your text and I'll provide detailed feedback.\n"
        "Supports: English, Chinese, Vietnamese\n\n"
        "Use /cancel to exit.",
        parse_mode="Markdown"
    )


async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle writing review"""
    text = update.message.text
    
    await update.message.reply_text("📝 Analyzing your writing...")
    
    try:
        feedback = await writing_coach.review(text)
        
        # Update progress
        with db.session_scope() as session:
            user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
            if user:
                ProgressService.update_progress(
                    session=session,
                    user_id=user.id,
                    language="en",
                    skill="writing",
                    session_minutes=5
                )
                AchievementService.check_and_award_achievements(session, user.id)
        
        # Send feedback
        if len(feedback) > 4000:
            for i in range(0, len(feedback), 4000):
                await update.message.reply_text(feedback[i:i+4000])
        else:
            await update.message.reply_text(feedback)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    context.user_data["mode"] = None


# ============ CONVERSATION PRACTICE ============
async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation practice"""
    keyboard = [
        [InlineKeyboardButton("🎯 Job Interview", callback_data="practice_job_interview")],
        [InlineKeyboardButton("🤝 Client Meeting", callback_data="practice_client_meeting")],
        [InlineKeyboardButton("💰 Negotiation", callback_data="practice_negotiation")],
        [InlineKeyboardButton("🌐 Networking", callback_data="practice_networking")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎭 *Choose a scenario:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def start_practice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle practice scenario selection"""
    query = update.callback_query
    await query.answer()
    
    scenario = query.data.replace("practice_", "")
    user_id = update.effective_user.id
    
    # Create conversation partner
    active_conversations[user_id] = ConversationPartner(
        language="en",
        scenario=scenario,
        difficulty="intermediate"
    )
    
    # Create database record
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(user_id))
        if user:
            conv = ConversationService.start_conversation(
                session=session,
                user_id=user.id,
                language="en",
                scenario=scenario
            )
            active_conversation_ids[user_id] = conv.id
    
    context.user_data["mode"] = "practice"
    
    await query.edit_message_text(
        f"🎭 *Practice Started!*\n\n"
        f"Scenario: {scenario.replace('_', ' ').title()}\n"
        f"Language: English\n\n"
        f"Type your messages to practice.\n"
        f"Use /stop to end and get feedback.\n\n"
        f"_Let's begin! Introduce yourself..._",
        parse_mode="Markdown"
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop practice and get feedback"""
    user_id = update.effective_user.id
    
    if user_id not in active_conversations:
        await update.message.reply_text("No active practice session.")
        return
    
    await update.message.reply_text("📊 Generating feedback...")
    
    # Get final feedback
    partner = active_conversations[user_id]
    final_feedback = await partner.chat(
        "Please provide a comprehensive summary of my performance."
    )
    
    # Update database
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(user_id))
        if user and user_id in active_conversation_ids:
            ConversationService.complete_conversation(
                session=session,
                conversation_id=active_conversation_ids[user_id],
                feedback=final_feedback
            )
            
            ProgressService.update_progress(
                session=session,
                user_id=user.id,
                language=partner.language,
                skill="speaking",
                session_minutes=10
            )
            
            newly_earned = AchievementService.check_and_award_achievements(session, user.id)
            del active_conversation_ids[user_id]
    
    # Cleanup
    del active_conversations[user_id]
    context.user_data["mode"] = None
    
    # Send feedback
    feedback_text = f"✅ *Practice Complete!*\n\n{final_feedback}"
    
    if len(feedback_text) > 4000:
        for i in range(0, len(feedback_text), 4000):
            await update.message.reply_text(feedback_text[i:i+4000], parse_mode="Markdown")
    else:
        await update.message.reply_text(feedback_text, parse_mode="Markdown")


async def handle_practice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages during practice"""
    user_id = update.effective_user.id
    text = update.message.text
    
    try:
        response = await active_conversations[user_id].respond(text)
        
        # Store in database
        with db.session_scope() as session:
            if user_id in active_conversation_ids:
                ConversationService.add_message(
                    session=session,
                    conversation_id=active_conversation_ids[user_id],
                    role="user",
                    content=text
                )
                ConversationService.add_message(
                    session=session,
                    conversation_id=active_conversation_ids[user_id],
                    role="assistant",
                    content=response
                )
        
        await update.message.reply_text(response)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ============ LESSONS & CHALLENGES ============
async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a lesson"""
    args = context.args
    topic = " ".join(args) if args else "business email writing"
    
    await update.message.reply_text("📚 Generating your lesson...")
    
    try:
        lesson = await lesson_generator.generate_lesson(
            topic=topic,
            language="en",
            level="B1"
        )
        
        if len(lesson) > 4000:
            for i in range(0, len(lesson), 4000):
                await update.message.reply_text(lesson[i:i+4000])
        else:
            await update.message.reply_text(lesson)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def challenge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get daily challenge"""
    await update.message.reply_text("🎯 Generating today's challenge...")
    
    try:
        challenge = await lesson_generator.generate_daily_challenge("en", "B1")
        await update.message.reply_text(f"🎯 *Daily Challenge*\n\n{challenge}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ============ VOCABULARY ============
async def vocab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add vocabulary"""
    context.user_data["mode"] = "vocab_word"
    await update.message.reply_text(
        "📚 *Add Vocabulary*\n\n"
        "Send me the word or phrase you want to learn.\n"
        "Use /cancel to exit.",
        parse_mode="Markdown"
    )


async def handle_vocab_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle vocabulary word input"""
    context.user_data["vocab_word"] = update.message.text
    context.user_data["mode"] = "vocab_translation"
    await update.message.reply_text("Now send the translation:")


async def handle_vocab_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle vocabulary translation input"""
    word = context.user_data.get("vocab_word")
    translation = update.message.text
    
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
        
        if user:
            VocabularyService.add_vocabulary(
                session=session,
                user_id=user.id,
                word=word,
                language="en",
                translation=translation,
                source="telegram"
            )
    
    context.user_data["mode"] = None
    await update.message.reply_text(
        f"✅ Added to your vocabulary!\n\n"
        f"*{word}* - {translation}\n"
        f"📅 First review: Tomorrow",
        parse_mode="Markdown"
    )


async def ankideck_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate Anki deck"""
    await update.message.reply_text("📇 Generating your Anki deck...")
    
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
        
        if not user:
            await update.message.reply_text("Please use /start first.")
            return
        
        from database import VocabularyItem
        vocab_items = session.query(VocabularyItem).filter(
            VocabularyItem.user_id == user.id
        ).all()
        
        if not vocab_items:
            await update.message.reply_text("You don't have any vocabulary yet. Add some with /vocab!")
            return
        
        cards = [
            AnkiCard(
                front=v.word,
                back=v.translation,
                example=v.example or "",
                tags=v.tags or []
            )
            for v in vocab_items
        ]
        
        deck_name = f"PolyBiz AI - {user.username}"
        deck_path = anki_generator.create_deck(
            deck_name=deck_name,
            cards=cards,
            template_name="vocabulary"
        )
        
        await update.message.reply_document(
            document=open(deck_path, "rb"),
            caption=f"📇 Your Anki deck with {len(cards)} cards!"
        )


# ============ MESSAGE HANDLER ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages based on mode"""
    user_id = update.effective_user.id
    mode = context.user_data.get("mode")
    
    if mode == "review":
        await handle_review(update, context)
    elif mode == "vocab_word":
        await handle_vocab_word(update, context)
    elif mode == "vocab_translation":
        await handle_vocab_translation(update, context)
    elif user_id in active_conversations:
        await handle_practice_message(update, context)
    else:
        await update.message.reply_text("Use /start to see available options or /help for commands.")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    context.user_data["mode"] = None
    await update.message.reply_text("Cancelled. Use /help to see available commands.")


# ============ CALLBACKS ============
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "challenge":
        await query.edit_message_text("🎯 Generating challenge...")
        challenge = await lesson_generator.generate_daily_challenge("en", "B1")
        await query.message.reply_text(f"🎯 *Daily Challenge*\n\n{challenge}", parse_mode="Markdown")
    
    elif query.data == "practice_menu":
        keyboard = [
            [InlineKeyboardButton("🎯 Job Interview", callback_data="practice_job_interview")],
            [InlineKeyboardButton("🤝 Client Meeting", callback_data="practice_client_meeting")],
            [InlineKeyboardButton("💰 Negotiation", callback_data="practice_negotiation")],
            [InlineKeyboardButton("🌐 Networking", callback_data="practice_networking")],
        ]
        await query.edit_message_text(
            "🎭 *Choose a scenario:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif query.data.startswith("practice_"):
        await start_practice_callback(update, context)
    
    elif query.data == "review":
        context.user_data["mode"] = "review"
        await query.edit_message_text(
            "📝 *Writing Review Mode*\n\nSend me your text for feedback.",
            parse_mode="Markdown"
        )
    
    elif query.data == "lesson_menu":
        await query.edit_message_text(
            "📚 Use /lesson [topic] to generate a lesson.\n\n"
            "Example: /lesson business email writing"
        )
    
    elif query.data == "stats":
        with db.session_scope() as session:
            user = UserService.get_user_by_platform(session, telegram_id=str(update.effective_user.id))
            if user:
                stats = UserService.get_user_stats(session, user.id)
                await query.edit_message_text(
                    f"📊 *Your Statistics*\n\n"
                    f"💬 Conversations: {stats['total_conversations']}\n"
                    f"📚 Vocabulary: {stats['total_vocabulary']}\n"
                    f"✍️ Writing: {stats['total_writing_submissions']}",
                    parse_mode="Markdown"
                )


def main():
    """Run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    # Initialize database
    db.create_tables()
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("review", review_command))
    app.add_handler(CommandHandler("practice", practice_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("lesson", lesson_command))
    app.add_handler(CommandHandler("challenge", challenge_command))
    app.add_handler(CommandHandler("vocab", vocab_command))
    app.add_handler(CommandHandler("ankideck", ankideck_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Starting PolyBiz AI Telegram Bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
