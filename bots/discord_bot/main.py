"""
PolyBiz AI - Discord Bot
"""
import discord
from discord.ext import commands
from discord import app_commands
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import DISCORD_BOT_TOKEN
from agents import WritingCoach, ConversationPartner, LessonGenerator, ToucanTTS

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

writing_coach = WritingCoach()
lesson_generator = LessonGenerator()
active_conversations = {}

# TTS instance (lazy loaded)
tts = None


def get_tts():
    global tts
    if tts is None:
        try:
            tts = ToucanTTS(device=os.getenv("TOUCAN_DEVICE", "cpu"))
        except:
            pass
    return tts


@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"📝 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.tree.command(name="review", description="Submit writing for AI feedback")
@app_commands.describe(text="Your text to review")
async def review_writing(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    try:
        feedback = await writing_coach.review(text)
        if len(feedback) > 2000:
            chunks = [feedback[i:i+1900] for i in range(0, len(feedback), 1900)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            await interaction.followup.send(feedback)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


@bot.tree.command(name="practice", description="Start a conversation practice session")
@app_commands.describe(
    language="Language to practice (en/zh/vi)",
    scenario="Business scenario"
)
async def start_practice(
    interaction: discord.Interaction, 
    language: str = "en",
    scenario: str = "networking"
):
    user_id = interaction.user.id
    active_conversations[user_id] = ConversationPartner(language=language, scenario=scenario)
    
    await interaction.response.send_message(
        f"🎭 **Conversation Practice Started!**\n\n"
        f"Scenario: {scenario}\n"
        f"Language: {language.upper()}\n\n"
        f"Type your messages to practice. Use `/endpractice` to finish."
    )


@bot.tree.command(name="endpractice", description="End conversation practice")
async def end_practice(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in active_conversations:
        del active_conversations[user_id]
        await interaction.response.send_message("✅ Practice session ended. Great job! 🎉")
    else:
        await interaction.response.send_message("No active practice session.")


@bot.tree.command(name="speak", description="Convert text to speech (Toucan TTS)")
@app_commands.describe(
    text="Text to speak",
    language="Language (en/zh/vi)"
)
async def speak_text(interaction: discord.Interaction, text: str, language: str = "en"):
    await interaction.response.defer()
    
    tts_instance = get_tts()
    if tts_instance is None:
        await interaction.followup.send("❌ TTS not available. Install Toucan TTS first.")
        return
    
    try:
        output_path = f"audio_output/{interaction.user.id}_{interaction.id}.wav"
        os.makedirs("audio_output", exist_ok=True)
        
        tts_instance.synthesize(text, output_path, language)
        
        await interaction.followup.send(
            f"🔊 **{language.upper()}**: {text}",
            file=discord.File(output_path)
        )
        os.remove(output_path)
    except Exception as e:
        await interaction.followup.send(f"❌ TTS Error: {str(e)}")


@bot.tree.command(name="lesson", description="Generate a personalized lesson")
@app_commands.describe(topic="Topic to learn about", language="Target language", level="Your level")
async def generate_lesson(
    interaction: discord.Interaction,
    topic: str,
    language: str = "en",
    level: str = "B1"
):
    await interaction.response.defer()
    try:
        lesson = await lesson_generator.generate_lesson(topic=topic, language=language, level=level)
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
async def daily_challenge(interaction: discord.Interaction, language: str = "en", level: str = "B1"):
    await interaction.response.defer()
    try:
        challenge = await lesson_generator.generate_daily_challenge(language, level)
        await interaction.followup.send(challenge)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = message.author.id
    if user_id in active_conversations:
        async with message.channel.typing():
            try:
                response = await active_conversations[user_id].respond(message.content)
                await message.reply(response)
            except Exception as e:
                await message.reply(f"❌ Error: {str(e)}")
        return
    
    await bot.process_commands(message)


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    bot.run(DISCORD_BOT_TOKEN)
