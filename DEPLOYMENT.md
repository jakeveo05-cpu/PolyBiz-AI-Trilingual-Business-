# PolyBiz AI - Deployment Guide

## Quick Start (Local Development)

### 1. Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd polybiz-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
# Required:
# - DISCORD_BOT_TOKEN
# - TELEGRAM_BOT_TOKEN
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### 3. Run Tests

```bash
# Run local tests (no API keys needed)
python scripts/test_local.py

# Run unit tests
python -m pytest tests/ --ignore=tests/test_simulation.py -v
```

### 4. Run Health Check

```bash
python scripts/run_dev.py health
```

### 5. Start Bots

```bash
# Discord bot
python scripts/run_dev.py discord

# Telegram bot (in another terminal)
python scripts/run_dev.py telegram
```

---

## Docker Deployment

### 1. Build Image

```bash
docker build -t polybiz-ai .
```

### 2. Run with Docker Compose

```bash
# Create .env file first
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Individual Services

```bash
# Discord bot only
docker-compose up -d discord-bot

# Telegram bot only
docker-compose up -d telegram-bot
```

---

## Cloud Deployment

### Railway

1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Render

1. Create new Web Service
2. Connect GitHub repository
3. Set environment variables
4. Deploy

### VPS (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv git

# Clone and setup
git clone <repo-url>
cd polybiz-ai
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo cp deploy/polybiz-discord.service /etc/systemd/system/
sudo systemctl enable polybiz-discord
sudo systemctl start polybiz-discord
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot token |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token |
| `OPENAI_API_KEY` | One of | OpenAI API key |
| `ANTHROPIC_API_KEY` | One of | Anthropic API key |
| `DATABASE_URL` | No | Database URL (default: SQLite) |
| `REDIS_URL` | No | Redis URL for caching |
| `TZ` | No | Timezone (default: Asia/Ho_Chi_Minh) |

---

## Health Check Endpoints

Run health check to verify all components:

```bash
python -m utils.health_check
```

Checks:
- ✅ Environment variables
- ✅ Database connection
- ✅ AI API configuration
- ✅ Disk space
- ✅ Memory

---

## Monitoring

### Logs

Logs are written to `logs/polybiz.log`

```bash
# View logs
tail -f logs/polybiz.log

# Docker logs
docker-compose logs -f discord-bot
```

### Database

SQLite database at `polybiz.db` (or configured DATABASE_URL)

```bash
# Backup database
python -c "from utils.backup import get_backup_manager; get_backup_manager().create_backup()"
```

---

## Troubleshooting

### Bot not responding

1. Check API keys are valid
2. Check bot has correct permissions in Discord/Telegram
3. Check logs for errors

### Rate limit errors

- Rate limiter is configured for 20 requests/minute per user
- Adjust in `utils/rate_limiter.py` if needed

### Database errors

```bash
# Reset database (WARNING: deletes all data)
rm polybiz.db
python -c "from database import get_db; get_db().create_tables()"
```

---

## Support

- GitHub Issues: [link]
- Discord Community: [link]
