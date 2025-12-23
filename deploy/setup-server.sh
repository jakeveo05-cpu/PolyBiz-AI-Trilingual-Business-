#!/bin/bash
# PolyBiz AI - Server Setup Script
# Run on a fresh Ubuntu 22.04+ server

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./setup-server.sh)"
    exit 1
fi

log_info "Setting up PolyBiz AI server..."

# Update system
log_info "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose
log_info "Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# Create polybiz user
log_info "Creating polybiz user..."
if ! id "polybiz" &>/dev/null; then
    useradd -m -s /bin/bash polybiz
    usermod -aG docker polybiz
fi

# Create directories
log_info "Creating directories..."
mkdir -p /opt/polybiz-ai
mkdir -p /var/log/polybiz
chown -R polybiz:polybiz /opt/polybiz-ai
chown -R polybiz:polybiz /var/log/polybiz

# Clone repository
log_info "Cloning repository..."
if [ ! -d "/opt/polybiz-ai/.git" ]; then
    sudo -u polybiz git clone https://github.com/jakeveo05-cpu/PolyBiz-AI-Trilingual-Business-.git /opt/polybiz-ai
fi

# Setup environment
log_info "Setting up environment..."
cd /opt/polybiz-ai
if [ ! -f ".env" ]; then
    cp .env.example .env
    log_warn "Please edit /opt/polybiz-ai/.env with your API keys!"
fi

# Create data directories
mkdir -p data logs output
chown -R polybiz:polybiz data logs output

# Make deploy script executable
chmod +x deploy/deploy.sh
chmod +x deploy/setup-server.sh

log_info "=========================================="
log_info "Server setup complete!"
log_info ""
log_info "Next steps:"
log_info "1. Edit /opt/polybiz-ai/.env with your API keys"
log_info "2. cd /opt/polybiz-ai"
log_info "3. ./deploy/deploy.sh start"
log_info ""
log_info "Commands:"
log_info "  ./deploy/deploy.sh start   - Start bots"
log_info "  ./deploy/deploy.sh stop    - Stop bots"
log_info "  ./deploy/deploy.sh logs    - View logs"
log_info "  ./deploy/deploy.sh status  - Check status"
log_info "=========================================="
