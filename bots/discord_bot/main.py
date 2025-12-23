"""
PolyBiz AI - Discord Bot (Enhanced)
Full integration with database, automation, and all AI agents
"""
import discord
from discord.ext import commands
from discord import app_commands
import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import DISCORD_BOT_TOKEN
from agents import (
    WritingCoach, ConversationPartner, LessonGenerator, 
    ContentCreator, ToucanTTS, AnkiGenerator, AnkiCard,
    VocabularyExtractor
)
from database import get_db, User, Conversation, VocabularyItem
from database.services import UserService, ProgressService, VocabularyService, ConversationService, AchievementService
from automation import get_scheduler
from utils import (
    check_and_record, format_error_for_user, log_user_action,
    validate_text_input, validate_language, validate_level,
    RateLimitError, ValidationError, logger
)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize agents (lazy loading to avoid startup errors)
writing_coach = None
lesson_generator = None
content_creator = None
vocab_extractor = None
anki_generator = None

def get_agents():
    """Lazy load agents"""
    global writing_coach, lesson_generator, content_creator, vocab_extractor, anki_generator
    if writing_coach is None:
        writing_coach = WritingCoach()
        lesson_generator = LessonGenerator()
        content_creator = ContentCreator()
        vocab_extractor = VocabularyExtractor()
        anki_generator = AnkiGenerator()
    return writing_coach, lesson_generator, content_creator, vocab_extractor, anki_generator

# Active sessions
active_conversations = {}  # user_id -> ConversationPartner
active_conversation_ids = {}  # user_id -> database conversation_id

# Database
db = get_db()


# ============ HELPER FUNCTIONS ============
async def check_rate_limit(interaction: discord.Interaction) -> bool:
    """Check rate limit before processing command"""
    user_id = str(interaction.user.id)
    allowed, retry_after = await check_and_record(user_id)
    
    if not allowed:
        await interaction.response.send_message(
            f"⏳ Bạn đang gửi quá nhiều yêu cầu. Vui lòng đợi {retry_after} giây.",
            ephemeral=True
        )
        return False
    return True


async def safe_respond(interaction: discord.Interaction, content: str = None, embed: discord.Embed = None, **kwargs):
    """Safely respond to interaction, handling message length"""
    try:
        if content and len(content) > 2000:
            # Split long messages
            chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
            await interaction.followup.send(chunks[0], **kwargs)
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            await interaction.followup.send(content=content, embed=embed, **kwargs)
    except discord.HTTPException as e:
        logger.error(f"Discord HTTP error: {e}")
        await interaction.followup.send("❌ Lỗi gửi tin nhắn. Vui lòng thử lại.")


# ============ EVENTS ============
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Initialize database
    db.create_tables()
    
    # Start scheduler
    scheduler = get_scheduler(async_mode=True)
    scheduler.start()
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f"📝 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_member_join(member):
    """Welcome new members and create user profile"""
    with db.session_scope() as session:
        # Check if user exists
        user = UserService.get_user_by_platform(session, discord_id=str(member.id))
        
        if not user:
            # Create new user
            user = UserService.create_user(
                session=session,
                username=member.display_name,
                discord_id=str(member.id)
            )
            
            # Send welcome DM
            try:
                welcome_msg = f"""🌏 **Welcome to PolyBiz AI, {member.display_name}!**

I'm your AI-powered language learning assistant for business English and Chinese.

**Quick Start:**
• `/profile` - Set up your learning profile
• `/challenge` - Try today's daily challenge
• `/practice` - Start a conversation practice
• `/lesson` - Get a personalized lesson
• `/help` - See all commands

Let's start your journey to business fluency! 🚀"""
                
                await member.send(welcome_msg)
            except:
                pass  # DMs might be disabled


