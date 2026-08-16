import { Icon } from "./Icon";
import type { useWorkspace } from "./useWorkspace";

function pct(v: number | undefined) {
  return typeof v === "number" ? `${Math.round(v)}%` : "—";
}

export function ContextPanel({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const { activeModel, fmtSize, ctxUsed, health, tokensPerSec, ttft, uptime } = ws;

  const ctxPct = activeModel && activeModel.ctxMax > 0 ? Math.min(100, Math.round((ctxUsed / activeModel.ctxMax) * 100)) : 0;
  const stateLabel = activeModel?.status === "running" ? "RUNNING" : activeModel?.status === "loading" ? "LOADING" : "AVAILABLE";

  return (
    <aside className="context-panel">
      <div className="context-header">
        <div className="context-title">Context</div>
        <button className="context-manage-btn" onClick={() => ws.showToast("Not available yet")}>Manage</button>
      </div>

      <div className="context-section">
        <div className="context-section-label">Model</div>
        <div className="model-card">
          <div className="model-card-info">
            <div className="model-card-name">{activeModel ? `${activeModel.name} (${activeModel.params})` : "No model loaded"}</div>
            <div className="model-card-meta">{activeModel ? `${activeModel.quant} · ${fmtSize(activeModel.sizeGb)}` : "—"}</div>
          </div>
          <div
            className="model-card-state"
            style={{
              color: activeModel?.status === "running" ? "var(--success)" : activeModel?.status === "loading" ? "var(--warning)" : "var(--text-muted)",
              background: activeModel?.status === "running" ? "var(--success-soft)" : activeModel?.status === "loading" ? "var(--warning-soft)" : "var(--panel)",
            }}
          >
            {stateLabel}
          </div>
        </div>
      </div>

      <div className="context-section">
        <div className="context-section-label">Context Window</div>
        <div className="ctx-window-row">
          <span className="ctx-window-label">Tokens used (est.)</span>
          <span className="ctx-window-value">{ctxUsed.toLocaleString()} / {activeModel?.ctxMax.toLocaleString() ?? "—"}</span>
        </div>
        <div className="progress-track">
          <div className={`progress-fill ${ctxPct > 90 ? "crit" : ctxPct > 70 ? "warn" : ""}`} style={{ width: `${ctxPct}%` }} />
        </div>
        <div className="ctx-window-pct">{ctxPct}%</div>
      </div>

      <div className="context-section">
        <div className="context-section-label">Tools</div>
        <div className="tool-row"><Icon id="i-folder" size={14} /><span className="tool-name">RAG Documents</span><span className="tool-state enabled">Enabled</span></div>
        <div className="tool-row"><Icon id="i-search2" size={14} /><span className="tool-name">RAG Search</span><span className="tool-state enabled">Enabled</span></div>
        <div className="tool-row"><Icon id="i-terminal" size={14} /><span className="tool-name">Terminal</span><span className="tool-state disabled">Disabled</span></div>
        <div className="tool-row"><Icon id="i-globe" size={14} /><span className="tool-name">Web Access</span><span className="tool-state disabled">Disabled</span></div>
      </div>

      <div className="context-section">
        <div className="context-section-label">Runtime</div>
        <div className="runtime-row"><span className="runtime-label">Tokens / sec</span><span className="runtime-value">{tokensPerSec != null ? `${tokensPerSec} tok/s` : "—"}</span></div>
        <div className="runtime-row"><span className="runtime-label">TTFT (p50)</span><span className="runtime-value">{ttft.p50Ms != null ? `${ttft.p50Ms} ms` : "—"}</span></div>
        <div className="runtime-row"><span className="runtime-label">Total Tokens</span><span className="runtime-value">{ws.totalTokens.toLocaleString()}</span></div>
        <div className="runtime-row"><span className="runtime-label">Uptime</span><span className="runtime-value">{uptime}</span></div>
        <button className="runtime-details-btn" onClick={() => ws.setDrawerOpen(true)}>View Details</button>
      </div>

      <div className="context-section">
        <div className="context-section-label">Hardware</div>
        <div className="hw-row">
          <div className="hw-top"><span className="hw-name">CPU</span><span className="hw-pct">{pct(health.cpuPercent)}</span></div>
          <div className="progress-track"><div className="progress-fill" style={{ width: pct(health.cpuPercent) }} /></div>
        </div>
        <div className="hw-row">
          <div className="hw-top"><span className="hw-name">RAM</span><span className="hw-pct">{pct(health.ramPercent)}</span></div>
          <div className="progress-track"><div className="progress-fill" style={{ width: pct(health.ramPercent) }} /></div>
          {health.ramTotalGb != null && (
            <div className="hw-sub">{health.ramUsedGb?.toFixed(1)} / {health.ramTotalGb.toFixed(1)} GB</div>
          )}
        </div>
        {health.gpuPercent != null && (
          <div className="hw-row">
            <div className="hw-top"><span className="hw-name">GPU</span><span className="hw-pct">{pct(health.gpuPercent)}</span></div>
            <div className="progress-track"><div className="progress-fill" style={{ width: pct(health.gpuPercent) }} /></div>
          </div>
        )}
      </div>

      <div className="privacy-panel">
        <div className="privacy-top">
          <Icon id="i-lock" size={14} />
          <span className="privacy-title">Privacy</span>
        </div>
        <div className="privacy-main">100% Local</div>
        <div className="privacy-sub">No data leaves your machine</div>
      </div>
    </aside>
  );
}
