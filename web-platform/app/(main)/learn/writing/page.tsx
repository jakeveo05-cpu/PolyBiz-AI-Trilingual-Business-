"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, PenTool, Construction } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function WritingStagePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/learn">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <PenTool className="w-5 h-5 text-purple-600" />
            <span className="font-bold text-slate-800">Writing Stage</span>
          </div>
          <div className="w-10" />
        </div>
      </header>

      <main className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto text-center"
        >
          <Construction className="w-24 h-24 text-purple-400 mx-auto mb-6" />
          <h1 className="text-4xl font-bold text-slate-800 mb-4">
            Writing Stage
          </h1>
          <p className="text-xl text-slate-600 mb-8">
            Tính năng đang được phát triển. Sẽ sớm ra mắt với AI feedback cho bài viết của bạn!
          </p>
          <Link href="/learn">
            <Button className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Quay lại Dashboard
            </Button>
          </Link>
        </motion.div>
      </main>
    </div>
  );
}
