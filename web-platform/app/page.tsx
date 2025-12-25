"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { 
  Sparkles, 
  Zap, 
  Heart, 
  Flame, 
  Trophy,
  PenTool,
  Mic,
  Languages,
  Gamepad2,
  ArrowRight,
  Github,
  Users
} from "lucide-react";

const stages = [
  {
    id: "writing",
    title: "Writing Stage",
    description: "Luyện viết với AI feedback",
    icon: PenTool,
    color: "from-purple-500 to-purple-600",
    bgColor: "bg-purple-500/10",
    href: "/learn/writing",
  },
  {
    id: "speaking",
    title: "Speaking Stage",
    description: "Luyện phát âm & hội thoại",
    icon: Mic,
    color: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-500/10",
    href: "/learn/speaking",
  },
  {
    id: "hanzi",
    title: "Hanzi Stage",
    description: "Viết chữ Hán trong không khí",
    icon: Languages,
    color: "from-orange-500 to-orange-600",
    bgColor: "bg-orange-500/10",
    href: "/learn/hanzi",
  },
  {
    id: "games",
    title: "Games Stage",
    description: "Học qua trò chơi tương tác",
    icon: Gamepad2,
    color: "from-green-500 to-green-600",
    bgColor: "bg-green-500/10",
    href: "/learn/games",
  },
];

const features = [
  { icon: Zap, label: "XP System", value: "Level Up!" },
  { icon: Heart, label: "Hearts", value: "5 Lives" },
  { icon: Flame, label: "Streaks", value: "Daily Goals" },
  { icon: Trophy, label: "Achievements", value: "50+ Badges" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute top-40 right-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-accent/10 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto px-4 py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            {/* Badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary font-medium mb-6"
            >
              <Sparkles className="w-4 h-4" />
              <span>Dành cho AI Natives</span>
            </motion.div>

            {/* Title */}
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">PolyBiz</span>
              <br />
              <span className="text-slate-800">Learning Stage</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
              Sân khấu học tập nơi bạn <strong>nhập vai</strong>, <strong>sáng tạo</strong> 
              và khám phá hành trình tự học của mình. 
              Học ngoại ngữ chỉ là cái cớ - xây dựng cộng đồng mới là mục tiêu.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/learn">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-primary text-white font-bold rounded-2xl shadow-lg hover:shadow-xl transition-shadow flex items-center gap-2"
                >
                  Bắt đầu miễn phí
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              <Link href="/learn">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-white text-slate-700 font-bold rounded-2xl border-2 border-slate-200 hover:border-primary transition-colors"
                >
                  Khám phá ngay
                </motion.button>
              </Link>
            </div>
          </motion.div>

          {/* Features bar */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-16 flex flex-wrap justify-center gap-6"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-center gap-3 px-6 py-3 bg-white rounded-2xl shadow-md"
              >
                <feature.icon className="w-6 h-6 text-primary" />
                <div>
                  <p className="text-xs text-slate-500">{feature.label}</p>
                  <p className="font-bold text-slate-800">{feature.value}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Stages Section */}
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-4">
              Chọn Sân Khấu Của Bạn
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Mỗi sân khấu là một trải nghiệm học tập độc đáo. 
              Hãy khám phá và tìm ra phong cách học phù hợp với bạn.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stages.map((stage, index) => (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Link href={stage.href}>
                  <div className="stage-card group relative p-6 bg-white rounded-3xl shadow-lg hover:shadow-2xl cursor-pointer overflow-hidden">
                    {/* Background gradient on hover */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${stage.color} opacity-0 group-hover:opacity-5 transition-opacity`} />
                    
                    {/* Icon */}
                    <div className={`w-16 h-16 ${stage.bgColor} rounded-2xl flex items-center justify-center mb-4`}>
                      <stage.icon className={`w-8 h-8 bg-gradient-to-br ${stage.color} bg-clip-text text-transparent`} 
                        style={{ color: stage.color.includes('purple') ? '#a855f7' : 
                                        stage.color.includes('blue') ? '#3b82f6' :
                                        stage.color.includes('orange') ? '#f97316' : '#22c55e' }} 
                      />
                    </div>

                    {/* Content */}
                    <h3 className="text-xl font-bold text-slate-800 mb-2">
                      {stage.title}
                    </h3>
                    <p className="text-slate-600 text-sm">
                      {stage.description}
                    </p>

                    {/* Arrow */}
                    <div className="mt-4 flex items-center text-primary font-medium text-sm group-hover:translate-x-2 transition-transform">
                      Khám phá
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Community Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary/10 rounded-full text-secondary font-medium mb-6">
              <Users className="w-4 h-4" />
              <span>Cộng đồng AI Natives</span>
            </div>

            <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-4">
              Học một mình thì chán,<br />
              <span className="gradient-text">học cùng nhau thì vui!</span>
            </h2>

            <p className="text-slate-600 mb-8">
              Tham gia cộng đồng Discord/Telegram để kết nối với những AI Natives khác.
              Chia sẻ kinh nghiệm, thách đấu bạn bè, và cùng nhau tiến bộ.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="https://discord.gg/polybiz" 
                target="_blank"
                className="px-6 py-3 bg-[#5865F2] text-white font-bold rounded-xl hover:bg-[#4752C4] transition-colors"
              >
                Join Discord
              </a>
              <a 
                href="https://t.me/polybiz" 
                target="_blank"
                className="px-6 py-3 bg-[#0088cc] text-white font-bold rounded-xl hover:bg-[#006699] transition-colors"
              >
                Join Telegram
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-200">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-600 text-sm">
              © 2024 PolyBiz AI. Made with ❤️ for AI Natives.
            </p>
            <div className="flex items-center gap-4">
              <a 
                href="https://github.com/jakeveo05-cpu/polybiz-ai" 
                target="_blank"
                className="text-slate-600 hover:text-slate-800 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
