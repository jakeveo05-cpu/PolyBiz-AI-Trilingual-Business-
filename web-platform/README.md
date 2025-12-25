# PolyBiz Learning Stage 🎭

**Immersive AI-Native Learning Platform**

Sân khấu học tập nơi AI Natives nhập vai, sáng tạo và khám phá hành trình tự học của mình.

## 🎯 Vision

- **Học ngoại ngữ là cái cớ** - Xây dựng cộng đồng AI Natives
- **Web như sân khấu** - UX/UI ấn tượng, immersive experience
- **Learn by Building** - Từ Consumer → Explorer → Creator

## 🛠 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + Shadcn UI
- **Animation**: Framer Motion + GSAP
- **Hand Tracking**: MediaPipe Hands
- **Database**: Neon (PostgreSQL) + Drizzle ORM
- **Auth**: Clerk
- **AI**: Google Gemini API
- **Storage**: LocalStorage + Google Drive Sync

## 📁 Structure

```
web-platform/
├── app/                    # Next.js App Router
│   ├── (main)/            # Main routes (with sidebar)
│   │   ├── learn/         # Learning stages
│   │   │   ├── hanzi/     # Hanzi Writer + Air Writing
│   │   │   ├── writing/   # Writing practice
│   │   │   └── speaking/  # Speaking practice
│   │   ├── leaderboard/   # Rankings
│   │   └── profile/       # User profile
│   ├── (auth)/            # Auth routes
│   └── api/               # API routes
├── components/
│   ├── ui/                # Shadcn components
│   ├── gamification/      # XP, Hearts, Streaks
│   ├── interactive/       # MediaPipe Air Writing
│   └── vocab/             # Vocabulary manager
├── lib/
│   ├── storage.ts         # LocalStorage + SRS
│   ├── google-drive.ts    # Google Drive sync
│   ├── db/                # Database (Drizzle)
│   └── utils.ts           # Utilities
└── public/
    ├── characters/        # Game characters
    └── sounds/            # Sound effects
```

## 🎮 Features

### ✅ Implemented

#### Gamification
- ⚡ XP System + Levels
- ❤️ Hearts/Lives
- 🔥 Streaks with celebration
- 📊 Daily Quests

#### Hanzi Stage
- ✍️ Hanzi Writer (animation + quiz)
- 🖐️ Air Writing với MediaPipe
- 🔊 Text-to-Speech (Web Speech API)
- 📖 Vocabulary Manager

#### Data Management
- 💾 LocalStorage persistence
- 📤 Export CSV (Anki compatible)
- 📥 Import CSV/JSON
- 🔄 SRS (Spaced Repetition System)

### 🚧 Coming Soon
- ☁️ Google Drive Sync
- 🏆 Leaderboard
- 🎯 Achievements
- 🗣️ Speaking Stage
- ✏️ Writing Stage with AI feedback

## 🚀 Quick Start

```bash
cd web-platform

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with your keys

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📝 Environment Variables

```env
# Required
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# Optional (for database)
DATABASE_URL=postgresql://...

# Optional (for Google Drive sync)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx
NEXT_PUBLIC_GOOGLE_API_KEY=xxx
```

## 🎨 Design Philosophy

- **Immersive**: Mỗi trang là một "sân khấu" với animation mượt mà
- **Gamified**: XP, streaks, achievements để tạo động lực
- **Accessible**: Hoạt động offline với LocalStorage
- **Portable**: Export/Import để sync với Anki, Google Drive

## 📝 Credits

- Hanzi Writer: [chanind/hanzi-writer](https://github.com/chanind/hanzi-writer)
- MediaPipe: [google/mediapipe](https://github.com/google/mediapipe)
- UI inspiration: [Duolingo](https://duolingo.com)
