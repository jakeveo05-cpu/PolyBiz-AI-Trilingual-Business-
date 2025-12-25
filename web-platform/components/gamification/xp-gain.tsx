"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Zap } from "lucide-react";

interface XPGainProps {
  amount: number;
  show: boolean;
  onComplete?: () => void;
}

export function XPGain({ amount, show, onComplete }: XPGainProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.8 }}
          animate={{ opacity: 1, y: -30, scale: 1 }}
          exit={{ opacity: 0, y: -60 }}
          transition={{ duration: 0.8 }}
          onAnimationComplete={onComplete}
          className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 pointer-events-none"
        >
          <div className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-full shadow-2xl">
            <Zap className="w-6 h-6 fill-white" />
            <span className="text-2xl font-bold">+{amount} XP</span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
