# PolyBiz AI 🌏

**AI-Powered Trilingual Business Language Learning Platform**

Cộng đồng học ngôn ngữ kinh doanh (Việt - Anh - Trung) cho AI Natives - nơi bạn vượt qua nỗi sợ, xây kỷ luật, và kết nối toàn cầu.

## 🎯 Vấn đề giải quyết

- Học ngoại ngữ truyền thống quá chậm, không practical
- AI có thể dịch nhưng không thể thay thế kỹ năng giao tiếp thực
- Thiếu môi trường thực hành business context
- Học một mình dễ bỏ cuộc, thiếu accountability

## 🚀 Giải pháp

Hệ thống AI Agents hỗ trợ học viên 24/7:

| Agent | Chức năng |
|-------|-----------|
| **Writing Coach** | Chấm bài viết, feedback ngữ pháp + style (IELTS/TOEFL/HSK rubrics) |
| **Conversation Partner** | Role-play 8+ business scenarios (interview, negotiation, networking...) |
| **Pronunciation Coach** | Đánh giá phát âm, gợi ý cải thiện (Azure Speech) |
| **Lesson Generator** | Tạo bài học personalized, daily challenges, weekly plans |
| **Content Creator** | Auto-generate social media content cho community |
| **Anki Integration** | Tự động tạo flashcards từ lessons, sync với Anki |
| **Toucan TTS** | Text-to-Speech 7000+ ngôn ngữ (self-hosted, FREE) |

## 🛠 Tech Stack

- **Bot Platform**: Discord + Telegram
- **AI**: Claude/GPT API
- **Voice TTS**: [IMS Toucan](https://github.com/DigitalPhonetics/IMS-Toucan) (7000+ languages, FREE)
- **Voice STT**: Azure Speech / Whisper
- **Automation**: n8n workflows
- **Database**: SQLite/PostgreSQL

## 📁 Project Structure

```
polybiz-ai/
├── agents/
│   ├── base.py              # Base agent class
│   ├── writing_coach.py     # Writing feedback
│   ├── conversation.py      # Business role-play
│   ├── pronunciation.py     # Pronunciation assessment
│   ├── lesson_generator.py  # Personalized lessons
│   └── tts_toucan.py        # Toucan TTS integration
├── bots/
│   ├── discord_bot/         # Discord bot
│   └── telegram_bot/        # Telegram bot
├── config/
│   └── settings.py
├── prompts/                  # AI prompt templates
└── workflows/                # n8n workflow exports
```

## 🏃 Quick Start

```bash
# Clone repo
git clone https://github.com/jakeveo05-cpu/PolyBiz-AI-Trilingual-Business-jakeveo05-gmail.com.git
cd PolyBiz-AI-Trilingual-Business-jakeveo05-gmail.com

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run Discord bot
python bots/discord_bot/main.py
```

## 🔊 Toucan TTS Setup (Optional - Free Self-hosted TTS)

```bash
# Clone Toucan TTS
git clone https://github.com/DigitalPhonetics/IMS-Toucan
cd IMS-Toucan
pip install -e .

# Usage in code
from agents import ToucanTTS

tts = ToucanTTS(device="cpu")  # or "cuda" for GPU
tts.synthesize("Hello world", output_path="output.wav", language="en")
tts.synthesize("Xin chào", output_path="output_vi.wav", language="vi")
tts.synthesize("你好", output_path="output_zh.wav", language="zh")
```

## 📇 Anki Integration (Spaced Repetition Learning)

### Method 1: Generate .apkg files (No Anki needed)

```python
from agents import create_vocabulary_deck

words = [
    {"word": "leverage", "translation": "tận dụng", "example": "We leverage AI tools."},
    {"word": "synergy", "translation": "hiệu ứng cộng hưởng", "example": "Create synergy."}
]

deck_path = create_vocabulary_deck(words, "Business Vocab - Week 1", language="en")
# Download and import into Anki!
```

### Method 2: Live sync with AnkiConnect

```python
from agents import AnkiConnect, AnkiCard

# 1. Install AnkiConnect addon in Anki
# 2. Make sure Anki is running

connector = AnkiConnect()
cards = [
    AnkiCard(front="ROI", back="Return on Investment", tags=["business", "acronyms"])
]
connector.add_cards_bulk("PolyBiz AI - Acronyms", cards)
connector.sync()  # Sync with AnkiWeb
```

### Auto-extract vocabulary from lessons

```python
from agents import VocabularyExtractor

extractor = VocabularyExtractor()

# Extract from any text
lesson_text = "Today we'll learn about leveraging synergies..."
deck_path = await extractor.create_anki_deck_from_text(
    text=lesson_text,
    deck_name="Lesson 1 Vocabulary",
    method="file"  # or "sync" for live sync
)
```

## 🎯 Target Audience

- Người Việt 18-30 tuổi
- Biết 2 thứ tiếng (Việt + Anh hoặc Việt + Trung)
- Muốn học nâng cao cho business context
- AI native, quen dùng công nghệ

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 🙏 Credits

- [IMS Toucan TTS](https://github.com/DigitalPhonetics/IMS-Toucan) - University of Stuttgart
