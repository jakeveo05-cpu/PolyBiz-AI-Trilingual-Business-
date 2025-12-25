"""
PolyBiz AI - Configuration Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Settings
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# AI APIs (at least one required)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # For Gemini

# Voice APIs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastasia")

# Toucan TTS
TOUCAN_DEVICE = os.getenv("TOUCAN_DEVICE", "cpu")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///polybiz.db")

# Redis (optional, for caching)
REDIS_URL = os.getenv("REDIS_URL")

# Supported Languages
LANGUAGES = {
    "vi": "Vietnamese",
    "en": "English", 
    "zh": "Chinese"
}

# AI Model Settings - Priority: Gemini > Claude > GPT
# Change DEFAULT_AI_MODEL based on your preferred provider
DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "gemini-1.5-flash")
FALLBACK_AI_MODEL = "gpt-4o-mini"

# Voice Settings
DEFAULT_VOICE_EN = "Rachel"
DEFAULT_VOICE_ZH = "Lily"
DEFAULT_VOICE_VI = "custom"