# ============ USER PROFILE ============
@bot.tree.command(name="profile", description="View or setup your learning profile")
async def view_profile(interaction: discord.Interaction):
    """View user profile and stats"""
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            # Create user
            user = UserService.create_user(
                session=session,
                username=interaction.user.display_name,
                discord_id=str(interaction.user.id)
            )
        
        # Get stats
        stats = UserService.get_user_stats(session, user.id)
        
        # Build profile embed
        embed = discord.Embed(
            title=f"📊 {user.username}'s Profile",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Learning Goals",
            value=", ".join(user.learning_goals) if user.learning_goals else "Not set",
            inline=False
        )
        
        embed.add_field(
            name="🌍 Languages",
            value=f"Native: {user.native_language.upper()}\nLearning: {', '.join([l.upper() for l in user.target_languages]) if user.target_languages else 'Not set'}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Activity",
            value=f"Conversations: {stats['total_conversations']}\nVocabulary: {stats['total_vocabulary']}\nWriting: {stats['total_writing_submissions']}",
            inline=True
        )
        
        # Progress by language
        if stats['progress_by_language']:
            progress_text = ""
            for lang, data in stats['progress_by_language'].items():
                progress_text += f"**{lang.upper()}**: Level {data['level'] or 'N/A'}, 🔥 {data['streak']} day streak\n"
            embed.add_field(name="📚 Progress", value=progress_text, inline=False)
        
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="setlanguage", description="Set your target languages")
@app_commands.describe(
    native="Your native language (vi/en/zh)",
    learning="Languages you're learning (comma separated: en,zh)"
)
async def set_language(interaction: discord.Interaction, native: str, learning: str):
    """Set user's language preferences"""
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            user = UserService.create_user(
                session=session,
                username=interaction.user.display_name,
                discord_id=str(interaction.user.id)
            )
        
        user.native_language = native.lower()
        user.target_languages = [l.strip().lower() for l in learning.split(",")]
        
        await interaction.response.send_message(
            f"✅ Languages updated!\n"
            f"Native: {native.upper()}\n"
            f"Learning: {learning.upper()}"
        )


# ============ WRITING COACH ============
@bot.tree.command(name="review", description="Submit writing for AI feedback")
@app_commands.describe(text="Your text to review")
async def review_writing(interaction: discord.Interaction, text: str):
    # Rate limit check
    if not await check_rate_limit(interaction):
        return
    
    await interaction.response.defer()
    
    try:
        # Validate input
        text = validate_text_input(text, "text", min_length=10, max_length=5000)
        
        # Log action
        log_user_action("review_writing", str(interaction.user.id), {"text_length": len(text)})
        
        # Get agent
        writing_coach, _, _, _, _ = get_agents()
        feedback = await writing_coach.review(text)
        
        # Update user progress
        with db.session_scope() as session:
            user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
            if user:
                ProgressService.update_progress(
                    session=session,
                    user_id=user.id,
                    language="en",
                    skill="writing",
                    session_minutes=5
                )
                AchievementService.check_and_award_achievements(session, user.id)
        
        await safe_respond(interaction, feedback)
        
    except ValidationError as e:
        await interaction.followup.send(e.user_message)
    except RateLimitError as e:
        await interaction.followup.send(e.user_message)
    except Exception as e:
        logger.error(f"Error in review_writing: {e}")
        await interaction.followup.send(format_error_for_user(e))


