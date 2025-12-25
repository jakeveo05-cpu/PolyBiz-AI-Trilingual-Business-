"""
PolyBiz AI Connector - Unified interface for multiple AI providers
Supports: API (cloud), Open Source (local), Hybrid modes
"""

import json
import os
import httpx
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path


class AIMode(Enum):
    API = "api"           # Cloud APIs only (Gemini, OpenAI, Claude, etc.)
    LOCAL = "local"       # Local models only (Ollama, LM Studio, etc.)
    HYBRID = "hybrid"     # Smart switching between local and API


class TaskType(Enum):
    """Task types for hybrid mode routing"""
    QUICK_TRANSLATION = "quick_translation"
    VOCABULARY_LOOKUP = "vocabulary_lookup"
    SIMPLE_GRAMMAR = "simple_grammar_check"
    FLASHCARD = "flashcard_generation"
    ESSAY = "essay_writing"
    COMPLEX_GRAMMAR = "complex_grammar_explanation"
    MNEMONIC = "mnemonic_creation"
    CONVERSATION = "conversation_practice"
    GENERAL = "general"


class BaseProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass


class OllamaProvider(BaseProvider):
    """Ollama local provider - supports Qwen, Llama, Phi, etc."""
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        endpoint = self.config.get("endpoint", "http://localhost:11434")
        model = kwargs.get("model", self.config.get("model", "qwen2.5:7b"))
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{endpoint}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 2048)
                    }
                }
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
    
    async def health_check(self) -> bool:
        try:
            endpoint = self.config.get("endpoint", "http://localhost:11434")
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{endpoint}/api/tags")
                return response.status_code == 200
        except:
            return False


class OpenAICompatibleProvider(BaseProvider):
    """OpenAI-compatible API provider (OpenAI, Groq, OpenRouter, LM Studio)"""
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        endpoint = self.config.get("endpoint", "https://api.openai.com/v1")
        api_key = self.config.get("api_key", "")
        model = kwargs.get("model", self.config.get("model", "gpt-4o-mini"))
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenRouter specific header
        if "openrouter" in endpoint:
            headers["HTTP-Referer"] = "https://polybiz.ai"
            headers["X-Title"] = "PolyBiz AI Learning"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{endpoint}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048)
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def health_check(self) -> bool:
        try:
            endpoint = self.config.get("endpoint")
            api_key = self.config.get("api_key", "")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{endpoint}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                return response.status_code == 200
        except:
            return False


class GeminiProvider(BaseProvider):
    """Google Gemini provider"""
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        api_key = self.config.get("api_key", "")
        model = kwargs.get("model", self.config.get("model", "gemini-1.5-flash"))
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                params={"key": api_key},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "maxOutputTokens": kwargs.get("max_tokens", 2048)
                    }
                }
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    async def health_check(self) -> bool:
        try:
            api_key = self.config.get("api_key", "")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": api_key}
                )
                return response.status_code == 200
        except:
            return False


class ClaudeProvider(BaseProvider):
    """Anthropic Claude provider"""
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        api_key = self.config.get("api_key", "")
        model = kwargs.get("model", self.config.get("model", "claude-3-haiku-20240307"))
        
        # Extract system message if present
        system = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "system": system,
                    "messages": chat_messages
                }
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
    
    async def health_check(self) -> bool:
        # Claude doesn't have a simple health check endpoint
        return bool(self.config.get("api_key"))



