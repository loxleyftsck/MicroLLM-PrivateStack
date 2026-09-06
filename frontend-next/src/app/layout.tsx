import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "MicroLLM PrivateStack — Private AI at the speed of localhost",
    template: "%s · MicroLLM PrivateStack",
  },
  description:
    "Run a real LLM entirely on your own hardware: chat, RAG with citations, and model hot-swap in 2GB of RAM, with nothing leaving the machine.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#080B12] text-[#e8eaf0]">
        {children}
      </body>
    </html>
  );
}
