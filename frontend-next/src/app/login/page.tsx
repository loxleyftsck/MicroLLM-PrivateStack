import type { Metadata } from "next";
import { LoginShell } from "@/components/auth/LoginShell";

export const metadata: Metadata = {
  title: "Sign in",
  description: "Sign in to your private, locally hosted AI workspace.",
};

export default function LoginPage() {
  return <LoginShell />;
}