class AIConnector:
    """
    Main AI Connector class - unified interface for all providers
    
    Usage:
        connector = AIConnector("config/ai_config.json")
        
        # Simple chat
        response = await connector.chat("Giải thích ngữ pháp 把 trong tiếng Trung")
        
        # With task type (for hybrid routing)
        response = await connector.chat(
            "Dịch: Tôi yêu bạn",
            task_type=TaskType.QUICK_TRANSLATION
        )
        
        # Specialized methods
        mnemonic = await connector.create_mnemonic("好")
        grammar = await connector.explain_grammar("我把书放在桌子上")
        essay = await connector.write_essay("我的家庭", level="HSK3")
    """
    
    def __init__(self, config_path: str = "config/ai_config.json"):
        self.config = self._load_config(config_path)
        self.mode = AIMode(self.config.get("mode", "hybrid"))
        self.preferences = self.config.get("preferences", {})
        
        # Initialize providers
        self.api_providers: Dict[str, BaseProvider] = {}
        self.local_providers: Dict[str, BaseProvider] = {}
        self._init_providers()
        
        # Hybrid routing rules
        self.hybrid_rules = self.config.get("hybrid_rules", {})
        self.local_tasks = set(self.hybrid_rules.get("use_local_for", []))
        self.api_tasks = set(self.hybrid_rules.get("use_api_for", []))
    
    def _load_config(self, config_path: str) -> Dict:
        path = Path(config_path)
        if not path.exists():
            # Try example config
            example_path = Path("config/ai_config.example.json")
            if example_path.exists():
                print(f"⚠️  Config not found at {config_path}, using example config")
                path = example_path
            else:
                raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _init_providers(self):
        """Initialize all enabled providers"""
        
        # API providers
        api_configs = self.config.get("api_providers", {})
        
        if api_configs.get("gemini", {}).get("enabled"):
            self.api_providers["gemini"] = GeminiProvider(api_configs["gemini"])
        
        if api_configs.get("openai", {}).get("enabled"):
            self.api_providers["openai"] = OpenAICompatibleProvider(api_configs["openai"])
        
        if api_configs.get("claude", {}).get("enabled"):
            self.api_providers["claude"] = ClaudeProvider(api_configs["claude"])
        
        if api_configs.get("groq", {}).get("enabled"):
            self.api_providers["groq"] = OpenAICompatibleProvider(api_configs["groq"])
        
        if api_configs.get("openrouter", {}).get("enabled"):
            self.api_providers["openrouter"] = OpenAICompatibleProvider(api_configs["openrouter"])
        
        # Local providers
        local_configs = self.config.get("local_providers", {})
        
        if local_configs.get("ollama", {}).get("enabled"):
            self.local_providers["ollama"] = OllamaProvider(local_configs["ollama"])
        
        if local_configs.get("lmstudio", {}).get("enabled"):
            self.local_providers["lmstudio"] = OpenAICompatibleProvider(local_configs["lmstudio"])
        
        if local_configs.get("llamacpp", {}).get("enabled"):
            self.local_providers["llamacpp"] = OpenAICompatibleProvider(local_configs["llamacpp"])
    
    def _get_provider(self, task_type: TaskType = TaskType.GENERAL) -> BaseProvider:
        """Get appropriate provider based on mode and task type"""
        
        if self.mode == AIMode.LOCAL:
            if self.local_providers:
                return list(self.local_providers.values())[0]
            raise RuntimeError("No local providers configured")
        
        elif self.mode == AIMode.API:
            if self.api_providers:
                return list(self.api_providers.values())[0]
            raise RuntimeError("No API providers configured")
        
        else:  # HYBRID
            task_name = task_type.value
            
            # Check if task should use local
            if task_name in self.local_tasks and self.local_providers:
                return list(self.local_providers.values())[0]
            
            # Check if task should use API
            if task_name in self.api_tasks and self.api_providers:
                return list(self.api_providers.values())[0]
            
            # Default: prefer local if available
            fallback_order = self.hybrid_rules.get("fallback_order", ["local", "api"])
            for fallback in fallback_order:
                if fallback == "local" and self.local_providers:
                    return list(self.local_providers.values())[0]
                if fallback == "api" and self.api_providers:
                    return list(self.api_providers.values())[0]
            
            raise RuntimeError("No providers available")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on preferences"""
        lang = self.preferences.get("response_language", "vi")
        target = self.preferences.get("target_language", "zh")
        style = self.preferences.get("explanation_style", "detailed")
        
        lang_names = {"vi": "tiếng Việt", "en": "English", "zh": "中文"}
        
        return f"""Bạn là trợ lý học ngôn ngữ chuyên nghiệp.
