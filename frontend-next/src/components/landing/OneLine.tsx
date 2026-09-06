import { Eyebrow, Panel } from "@/components/landing/primitives";

export function OneLine() {
  return (
    <Panel className="border-[#241a44] bg-[#0D0A17] px-4 py-10 sm:px-10 sm:py-12 lg:px-14">
      <Eyebrow>In one line</Eyebrow>
      <p className="mt-5 max-w-[900px] text-[19px] leading-[1.55] tracking-tight text-[#d6d9e2] sm:text-[23px]">
        MicroLLM is the private inference layer for teams that cannot send their
        data to a vendor. The model, the vector index, the chat history, and the
        audit trail all stay inside your own infrastructure — and it still fits
        on a 2GB machine.
      </p>
    </Panel>
  );
}
