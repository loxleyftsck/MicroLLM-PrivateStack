import { FileText, Zap } from "lucide-react";

/**
 * A static, decorative rendering of the workspace UI. Not interactive — it
 * exists to show what the product looks like above the fold.
 */
export function WorkspacePreview() {
  return (
    <div
      className="relative w-full overflow-hidden rounded-[16px] border border-[#1a1f2b] bg-[#0E121B] shadow-[0_30px_80px_-40px_rgba(0,0,0,0.9)]"
      aria-hidden="true"
    >
      <div className="flex items-center gap-2 border-b border-[#161b25] bg-[#0B0E14] px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-[#252b38]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#252b38]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#252b38]" />
        <span className="ml-3 font-mono text-[11px] text-[#565d6e]">
          localhost:8000 — no egress
        </span>
      </div>

      <div className="flex flex-col gap-4 p-4 sm:p-5">
        <div className="flex justify-end">
          <p className="max-w-[78%] rounded-[12px] rounded-br-[4px] bg-[#1a1430] px-3.5 py-2.5 text-[13px] leading-relaxed text-[#d6d9e2]">
            Which retention window does our DPA commit to?
          </p>
        </div>

        <div className="flex flex-col gap-2.5">
          <p className="max-w-[88%] rounded-[12px] rounded-bl-[4px] border border-[#1a1f2b] bg-[#11151f] px-3.5 py-2.5 text-[13px] leading-relaxed text-[#c7ccd6]">
            The agreement commits to a 30-day retention window for processed
            records, after which they are purged from primary storage and
            backups within a further 14 days.
          </p>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#2a2145] bg-[#120C24] px-2.5 py-1 font-mono text-[10px] text-[#a78bfa]">
              <Zap size={10} />
              ttft 42.3ms
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#242a36] bg-[#12151d] px-2.5 py-1 font-mono text-[10px] text-[#8a90a2]">
              cache miss
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#242a36] bg-[#12151d] px-2.5 py-1 font-mono text-[10px] text-[#8a90a2]">
              deepseek-r1-1.5b · q4
            </span>
          </div>

          <div className="rounded-[10px] border border-[#1a1f2b] bg-[#0B0E14] p-3">
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#565d6e]">
              rag_sources
            </p>
            <div className="flex items-start gap-2.5">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[#161b26] text-[#a78bfa]">
                <FileText size={12} />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-3">
                  <span className="truncate text-[12px] font-medium text-[#c7ccd6]">
                    vendor-dpa-2024.pdf
                  </span>
                  <span className="shrink-0 font-mono text-[11px] text-[#7c5ce0]">
                    0.93
                  </span>
                </div>
                <p className="mt-0.5 truncate text-[11px] text-[#6b7183]">
                  &ldquo;…Processor shall retain Personal Data for no longer
                  than thirty (30) days…&rdquo;
                </p>
                <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-[#161b26]">
                  <div className="h-full w-[93%] rounded-full bg-[#6D3FD6]" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
