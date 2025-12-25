"""
Unit Tests for Error Handler
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.error_handler import (
    PolyBizError,
    AIAPIError,
    RateLimitError,
    DatabaseError,
    ValidationError,
    async_error_handler,
    sync_error_handler,
    format_error_for_user
)


class TestCustomExceptions:
    """Tests for custom exception classes"""
    
    def test_polybiz_error(self):
        error = PolyBizError("Internal error", "User friendly message")
        
        assert str(error) == "Internal error"
        assert error.message == "Internal error"
        assert error.user_message == "User friendly message"
    
    def test_polybiz_error_default_user_message(self):
        error = PolyBizError("Internal error")
        
        assert error.user_message == "Đã xảy ra lỗi. Vui lòng thử lại sau."
    
    def test_ai_api_error(self):
        error = AIAPIError("Connection failed", "OpenAI")
        
        assert "OpenAI" in error.user_message
        assert "API" in error.user_message
    
    def test_rate_limit_error(self):
        error = RateLimitError(retry_after=120)
        
        assert error.retry_after == 120
        assert "120" in error.user_message
    
    def test_database_error(self):
        error = DatabaseError("Connection pool exhausted")
        
        assert "lưu trữ" in error.user_message.lower() or "dữ liệu" in error.user_message.lower()
    
    def test_validation_error(self):
        error = ValidationError("Email format invalid", "email")
        
        assert "Email format invalid" in error.user_message


class TestFormatErrorForUser:
    """Tests for format_error_for_user"""
    
    def test_polybiz_error_returns_user_message(self):
        error = PolyBizError("Internal", "Custom user message")
        result = format_error_for_user(error)
        
        assert result == "Custom user message"
    
    def test_rate_limit_error_detected(self):
        error = Exception("Rate limit exceeded (429)")
        result = format_error_for_user(error)
        
        assert "đợi" in result.lower() or "bận" in result.lower()
    
    def test_timeout_error_detected(self):
        error = Exception("Request timeout")
        result = format_error_for_user(error)
        
        assert "thời gian" in result.lower()
    
    def test_connection_error_detected(self):
        error = Exception("Connection refused")
        result = format_error_for_user(error)
        
        assert "kết nối" in result.lower() or "mạng" in result.lower()
    
    def test_generic_error(self):
        error = Exception("Something went wrong")
        result = format_error_for_user(error)
        
        assert "lỗi" in result.lower()


class TestAsyncErrorHandler:
    """Tests for async_error_handler decorator"""
    
    @pytest.mark.asyncio
    async def test_passes_through_success(self):
        @async_error_handler
        async def success_func():
            return "success"
        
        result = await success_func()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_reraises_polybiz_error(self):
        @async_error_handler
        async def error_func():
            raise PolyBizError("Test error")
        
        with pytest.raises(PolyBizError):
            await error_func()
    
    @pytest.mark.asyncio
    async def test_wraps_generic_exception(self):
        @async_error_handler
        async def error_func():
            raise ValueError("Generic error")
        
        with pytest.raises(PolyBizError):
            await error_func()
    
    @pytest.mark.asyncio
    async def test_handles_timeout(self):
        @async_error_handler
        async def timeout_func():
            raise asyncio.TimeoutError()
        
        with pytest.raises(PolyBizError) as exc_info:
            await timeout_func()
        
        assert "thời gian" in exc_info.value.user_message.lower()


class TestSyncErrorHandler:
    """Tests for sync_error_handler decorator"""
    
    def test_passes_through_success(self):
        @sync_error_handler
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"
    
    def test_reraises_polybiz_error(self):
        @sync_error_handler
        def error_func():
            raise PolyBizError("Test error")
        
        with pytest.raises(PolyBizError):
            error_func()
    
    def test_wraps_generic_exception(self):
        @sync_error_handler
        def error_func():
            raise ValueError("Generic error")
        
        with pytest.raises(PolyBizError):
            error_func()
