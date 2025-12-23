"""
Base Agent class for all AI agents
"""
from abc import ABC, abstractmethod
import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from anthropic import Anthropic, APIError, RateLimitError as AnthropicRateLimitError
from openai import OpenAI, APIError as OpenAIAPIError, RateLimitError as OpenAIRateLimitError
from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, DEFAULT_AI_MODEL
from utils.error_handler import AIAPIError, RateLimitError, async_error_handler, logger
from utils.retry import async_retry, RetryConfig

# Retry config for AI APIs
AI_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=2.0,
    max_delay=30.0,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, model: str = DEFAULT_AI_MODEL):
        self.model = model
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.openai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.logger = logging.getLogger(f'polybiz.agent.{self.__class__.__name__}')
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @async_retry(AI_RETRY_CONFIG)
    async def chat(self, user_message: str, context: dict = None) -> str:
        """Send a message to the AI and get response"""
        system_prompt = self.get_system_prompt()
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        # Try Anthropic first
        if self.anthropic and "claude" in self.model:
            try:
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                return response.content[0].text
            except AnthropicRateLimitError as e:
                self.logger.warning(f"Anthropic rate limit: {e}")
                raise RateLimitError(60)
            except APIError as e:
                self.logger.error(f"Anthropic API error: {e}")
                # Fall through to OpenAI
                if not self.openai:
                    raise AIAPIError(str(e), "Anthropic")
        
        # Fallback to OpenAI
        if self.openai:
            try:
                response = self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    timeout=60.0
                )
                return response.choices[0].message.content
            except OpenAIRateLimitError as e:
                self.logger.warning(f"OpenAI rate limit: {e}")
                raise RateLimitError(60)
            except OpenAIAPIError as e:
                self.logger.error(f"OpenAI API error: {e}")
                raise AIAPIError(str(e), "OpenAI")
        
        raise AIAPIError(
            "No AI API configured",
            "Chưa cấu hình API. Vui lòng set ANTHROPIC_API_KEY hoặc OPENAI_API_KEY"
        )
