"use client";

import { ArrowRight, KeyRound, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { EmailInput } from "@/components/auth/EmailInput";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { ApiKeyLogin } from "@/components/auth/ApiKeyLogin";
import { Button } from "@/components/ui/Button";

type Status = "idle" | "loading" | "error" | "success";

const API_URL = process.env.NEXT_PUBLIC_MICROLLM_API_URL ?? "http://localhost:8000";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false);

  const isLoading = status === "loading";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setErrorMessage("");

    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok || !data.token) {
        throw new Error(data.error ?? "invalid_credentials");
      }

      window.localStorage.setItem("microllm_token", data.token);
      setStatus("success");
      router.push("/workspace");
    } catch {
      setStatus("error");
      setErrorMessage("Unable to sign in. Check your credentials and try again.");
    }
  }

  async function handleApiKeyAuthenticate(apiKey: string) {
    try {
      // No dedicated API-key endpoint exists on the backend — validate the
      // pasted token the same way any bearer token is verified.
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!res.ok) throw new Error("invalid_api_key");
      window.localStorage.setItem("microllm_token", apiKey);
      setApiKeyModalOpen(false);
      router.push("/workspace");
    } catch {
      setErrorMessage("Unable to authenticate with this API key.");
    }
  }

  return (
    <div className="flex w-full flex-col">
      <div className="mb-11">
        <h1 className="text-[36px] font-bold tracking-tight text-[#f2f3f7]">
          Welcome Back
        </h1>
        <p className="mt-2 text-[15px] text-[#8a90a2]">
          Sign in to your private AI workspace
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate>
        <EmailInput
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          required
        />
        <div className="flex flex-col gap-2">
          <PasswordInput
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            required
          />
          <div className="flex justify-end">
            <a
              href="#forgot-password"
              className="text-[13px] font-medium text-[#a78bfa] hover:text-[#c4b5fd] transition-colors"
            >
              Forgot password?
            </a>
          </div>
        </div>

        <div aria-live="assertive">
          {status === "error" && (
            <p className="text-[13px] text-[#E5484D]">{errorMessage}</p>
          )}
        </div>

        <Button type="submit" variant="primary" disabled={isLoading} className="mt-1">
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin-slow" />
              Signing in...
            </>
          ) : (
            <>
              Sign In
              <ArrowRight size={18} className="ml-auto" />
            </>
          )}
        </Button>
      </form>

      <div className="my-6 flex items-center gap-4 text-[13px] text-[#565d6e]">
        <div className="h-px flex-1 bg-[#1c212c]" />
        or
        <div className="h-px flex-1 bg-[#1c212c]" />
      </div>

      <Button
        type="button"
        variant="secondary"
        onClick={() => setApiKeyModalOpen(true)}
      >
        <KeyRound size={16} />
        Sign in with API Key
      </Button>

      <ApiKeyLogin
        open={apiKeyModalOpen}
        onClose={() => setApiKeyModalOpen(false)}
        onAuthenticate={handleApiKeyAuthenticate}
      />
    </div>
  );
}
