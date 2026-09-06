import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";

/**
 * Shared shell for every landing section: the page background shows through the
 * gutters, and each block sits on a slightly lifted panel with a hairline edge.
 */
export function Panel({
  id,
  className = "",
  children,
}: {
  id?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className={`mx-auto w-full max-w-[1280px] scroll-mt-24 rounded-[24px] border border-[#171c27] bg-[#0B0E14] ${className}`}
    >
      {children}
    </section>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-[#2a2145] bg-[#120C24] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-[#a78bfa]">
      {children}
    </span>
  );
}

export function SectionHeading({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h2
      className={`text-[30px] font-bold leading-[1.12] tracking-tight text-[#f2f3f7] sm:text-[38px] ${className}`}
    >
      {children}
    </h2>
  );
}

type CtaProps = ComponentProps<typeof Link> & {
  variant?: "primary" | "ghost";
};

export function Cta({ variant = "primary", className = "", ...props }: CtaProps) {
  const styles =
    variant === "primary"
      ? "bg-[#6D3FD6] text-white hover:bg-[#7B4EE0] active:bg-[#5F35BD] border border-transparent"
      : "border border-[#252B35] bg-[#12151d] text-[#c7ccd6] hover:border-[#333a47] hover:bg-[#161a24]";

  return (
    <Link
      className={`inline-flex h-[46px] items-center justify-center gap-2 rounded-full px-6 text-[14px] font-medium transition-colors duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8B5CF6] ${styles} ${className}`}
      {...props}
    />
  );
}
