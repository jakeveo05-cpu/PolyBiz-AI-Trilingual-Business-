# 🤖 Hướng dẫn cài đặt AI cho PolyBiz

PolyBiz hỗ trợ 3 chế độ AI:

| Chế độ | Mô tả | Phù hợp với |
|--------|-------|-------------|
| **API** | Dùng cloud AI (Gemini, OpenAI, Claude) | Máy yếu, cần chất lượng cao |
| **Local** | Dùng AI chạy trên máy (Ollama, LM Studio) | Máy mạnh, muốn miễn phí & riêng tư |
| **Hybrid** | Kết hợp cả hai | Tối ưu chi phí & hiệu suất |

---

## 🚀 Bắt đầu nhanh

### 1. Copy file config

```bash
cp config/ai_config.example.json config/ai_config.json
```

### 2. Chọn chế độ

Mở `config/ai_config.json` và đặt `mode`:

```json
{
  "mode": "hybrid"  // "api", "local", hoặc "hybrid"
}
```

---

## ☁️ Chế độ API (Cloud)

### Gemini (Khuyên dùng - MIỄN PHÍ)

1. Lấy API key tại: https://makersuite.google.com/app/apikey
2. Cập nhật config:

```json
{
  "mode": "api",
  "api_providers": {
    "gemini": {
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "model": "gemini-1.5-flash"
    }
  }
}
```

### Groq (MIỄN PHÍ, cực nhanh)

1. Đăng ký tại: https://console.groq.com
2. Cập nhật config:

```json
{
  "api_providers": {
    "groq": {
      "enabled": true,
      "api_key": "YOUR_GROQ_KEY",
      "model": "llama-3.1-70b-versatile"
    }
  }
}
```

### OpenAI / Claude (Trả phí)

```json
{
  "api_providers": {
    "openai": {
      "enabled": true,
      "api_key": "sk-...",
      "model": "gpt-4o-mini"
    },
    "claude": {
      "enabled": true,
      "api_key": "sk-ant-...",
      "model": "claude-3-haiku-20240307"
    }
  }
}
```

---

## 💻 Chế độ Local (Open Source)

### Ollama + Qwen (Khuyên dùng cho tiếng Trung)

**Bước 1: Cài Ollama**

```bash
# Windows (PowerShell)
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

**Bước 2: Tải model Qwen**

```bash
# Chọn theo RAM của bạn:
ollama pull qwen2.5:3b    # 4GB RAM - nhẹ
ollama pull qwen2.5:7b    # 8GB RAM - cân bằng (khuyên dùng)
ollama pull qwen2.5:14b   # 16GB RAM - tốt hơn
ollama pull qwen2.5:32b   # 32GB RAM - rất tốt
```

**Bước 3: Chạy Ollama**

```bash
ollama serve
```

**Bước 4: Cập nhật config**

```json
{
  "mode": "local",
  "local_providers": {
    "ollama": {
      "enabled": true,
      "endpoint": "http://localhost:11434",
      "model": "qwen2.5:7b"
    }
  }
}
```

### LM Studio (GUI dễ dùng)

1. Tải tại: https://lmstudio.ai
2. Tải model từ trong app (tìm "qwen" hoặc "llama")
3. Bật "Local Server" trong app
4. Cập nhật config:

```json
{
  "local_providers": {
    "lmstudio": {
      "enabled": true,
      "endpoint": "http://localhost:1234/v1",
      "model": "local-model"
    }
  }
}
```

---

## ⚡ Chế độ Hybrid (Khuyên dùng)

Kết hợp local cho tác vụ đơn giản, API cho tác vụ phức tạp:

```json
{
  "mode": "hybrid",
  
  "api_providers": {
    "gemini": {
      "enabled": true,
      "api_key": "YOUR_KEY",
      "model": "gemini-1.5-flash"
    }
  },
  
  "local_providers": {
    "ollama": {
      "enabled": true,
      "endpoint": "http://localhost:11434",
      "model": "qwen2.5:7b"
    }
  },
  
  "hybrid_rules": {
    "use_local_for": [
      "quick_translation",
      "vocabulary_lookup",
      "simple_grammar_check",
      "flashcard_generation"
    ],
    "use_api_for": [
      "essay_writing",
      "complex_grammar_explanation",
      "mnemonic_creation",
      "conversation_practice"
    ],
    "fallback_order": ["local", "api"],
    "auto_switch_on_error": true
  }
}
```

---

## 🔧 Models khuyên dùng

### Cho tiếng Trung

| Model | RAM | Chất lượng | Ghi chú |
|-------|-----|------------|---------|
| `qwen2.5:7b` | 8GB | ⭐⭐⭐⭐ | Tốt nhất cho tiếng Trung |
| `qwen2.5:3b` | 4GB | ⭐⭐⭐ | Nhẹ, vẫn tốt |
| `glm4:9b` | 12GB | ⭐⭐⭐⭐ | Zhipu AI, rất tốt |
| `yi:9b` | 12GB | ⭐⭐⭐⭐ | 01.AI, đa ngôn ngữ |

### Đa năng

| Model | RAM | Chất lượng | Ghi chú |
|-------|-----|------------|---------|
| `llama3.1:8b` | 8GB | ⭐⭐⭐⭐ | Meta, đa năng |
| `phi3:medium` | 8GB | ⭐⭐⭐⭐ | Microsoft, nhỏ gọn |
| `gemma2:9b` | 12GB | ⭐⭐⭐⭐ | Google, mới nhất |
| `mistral:7b` | 8GB | ⭐⭐⭐ | Nhanh, ổn định |

---

## 🧪 Test kết nối

```bash
python utils/ai_connector.py
```

Output mong đợi:
```
🤖 PolyBiz AI Connector Test

📊 Status:
{
  "mode": "hybrid",
  "local_providers": ["ollama"],
  "api_providers": ["gemini"]
}

🔍 Checking providers...
  ✅ local/ollama
  ✅ api/gemini

💬 Test chat:
好 (hǎo) là một chữ Hán rất phổ biến...
```

---

## ❓ FAQ

**Q: Máy tôi yếu, nên dùng gì?**
A: Dùng mode `api` với Gemini (miễn phí) hoặc Groq (miễn phí, nhanh).

**Q: Tôi muốn hoàn toàn offline?**
A: Dùng mode `local` với Ollama + qwen2.5:3b (chỉ cần 4GB RAM).

**Q: Model nào tốt nhất cho tiếng Trung?**
A: Qwen2.5 của Alibaba - được train với lượng lớn dữ liệu tiếng Trung.

**Q: Hybrid hoạt động thế nào?**
A: Tác vụ đơn giản (dịch nhanh, tra từ) → Local (miễn phí, nhanh)
   Tác vụ phức tạp (viết luận, giải thích ngữ pháp) → API (chất lượng cao)

---

## 🔗 Links hữu ích

- [Ollama](https://ollama.com) - Chạy LLM local
- [LM Studio](https://lmstudio.ai) - GUI cho local LLM
- [Google AI Studio](https://makersuite.google.com) - Gemini API key
- [Groq Console](https://console.groq.com) - Groq API key (free)
- [OpenRouter](https://openrouter.ai) - Nhiều model, 1 API