- Trả lời bằng {lang_names.get(lang, lang)}
- Ngôn ngữ đang học: {target}
- Phong cách giải thích: {style}
- Luôn kèm pinyin khi có chữ Hán
- Đưa ví dụ thực tế, dễ hiểu"""
    
    async def chat(
        self, 
        message: str, 
        task_type: TaskType = TaskType.GENERAL,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Send a chat message to AI
        
        Args:
            message: User message
            task_type: Type of task (for hybrid routing)
            system_prompt: Custom system prompt (optional)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            AI response string
        """
        provider = self._get_provider(task_type)
        
        messages = [
            {"role": "system", "content": system_prompt or self._build_system_prompt()},
            {"role": "user", "content": message}
        ]
        
        # Merge preferences with kwargs
        params = {**self.preferences, **kwargs}
        
        try:
            return await provider.chat(messages, **params)
        except Exception as e:
            # Auto-switch on error if enabled
            if self.hybrid_rules.get("auto_switch_on_error") and self.mode == AIMode.HYBRID:
                # Try other providers
                all_providers = list(self.local_providers.values()) + list(self.api_providers.values())
                for p in all_providers:
                    if p != provider:
                        try:
                            return await p.chat(messages, **params)
                        except:
                            continue
            raise e
    
    # ============ Specialized Methods ============
    
    async def create_mnemonic(self, character: str) -> Dict[str, Any]:
        """Create mnemonic story for a Chinese character"""
        prompt = f"""Tạo mnemonic (câu chuyện ghi nhớ) cho chữ Hán: {character}

Trả về JSON với format:
{{
    "character": "{character}",
    "pinyin": "...",
    "meaning": "...",
    "components": [
        {{"part": "bộ thủ", "meaning": "nghĩa"}}
    ],
    "mnemonic_vi": "Câu chuyện ghi nhớ bằng tiếng Việt",
    "mnemonic_en": "Mnemonic story in English",
    "examples": [
        {{"word": "từ ghép", "pinyin": "...", "meaning": "..."}}
    ]
}}"""
        
        response = await self.chat(prompt, task_type=TaskType.MNEMONIC)
        
        # Try to parse JSON from response
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"character": character, "raw_response": response}
    
    async def explain_grammar(self, sentence: str) -> str:
        """Explain grammar structure of a Chinese sentence"""
        prompt = f"""Phân tích ngữ pháp câu tiếng Trung sau:

"{sentence}"

Giải thích:
1. Cấu trúc ngữ pháp chính
2. Từng thành phần (chủ ngữ, vị ngữ, tân ngữ, bổ ngữ...)
3. Điểm ngữ pháp đặc biệt (nếu có)
4. Ví dụ tương tự"""
        
        return await self.chat(prompt, task_type=TaskType.COMPLEX_GRAMMAR)
    
    async def translate(self, text: str, direction: str = "vi->zh") -> str:
        """Quick translation"""
        src, tgt = direction.split("->")
        lang_names = {"vi": "tiếng Việt", "en": "English", "zh": "tiếng Trung"}
        
        prompt = f"Dịch từ {lang_names.get(src, src)} sang {lang_names.get(tgt, tgt)}:\n\n{text}"
        
        return await self.chat(prompt, task_type=TaskType.QUICK_TRANSLATION)
    
    async def write_essay(self, topic: str, level: str = "HSK3", word_count: int = 200) -> str:
        """Write an essay in Chinese"""
        prompt = f"""Viết một bài luận tiếng Trung về chủ đề: {topic}

Yêu cầu:
- Trình độ: {level}
- Độ dài: khoảng {word_count} chữ
- Kèm pinyin
- Giải thích từ vựng khó"""
        
        return await self.chat(prompt, task_type=TaskType.ESSAY)
    
    async def correct_writing(self, text: str) -> str:
        """Correct Chinese writing with explanations"""
        prompt = f"""Sửa lỗi bài viết tiếng Trung sau và giải thích:

"{text}"

Format:
1. Bản sửa hoàn chỉnh
2. Danh sách lỗi và cách sửa
3. Gợi ý cải thiện"""
        
        return await self.chat(prompt, task_type=TaskType.COMPLEX_GRAMMAR)
    
    async def generate_flashcards(self, topic: str, count: int = 10) -> List[Dict]:
        """Generate flashcards for a topic"""
        prompt = f"""Tạo {count} flashcard học từ vựng tiếng Trung về chủ đề: {topic}

Trả về JSON array:
[
    {{
        "front": "từ tiếng Trung",
        "back": "pinyin | nghĩa tiếng Việt",
        "example": "câu ví dụ"
    }}
]"""
        
        response = await self.chat(prompt, task_type=TaskType.FLASHCARD)
        
        try:
            import re
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return [{"raw_response": response}]
    
    # ============ Health & Status ============
    
    async def check_providers(self) -> Dict[str, bool]:
        """Check health of all configured providers"""
        status = {}
        
        for name, provider in self.local_providers.items():
            status[f"local/{name}"] = await provider.health_check()
        
        for name, provider in self.api_providers.items():
            status[f"api/{name}"] = await provider.health_check()
        
        return status
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connector status"""
        return {
            "mode": self.mode.value,
            "local_providers": list(self.local_providers.keys()),
            "api_providers": list(self.api_providers.keys()),
            "preferences": self.preferences
        }


# ============ CLI for testing ============

async def main():
    """Test AI Connector"""
    import asyncio
    
    print("🤖 PolyBiz AI Connector Test\n")
    
    connector = AIConnector("config/ai_config.example.json")
    
    # Check status
    print("📊 Status:")
    print(json.dumps(connector.get_status(), indent=2, ensure_ascii=False))
    
    # Check providers
    print("\n🔍 Checking providers...")
    status = await connector.check_providers()
    for name, ok in status.items():
        emoji = "✅" if ok else "❌"
        print(f"  {emoji} {name}")
    
    # Test chat if any provider is available
    if any(status.values()):
        print("\n💬 Test chat:")
        try:
            response = await connector.chat("Xin chào! Giải thích ngắn gọn chữ 好")
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
