"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  Home, 
  BookOpen, 
  Trophy, 
  User, 
  Settings,
  Menu,
  X
} from "lucide-react";

const navItems = [
  { href: "/learn", icon: BookOpen, label: "Học tập" },
  { href: "/leaderboard", icon: Trophy, label: "Bảng xếp hạng" },
  { href: "/profile", icon: User, label: "Hồ sơ" },
];

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200">
        <div className="flex items-center justify-between px-4 py-3">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🎭</span>
            <span className="font-bold text-slate-800">PolyBiz</span>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg hover:bg-slate-100"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-full left-0 right-0 bg-white border-b border-slate-200 shadow-lg"
          >
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 ${
                  pathname.startsWith(item.href)
                    ? "bg-primary/10 text-primary"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            ))}
          </motion.nav>
        )}
      </header>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-slate-200 flex-col">
        <div className="p-6">
          <Link href="/" className="flex items-center gap-3">
            <span className="text-3xl">🎭</span>
            <div>
              <h1 className="font-bold text-xl text-slate-800">PolyBiz</h1>
              <p className="text-xs text-slate-500">Learning Stage</p>
            </div>
          </Link>
        </div>

        <nav className="flex-1 px-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl mb-2 transition-all ${
                pathname.startsWith(item.href)
                  ? "bg-primary text-white shadow-lg shadow-primary/30"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <Link
            href="/settings"
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-100"
          >
            <Settings className="w-5 h-5" />
            <span>Cài đặt</span>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:ml-64 pt-16 lg:pt-0">
        {children}
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-50">
        <div className="flex justify-around py-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-1 px-4 py-2 rounded-xl ${
                pathname.startsWith(item.href)
                  ? "text-primary"
                  : "text-slate-400"
              }`}
            >
              <item.icon className="w-6 h-6" />
              <span className="text-xs">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
