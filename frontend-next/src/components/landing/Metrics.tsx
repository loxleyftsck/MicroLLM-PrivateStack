import { Panel } from "@/components/landing/primitives";
import { METRICS } from "@/components/landing/content";

export function Metrics() {
  return (
    <Panel className="grid gap-px overflow-hidden bg-[#171c27] sm:grid-cols-2 lg:grid-cols-4">
      {METRICS.map(({ value, label, note }) => (
        <div key={label} className="bg-[#0B0E14] px-6 py-8 sm:px-8">
          <p className="text-[30px] font-bold tracking-tight text-[#f2f3f7] sm:text-[34px]">
            {value}
          </p>
          <p className="mt-1.5 text-[14px] font-medium text-[#c7ccd6]">{label}</p>
          <p className="mt-0.5 text-[12.5px] text-[#565d6e]">{note}</p>
        </div>
      ))}
    </Panel>
  );
}
