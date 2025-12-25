/**
 * Local Storage Manager for PolyBiz Learning Stage
 * Handles user progress, vocabulary lists, and SRS data
 */

// Types
export interface VocabItem {
  char: string;
  pinyin: string;
  meaning: string;
  radical?: string;
  level?: number; // SRS level 0-5
  nextReview?: number; // timestamp
  correctCount?: number;
  wrongCount?: number;
}

export interface UserProgress {
  xp: number;
  level: number;
  hearts: number;
  streak: number;
  lastPractice: string; // ISO date
  totalPractice: number;
  achievements: string[];
}

export interface SRSData {
  [char: string]: {
    level: number;
    nextReview: number;
    correctCount: number;
    wrongCount: number;
    lastPractice: number;
  };
}

// Storage Keys
const KEYS = {
  VOCAB_LIST: "polybiz_vocab_list",
  USER_PROGRESS: "polybiz_user_progress",
  SRS_DATA: "polybiz_srs_data",
  FAVORITES: "polybiz_favorites",
  SETTINGS: "polybiz_settings",
};

// Default values
const DEFAULT_PROGRESS: UserProgress = {
  xp: 0,
  level: 1,
  hearts: 5,
  streak: 0,
  lastPractice: "",
  totalPractice: 0,
  achievements: [],
};

// Helper functions
function safeGetItem<T>(key: string, defaultValue: T): T {
  if (typeof window === "undefined") return defaultValue;
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch {
    return defaultValue;
  }
}

function safeSetItem(key: string, value: any): boolean {
  if (typeof window === "undefined") return false;
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

// Vocabulary List
export function getVocabList(): VocabItem[] {
  return safeGetItem(KEYS.VOCAB_LIST, []);
}

export function setVocabList(list: VocabItem[]): boolean {
  return safeSetItem(KEYS.VOCAB_LIST, list);
}

export function addToVocabList(items: VocabItem[]): boolean {
  const current = getVocabList();
  const newItems = items.filter(
    (item) => !current.some((c) => c.char === item.char)
  );
  return setVocabList([...current, ...newItems]);
}

// User Progress
export function getUserProgress(): UserProgress {
  return safeGetItem(KEYS.USER_PROGRESS, DEFAULT_PROGRESS);
}

export function updateUserProgress(updates: Partial<UserProgress>): boolean {
  const current = getUserProgress();
  return safeSetItem(KEYS.USER_PROGRESS, { ...current, ...updates });
}

export function addXP(amount: number): { newXP: number; levelUp: boolean } {
  const progress = getUserProgress();
  const newXP = progress.xp + amount;
  const xpPerLevel = 100;
  const newLevel = Math.floor(newXP / xpPerLevel) + 1;
  const levelUp = newLevel > progress.level;

  updateUserProgress({
    xp: newXP,
    level: newLevel,
    totalPractice: progress.totalPractice + 1,
    lastPractice: new Date().toISOString().split("T")[0],
  });

  return { newXP, levelUp };
}

// SRS (Spaced Repetition System)
export function getSRSData(): SRSData {
  return safeGetItem(KEYS.SRS_DATA, {});
}

export function updateSRS(char: string, correct: boolean): void {
  const data = getSRSData();
  const current = data[char] || {
    level: 0,
    nextReview: Date.now(),
    correctCount: 0,
    wrongCount: 0,
    lastPractice: Date.now(),
  };

  // FSRS-inspired intervals (in hours)
  const intervals = [0, 1, 6, 24, 72, 168, 336]; // 0, 1h, 6h, 1d, 3d, 7d, 14d

  if (correct) {
    current.level = Math.min(current.level + 1, 6);
    current.correctCount++;
  } else {
    current.level = Math.max(current.level - 1, 0);
    current.wrongCount++;
  }

  current.nextReview = Date.now() + intervals[current.level] * 60 * 60 * 1000;
  current.lastPractice = Date.now();

  data[char] = current;
  safeSetItem(KEYS.SRS_DATA, data);
}

export function getDueForReview(): string[] {
  const data = getSRSData();
  const now = Date.now();
  return Object.entries(data)
    .filter(([_, info]) => info.nextReview <= now)
    .sort((a, b) => a[1].nextReview - b[1].nextReview)
    .map(([char]) => char);
}

export function getWeakCharacters(): string[] {
  const data = getSRSData();
  return Object.entries(data)
    .filter(([_, info]) => info.level <= 1 && info.wrongCount > info.correctCount)
    .map(([char]) => char);
}

export function getMasteredCharacters(): string[] {
  const data = getSRSData();
  return Object.entries(data)
    .filter(([_, info]) => info.level >= 4)
    .map(([char]) => char);
}

// Favorites
export function getFavorites(): string[] {
  return safeGetItem(KEYS.FAVORITES, []);
}

export function toggleFavorite(char: string): boolean {
  const favorites = getFavorites();
  const index = favorites.indexOf(char);
  if (index > -1) {
    favorites.splice(index, 1);
  } else {
    favorites.push(char);
  }
  return safeSetItem(KEYS.FAVORITES, favorites);
}

// Streak Management
export function checkAndUpdateStreak(): { streak: number; maintained: boolean } {
  const progress = getUserProgress();
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];

  if (progress.lastPractice === today) {
    return { streak: progress.streak, maintained: true };
  }

  if (progress.lastPractice === yesterday) {
    const newStreak = progress.streak + 1;
    updateUserProgress({ streak: newStreak, lastPractice: today });
    return { streak: newStreak, maintained: true };
  }

  // Streak broken
  updateUserProgress({ streak: 1, lastPractice: today });
  return { streak: 1, maintained: false };
}

