"""
Error Handler - Centralized error handling and logging
"""
import logging
import traceback
import asyncio
from functools import wraps
from typing import Callable, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/polybiz.log', encoding='utf-8')
    ]
)

logger = logging.getLogger('polybiz')


class PolyBizError(Exception):
    """Base exception for PolyBiz AI"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or "Đã xảy ra lỗi. Vui lòng thử lại sau."
        super().__init__(self.message)


class AIAPIError(PolyBizError):
    """Error when calling AI APIs (OpenAI/Anthropic)"""
    def __init__(self, message: str, provider: str = "AI"):
        user_msg = f"⚠️ {provider} API đang gặp sự cố. Vui lòng thử lại sau ít phút."
        super().__init__(message, user_msg)


class RateLimitError(PolyBizError):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        user_msg = f"⏳ Bạn đang gửi quá nhiều yêu cầu. Vui lòng đợi {retry_after} giây."
        super().__init__("Rate limit exceeded", user_msg)


class DatabaseError(PolyBizError):
    """Database operation error"""
    def __init__(self, message: str):
        user_msg = "💾 Lỗi lưu trữ dữ liệu. Vui lòng thử lại."
        super().__init__(message, user_msg)


class ValidationError(PolyBizError):
    """Input validation error"""
    def __init__(self, message: str, field: str = None):
        user_msg = f"❌ Dữ liệu không hợp lệ: {message}"
        super().__init__(message, user_msg)


def async_error_handler(func: Callable) -> Callable:
    """Decorator for async functions with error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except PolyBizError as e:
            logger.error(f"PolyBiz Error in {func.__name__}: {e.message}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout in {func.__name__}")
            raise PolyBizError("Request timed out", "⏰ Yêu cầu quá thời gian. Vui lòng thử lại.")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            raise PolyBizError(str(e))
    return wrapper


def sync_error_handler(func: Callable) -> Callable:
    """Decorator for sync functions with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except PolyBizError:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            raise PolyBizError(str(e))
    return wrapper


def log_user_action(action: str, user_id: str, details: dict = None):
    """Log user actions for analytics"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "details": details or {}
    }
    logger.info(f"USER_ACTION: {log_entry}")


def format_error_for_user(error: Exception) -> str:
    """Format error message for end user"""
    if isinstance(error, PolyBizError):
        return error.user_message
    
    # Generic error messages based on error type
    error_str = str(error).lower()
    
    if "rate limit" in error_str or "429" in error_str:
        return "⏳ Hệ thống đang bận. Vui lòng đợi 1 phút rồi thử lại."
    
    if "timeout" in error_str:
        return "⏰ Yêu cầu quá thời gian. Vui lòng thử lại."
    
    if "connection" in error_str or "network" in error_str:
        return "🌐 Lỗi kết nối mạng. Vui lòng kiểm tra internet."
    
    if "api" in error_str or "key" in error_str:
        return "🔑 Lỗi xác thực API. Vui lòng liên hệ admin."
    
    return "❌ Đã xảy ra lỗi. Vui lòng thử lại sau."
