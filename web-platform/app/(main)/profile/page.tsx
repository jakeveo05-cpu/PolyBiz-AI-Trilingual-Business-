"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  User,
  Flame,
  Zap,
  Heart,
  Trophy,
  Calendar,
  Target,
  Download,
  Upload,
  Trash2,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { UserProgress } from "@/components/gamification/user-progress";
import {
  getUserProgress,
  getSRSData,
  getWeakCharacters,
  getMasteredCharacters,
  getDueForReview,
  exportAllData,
  importAllData,
  resetAllData,
} from "@/lib/storage";

export default function ProfilePage() {
  const [progress, setProgress] = useState({
    xp: 0,
    level: 1,
    hearts: 5,
    streak: 0,
    lastPractice: "",
    totalPractice: 0,
    achievements: [] as string[],
  });
  const [stats, setStats] = useState({
    weak: 0,
    learning: 0,
    mastered: 0,
    dueForReview: 0,
  });
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  useEffect(() => {
    const p = getUserProgress();
    setProgress(p);

    const srsData = getSRSData();
    const weak = getWeakCharacters().length;
    const mastered = getMasteredCharacters().length;
    const total = Object.keys(srsData).length;
    const dueForReview = getDueForReview().length;

    setStats({
      weak,
      learning: total - weak - mastered,
      mastered,
      dueForReview,
    });
  }, []);

  const handleExport = () => {
    const data = exportAllData();
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `polybiz_backup_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const content = await file.text();
        if (importAllData(content)) {
          window.location.reload();
        }
      }
    };
    input.click();
  };

  const handleReset = () => {
    resetAllData();
    window.location.reload();
  };

  const xpToNextLevel = 100;
  const currentLevelXP = progress.xp % xpToNextLevel;
  const xpProgress = (currentLevelXP / xpToNextLevel) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="w-5 h-5 text-slate-600" />
            <span className="font-bold text-slate-800">Hồ sơ</span>
          </div>
          <UserProgress hearts={progress.hearts} streak={progress.streak} xp={progress.xp} />
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-3xl shadow-xl p-8 mb-8"
        >
          {/* Avatar & Level */}
          <div className="flex items-center gap-6 mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-4xl">
              🎭
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-slate-800 mb-1">
                AI Native Learner
              </h1>
              <div className="flex items-center gap-2 text-slate-600 mb-3">
                <Trophy className="w-4 h-4 text-yellow-500" />
                <span>Level {progress.level}</span>
              </div>
              {/* XP Progress Bar */}
              <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${xpProgress}%` }}
                  className="h-full bg-gradient-to-r from-primary to-secondary"
                />
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {currentLevelXP} / {xpToNextLevel} XP to Level {progress.level + 1}
              </p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              icon={<Zap className="w-6 h-6 text-yellow-500" />}
              value={progress.xp}
              label="Total XP"
              color="bg-yellow-50"
            />
            <StatCard
              icon={<Flame className="w-6 h-6 text-orange-500" />}
              value={progress.streak}
              label="Day Streak"
              color="bg-orange-50"
            />
            <StatCard
              icon={<Target className="w-6 h-6 text-blue-500" />}
              value={progress.totalPractice}
              label="Lượt luyện"
              color="bg-blue-50"
            />
            <StatCard
              icon={<Calendar className="w-6 h-6 text-green-500" />}
              value={progress.lastPractice || "—"}
              label="Lần cuối"
              color="bg-green-50"
              isDate
            />
          </div>
        </motion.div>

        {/* SRS Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-3xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
            📊 Thống kê SRS
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-red-50 rounded-xl text-center">
              <p className="text-3xl font-bold text-red-600">{stats.weak}</p>
              <p className="text-sm text-red-600">🔴 Cần ôn</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-xl text-center">
              <p className="text-3xl font-bold text-yellow-600">{stats.learning}</p>
              <p className="text-sm text-yellow-600">🟡 Đang học</p>
            </div>
            <div className="p-4 bg-green-50 rounded-xl text-center">
              <p className="text-3xl font-bold text-green-600">{stats.mastered}</p>
              <p className="text-sm text-green-600">🟢 Đã thuộc</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-xl text-center">
              <p className="text-3xl font-bold text-blue-600">{stats.dueForReview}</p>
              <p className="text-sm text-blue-600">📅 Cần ôn hôm nay</p>
            </div>
          </div>
        </motion.div>

        {/* Data Management */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-xl p-8"
        >
          <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
            💾 Quản lý dữ liệu
          </h2>

          <div className="space-y-4">
            <div className="flex flex-wrap gap-3">
              <Button onClick={handleExport} variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Export Backup
              </Button>
              <Button onClick={handleImport} variant="outline" className="gap-2">
                <Upload className="w-4 h-4" />
                Import Backup
              </Button>
            </div>

            <hr className="border-slate-200" />

            {showResetConfirm ? (
              <div className="p-4 bg-red-50 rounded-xl">
                <p className="text-red-700 mb-3">
                  ⚠️ Bạn có chắc muốn xóa tất cả dữ liệu? Hành động này không thể hoàn tác!
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={handleReset}
                    variant="destructive"
                    size="sm"
                    className="gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Xác nhận xóa
                  </Button>
                  <Button
                    onClick={() => setShowResetConfirm(false)}
                    variant="outline"
                    size="sm"
                  >
                    Hủy
                  </Button>
                </div>
              </div>
            ) : (
              <Button
                onClick={() => setShowResetConfirm(true)}
                variant="ghost"
                className="gap-2 text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
                Reset tất cả dữ liệu
              </Button>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  );
}

function StatCard({
  icon,
  value,
  label,
  color,
  isDate = false,
}: {
  icon: React.ReactNode;
  value: number | string;
  label: string;
  color: string;
  isDate?: boolean;
}) {
  return (
    <div className={`p-4 rounded-xl ${color}`}>
      <div className="flex items-center gap-2 mb-2">{icon}</div>
      <p className="text-2xl font-bold text-slate-800">
        {isDate && typeof value === "string" && value !== "—"
          ? new Date(value).toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" })
          : value}
      </p>
      <p className="text-sm text-slate-600">{label}</p>
    </div>
  );
}
