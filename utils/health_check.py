"""
Health Check - Monitor system health and dependencies
"""
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger('polybiz.health')


class HealthStatus:
    """Health check result"""
    def __init__(self, name: str, healthy: bool, message: str = "", details: dict = None):
        self.name = name
        self.healthy = healthy
        self.message = message
        self.details = details or {}
        self.checked_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "healthy": self.healthy,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat()
        }


def check_environment() -> HealthStatus:
    """Check required environment variables"""
    required_vars = [
        "DISCORD_BOT_TOKEN",
        "TELEGRAM_BOT_TOKEN",
    ]
    
    ai_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    has_ai_key = any(os.getenv(var) for var in ai_vars)
    
    if missing:
        return HealthStatus(
            "environment",
            False,
            f"Missing required variables: {', '.join(missing)}",
            {"missing": missing}
        )
    
    if not has_ai_key:
        return HealthStatus(
            "environment",
            False,
            "No AI API key configured (need OPENAI_API_KEY or ANTHROPIC_API_KEY)",
            {"missing_ai_keys": ai_vars}
        )
    
    return HealthStatus("environment", True, "All required variables set")


def check_database() -> HealthStatus:
    """Check database connection"""
    try:
        from database import get_db
        from sqlalchemy import text
        
        db = get_db()
        
        # Try to create tables (idempotent)
        db.create_tables()
        
        # Try a simple query
        with db.session_scope() as session:
            session.execute(text("SELECT 1"))
        
        return HealthStatus("database", True, "Database connected")
        
    except Exception as e:
        return HealthStatus(
            "database",
            False,
            f"Database error: {str(e)}",
            {"error": str(e)}
        )


def check_ai_apis() -> HealthStatus:
    """Check AI API connectivity (without making actual calls)"""
    details = {}
    
    google_key = os.getenv("GOOGLE_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if google_key:
        details["google_gemini"] = "configured" if len(google_key) > 10 else "invalid_key"
    else:
        details["google_gemini"] = "not_configured"
    
    if anthropic_key:
        details["anthropic"] = "configured" if len(anthropic_key) > 10 else "invalid_key"
    else:
        details["anthropic"] = "not_configured"
    
    if openai_key:
        details["openai"] = "configured" if len(openai_key) > 10 else "invalid_key"
    else:
        details["openai"] = "not_configured"
    
    has_valid_key = "configured" in details.values()
    
    return HealthStatus(
        "ai_apis",
        has_valid_key,
        "At least one AI API configured" if has_valid_key else "No valid AI API keys",
        details
    )


def check_disk_space() -> HealthStatus:
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        free_gb = free / (1024 ** 3)
        used_percent = (used / total) * 100
        
        healthy = free_gb > 1.0  # At least 1GB free
        
        return HealthStatus(
            "disk_space",
            healthy,
            f"{free_gb:.1f}GB free ({used_percent:.1f}% used)",
            {"free_gb": round(free_gb, 2), "used_percent": round(used_percent, 1)}
        )
        
    except Exception as e:
        return HealthStatus("disk_space", True, "Could not check disk space")


def check_memory() -> HealthStatus:
    """Check memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        available_mb = memory.available / (1024 ** 2)
        used_percent = memory.percent
        
        healthy = available_mb > 256  # At least 256MB available
        
        return HealthStatus(
            "memory",
            healthy,
            f"{available_mb:.0f}MB available ({used_percent:.1f}% used)",
            {"available_mb": round(available_mb), "used_percent": used_percent}
        )
        
    except ImportError:
        return HealthStatus("memory", True, "psutil not installed, skipping memory check")
    except Exception as e:
        return HealthStatus("memory", True, f"Could not check memory: {e}")


def run_health_checks() -> Dict:
    """Run all health checks and return summary"""
    checks = [
        check_environment(),
        check_database(),
        check_ai_apis(),
        check_disk_space(),
        check_memory(),
    ]
    
    all_healthy = all(c.healthy for c in checks)
    
    return {
        "healthy": all_healthy,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": [c.to_dict() for c in checks],
        "summary": {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.healthy),
            "failed": sum(1 for c in checks if not c.healthy)
        }
    }


def print_health_report():
    """Print formatted health report"""
    result = run_health_checks()
    
    print("\n" + "=" * 50)
    print("🏥 PolyBiz AI Health Check")
    print("=" * 50)
    
    for check in result["checks"]:
        status = "✅" if check["healthy"] else "❌"
        print(f"{status} {check['name']}: {check['message']}")
    
    print("-" * 50)
    summary = result["summary"]
    overall = "✅ HEALTHY" if result["healthy"] else "❌ UNHEALTHY"
    print(f"Overall: {overall} ({summary['passed']}/{summary['total']} checks passed)")
    print("=" * 50 + "\n")
    
    return result["healthy"]


if __name__ == "__main__":
    # Run health check from command line
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    healthy = print_health_report()
    sys.exit(0 if healthy else 1)