# ============ CONVERSATION PRACTICE ============
@bot.tree.command(name="practice", description="Start a conversation practice session")
@app_commands.describe(
    language="Language to practice (en/zh/vi)",
    scenario="Business scenario",
    difficulty="Difficulty level"
)
@app_commands.choices(scenario=[
    app_commands.Choice(name="Job Interview", value="job_interview"),
    app_commands.Choice(name="Client Meeting", value="client_meeting"),
    app_commands.Choice(name="Negotiation", value="negotiation"),
    app_commands.Choice(name="Networking", value="networking"),
    app_commands.Choice(name="Presentation Q&A", value="presentation"),
    app_commands.Choice(name="Phone Follow-up", value="phone_followup"),
])
@app_commands.choices(difficulty=[
    app_commands.Choice(name="Beginner", value="beginner"),
    app_commands.Choice(name="Intermediate", value="intermediate"),
    app_commands.Choice(name="Advanced", value="advanced"),
])
async def start_practice(
    interaction: discord.Interaction, 
    language: str = "en",
    scenario: str = "networking",
    difficulty: str = "intermediate"
):
    user_id = interaction.user.id
    
    # Create conversation partner
    active_conversations[user_id] = ConversationPartner(
        language=language, 
        scenario=scenario,
        difficulty=difficulty
    )
    
    # Create database record
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(user_id))
        if user:
            conv = ConversationService.start_conversation(
                session=session,
                user_id=user.id,
                language=language,
                scenario=scenario,
                difficulty=difficulty
            )
            active_conversation_ids[user_id] = conv.id
    
    scenarios_display = {
        "job_interview": "🎯 Job Interview",
        "client_meeting": "🤝 Client Meeting", 
        "negotiation": "💰 Negotiation",
        "presentation": "📊 Presentation Q&A",
        "networking": "🌐 Networking",
        "phone_followup": "📞 Phone Follow-up"
    }
    
    embed = discord.Embed(
        title="🎭 Conversation Practice Started!",
        description=f"**Scenario**: {scenarios_display.get(scenario, scenario)}\n**Language**: {language.upper()}\n**Difficulty**: {difficulty.capitalize()}",
        color=discord.Color.green()
    )
    embed.add_field(
        name="How to play",
        value="Type your messages to practice. I'll respond in character and give you feedback.\n\nUse `/endpractice` when you're done.",
        inline=False
    )
    embed.set_footer(text="Let's begin! Introduce yourself...")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="endpractice", description="End conversation practice and get feedback")
async def end_practice(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    if user_id not in active_conversations:
        await interaction.response.send_message("No active practice session.")
        return
    
    await interaction.response.defer()
    
    # Get final feedback
    partner = active_conversations[user_id]
    final_feedback = await partner.chat(
        "Please provide a comprehensive summary of my performance in this conversation. "
        "Include scores for grammar, vocabulary, fluency, and overall performance."
    )
    
    # Update database
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(user_id))
        if user and user_id in active_conversation_ids:
            ConversationService.complete_conversation(
                session=session,
                conversation_id=active_conversation_ids[user_id],
                feedback=final_feedback
            )
            
            # Update progress
            ProgressService.update_progress(
                session=session,
                user_id=user.id,
                language=partner.language,
                skill="speaking",
                session_minutes=10
            )
            
            # Check achievements
            newly_earned = AchievementService.check_and_award_achievements(session, user.id)
            
            del active_conversation_ids[user_id]
    
    # Cleanup
    del active_conversations[user_id]
    
    # Send feedback
    embed = discord.Embed(
        title="✅ Practice Session Complete!",
        description=final_feedback[:4000],
        color=discord.Color.gold()
    )
    
    if newly_earned:
        achievements_text = "\n".join([f"🏆 {a.achievement_name}" for a in newly_earned])
        embed.add_field(name="🎉 New Achievements!", value=achievements_text, inline=False)
    
    await interaction.followup.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = message.author.id
    
    # Check if user has active conversation
    if user_id in active_conversations:
        async with message.channel.typing():
            try:
                response = await active_conversations[user_id].respond(message.content)
                
                # Store message in database
                with db.session_scope() as session:
                    if user_id in active_conversation_ids:
                        ConversationService.add_message(
                            session=session,
                            conversation_id=active_conversation_ids[user_id],
                            role="user",
                            content=message.content
                        )
                        ConversationService.add_message(
                            session=session,
                            conversation_id=active_conversation_ids[user_id],
                            role="assistant",
                            content=response
                        )
                
                await message.reply(response)
            except Exception as e:
                await message.reply(f"❌ Error: {str(e)}")
        return
    
    await bot.process_commands(message)


