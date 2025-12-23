"""
Base Agent class for all AI agents
"""
from abc import ABC, abstractmethod
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from anthropic import Anthropic
from openai import OpenAI
from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, DEFAULT_AI_MODEL


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, model: str = DEFAULT_AI_MODEL):
        self.model = model
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.openai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """Send a message to the AI and get response"""
        system_prompt = self.get_system_prompt()
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        if self.anthropic and "claude" in self.model:
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        
        elif self.openai:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError("No AI API configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
