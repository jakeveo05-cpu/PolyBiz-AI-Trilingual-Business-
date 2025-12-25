"use client";

import { motion } from "framer-motion";
import { Heart, Flame, Zap, Trophy } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn, formatNumber, calculateLevel, xpForNextLevel } from "@/lib/utils";

interface UserProgressProps {
  hearts: number;
  maxHearts?: number;
  streak: number;
  xp: number;
  className?: string;
}

export function UserProgress({ 
  hearts, 
  maxHearts = 5, 
  streak, 
  xp,
  className 
}: UserProgressProps) {
  const level = calculateLevel(xp);
  const { current, needed, progress } = xpForNextLevel(xp);

  return (
    <div className={cn("flex items-center gap-6", className)}>
      {/* Hearts */}
      <motion.div 
        className="flex items-center gap-2"
        whileHover={{ scale: 1.05 }}
      >
        <Heart 
          className={cn(
            "w-6 h-6",
            hearts > 0 ? "text-danger fill-danger" : "text-slate-300"
          )} 
        />
        <span className="font-bold text-slate-700">
          {hearts}/{maxHearts}
        </span>
      </motion.div>

      {/* Streak */}
      <motion.div 
        className="flex items-center gap-2"
        whileHover={{ scale: 1.05 }}
      >
        <Flame 
          className={cn(
            "w-6 h-6",
            streak > 0 ? "text-accent streak-fire" : "text-slate-300"
          )} 
        />
        <span className="font-bold text-slate-700">
          {streak}
        </span>
      </motion.div>

      {/* XP & Level */}
      <motion.div 
        className="flex items-center gap-3"
        whileHover={{ scale: 1.02 }}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
            <Trophy className="w-4 h-4 text-primary" />
          </div>
          <span className="font-bold text-primary">Lv.{level}</span>
        </div>
        
        <div className="w-32">
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>{formatNumber(current)} XP</span>
            <span>{formatNumber(needed)}</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </motion.div>
    </div>
  );
}