# ============ LESSONS ============
@bot.tree.command(name="lesson", description="Generate a personalized lesson")
@app_commands.describe(
    topic="Topic to learn about",
    language="Target language (en/zh/vi)",
    level="Your level (A1/A2/B1/B2/C1/C2)"
)
async def generate_lesson(
    interaction: discord.Interaction,
    topic: str,
    language: str = "en",
    level: str = "B1"
):
    await interaction.response.defer()
    
    try:
        lesson = await lesson_generator.generate_lesson(
            topic=topic,
            language=language,
            level=level
        )
        
        if len(lesson) > 2000:
            chunks = [lesson[i:i+1900] for i in range(0, len(lesson), 1900)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            await interaction.followup.send(lesson)
            
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


@bot.tree.command(name="challenge", description="Get today's daily challenge")
@app_commands.describe(language="Target language (en/zh/vi)")
async def daily_challenge(interaction: discord.Interaction, language: str = "en"):
    await interaction.response.defer()
    
    try:
        challenge = await lesson_generator.generate_daily_challenge(language, "B1")
        
        embed = discord.Embed(
            title="🎯 Daily Challenge",
            description=challenge,
            color=discord.Color.orange()
        )
        embed.set_footer(text="Complete the challenge and share your answer!")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


# ============ VOCABULARY & ANKI ============
@bot.tree.command(name="vocab", description="Add vocabulary to your learning list")
@app_commands.describe(
    word="Word or phrase to learn",
    translation="Translation",
    example="Example sentence"
)
async def add_vocab(
    interaction: discord.Interaction,
    word: str,
    translation: str,
    example: str = ""
):
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            await interaction.response.send_message("Please set up your profile first with `/profile`")
            return
        
        vocab = VocabularyService.add_vocabulary(
            session=session,
            user_id=user.id,
            word=word,
            language="en",
            translation=translation,
            example=example,
            source="manual",
            tags=["discord", "manual"]
        )
        
        await interaction.response.send_message(
            f"✅ Added to your vocabulary!\n"
            f"**{word}** - {translation}\n"
            f"📅 First review: Tomorrow"
        )


@bot.tree.command(name="review_vocab", description="Review your vocabulary (SRS)")
async def review_vocab(interaction: discord.Interaction):
    await interaction.response.defer()
    
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            await interaction.followup.send("Please set up your profile first with `/profile`")
            return
        
        due_items = VocabularyService.get_due_reviews(session, user.id, limit=5)
        
        if not due_items:
            await interaction.followup.send("🎉 No vocabulary due for review! Check back later.")
            return
        
        # Show first item
        vocab = due_items[0]
        
        embed = discord.Embed(
            title="📚 Vocabulary Review",
            description=f"**What does this mean?**\n\n# {vocab.word}",
            color=discord.Color.purple()
        )
        embed.add_field(name="Items remaining", value=f"{len(due_items)} words to review")
        embed.set_footer(text="React with ✅ if you knew it, ❌ if you didn't")
        
        msg = await interaction.followup.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        # Wait for reaction
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]
        
        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            
            is_correct = str(reaction.emoji) == "✅"
            VocabularyService.record_review(session, vocab.id, is_correct)
            
            # Show answer
            answer_embed = discord.Embed(
                title=f"{'✅ Correct!' if is_correct else '❌ Keep practicing!'}",
                description=f"**{vocab.word}**\n{vocab.translation}\n\n*{vocab.example}*" if vocab.example else f"**{vocab.word}**\n{vocab.translation}",
                color=discord.Color.green() if is_correct else discord.Color.red()
            )
            answer_embed.add_field(
                name="Next review",
                value=f"In {vocab.interval_days} day(s)"
            )
            
            await interaction.channel.send(embed=answer_embed)
            
        except asyncio.TimeoutError:
            await interaction.channel.send("⏰ Review timed out. Use `/review_vocab` to continue.")


