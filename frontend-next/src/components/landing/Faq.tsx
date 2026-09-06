import { Plus } from "lucide-react";
import { Panel, SectionHeading } from "@/components/landing/primitives";
import { FAQS } from "@/components/landing/content";

export function Faq() {
  return (
    <Panel id="faq" className="px-4 py-12 sm:px-10 sm:py-16 lg:px-14">
      <SectionHeading>Questions worth asking first</SectionHeading>

      <div className="mt-10 overflow-hidden rounded-[16px] border border-[#171c27]">
        {FAQS.map(({ number, question, answer }) => (
          <details
            key={number}
            className="group border-b border-[#171c27] bg-[#0B0E14] last:border-b-0 open:bg-[#0E121B]"
          >
            <summary className="flex cursor-pointer list-none items-center gap-4 px-5 py-5 transition-colors hover:bg-[#0E121B] sm:px-7 [&::-webkit-details-marker]:hidden">
              <span className="font-mono text-[12px] text-[#6D3FD6]">
                {number}
              </span>
              <span className="flex-1 text-[15px] font-medium tracking-tight text-[#e8eaf0] sm:text-[16px]">
                {question}
              </span>
              <Plus
                size={16}
                className="shrink-0 text-[#565d6e] transition-transform duration-200 group-open:rotate-45"
              />
            </summary>
            <p className="px-5 pb-6 pl-[52px] text-[14px] leading-[1.7] text-[#8a90a2] sm:px-7 sm:pl-[70px]">
              {answer}
            </p>
          </details>
        ))}
      </div>
    </Panel>
  );
}
