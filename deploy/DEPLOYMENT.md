# PolyBiz AI - Deployment Guide

## Quick Start (Docker - Recommended)

### Prerequisites
- Ubuntu 22.04+ or any Linux with Docker
- Docker & Docker Compose
- 1GB RAM minimum (2GB recommended)
- API keys: Discord, Telegram, OpenAI/Anthropic

### 1. Server Setup (Fresh Ubuntu)

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/jakeveo05-cpu/PolyBiz-AI-Trilingual-Business-/main/deploy/setup-server.sh | sudo bash
```

Or manually:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone repository
git clone https://github.com/jakeveo05-cpu/PolyBiz-AI-Trilingual-Business-.git
cd PolyBiz-AI-Trilingual-Business-
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

Required keys:
- `DISCORD_BOT_TOKEN` - From Discord Developer Portal
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For AI features

### 3. Start Services

```bash
./deploy/deploy.sh start
```

### 4. Check Status

```bash
./deploy/deploy.sh status
./deploy/deploy.sh logs
```

---

## Deployment Options

### Option A: Docker Compose (Recommended)

Best for: VPS, cloud servers, easy management

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Option B: Systemd Services

Best for: Dedicated servers, more control

```bash
# Copy service files
sudo cp deploy/systemd/*.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable polybiz-discord polybiz-telegram polybiz-scheduler
sudo systemctl start polybiz-discord polybiz-telegram polybiz-scheduler

# Check status
sudo systemctl status polybiz-discord
```

### Option C: Railway/Render (PaaS)

Best for: Zero server management

**Railway:**
1. Connect GitHub repo
2. Add environment variables
3. Deploy

**Render:**
1. Create new Web Service
2. Connect repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python -m bots.discord_bot.main`

---

## Cloud Providers

### AWS EC2

```bash
# t3.micro (free tier) or t3.small recommended
# Ubuntu 22.04 AMI

# Security Group: Allow outbound only (bots don't need inbound)
```

### DigitalOcean

```bash
# $6/month Droplet (1GB RAM)
# Ubuntu 22.04

# Use setup script
curl -fsSL https://raw.githubusercontent.com/.../setup-server.sh | sudo bash
```

### Oracle Cloud (Free Tier)

```bash
# ARM instance (free forever)
# 4 OCPU, 24GB RAM available free
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot token |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token |
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key |
| `DATABASE_URL` | No | SQLite by default |
| `AZURE_SPEECH_KEY` | No | For pronunciation |
| `ELEVENLABS_API_KEY` | No | For TTS |

*At least one AI API key required

---

## Monitoring

### View Logs

```bash
# All services
./deploy/deploy.sh logs

# Specific service
./deploy/deploy.sh logs discord-bot
./deploy/deploy.sh logs telegram-bot
./deploy/deploy.sh logs scheduler
```

### Health Check

```bash
# Check if containers are running
docker ps

# Check resource usage
docker stats
```

---

## Updating

```bash
./deploy/deploy.sh update
```

Or manually:

```bash
git pull origin main
docker compose build --no-cache
docker compose up -d
```

---

## Troubleshooting

### Bot not responding

1. Check logs: `./deploy/deploy.sh logs`
2. Verify tokens in `.env`
3. Ensure bot is added to server with correct permissions

### Database errors

```bash
# Reset database
rm data/polybiz.db
./deploy/deploy.sh restart
```

### Out of memory

```bash
# Check memory
free -h

# Restart with limits
docker compose down
docker compose up -d
```

---

## Backup

```bash
# Backup database
cp data/polybiz.db backups/polybiz-$(date +%Y%m%d).db

# Backup everything
tar -czf polybiz-backup-$(date +%Y%m%d).tar.gz data/ .env
```

---

## Security

- Never commit `.env` file
- Use strong, unique bot tokens
- Regularly update dependencies
- Enable 2FA on Discord/Telegram accounts
- Use firewall (only outbound needed)

---

## Support

- GitHub Issues: [Report bugs](https://github.com/jakeveo05-cpu/PolyBiz-AI-Trilingual-Business-/issues)
- Discord: Coming soon