@bot.tree.command(name="ankideck", description="Generate Anki deck from your vocabulary")
async def generate_anki_deck(interaction: discord.Interaction):
    await interaction.response.defer()
    
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            await interaction.followup.send("Please set up your profile first with `/profile`")
            return
        
        # Get user's vocabulary
        vocab_items = session.query(VocabularyItem).filter(
            VocabularyItem.user_id == user.id
        ).all()
        
        if not vocab_items:
            await interaction.followup.send("You don't have any vocabulary yet. Add some with `/vocab`!")
            return
        
        # Create Anki cards
        cards = [
            AnkiCard(
                front=v.word,
                back=v.translation,
                example=v.example or "",
                tags=v.tags or []
            )
            for v in vocab_items
        ]
        
        # Generate deck
        deck_name = f"PolyBiz AI - {user.username}"
        deck_path = anki_generator.create_deck(
            deck_name=deck_name,
            cards=cards,
            template_name="vocabulary"
        )
        
        # Send file
        await interaction.followup.send(
            f"📇 **Anki Deck Generated!**\n{len(cards)} cards",
            file=discord.File(deck_path)
        )


# ============ STATS & LEADERBOARD ============
@bot.tree.command(name="stats", description="View your learning statistics")
async def view_stats(interaction: discord.Interaction):
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            await interaction.response.send_message("Please set up your profile first with `/profile`")
            return
        
        stats = UserService.get_user_stats(session, user.id)
        
        embed = discord.Embed(
            title=f"📊 {user.username}'s Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="💬 Conversations", value=stats['total_conversations'], inline=True)
        embed.add_field(name="📚 Vocabulary", value=stats['total_vocabulary'], inline=True)
        embed.add_field(name="✍️ Writing", value=stats['total_writing_submissions'], inline=True)
        
        # Streaks
        if stats['progress_by_language']:
            max_streak = max([p.get('streak', 0) for p in stats['progress_by_language'].values()])
            embed.add_field(name="🔥 Best Streak", value=f"{max_streak} days", inline=True)
        
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="achievements", description="View your achievements")
async def view_achievements(interaction: discord.Interaction):
    with db.session_scope() as session:
        user = UserService.get_user_by_platform(session, discord_id=str(interaction.user.id))
        
        if not user:
            await interaction.response.send_message("Please set up your profile first with `/profile`")
            return
        
        from database import Achievement
        achievements = session.query(Achievement).filter(
            Achievement.user_id == user.id
        ).all()
        
        embed = discord.Embed(
            title="🏆 Your Achievements",
            color=discord.Color.gold()
        )
        
        for achievement in achievements:
            status = "✅" if achievement.is_completed else f"🔄 {achievement.current_value}/{achievement.target_value}"
            embed.add_field(
                name=f"{status} {achievement.achievement_name}",
                value=achievement.description or f"Progress: {achievement.current_value}/{achievement.target_value}",
                inline=False
            )
        
        if not achievements:
            embed.description = "Start learning to earn achievements!"
        
        await interaction.response.send_message(embed=embed)


# ============ HELP ============
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌏 PolyBiz AI - Commands",
        description="Your AI-powered business language learning assistant",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="👤 Profile",
        value="`/profile` - View your profile\n`/setlanguage` - Set languages\n`/stats` - View statistics\n`/achievements` - View achievements",
        inline=False
    )
    
    embed.add_field(
        name="📝 Writing",
        value="`/review [text]` - Get AI feedback on your writing",
        inline=False
    )
    
    embed.add_field(
        name="🗣️ Conversation",
        value="`/practice` - Start conversation practice\n`/endpractice` - End and get feedback",
        inline=False
    )
    
    embed.add_field(
        name="📚 Learning",
        value="`/lesson [topic]` - Generate a lesson\n`/challenge` - Daily challenge",
        inline=False
    )
    
    embed.add_field(
        name="📇 Vocabulary",
        value="`/vocab` - Add vocabulary\n`/review_vocab` - SRS review\n`/ankideck` - Generate Anki deck",
        inline=False
    )
    
    embed.set_footer(text="Languages: en (English), zh (Chinese), vi (Vietnamese)")
    
    await interaction.response.send_message(embed=embed)


# Run bot
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    
    print("🚀 Starting PolyBiz AI Discord Bot...")
    bot.run(DISCORD_BOT_TOKEN)
