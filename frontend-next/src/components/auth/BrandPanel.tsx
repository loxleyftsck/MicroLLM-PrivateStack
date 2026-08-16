import { Lock, Shield, Zap } from "lucide-react";
import { MicroLLMLogo } from "@/components/branding/MicroLLMLogo";

const FEATURES = [
  {
    icon: Lock,
    title: "100% Local Inference",
    description: "No data leaves your machine",
  },
  {
    icon: Shield,
    title: "Private & Secure",
    description: "End-to-end encrypted",
  },
  {
    icon: Zap,
    title: "Developer First",
    description: "Built for serious developers",
  },
];

export function BrandPanel() {
  return (
    <div className="relative hidden md:flex w-full md:w-[40%] flex-col justify-between overflow-hidden bg-[#0C1020] px-10 py-10 lg:px-12 lg:py-12">
      <div
        className="pointer-events-none absolute -bottom-24 -left-24 h-80 w-80 rounded-full bg-[#6D3FD6] opacity-[0.12] blur-[90px]"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.15] [background-image:radial-gradient(circle,#3a4258_1px,transparent_1px)] [background-size:22px_22px] [mask-image:linear-gradient(to_bottom,black,transparent_55%)]"
        aria-hidden="true"
      />

      <div className="relative z-10 flex flex-col gap-14">
        <div className="flex items-center gap-2.5">
          <MicroLLMLogo className="h-7 w-7" />
          <span className="text-[17px] font-semibold tracking-tight text-[#e8eaf0]">
            MicroLLM
          </span>
        </div>

        <div className="flex flex-col gap-6">
          <h1 className="text-[44px] font-bold leading-[1.05] tracking-tight lg:text-[50px]">
            <span className="text-white">Private AI.</span>
            <br />
            <span className="text-[#8B5CF6]">Runs Locally.</span>
          </h1>
          <p className="max-w-sm text-[15px] leading-relaxed text-[#8a90a2]">
            Your data stays on your machine.
            <br />
            Powerful models. Total privacy.
          </p>
        </div>

        <ul className="flex flex-col gap-5">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <li key={title} className="flex items-start gap-3.5">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#1a1f30] text-[#a78bfa]">
                <Icon size={16} />
              </span>
              <div className="flex flex-col gap-0.5">
                <span className="text-[14px] font-semibold text-[#e8eaf0]">
                  {title}
                </span>
                <span className="text-[13px] text-[#7a8194]">{description}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="relative z-10 mt-10 flex justify-center" aria-hidden="true">
        <LocalComputeIllustration />
      </div>
    </div>
  );
}

function LocalComputeIllustration() {
  return (
    <svg width="220" height="150" viewBox="0 0 220 150" fill="none">
      <ellipse cx="110" cy="128" rx="70" ry="10" fill="#6D3FD6" opacity="0.15" />
      <g opacity="0.9">
        <path
          d="M50 100 L110 70 L170 100 L110 130 Z"
          fill="#11162a"
          stroke="#3a3f6b"
          strokeWidth="1"
        />
        <path
          d="M50 100 L110 130 L110 118 L50 88 Z"
          fill="#0d1120"
          stroke="#3a3f6b"
          strokeWidth="1"
        />
        <path
          d="M170 100 L110 130 L110 118 L170 88 Z"
          fill="#171c34"
          stroke="#3a3f6b"
          strokeWidth="1"
        />
      </g>
      <g opacity="0.95">
        <path
          d="M64 76 L110 54 L156 76 L110 98 Z"
          fill="#171c34"
          stroke="#5B7FE0"
          strokeWidth="1.2"
        />
        <path
          d="M64 76 L110 98 L110 86 L64 64 Z"
          fill="#12162b"
          stroke="#5B7FE0"
          strokeWidth="1"
        />
        <path
          d="M156 76 L110 98 L110 86 L156 64 Z"
          fill="#1c2140"
          stroke="#5B7FE0"
          strokeWidth="1"
        />
        <text
          x="110"
          y="74"
          textAnchor="middle"
          fontSize="10"
          fill="#a78bfa"
          fontFamily="var(--font-geist-mono), monospace"
        >
          uLLM
        </text>
      </g>
      <line
        x1="110"
        y1="98"
        x2="110"
        y2="118"
        stroke="#8B5CF6"
        strokeWidth="1"
        opacity="0.5"
      />
    </svg>
  );
}
