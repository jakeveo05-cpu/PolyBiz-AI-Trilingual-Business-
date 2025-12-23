"""
PolyBiz AI - Telegram Bot
"""
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import TELEGRAM_BOT_TOKEN
from agents import WritingCoach, ConversationPartner, LessonGenerator, ToucanTTS

writing_coach = WritingCoach()
lesson_generator = LessonGenerator()
active_conversations = {}
tts = None


def get_tts():
    global tts
    if tts is None:
        try:
            tts = ToucanTTS(device=os.getenv("TOUCAN_DEVICE", "cpu"))
        except:
            pass
    return tts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Review Writing", callback_data="menu_review")],
        [InlineKeyboardButton("🗣️ Practice Conversation", callback_data="menu_practice")],
        [InlineKeyboardButton("📚 Get Lesson", callback_data="menu_lesson")],
        [InlineKeyboardButton("🔊 Text to Speech", callback_data="menu_tts")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌏 **Welcome to PolyBiz AI!**\n\n"
        "Your AI-powered trilingual business language coach.\n\n"
        "Commands:\n"
        "• /review - Submit writing for feedback\n"
        "• /practice - Start conversation practice\n"
        "• /lesson - Generate a lesson\n"
        "• /speak - Text to speech\n"
        "• /help - Show all commands",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "review"
    await update.message.reply_text("📝 Send me your text and I'll provide feedback.")


async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    language = args[0] if args else "en"
    
    active_conversations[user_id] = ConversationPartner(language=language, scenario="networking")
    context.user_data["mode"] = "practice"
    
    await update.message.reply_text(
        f"🎭 **Practice Started!** Language: {language.upper()}\n"
        f"Use /stop to end. Let's begin - introduce yourself!",
        parse_mode="Markdown"
    )


async def speak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /speak [language] [text]\nExample: /speak en Hello world")
        return
    
    language = args[0] if args[0] in ["en", "zh", "vi"] else "en"
    text = " ".join(args[1:]) if args[0] in ["en", "zh", "vi"] else " ".join(args)
    
    tts_instance = get_tts()
    if tts_instance is None:
        await update.message.reply_text("❌ TTS not available")
        return
    
    try:
        output_path = f"audio_output/{update.effective_user.id}.wav"
        os.makedirs("audio_output", exist_ok=True)
        tts_instance.synthesize(text, output_path, language)
        
        await update.message.reply_voice(voice=open(output_path, "rb"), caption=f"🔊 {text}")
        os.remove(output_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_conversations:
        del active_conversations[user_id]
    context.user_data["mode"] = None
    await update.message.reply_text("✅ Session ended!")


async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    topic = " ".join(args) if args else "business email writing"
    
    await update.message.reply_text("📚 Generating lesson...")
    try:
        lesson = await lesson_generator.generate_lesson(topic=topic, language="en", level="B1")
        if len(lesson) > 4000:
            for i in range(0, len(lesson), 4000):
                await update.message.reply_text(lesson[i:i+4000])
        else:
            await update.message.reply_text(lesson)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    mode = context.user_data.get("mode")
    
    if mode == "review":
        await update.message.reply_text("📝 Analyzing...")
        try:
            feedback = await writing_coach.review(text)
            if len(feedback) > 4000:
                for i in range(0, len(feedback), 4000):
                    await update.message.reply_text(feedback[i:i+4000])
            else:
                await update.message.reply_text(feedback)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return
    
    if user_id in active_conversations:
        try:
            response = await active_conversations[user_id].respond(text)
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return
    
    await update.message.reply_text("Use /start to see options.")


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("review", review_command))
    app.add_handler(CommandHandler("practice", practice_command))
    app.add_handler(CommandHandler("speak", speak_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("lesson", lesson_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Telegram bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
