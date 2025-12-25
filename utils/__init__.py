"""
PolyBiz AI Utilities
"""
from .error_handler import (
    PolyBizError,
    AIAPIError,
    RateLimitError,
    DatabaseError,
    ValidationError,
    async_error_handler,
    sync_error_handler,
    format_error_for_user,
    log_user_action,
    logger
)
from .rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    get_rate_limiter,
    check_and_record
)
from .validators import (
    validate_text_input,
    validate_language,
    validate_level,
    validate_scenario,
    validate_word,
    sanitize_text,
    detect_language,
    check_content_safety
)
from .retry import (
    async_retry,
    sync_retry,
    RetryConfig,
    AI_API_RETRY,
    DATABASE_RETRY
)
from .session_manager import (
    Session,
    SessionManager,
    get_session_manager
)
from .backup import (
    DatabaseBackup,
    get_backup_manager,
    scheduled_backup
)
from .health_check import (
    run_health_checks,
    print_health_report
)
from .cache import (
    CacheManager,
    get_cache_manager,
    cached,
    cache_key
)

__all__ = [
    # Error handling
    "PolyBizError",
    "AIAPIError", 
    "RateLimitError",
    "DatabaseError",
    "ValidationError",
    "async_error_handler",
    "sync_error_handler",
    "format_error_for_user",
    "log_user_action",
    "logger",
    # Rate limiting
    "RateLimiter",
    "RateLimitConfig",
    "get_rate_limiter",
    "check_and_record",
    # Validators
    "validate_text_input",
    "validate_language",
    "validate_level",
    "validate_scenario",
    "validate_word",
    "sanitize_text",
    "detect_language",
    "check_content_safety",
    # Retry
    "async_retry",
    "sync_retry",
    "RetryConfig",
    "AI_API_RETRY",
    "DATABASE_RETRY",
    # Session management
    "Session",
    "SessionManager",
    "get_session_manager",
    # Backup
    "DatabaseBackup",
    "get_backup_manager",
    "scheduled_backup",
    # Health check
    "run_health_checks",
    "print_health_report",
    # Cache
    "CacheManager",
    "get_cache_manager",
    "cached",
    "cache_key",
]
