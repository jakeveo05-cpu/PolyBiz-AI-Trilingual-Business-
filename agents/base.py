"""
Base Agent class for all AI agents
Supports: Google Gemini, Anthropic Claude, OpenAI GPT
"""
from abc import ABC, abstractmethod
import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import (
    ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY,
    DEFAULT_AI_MODEL
)
from utils.error_handler import AIAPIError, RateLimitError, logger
from utils.retry import async_retry, RetryConfig

# Retry config for AI APIs
AI_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=2.0,
    max_delay=30.0,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)

# Lazy imports for optional dependencies
_anthropic = None
_openai = None
_genai = None


def get_anthropic():
    global _anthropic
    if _anthropic is None and ANTHROPIC_API_KEY:
        try:
            from anthropic import Anthropic
            _anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        except ImportError:
            pass
    return _anthropic


def get_openai():
    global _openai
    if _openai is None and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            _openai = OpenAI(api_key=OPENAI_API_KEY)
        except ImportError:
            pass
    return _openai


def get_gemini():
    global _genai
    if _genai is None and GOOGLE_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            _genai = genai
        except ImportError:
            pass
    return _genai


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, model: str = None):
        self.model = model or DEFAULT_AI_MODEL
        self.logger = logging.getLogger(f'polybiz.agent.{self.__class__.__name__}')
        
        # Determine which API to use based on model name or availability
        self._api_priority = self._determine_api_priority()
    
    def _determine_api_priority(self) -> list:
        """Determine API priority based on model and available keys"""
        priority = []
        
        # Check model name for hints
        model_lower = self.model.lower() if self.model else ""
        
        if "gemini" in model_lower:
            if GOOGLE_API_KEY:
                priority.append("gemini")
        elif "claude" in model_lower:
            if ANTHROPIC_API_KEY:
                priority.append("anthropic")
        elif "gpt" in model_lower:
            if OPENAI_API_KEY:
                priority.append("openai")
        
        # Add fallbacks based on available keys
        if GOOGLE_API_KEY and "gemini" not in priority:
            priority.append("gemini")
        if ANTHROPIC_API_KEY and "anthropic" not in priority:
            priority.append("anthropic")
        if OPENAI_API_KEY and "openai" not in priority:
            priority.append("openai")
        
        return priority
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    async def _call_gemini(self, system_prompt: str, user_message: str) -> str:
        """Call Google Gemini API"""
        genai = get_gemini()
        if not genai:
            raise AIAPIError("Gemini not available", "Google")
        
        try:
            # Use gemini-1.5-flash for speed, or gemini-1.5-pro for quality
            model_name = "gemini-1.5-flash"
            if "pro" in self.model.lower():
                model_name = "gemini-1.5-pro"
            
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt
            )
            
            # Run in thread to avoid blocking
            response = await asyncio.to_thread(
                model.generate_content,
                user_message,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.7
                )
            )
            
            return response.text
            
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str:
                self.logger.warning(f"Gemini rate limit: {e}")
                raise RateLimitError(60)
            self.logger.error(f"Gemini API error: {e}")
            raise AIAPIError(str(e), "Google Gemini")
    
    async def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        """Call Anthropic Claude API"""
        anthropic = get_anthropic()
        if not anthropic:
            raise AIAPIError("Anthropic not available", "Anthropic")
        
        try:
            from anthropic import APIError, RateLimitError as AnthropicRateLimitError
            
            response = await asyncio.to_thread(
                anthropic.messages.create,
                model=self.model if "claude" in self.model else "claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
            
        except Exception as e:
            if "RateLimit" in type(e).__name__:
                self.logger.warning(f"Anthropic rate limit: {e}")
                raise RateLimitError(60)
            self.logger.error(f"Anthropic API error: {e}")
            raise AIAPIError(str(e), "Anthropic")
    
    async def _call_openai(self, system_prompt: str, user_message: str) -> str:
        """Call OpenAI GPT API"""
        openai = get_openai()
        if not openai:
            raise AIAPIError("OpenAI not available", "OpenAI")
        
        try:
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                timeout=60.0
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if "RateLimit" in type(e).__name__:
                self.logger.warning(f"OpenAI rate limit: {e}")
                raise RateLimitError(60)
            self.logger.error(f"OpenAI API error: {e}")
            raise AIAPIError(str(e), "OpenAI")
    
    @async_retry(AI_RETRY_CONFIG)
    async def chat(self, user_message: str, context: dict = None) -> str:
        """Send a message to the AI and get response"""
        system_prompt = self.get_system_prompt()
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        last_error = None
        
        # Try each API in priority order
        for api in self._api_priority:
            try:
                if api == "gemini":
                    return await self._call_gemini(system_prompt, user_message)
                elif api == "anthropic":
                    return await self._call_anthropic(system_prompt, user_message)
                elif api == "openai":
                    return await self._call_openai(system_prompt, user_message)
            except RateLimitError:
                raise  # Don't fallback on rate limit
            except AIAPIError as e:
                last_error = e
                self.logger.warning(f"{api} failed, trying next: {e}")
                continue
        
        # No API worked
        if last_error:
            raise last_error
        
        raise AIAPIError(
            "No AI API configured",
            "Chưa cấu hình API. Vui lòng set GOOGLE_API_KEY, ANTHROPIC_API_KEY hoặc OPENAI_API_KEY"
        )
