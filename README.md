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
| **Writing Coach** | Chấm bài viết, feedback ngữ pháp + style |
| **Conversation Partner** | Role-play scenarios kinh doanh |
| **Pronunciation Coach** | Đánh giá phát âm, gợi ý cải thiện |
| **Lesson Generator** | Tạo bài học personalized |
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
