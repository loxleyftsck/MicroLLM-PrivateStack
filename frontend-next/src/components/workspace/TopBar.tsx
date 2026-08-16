import { Icon } from "./Icon";
import type { useWorkspace } from "./useWorkspace";

export function TopBar({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const { activeModel, models, fmtSize, dropdownOpen, setDropdownOpen, switchModel, switchingModel } = ws;

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="nav-toggle" onClick={ws.toggleSidebar} aria-label="Toggle sessions">
          <Icon id="i-menu" size={18} />
        </button>
        <div className="brand">
          <div className="brand-mark"><Icon id="i-mark" size={16} /></div>
          <div className="brand-text">
            <div className="brand-title">MicroLLM</div>
            <div className="brand-subtitle">Private local inference</div>
          </div>
        </div>
      </div>

      <div className="model-selector">
        <button
          className="model-selector-btn"
          aria-expanded={dropdownOpen}
          aria-haspopup="listbox"
          onClick={(e) => {
            e.stopPropagation();
            setDropdownOpen(!dropdownOpen);
          }}
        >
          <span className={`model-status-dot ${activeModel?.status ?? ""}`} />
          <span className="model-selector-label">
            <div className="model-selector-name">
              {activeModel ? `${activeModel.name} (${activeModel.params})` : "No model"}
            </div>
            <div className="model-selector-meta">
              {activeModel ? `${activeModel.quant} · ${fmtSize(activeModel.sizeGb)}` : "—"}
            </div>
          </span>
          <Icon id="i-chevron-down" size={14} />
        </button>
        <div className={`model-dropdown ${dropdownOpen ? "open" : ""}`} role="listbox">
          <div className="model-dropdown-label">Local models</div>
          <div>
            {models.map((m) => {
              const label =
                m.status === "running" ? "RUNNING" : m.status === "loading" ? "LOADING" : m.status === "unavailable" ? "UNAVAILABLE" : "AVAILABLE";
              const dotClass = m.status === "running" ? "running" : m.status === "loading" ? "loading" : "";
              return (
                <button
                  key={m.id}
                  className="model-option"
                  disabled={m.status === "loading" || m.status === "unavailable" || switchingModel}
                  role="option"
                  aria-selected={m.id === activeModel?.id}
                  onClick={() => {
                    setDropdownOpen(false);
                    switchModel(m.id);
                  }}
                >
                  <span className={`model-status-dot ${dotClass}`} />
                  <span className="model-option-info">
                    <div className="model-option-name">{m.name}</div>
                    <div className="model-option-meta">{m.params} · {m.quant}</div>
                  </span>
                  <span className={`model-option-state ${m.status}`}>{label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="topbar-right">
        <div className="local-indicator">
          <span className="local-dot" />
          <span className="local-indicator-text">
            <div className="local-indicator-title">Local</div>
            <div className="local-indicator-sub">No cloud traffic</div>
          </span>
        </div>
        <div className="topbar-divider" />
        <button className="icon-btn context-toggle-btn" onClick={ws.toggleContext} aria-label="Toggle context panel" title="Context">
          <Icon id="i-terminal" size={17} />
        </button>
        <button className="icon-btn" onClick={() => ws.showToast("Not available yet")} aria-label="Settings" title="Settings">
          <Icon id="i-settings" size={17} />
        </button>
        <button className="avatar-btn" title={ws.user?.email} aria-label="Account" onClick={ws.logout}>
          {ws.user?.display_name?.[0]?.toUpperCase() ?? "?"}
        </button>
      </div>
    </header>
  );
}
