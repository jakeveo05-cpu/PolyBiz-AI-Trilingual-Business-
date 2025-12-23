"""
Input Validators - Validate and sanitize user input
"""
import re
from typing import Optional, List, Tuple
from .error_handler import ValidationError


# Constants
MAX_TEXT_LENGTH = 10000  # Max characters for text input
MAX_WORD_LENGTH = 200    # Max characters for single word
MIN_TEXT_LENGTH = 3      # Min characters for meaningful input
SUPPORTED_LANGUAGES = ["en", "zh", "vi"]
SUPPORTED_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SUPPORTED_SCENARIOS = [
    "job_interview", "client_meeting", "negotiation", 
    "presentation", "networking", "phone_followup",
    "salary_negotiation", "complaint_handling"
]


def validate_text_input(
    text: str, 
    field_name: str = "text",
    min_length: int = MIN_TEXT_LENGTH,
    max_length: int = MAX_TEXT_LENGTH
) -> str:
    """
    Validate and sanitize text input
    
    Args:
        text: Input text to validate
        field_name: Name of field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValidationError: If validation fails
    """
    if not text:
        raise ValidationError(f"{field_name} không được để trống", field_name)
    
    # Strip whitespace
    text = text.strip()
    
    if len(text) < min_length:
        raise ValidationError(
            f"{field_name} phải có ít nhất {min_length} ký tự", 
            field_name
        )
    
    if len(text) > max_length:
        raise ValidationError(
            f"{field_name} không được vượt quá {max_length} ký tự", 
            field_name
        )
    
    # Remove potentially harmful content
    text = sanitize_text(text)
    
    return text


def validate_language(language: str) -> str:
    """Validate language code"""
    language = language.lower().strip()
    
    if language not in SUPPORTED_LANGUAGES:
        raise ValidationError(
            f"Ngôn ngữ không hỗ trợ. Chọn: {', '.join(SUPPORTED_LANGUAGES)}",
            "language"
        )
    
    return language


def validate_level(level: str) -> str:
    """Validate CEFR level"""
    level = level.upper().strip()
    
    if level not in SUPPORTED_LEVELS:
        raise ValidationError(
            f"Level không hợp lệ. Chọn: {', '.join(SUPPORTED_LEVELS)}",
            "level"
        )
    
    return level


def validate_scenario(scenario: str) -> str:
    """Validate conversation scenario"""
    scenario = scenario.lower().strip()
    
    if scenario not in SUPPORTED_SCENARIOS:
        raise ValidationError(
            f"Scenario không hợp lệ",
            "scenario"
        )
    
    return scenario


def validate_word(word: str) -> str:
    """Validate vocabulary word"""
    word = word.strip()
    
    if not word:
        raise ValidationError("Từ vựng không được để trống", "word")
    
    if len(word) > MAX_WORD_LENGTH:
        raise ValidationError(
            f"Từ vựng không được vượt quá {MAX_WORD_LENGTH} ký tự",
            "word"
        )
    
    return word


def sanitize_text(text: str) -> str:
    """
    Sanitize text to remove potentially harmful content
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    return text.strip()


def detect_language(text: str) -> str:
    """
    Simple language detection based on character ranges
    
    Returns: 'en', 'zh', 'vi', or 'unknown'
    """
    # Count character types
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    vietnamese_chars = len(re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower()))
    total_chars = len(text)
    
    if total_chars == 0:
        return 'unknown'
    
    # If more than 10% Chinese characters
    if chinese_chars / total_chars > 0.1:
        return 'zh'
    
    # If Vietnamese diacritics present
    if vietnamese_chars > 0:
        return 'vi'
    
    # Default to English
    return 'en'


def validate_email(email: str) -> str:
    """Validate email format"""
    email = email.strip().lower()
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Email không hợp lệ", "email")
    
    return email


def validate_username(username: str) -> str:
    """Validate username"""
    username = username.strip()
    
    if len(username) < 2:
        raise ValidationError("Tên phải có ít nhất 2 ký tự", "username")
    
    if len(username) > 50:
        raise ValidationError("Tên không được vượt quá 50 ký tự", "username")
    
    return username


def check_content_safety(text: str) -> Tuple[bool, Optional[str]]:
    """
    Basic content safety check
    
    Returns:
        (is_safe: bool, reason: Optional[str])
    """
    text_lower = text.lower()
    
    # List of blocked patterns (expand as needed)
    blocked_patterns = [
        r'\b(hack|exploit|inject|malware)\b',
        r'<script',
        r'javascript:',
        r'data:text/html',
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, text_lower):
            return False, "Nội dung không được phép"
    
    return True, None
