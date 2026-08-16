"use client";

import { InputHTMLAttributes, ReactNode, forwardRef, useId } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  icon?: ReactNode;
  trailing?: ReactNode;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, icon, trailing, error, id, className = "", ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const errorId = `${inputId}-error`;

    return (
      <div className="flex flex-col gap-2">
        <label
          htmlFor={inputId}
          className="text-[14px] font-medium text-[#e8eaf0]"
        >
          {label}
        </label>
        <div
          className={`flex items-center gap-2.5 h-[56px] rounded-[9px] border bg-[#141820] px-4 transition-colors duration-150 ${
            error
              ? "border-[#E5484D] focus-within:border-[#E5484D]"
              : "border-[#252B35] focus-within:border-[#8B5CF6]"
          }`}
        >
          {icon && (
            <span className="shrink-0 text-[#6b7280]" aria-hidden="true">
              {icon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? errorId : undefined}
            className={`peer w-full bg-transparent text-[15px] text-[#e8eaf0] placeholder:text-[#5b6270] outline-none ${className}`}
            {...props}
          />
          {trailing && <span className="shrink-0">{trailing}</span>}
        </div>
        {error && (
          <p id={errorId} className="text-[13px] text-[#E5484D]" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
