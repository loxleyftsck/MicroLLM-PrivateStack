"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("light", !isDark);
  }, [isDark]);

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      onClick={() => setIsDark((v) => !v)}
      className="flex items-center gap-1 rounded-full border border-[#252B35] bg-[#12151d] p-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8B5CF6]"
    >
      <span
        className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
          !isDark ? "bg-[#1f2430] text-[#f4c95d]" : "text-[#5b6270]"
        }`}
      >
        <Sun size={15} />
      </span>
      <span
        className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
          isDark ? "bg-[#312a5e] text-[#a78bfa]" : "text-[#5b6270]"
        }`}
      >
        <Moon size={14} />
      </span>
    </button>
  );
}
