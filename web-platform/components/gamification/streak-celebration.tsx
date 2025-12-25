"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Flame } from "lucide-react";
import Confetti from "react-confetti";
import { useWindowSize } from "react-use";

interface StreakCelebrationProps {
  streak: number;
  show: boolean;
  onClose: () => void;
}

export function StreakCelebration({ streak, show, onClose }: StreakCelebrationProps) {
  const { width, height } = useWindowSize();

  return (
    <AnimatePresence>
      {show && (
        <>
          <Confetti
            width={width}
            height={height}
            recycle={false}
            numberOfPieces={200}
            colors={["#FF9600", "#FF4B4B", "#FFD700", "#58CC02"]}
          />
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center"
            onClick={onClose}
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 180 }}
              transition={{ type: "spring", damping: 15 }}
              className="bg-white rounded-3xl p-8 text-center max-w-sm mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 10, -10, 0]
                }}
                transition={{ 
                  duration: 0.5,
                  repeat: Infinity,
                  repeatDelay: 1
                }}
                className="w-24 h-24 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <Flame className="w-12 h-12 text-white" />
              </motion.div>

              <h2 className="text-3xl font-bold text-slate-800 mb-2">
                🔥 {streak} Day Streak!
              </h2>
              
              <p className="text-slate-600 mb-6">
                Tuyệt vời! Bạn đã học liên tục {streak} ngày. Tiếp tục phát huy nhé!
              </p>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onClose}
                className="px-8 py-3 bg-primary text-white font-bold rounded-xl"
              >
                Tiếp tục học
              </motion.button>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
