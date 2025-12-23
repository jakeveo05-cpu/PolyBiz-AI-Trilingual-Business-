#!/bin/bash
# PolyBiz AI - Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|status]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check requirements
check_requirements() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Copy .env.example to .env and configure it."
        exit 1
    fi
}

# Docker compose command (v1 or v2)
docker_compose() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

start() {
    log_info "Starting PolyBiz AI..."
    check_requirements
    
    # Create directories
    mkdir -p data logs output
    
    # Build and start
    docker_compose up -d --build
    
    log_info "PolyBiz AI started successfully!"
    log_info "Use './deploy.sh logs' to view logs"
}

stop() {
    log_info "Stopping PolyBiz AI..."
    docker_compose down
    log_info "PolyBiz AI stopped"
}

restart() {
    log_info "Restarting PolyBiz AI..."
    stop
    start
}

logs() {
    SERVICE=${2:-""}
    if [ -n "$SERVICE" ]; then
        docker_compose logs -f "$SERVICE"
    else
        docker_compose logs -f
    fi
}

status() {
    log_info "PolyBiz AI Status:"
    docker_compose ps
}

update() {
    log_info "Updating PolyBiz AI..."
    git pull origin main
    docker_compose build --no-cache
    restart
    log_info "Update complete!"
}

# Main
case "${1:-help}" in
    start)   start ;;
    stop)    stop ;;
    restart) restart ;;
    logs)    logs "$@" ;;
    status)  status ;;
    update)  update ;;
    *)
        echo "PolyBiz AI Deployment"
        echo ""
        echo "Usage: $0 {start|stop|restart|logs|status|update}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View logs (optional: service name)"
        echo "  status  - Show service status"
        echo "  update  - Pull latest code and restart"
        ;;
esac
