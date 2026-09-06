import { Panel, SectionHeading } from "@/components/landing/primitives";
import { STEPS } from "@/components/landing/content";

export function HowItWorks() {
  return (
    <Panel id="how-it-works" className="px-4 py-12 sm:px-10 sm:py-16 lg:px-14">
      <SectionHeading>How a private stack comes together</SectionHeading>

      <div className="mt-10 grid gap-px overflow-hidden rounded-[16px] border border-[#171c27] bg-[#171c27] sm:grid-cols-2">
        {STEPS.map(({ number, title, body }) => (
          <article
            key={number}
            className="flex flex-col bg-[#0B0E14] p-6 transition-colors duration-200 hover:bg-[#0E121B] sm:p-8"
          >
            <span className="font-mono text-[13px] font-medium text-[#6D3FD6]">
              {number}
            </span>
            <h3 className="mt-4 text-[18px] font-semibold tracking-tight text-[#e8eaf0]">
              {title}
            </h3>
            <p className="mt-2.5 text-[14px] leading-[1.65] text-[#8a90a2]">
              {body}
            </p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
