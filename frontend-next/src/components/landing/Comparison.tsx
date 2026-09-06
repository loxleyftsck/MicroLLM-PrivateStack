import { Panel, SectionHeading } from "@/components/landing/primitives";
import { COMPARISON } from "@/components/landing/content";

export function Comparison() {
  const [needCol, oursCol, theirsCol] = COMPARISON.columns;

  return (
    <Panel id="compare" className="px-4 py-12 sm:px-10 sm:py-16 lg:px-14">
      <SectionHeading className="max-w-[620px]">
        Running it yourself vs. renting someone else&rsquo;s model
      </SectionHeading>

      {/* Table layout on wide screens */}
      <div className="mt-10 hidden overflow-hidden rounded-[16px] border border-[#171c27] md:block">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="bg-[#0E121B]">
              <th className="w-[28%] px-6 py-4 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#565d6e]">
                {needCol}
              </th>
              <th className="w-[36%] border-l border-[#171c27] px-6 py-4 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#a78bfa]">
                {oursCol}
              </th>
              <th className="w-[36%] border-l border-[#171c27] px-6 py-4 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#565d6e]">
                {theirsCol}
              </th>
            </tr>
          </thead>
          <tbody>
            {COMPARISON.rows.map(([need, ours, theirs]) => (
              <tr key={need} className="border-t border-[#171c27]">
                <th
                  scope="row"
                  className="px-6 py-5 text-[14px] font-medium text-[#c7ccd6]"
                >
                  {need}
                </th>
                <td className="border-l border-[#171c27] bg-[#0C0A15] px-6 py-5 text-[14px] leading-[1.6] text-[#d6d9e2]">
                  {ours}
                </td>
                <td className="border-l border-[#171c27] px-6 py-5 text-[14px] leading-[1.6] text-[#7a8194]">
                  {theirs}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Stacked cards on narrow screens */}
      <div className="mt-8 flex flex-col gap-4 md:hidden">
        {COMPARISON.rows.map(([need, ours, theirs]) => (
          <div
            key={need}
            className="rounded-[14px] border border-[#171c27] bg-[#0E121B] p-5"
          >
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#565d6e]">
              {need}
            </p>
            <div className="mt-4 flex flex-col gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#a78bfa]">
                  {oursCol}
                </p>
                <p className="mt-1 text-[14px] leading-[1.6] text-[#d6d9e2]">
                  {ours}
                </p>
              </div>
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#565d6e]">
                  {theirsCol}
                </p>
                <p className="mt-1 text-[14px] leading-[1.6] text-[#7a8194]">
                  {theirs}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
