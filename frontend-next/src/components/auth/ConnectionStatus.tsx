"use client";

import { Wifi } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/Button";

type CheckState = "idle" | "checking" | "connected" | "failed";

const HEALTH_ENDPOINT =
  process.env.NEXT_PUBLIC_MICROLLM_API_URL ?? "http://localhost:8000";

export function ConnectionStatus() {
  const [state, setState] = useState<CheckState>("idle");

  async function checkConnection() {
    setState("checking");
    try {
      const res = await fetch(`${HEALTH_ENDPOINT}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(4000),
      });
      setState(res.ok ? "connected" : "failed");
    } catch {
      setState("failed");
    }
  }

  const indicator =
    state === "failed"
      ? "bg-[#E5484D]"
      : state === "checking"
      ? "bg-[#f4c95d]"
      : "bg-[#3DD68C]";

  const label =
    state === "connected"
      ? "Local backend connected"
      : state === "checking"
      ? "Checking..."
      : state === "failed"
      ? "Unable to reach localhost:8000"
      : "Localhost:8080";

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[#181c26] pt-5 text-[13px] text-[#7a8194]">
      <div className="flex items-center gap-2" aria-live="polite">
        <span
          className={`h-2 w-2 rounded-full ${indicator}`}
          aria-hidden="true"
        />
        <span>{label}</span>
        {state === "idle" && (
          <>
            <span aria-hidden="true">•</span>
            <span>Delta di Browser</span>
          </>
        )}
      </div>
      <Button
        type="button"
        variant="secondary"
        onClick={checkConnection}
        disabled={state === "checking"}
        className="!h-9 !w-auto px-3.5 text-[13px] gap-1.5"
      >
        <Wifi size={14} />
        Check Connection
      </Button>
    </div>
  );
}
