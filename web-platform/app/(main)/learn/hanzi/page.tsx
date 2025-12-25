"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ArrowLeft, 
  Play, 
  RotateCcw, 
  Hand, 
  Pencil,
  Volume2,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Camera
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { UserProgress } from "@/components/gamification/user-progress";
import { XPGain } from "@/components/gamification/xp-gain";
import { AirWriting } from "@/components/interactive/air-writing";

// Sample characters for demo
const DEMO_CHARACTERS = [
  { char: "你", pinyin: "nǐ", meaning: "you", radical: "亻+ 尔" },
  { char: "好", pinyin: "hǎo", meaning: "good", radical: "女 + 子" },
  { char: "我", pinyin: "wǒ", meaning: "I/me", radical: "手 + 戈" },
  { char: "是", pinyin: "shì", meaning: "am/is", radical: "日 + 正" },
  { char: "中", pinyin: "zhōng", meaning: "middle/China", radical: "丨+ 口" },
  { char: "国", pinyin: "guó", meaning: "country", radical: "囗 + 玉" },
  { char: "人", pinyin: "rén", meaning: "person", radical: "人" },
  { char: "大", pinyin: "dà", meaning: "big", radical: "大" },
  { char: "学", pinyin: "xué", meaning: "study", radical: "子 + 冖" },
  { char: "生", pinyin: "shēng", meaning: "life/born", radical: "生" },
];

type Mode = "animation" | "quiz" | "air-writing";

