import { ArrowRight } from "lucide-react";
import { Cta, Panel } from "@/components/landing/primitives";
import { REPO_URL } from "@/components/landing/content";
import { GithubMark } from "@/components/landing/GithubMark";

export function FinalCta() {
  return (
    <Panel className="relative overflow-hidden border-[#241a44] bg-[#0D0A17] px-4 py-16 text-center sm:px-10 sm:py-20">
      <div
        className="pointer-events-none absolute -bottom-32 left-1/2 h-[360px] w-[560px] -translate-x-1/2 rounded-full bg-[#6D3FD6] opacity-[0.14] blur-[110px]"
        aria-hidden="true"
      />

      <div className="relative z-10 flex flex-col items-center">
        <h2 className="max-w-[640px] text-[32px] font-bold leading-[1.1] tracking-tight text-[#f2f3f7] sm:text-[42px]">
          Run your own model tonight
        </h2>
        <p className="mt-5 max-w-[520px] text-[15px] leading-[1.65] text-[#8a90a2]">
          Clone the repo, generate a JWT secret, download the model, and have a
          private workspace answering questions about your own documents before
          the evening is out.
        </p>

        <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
          <Cta href="/login">
            Open the workspace
            <ArrowRight size={16} />
          </Cta>
          <Cta href={REPO_URL} target="_blank" rel="noreferrer" variant="ghost">
            <GithubMark size={16} />
            Star on GitHub
          </Cta>
        </div>
      </div>
    </Panel>
  );
}
