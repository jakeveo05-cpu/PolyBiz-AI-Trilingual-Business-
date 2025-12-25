import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
}

export function calculateLevel(xp: number): number {
  // XP needed per level: 100, 200, 300, 400...
  // Total XP for level n: n * (n + 1) * 50
  let level = 1;
  let totalXpNeeded = 100;
  
  while (xp >= totalXpNeeded) {
    level++;
    totalXpNeeded += level * 100;
  }
  
  return level;
}

export function xpForNextLevel(currentXp: number): { current: number; needed: number; progress: number } {
  const level = calculateLevel(currentXp);
  const xpForCurrentLevel = (level - 1) * level * 50;
  const xpForNext = level * (level + 1) * 50;
  const xpNeededForLevel = xpForNext - xpForCurrentLevel;
  const currentProgress = currentXp - xpForCurrentLevel;
  
  return {
    current: currentProgress,
    needed: xpNeededForLevel,
    progress: (currentProgress / xpNeededForLevel) * 100,
  };
}
