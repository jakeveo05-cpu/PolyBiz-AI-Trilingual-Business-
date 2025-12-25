"""
Unit Tests for Validators
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.validators import (
    validate_text_input,
    validate_language,
    validate_level,
    validate_scenario,
    validate_word,
    sanitize_text,
    detect_language,
    check_content_safety
)
from utils.error_handler import ValidationError


class TestValidateTextInput:
    """Tests for validate_text_input"""
    
    def test_valid_text(self):
        result = validate_text_input("Hello world", "test")
        assert result == "Hello world"
    
    def test_strips_whitespace(self):
        result = validate_text_input("  Hello world  ", "test")
        assert result == "Hello world"
    
    def test_empty_text_raises(self):
        with pytest.raises(ValidationError):
            validate_text_input("", "test")
    
    def test_none_text_raises(self):
        with pytest.raises(ValidationError):
            validate_text_input(None, "test")
    
    def test_too_short_raises(self):
        with pytest.raises(ValidationError):
            validate_text_input("ab", "test", min_length=5)
    
    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_text_input("a" * 100, "test", max_length=50)
    
    def test_custom_min_length(self):
        result = validate_text_input("abc", "test", min_length=2)
        assert result == "abc"


class TestValidateLanguage:
    """Tests for validate_language"""
    
    def test_valid_english(self):
        assert validate_language("en") == "en"
    
    def test_valid_chinese(self):
        assert validate_language("zh") == "zh"
    
    def test_valid_vietnamese(self):
        assert validate_language("vi") == "vi"
    
    def test_uppercase_normalized(self):
        assert validate_language("EN") == "en"
    
    def test_with_whitespace(self):
        assert validate_language("  en  ") == "en"
    
    def test_invalid_language_raises(self):
        with pytest.raises(ValidationError):
            validate_language("fr")
    
    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_language("")


class TestValidateLevel:
    """Tests for validate_level"""
    
    def test_valid_levels(self):
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            assert validate_level(level) == level
    
    def test_lowercase_normalized(self):
        assert validate_level("a1") == "A1"
    
    def test_with_whitespace(self):
        assert validate_level("  B1  ") == "B1"
    
    def test_invalid_level_raises(self):
        with pytest.raises(ValidationError):
            validate_level("D1")


class TestValidateScenario:
    """Tests for validate_scenario"""
    
    def test_valid_scenarios(self):
        valid = ["job_interview", "client_meeting", "negotiation", "networking"]
        for scenario in valid:
            assert validate_scenario(scenario) == scenario
    
    def test_uppercase_normalized(self):
        assert validate_scenario("JOB_INTERVIEW") == "job_interview"
    
    def test_invalid_scenario_raises(self):
        with pytest.raises(ValidationError):
            validate_scenario("invalid_scenario")


class TestValidateWord:
    """Tests for validate_word"""
    
    def test_valid_word(self):
        assert validate_word("hello") == "hello"
    
    def test_strips_whitespace(self):
        assert validate_word("  hello  ") == "hello"
    
    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_word("")
    
    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_word("a" * 300)


class TestSanitizeText:
    """Tests for sanitize_text"""
    
    def test_removes_null_bytes(self):
        result = sanitize_text("hello\x00world")
        assert "\x00" not in result
    
    def test_normalizes_whitespace(self):
        result = sanitize_text("hello    world")
        assert result == "hello world"
    
    def test_removes_control_chars(self):
        result = sanitize_text("hello\x07world")
        assert "\x07" not in result
    
    def test_preserves_newlines(self):
        # Newlines are converted to spaces by the regex
        result = sanitize_text("hello\nworld")
        assert "hello" in result and "world" in result


class TestDetectLanguage:
    """Tests for detect_language"""
    
    def test_detect_chinese(self):
        assert detect_language("你好世界") == "zh"
    
    def test_detect_vietnamese(self):
        assert detect_language("Xin chào") == "vi"
    
    def test_detect_english(self):
        assert detect_language("Hello world") == "en"
    
    def test_empty_string(self):
        assert detect_language("") == "unknown"
    
    def test_mixed_defaults_to_dominant(self):
        # Mostly Chinese
        assert detect_language("你好你好你好 hello") == "zh"


class TestCheckContentSafety:
    """Tests for check_content_safety"""
    
    def test_safe_content(self):
        is_safe, reason = check_content_safety("Hello, how are you?")
        assert is_safe is True
        assert reason is None
    
    def test_script_tag_blocked(self):
        is_safe, reason = check_content_safety("<script>alert('xss')</script>")
        assert is_safe is False
    
    def test_javascript_blocked(self):
        is_safe, reason = check_content_safety("javascript:void(0)")
        assert is_safe is False