// Export/Import for Google Drive sync
export function exportAllData(): string {
  const data = {
    vocabList: getVocabList(),
    userProgress: getUserProgress(),
    srsData: getSRSData(),
    favorites: getFavorites(),
    exportedAt: new Date().toISOString(),
  };
  return JSON.stringify(data, null, 2);
}

export function importAllData(jsonString: string): boolean {
  try {
    const data = JSON.parse(jsonString);
    if (data.vocabList) setVocabList(data.vocabList);
    if (data.userProgress) safeSetItem(KEYS.USER_PROGRESS, data.userProgress);
    if (data.srsData) safeSetItem(KEYS.SRS_DATA, data.srsData);
    if (data.favorites) safeSetItem(KEYS.FAVORITES, data.favorites);
    return true;
  } catch {
    return false;
  }
}

// CSV Export for Anki
export function exportToAnkiCSV(): string {
  const vocabList = getVocabList();
  const srsData = getSRSData();

  const lines = vocabList.map((item) => {
    const srs = srsData[item.char];
    const tags = srs?.level >= 4 ? "mastered" : srs?.level <= 1 ? "weak" : "learning";
    // Format: Front;Back;Tags
    return `${item.char};${item.pinyin} - ${item.meaning};${tags}`;
  });

  return lines.join("\n");
}

// Parse CSV from Anki or Google Sheets
export function parseCSV(csvContent: string): VocabItem[] {
  const lines = csvContent.trim().split("\n");
  const items: VocabItem[] = [];

  for (const line of lines) {
    const parts = line.split(/[,;\t]/);
    if (parts.length >= 1) {
      const char = parts[0].trim();
      // Only accept single Chinese characters
      if (/^[\u4e00-\u9fff]$/.test(char)) {
        items.push({
          char,
          pinyin: parts[1]?.trim() || "",
          meaning: parts[2]?.trim() || "",
        });
      }
    }
  }

  return items;
}

// Reset all data
export function resetAllData(): void {
  if (typeof window === "undefined") return;
  Object.values(KEYS).forEach((key) => localStorage.removeItem(key));
}
