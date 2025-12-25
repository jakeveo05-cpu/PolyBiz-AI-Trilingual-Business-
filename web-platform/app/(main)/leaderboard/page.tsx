"use client";

import { motion } from "framer-motion";
import { Trophy, Medal, Crown, Zap, Flame, Users } from "lucide-react";
import { UserProgress } from "@/components/gamification/user-progress";

// Mock leaderboard data
const MOCK_LEADERBOARD = [
  { rank: 1, name: "AI Master", xp: 15420, streak: 45, avatar: "🦊" },
  { rank: 2, name: "Hanzi Hero", xp: 12350, streak: 32, avatar: "🐼" },
  { rank: 3, name: "Language Ninja", xp: 11200, streak: 28, avatar: "🐉" },
  { rank: 4, name: "Study Star", xp: 9800, streak: 21, avatar: "⭐" },
  { rank: 5, name: "Word Wizard", xp: 8500, streak: 19, avatar: "🧙" },
  { rank: 6, name: "Vocab Viking", xp: 7200, streak: 15, avatar: "⚔️" },
  { rank: 7, name: "Character Champion", xp: 6100, streak: 12, avatar: "🏆" },
  { rank: 8, name: "Learning Legend", xp: 5500, streak: 10, avatar: "📚" },
  { rank: 9, name: "Practice Pro", xp: 4800, streak: 8, avatar: "💪" },
  { rank: 10, name: "Rising Star", xp: 4200, streak: 7, avatar: "🌟" },
];

export default function LeaderboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            <span className="font-bold text-slate-800">Bảng xếp hạng</span>
          </div>
          <UserProgress hearts={5} streak={7} xp={1250} />
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Coming Soon Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-yellow-400 to-orange-400 rounded-3xl p-6 mb-8 text-center text-white"
        >
          <Users className="w-12 h-12 mx-auto mb-3 opacity-80" />
          <h2 className="text-xl font-bold mb-2">Leaderboard Coming Soon!</h2>
          <p className="text-white/80 text-sm">
            Tính năng bảng xếp hạng sẽ được kích hoạt khi có đủ người dùng.
            Dưới đây là preview với dữ liệu mẫu.
          </p>
        </motion.div>

        {/* Top 3 Podium */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center items-end gap-4 mb-8"
        >
          {/* 2nd Place */}
          <div className="text-center">
            <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center text-3xl mb-2 mx-auto">
              {MOCK_LEADERBOARD[1].avatar}
            </div>
            <Medal className="w-6 h-6 text-slate-400 mx-auto mb-1" />
            <p className="font-bold text-slate-800 text-sm">{MOCK_LEADERBOARD[1].name}</p>
            <p className="text-xs text-slate-500">{MOCK_LEADERBOARD[1].xp.toLocaleString()} XP</p>
            <div className="w-20 h-24 bg-slate-200 rounded-t-lg mt-2" />
          </div>

          {/* 1st Place */}
          <div className="text-center">
            <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center text-4xl mb-2 mx-auto ring-4 ring-yellow-400">
              {MOCK_LEADERBOARD[0].avatar}
            </div>
            <Crown className="w-8 h-8 text-yellow-500 mx-auto mb-1" />
            <p className="font-bold text-slate-800">{MOCK_LEADERBOARD[0].name}</p>
            <p className="text-sm text-slate-500">{MOCK_LEADERBOARD[0].xp.toLocaleString()} XP</p>
            <div className="w-24 h-32 bg-yellow-400 rounded-t-lg mt-2" />
          </div>

          {/* 3rd Place */}
          <div className="text-center">
            <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center text-3xl mb-2 mx-auto">
              {MOCK_LEADERBOARD[2].avatar}
            </div>
            <Medal className="w-6 h-6 text-orange-400 mx-auto mb-1" />
            <p className="font-bold text-slate-800 text-sm">{MOCK_LEADERBOARD[2].name}</p>
            <p className="text-xs text-slate-500">{MOCK_LEADERBOARD[2].xp.toLocaleString()} XP</p>
            <div className="w-20 h-16 bg-orange-300 rounded-t-lg mt-2" />
          </div>
        </motion.div>

        {/* Full Leaderboard */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-xl overflow-hidden"
        >
          {MOCK_LEADERBOARD.map((user, index) => (
            <motion.div
              key={user.rank}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              className={`flex items-center gap-4 p-4 border-b border-slate-100 last:border-0 ${
                index < 3 ? "bg-yellow-50/50" : ""
              }`}
            >
              {/* Rank */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                index === 0 ? "bg-yellow-400 text-white" :
                index === 1 ? "bg-slate-300 text-white" :
                index === 2 ? "bg-orange-400 text-white" :
                "bg-slate-100 text-slate-600"
              }`}>
                {user.rank}
              </div>

              {/* Avatar */}
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center text-2xl">
                {user.avatar}
              </div>

              {/* Info */}
              <div className="flex-1">
                <p className="font-bold text-slate-800">{user.name}</p>
                <div className="flex items-center gap-3 text-sm text-slate-500">
                  <span className="flex items-center gap-1">
                    <Zap className="w-3 h-3 text-yellow-500" />
                    {user.xp.toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Flame className="w-3 h-3 text-orange-500" />
                    {user.streak} days
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Your Position */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 p-4 bg-primary/10 rounded-2xl"
        >
          <p className="text-center text-slate-600">
            Vị trí của bạn: <span className="font-bold text-primary">#42</span>
            {" "}• Tiếp tục luyện tập để leo hạng! 🚀
          </p>
        </motion.div>
      </main>
    </div>
  );
}
