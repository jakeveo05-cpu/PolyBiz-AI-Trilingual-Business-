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

# AI APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Voice APIs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastasia")

# Toucan TTS
TOUCAN_DEVICE = os.getenv("TOUCAN_DEVICE", "cpu")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///polybiz.db")

# Supported Languages
LANGUAGES = {
    "vi": "Vietnamese",
    "en": "English", 
    "zh": "Chinese"
}

# AI Model Settings
DEFAULT_AI_MODEL = "claude-3-5-sonnet-20241022"
FALLBACK_AI_MODEL = "gpt-4o-mini"

# Voice Settings
DEFAULT_VOICE_EN = "Rachel"
DEFAULT_VOICE_ZH = "Lily"
DEFAULT_VOICE_VI = "custom"
