"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MicroLLMLogo } from "@/components/branding/MicroLLMLogo";

interface CurrentUser {
  id: string;
  email: string;
  display_name: string;
}

type Status = "checking" | "authenticated" | "unauthenticated";

const API_URL = process.env.NEXT_PUBLIC_MICROLLM_API_URL ?? "http://localhost:8000";

export function WorkspacePlaceholder() {
  const router = useRouter();
  const [status, setStatus] = useState<Status>("checking");
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    async function verifySession() {
      const token = window.localStorage.getItem("microllm_token");
      if (!token) {
        setStatus("unauthenticated");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("invalid_session");
        const data = await res.json();
        setUser(data.user);
        setStatus("authenticated");
      } catch {
        window.localStorage.removeItem("microllm_token");
        setStatus("unauthenticated");
      }
    }

    verifySession();
  }, []);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/");
    }
  }, [status, router]);

  function handleLogout() {
    window.localStorage.removeItem("microllm_token");
    router.replace("/");
  }

  if (status !== "authenticated") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#080B12]">
        <p className="text-[14px] text-[#7a8194]">Checking session...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col bg-[#080B12] text-[#e8eaf0]">
      <header className="flex items-center justify-between border-b border-[#181c26] px-6 py-4 sm:px-10">
        <div className="flex items-center gap-2.5">
          <MicroLLMLogo className="h-6 w-6" />
          <span className="text-[15px] font-semibold">MicroLLM</span>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="flex items-center gap-2 rounded-[8px] border border-[#252B35] bg-[#12151d] px-3.5 py-2 text-[13px] text-[#c7ccd6] transition-colors hover:bg-[#161a24]"
        >
          <LogOut size={14} />
          Log out
        </button>
      </header>

      <div className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-md text-center">
          <h1 className="text-[26px] font-bold tracking-tight">
            Welcome, {user?.display_name || user?.email}
          </h1>
          <p className="mt-3 text-[15px] leading-relaxed text-[#8a90a2]">
            The workspace UI hasn&apos;t been built yet. You&apos;re signed
            in as <span className="text-[#c7ccd6]">{user?.email}</span> and
            your session is valid.
          </p>
        </div>
      </div>
    </main>
  );
}
