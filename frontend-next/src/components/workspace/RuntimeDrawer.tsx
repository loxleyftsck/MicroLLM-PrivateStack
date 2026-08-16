import { Icon } from "./Icon";
import type { useWorkspace } from "./useWorkspace";

export function RuntimeDrawer({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const { drawerOpen, setDrawerOpen, activeModel, health, tokensPerSec, ttft, uptime } = ws;

  return (
    <>
      <div className={`drawer-backdrop ${drawerOpen ? "open" : ""}`} onClick={() => setDrawerOpen(false)} />
      <div className={`drawer ${drawerOpen ? "open" : ""}`}>
        <div className="drawer-header">
          <div className="drawer-title">RUNTIME DETAILS</div>
          <button className="icon-btn" onClick={() => setDrawerOpen(false)}>
            <Icon id="i-x" size={16} />
          </button>
        </div>
        <div className="drawer-body">
          <div className="drawer-section-label">Model</div>
          <div className="drawer-row"><span className="drawer-row-label">Model</span><span className="drawer-row-value">{activeModel?.name ?? "—"}</span></div>
          <div className="drawer-row"><span className="drawer-row-label">Backend</span><span className="drawer-row-value">llama.cpp</span></div>
          <div className="drawer-row"><span className="drawer-row-label">Quantization</span><span className="drawer-row-value">{activeModel?.quant ?? "—"}</span></div>
          <div className="drawer-row"><span className="drawer-row-label">Context</span><span className="drawer-row-value">{activeModel?.ctxMax.toLocaleString() ?? "—"}</span></div>

          <div className="drawer-section-label">Hardware</div>
          <div className="drawer-row"><span className="drawer-row-label">CPU</span><span className="drawer-row-value">{health.cpuPercent != null ? `${Math.round(health.cpuPercent)}%` : "—"}</span></div>
          <div className="drawer-row"><span className="drawer-row-label">RAM</span><span className="drawer-row-value">{health.ramUsedGb != null && health.ramTotalGb != null ? `${health.ramUsedGb.toFixed(1)} / ${health.ramTotalGb.toFixed(1)} GB` : "—"}</span></div>
          {health.gpuPercent != null && (
            <div className="drawer-row"><span className="drawer-row-label">GPU Utilization</span><span className="drawer-row-value">{Math.round(health.gpuPercent)}%</span></div>
          )}

          <div className="drawer-section-label">Performance</div>
          <div className="drawer-row"><span className="drawer-row-label">Tokens/sec (last)</span><span className="drawer-row-value">{tokensPerSec != null ? `${tokensPerSec} tok/s` : "—"}</span></div>
          <div className="drawer-row"><span className="drawer-row-label">TTFT p50 ({ttft.samples} samples)</span><span className="drawer-row-value">{ttft.p50Ms != null ? `${ttft.p50Ms} ms` : "—"}</span></div>
          <div className="drawer-row"><span className="drawer-row-label">Uptime</span><span className="drawer-row-value">{uptime}</span></div>
        </div>
      </div>
    </>
  );
}
