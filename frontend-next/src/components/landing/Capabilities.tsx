import { ArrowUpRight } from "lucide-react";
import { Panel, SectionHeading } from "@/components/landing/primitives";
import { CAPABILITIES } from "@/components/landing/content";

export function Capabilities() {
  return (
    <Panel id="capabilities" className="px-4 py-12 sm:px-10 sm:py-16 lg:px-14">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <SectionHeading className="max-w-[560px]">
          What is actually in the box
        </SectionHeading>
        <p className="max-w-[380px] text-[14px] leading-[1.65] text-[#8a90a2]">
          Seven phases shipped, v1.2.0 in production. Every card below maps to a
          module you can open and read.
        </p>
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CAPABILITIES.map(({ tag, module, title, body }) => (
          <article
            key={title}
            className="group flex flex-col rounded-[14px] border border-[#171c27] bg-[#0E121B] p-5 transition-colors duration-200 hover:border-[#2a2145]"
          >
            <div className="flex items-center gap-2">
              <span className="rounded-full border border-[#2a2145] bg-[#120C24] px-2.5 py-0.5 font-mono text-[10px] text-[#a78bfa]">
                {tag}
              </span>
              <span className="truncate font-mono text-[11px] text-[#565d6e]">
                {module}
              </span>
              <ArrowUpRight
                size={14}
                className="ml-auto shrink-0 text-[#2f3644] transition-colors group-hover:text-[#8B5CF6]"
              />
            </div>

            <h3 className="mt-5 text-[17px] font-semibold tracking-tight text-[#e8eaf0]">
              {title}
            </h3>
            <p className="mt-2 text-[13.5px] leading-[1.65] text-[#8a90a2]">
              {body}
            </p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
