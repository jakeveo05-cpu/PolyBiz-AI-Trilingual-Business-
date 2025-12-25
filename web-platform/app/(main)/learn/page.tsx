"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { 
  PenTool, 
  Mic, 
  Languages, 
  Gamepad2,
  ArrowRight,
  Lock,
  Star,
  Zap
} from "lucide-react";
import { UserProgress } from "@/components/gamification/user-progress";

const stages = [
  {
    id: "hanzi",
    title: "Hanzi Stage",
    subtitle: "Viết chữ Hán",
    description: "Học viết chữ Hán với animation và quiz tương tác",
    icon: Languages,
    color: "from-orange-500 to-amber-500",
    bgColor: "bg-orange-500",
    href: "/learn/hanzi",
    available: true,
    xpReward: 20,
  },
  {
    id: "writing",
    title: "Writing Stage",
    subtitle: "Luyện viết",
    description: "Viết email, báo cáo với AI feedback",
    icon: PenTool,
    color: "from-purple-500 to-violet-500",
    bgColor: "bg-purple-500",
    href: "/learn/writing",
    available: false,
    xpReward: 30,
  },
  {
    id: "speaking",
    title: "Speaking Stage",
    subtitle: "Luyện nói",
    description: "Hội thoại với AI, luyện phát âm",
    icon: Mic,
    color: "from-blue-500 to-cyan-500",
    bgColor: "bg-blue-500",
    href: "/learn/speaking",
    available: false,
    xpReward: 25,
  },
  {
    id: "games",
    title: "Games Stage",
    subtitle: "Trò chơi",
    description: "Học qua mini-games vui nhộn",
    icon: Gamepad2,
    color: "from-green-500 to-emerald-500",
    bgColor: "bg-green-500",
    href: "/learn/games",
    available: false,
    xpReward: 15,
  },
];

const dailyQuests = [
  { id: 1, title: "Viết 5 chữ Hán", progress: 2, total: 5, xp: 50 },
  { id: 2, title: "Hoàn thành 1 bài học", progress: 0, total: 1, xp: 30 },
  { id: 3, title: "Đạt 100 XP", progress: 45, total: 100, xp: 20 },
];

export default function LearnPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🎭</span>
            <span className="font-bold text-slate-800">PolyBiz</span>
          </Link>

          <UserProgress hearts={5} streak={7} xp={1250} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Welcome */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-slate-800 mb-2">
              Chào mừng trở lại! 👋
            </h1>
            <p className="text-slate-600">
              Hãy chọn một sân khấu để bắt đầu hành trình học tập hôm nay.
            </p>
          </motion.div>

          {/* Daily Quests */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8 p-6 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl"
          >
            <div className="flex items-center gap-2 mb-4">
              <Star className="w-5 h-5 text-accent" />
              <h2 className="font-bold text-slate-800">Daily Quests</h2>
            </div>

            <div className="space-y-3">
              {dailyQuests.map((quest) => (
                <div 
                  key={quest.id}
                  className="flex items-center justify-between p-3 bg-white rounded-xl"
                >
                  <div className="flex-1">
                    <p className="font-medium text-slate-800 text-sm">{quest.title}</p>
                    <div className="mt-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full transition-all"
                        style={{ width: `${(quest.progress / quest.total) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="ml-4 flex items-center gap-1 text-sm font-bold text-primary">
                    <Zap className="w-4 h-4" />
                    {quest.xp}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Stages Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {stages.map((stage, index) => (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                {stage.available ? (
                  <Link href={stage.href}>
                    <StageCard stage={stage} />
                  </Link>
                ) : (
                  <StageCard stage={stage} locked />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

function StageCard({ stage, locked = false }: { stage: typeof stages[0]; locked?: boolean }) {
  return (
    <div className={`
      relative p-6 rounded-3xl transition-all duration-300
      ${locked 
        ? "bg-slate-100 cursor-not-allowed" 
        : "bg-white shadow-lg hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
      }
    `}>
      {/* Locked overlay */}
      {locked && (
        <div className="absolute inset-0 bg-slate-200/50 rounded-3xl flex items-center justify-center z-10">
          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow">
            <Lock className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-600">Coming Soon</span>
          </div>
        </div>
      )}

      {/* Icon */}
      <div className={`
        w-16 h-16 rounded-2xl flex items-center justify-center mb-4
        bg-gradient-to-br ${stage.color}
      `}>
        <stage.icon className="w-8 h-8 text-white" />
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-sm text-slate-500 mb-1">{stage.subtitle}</p>
        <h3 className="text-xl font-bold text-slate-800 mb-2">{stage.title}</h3>
        <p className="text-slate-600 text-sm">{stage.description}</p>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 text-sm font-medium text-primary">
          <Zap className="w-4 h-4" />
          +{stage.xpReward} XP
        </div>
        
        {!locked && (
          <div className="flex items-center text-primary font-medium text-sm">
            Bắt đầu
            <ArrowRight className="w-4 h-4 ml-1" />
          </div>
        )}
      </div>
    </div>
  );
}
