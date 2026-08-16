"use client";

import { Mail } from "lucide-react";
import { InputHTMLAttributes } from "react";
import { Input } from "@/components/ui/Input";

type EmailInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "type">;

export function EmailInput(props: EmailInputProps) {
  return (
    <Input
      id="email"
      type="email"
      label="Email"
      icon={<Mail size={18} />}
      placeholder="you@example.com"
      autoComplete="email"
      {...props}
    />
  );
}
