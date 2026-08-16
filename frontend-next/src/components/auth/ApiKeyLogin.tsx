"use client";

import { FormEvent, useId, useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { KeyRound } from "lucide-react";

interface ApiKeyLoginProps {
  open: boolean;
  onClose: () => void;
  onAuthenticate: (apiKey: string) => Promise<void> | void;
}

export function ApiKeyLogin({ open, onClose, onAuthenticate }: ApiKeyLoginProps) {
  const titleId = useId();
  const [apiKey, setApiKey] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!apiKey.trim()) return;
    setSubmitting(true);
    try {
      await onAuthenticate(apiKey.trim());
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} titleId={titleId}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div className="flex items-center gap-2.5">
          <KeyRound size={18} className="text-[#a78bfa]" />
          <h2 id={titleId} className="text-[18px] font-semibold text-[#e8eaf0]">
            Sign in with API Key
          </h2>
        </div>

        <Input
          label="API Key"
          type="password"
          placeholder="sk-local-••••••••••••"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          autoFocus
          autoComplete="off"
        />

        <p className="text-[13px] text-[#7a8194]">
          Your API key is only sent to your local MicroLLM instance and stored
          on this device.
        </p>

        <div className="flex items-center justify-end gap-3 pt-1">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            className="!w-auto px-5"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={submitting || !apiKey.trim()}
            className="!h-11 !w-auto px-5 text-[14px]"
          >
            {submitting ? "Authenticating..." : "Authenticate"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
