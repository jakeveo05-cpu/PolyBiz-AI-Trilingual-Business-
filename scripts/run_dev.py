#!/usr/bin/env python
"""
Development Runner - Run bots locally for testing
Requires real API keys in .env file
"""
import os
import sys
import asyncio
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()


def check_env():
    """Check required environment variables"""
    missing = []
    
    # Check bot tokens
    if not os.getenv("DISCORD_BOT_TOKEN"):
        missing.append("DISCORD_BOT_TOKEN")
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        missing.append("TELEGRAM_BOT_TOKEN")
    
    # Check AI keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease create a .env file with these variables.")
        print("See .env.example for reference.")
        return False
    
    return True


def run_discord():
    """Run Discord bot"""
    print("🤖 Starting Discord bot...")
    from bots.discord_bot.main import bot, DISCORD_BOT_TOKEN
    
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not set")
        return
    
    bot.run(DISCORD_BOT_TOKEN)


def run_telegram():
    """Run Telegram bot"""
    print("🤖 Starting Telegram bot...")
    from bots.telegram_bot.main import main
    main()


def run_health_check():
    """Run health check"""
    from utils.health_check import print_health_report
    return print_health_report()


def main():
    parser = argparse.ArgumentParser(description="PolyBiz AI Development Runner")
    parser.add_argument(
        "command",
        choices=["discord", "telegram", "health", "test"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("  🚀 PolyBiz AI - Development Mode")
    print("="*50 + "\n")
    
    if args.command == "health":
        run_health_check()
        return
    
    if args.command == "test":
        # Run local tests
        import subprocess
        subprocess.run([sys.executable, "scripts/test_local.py"])
        return
    
    # Check environment for bot commands
    if not check_env():
        sys.exit(1)
    
    if args.command == "discord":
        run_discord()
    elif args.command == "telegram":
        run_telegram()


if __name__ == "__main__":
    main()
