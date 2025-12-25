import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin", "vietnamese"] });

export const metadata: Metadata = {
  title: "PolyBiz Learning Stage 🎭",
  description: "Sân khấu học tập cho AI Natives - Học ngoại ngữ, xây dựng cộng đồng",
  keywords: ["AI", "language learning", "Vietnamese", "English", "Chinese", "business"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className={inter.className}>
        <Toaster position="top-center" richColors />
        {children}
      </body>
    </html>
  );
}
