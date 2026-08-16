"use client";

import { Eye, EyeOff, Lock } from "lucide-react";
import { InputHTMLAttributes, useState } from "react";
import { Input } from "@/components/ui/Input";

type PasswordInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "type">;

export function PasswordInput(props: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <Input
      id="password"
      type={visible ? "text" : "password"}
      label="Password"
      icon={<Lock size={18} />}
      placeholder="Enter your password"
      autoComplete="current-password"
      trailing={
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide password" : "Show password"}
          aria-pressed={visible}
          className="text-[#6b7280] hover:text-[#c7ccd6] transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8B5CF6] rounded"
        >
          {visible ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      }
      {...props}
    />
  );
}
