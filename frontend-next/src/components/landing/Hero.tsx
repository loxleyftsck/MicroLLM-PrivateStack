import { ArrowRight } from "lucide-react";
import { Cta, Panel } from "@/components/landing/primitives";
import { REPO_URL } from "@/components/landing/content";
import { GithubMark } from "@/components/landing/GithubMark";
import { WorkspacePreview } from "@/components/landing/WorkspacePreview";

export function Hero() {
  return (
    <Panel className="relative overflow-hidden px-4 py-12 sm:px-10 sm:py-16 lg:px-14 lg:py-20">
      <div
        className="pointer-events-none absolute -top-40 -right-24 h-[420px] w-[420px] rounded-full bg-[#6D3FD6] opacity-[0.10] blur-[120px]"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.12] [background-image:radial-gradient(circle,#3a4258_1px,transparent_1px)] [background-size:24px_24px] [mask-image:radial-gradient(70%_60%_at_20%_20%,black,transparent)]"
        aria-hidden="true"
      />

      <div className="relative z-10 grid items-center gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:gap-14">
        <div className="flex flex-col items-start">
          <h1 className="text-[40px] font-bold leading-[1.06] tracking-tight text-[#f2f3f7] sm:text-[54px] lg:text-[62px]">
            Private AI at the
            <br />
            speed of{" "}
            <span className="text-[#8B5CF6]">localhost</span>
          </h1>

          <p className="mt-6 max-w-[520px] text-[16px] leading-[1.65] text-[#8a90a2]">
            MicroLLM-PrivateStack runs a real language model — chat, retrieval
            with citations, model hot-swap — entirely on hardware you already
            own. 2GB of RAM, zero per-token cost, and not one request that
            leaves the machine.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Cta href="/login">
              Open the workspace
              <ArrowRight size={16} />
            </Cta>
            <Cta href={REPO_URL} target="_blank" rel="noreferrer" variant="ghost">
              <GithubMark size={16} />
              Star on GitHub
            </Cta>
          </div>

          <p className="mt-7 text-[13px] text-[#565d6e]">
            MIT licensed · Python 3.10+ · Windows, Linux, macOS
          </p>
        </div>

        <WorkspacePreview />
      </div>
    </Panel>
  );
}