export default function HanziStagePage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [mode, setMode] = useState<Mode>("animation");
  const [showXP, setShowXP] = useState(false);
  const [xpGained, setXpGained] = useState(0);
  const writerRef = useRef<HTMLDivElement>(null);
  const [writer, setWriter] = useState<any>(null);

  const currentChar = DEMO_CHARACTERS[currentIndex];

  // Initialize Hanzi Writer
  useEffect(() => {
    if (typeof window !== "undefined" && writerRef.current) {
      // Dynamic import for client-side only
      import("hanzi-writer").then((HanziWriter) => {
        writerRef.current!.innerHTML = "";
        
        const newWriter = HanziWriter.default.create(writerRef.current!, currentChar.char, {
          width: 300,
          height: 300,
          padding: 20,
          showOutline: true,
          strokeAnimationSpeed: 1,
          delayBetweenStrokes: 200,
          strokeColor: "#333",
          outlineColor: "#DDD",
          drawingColor: "#58CC02",
          showHintAfterMisses: 3,
          highlightOnComplete: true,
          charDataLoader: (char: string) => {
            return fetch(`https://cdn.jsdelivr.net/npm/hanzi-writer-data@2.0/${char}.json`)
              .then(res => res.json());
          }
        });

        setWriter(newWriter);
      });
    }
  }, [currentChar.char]);

  const playAnimation = () => {
    if (writer) {
      writer.animateCharacter();
    }
  };

  const startQuiz = () => {
    if (writer) {
      setMode("quiz");
      writer.quiz({
        onComplete: (summaryData: any) => {
          const xp = Math.round((1 - summaryData.totalMistakes / 10) * 20);
          setXpGained(Math.max(5, xp));
          setShowXP(true);
        }
      });
    }
  };

  const resetWriter = () => {
    if (writer) {
      writer.cancelQuiz();
      writer.hideCharacter();
      writer.showCharacter();
      setMode("animation");
    }
  };

  const speakCharacter = () => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(currentChar.char);
      utterance.lang = "zh-CN";
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const goNext = () => {
    if (currentIndex < DEMO_CHARACTERS.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setMode("animation");
    }
  };

  const goPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setMode("animation");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/learn">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>

          <div className="flex items-center gap-2">
            <span className="text-2xl">✍️</span>
            <span className="font-bold text-slate-800">Hanzi Stage</span>
          </div>

          <UserProgress hearts={5} streak={7} xp={1250} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Character Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <div className="flex items-center justify-center gap-4 mb-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={goPrev}
                disabled={currentIndex === 0}
              >
                <ChevronLeft className="w-6 h-6" />
              </Button>

              <div>
                <h1 className="text-6xl font-bold text-slate-800 mb-2">
                  {currentChar.char}
                </h1>
                <p className="text-xl text-slate-600">
                  <span className="text-accent font-medium">{currentChar.pinyin}</span>
                  {" • "}
                  <span>{currentChar.meaning}</span>
                </p>
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={goNext}
                disabled={currentIndex === DEMO_CHARACTERS.length - 1}
              >
                <ChevronRight className="w-6 h-6" />
              </Button>
            </div>

            <p className="text-sm text-slate-500">
              {currentIndex + 1} / {DEMO_CHARACTERS.length}
            </p>
          </motion.div>

          {/* Writer Canvas */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-3xl shadow-xl p-8 mb-8"
          >
            {/* Grid background */}
            <div className="relative mx-auto w-[300px] h-[300px]">
              {/* 米字格 Grid */}
              <svg 
                className="absolute inset-0 w-full h-full pointer-events-none"
                viewBox="0 0 300 300"
              >
                {/* Outer border */}
                <rect x="10" y="10" width="280" height="280" fill="none" stroke="#E5E7EB" strokeWidth="2" />
                {/* Cross lines */}
                <line x1="150" y1="10" x2="150" y2="290" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
                <line x1="10" y1="150" x2="290" y2="150" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
                {/* Diagonal lines */}
                <line x1="10" y1="10" x2="290" y2="290" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
                <line x1="290" y1="10" x2="10" y2="290" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
              </svg>

              {/* Hanzi Writer container */}
              <div ref={writerRef} className="relative z-10" />
            </div>

            {/* Mode indicator */}
            <div className="text-center mt-4">
              <span className={`
                inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium
                ${mode === "animation" ? "bg-blue-100 text-blue-700" : ""}
                ${mode === "quiz" ? "bg-green-100 text-green-700" : ""}
                ${mode === "air-writing" ? "bg-orange-100 text-orange-700" : ""}
              `}>
                {mode === "animation" && <><Play className="w-4 h-4" /> Animation Mode</>}
                {mode === "quiz" && <><Pencil className="w-4 h-4" /> Quiz Mode</>}
                {mode === "air-writing" && <><Hand className="w-4 h-4" /> Air Writing Mode</>}
              </span>
            </div>
          </motion.div>

          {/* Controls */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex flex-wrap justify-center gap-4"
          >
            <Button
              onClick={playAnimation}
              variant="outline"
              className="gap-2"
            >
              <Play className="w-5 h-5" />
              Xem Animation
            </Button>

            <Button
              onClick={startQuiz}
              className="gap-2"
            >
              <Pencil className="w-5 h-5" />
              Luyện Viết
            </Button>

            <Button
              onClick={speakCharacter}
              variant="secondary"
              className="gap-2"
            >
              <Volume2 className="w-5 h-5" />
              Phát Âm
            </Button>

            <Button
              onClick={resetWriter}
              variant="ghost"
              className="gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </Button>
          </motion.div>

          {/* Air Writing Section */}
          <AnimatePresence mode="wait">
            {mode === "air-writing" ? (
              <motion.div
                key="air-writing"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mt-8"
              >
                <div className="bg-white rounded-3xl shadow-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Hand className="w-6 h-6 text-orange-600" />
                      <h3 className="font-bold text-slate-800">Air Writing Mode</h3>
                      <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs rounded-full">
                        BETA
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setMode("animation")}
                    >
                      Đóng
                    </Button>
                  </div>
                  
                  <AirWriting 
                    targetChar={currentChar.char}
                    onStrokeComplete={(strokes) => {
                      // Award XP for completing strokes
                      if (strokes.length >= 3) {
                        setXpGained(15);
                        setShowXP(true);
                      }
                    }}
                  />
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="air-writing-teaser"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ delay: 0.4 }}
                className="mt-12 p-6 bg-gradient-to-r from-orange-100 to-amber-100 rounded-2xl"
              >
                <div className="flex flex-col md:flex-row items-center gap-6">
                  <div className="flex-1 text-center md:text-left">
                    <div className="flex items-center justify-center md:justify-start gap-2 mb-3">
                      <Hand className="w-6 h-6 text-orange-600" />
                      <Sparkles className="w-5 h-5 text-amber-500" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800 mb-2">
                      🖐️ Air Writing với MediaPipe
                    </h3>
                    <p className="text-slate-600 text-sm mb-4">
                      Viết chữ Hán trong không khí bằng webcam. 
                      Trải nghiệm học tập immersive hoàn toàn mới!
                    </p>
                    <Button
                      onClick={() => setMode("air-writing")}
                      className="gap-2 bg-orange-500 hover:bg-orange-600"
                    >
                      <Camera className="w-5 h-5" />
                      Thử Air Writing
                    </Button>
                  </div>
                  <div className="w-32 h-32 bg-white/50 rounded-2xl flex items-center justify-center">
                    <span className="text-6xl">{currentChar.char}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* XP Gain Animation */}
      <XPGain 
        amount={xpGained} 
        show={showXP} 
        onComplete={() => setShowXP(false)} 
      />
    </div>
  );
}
