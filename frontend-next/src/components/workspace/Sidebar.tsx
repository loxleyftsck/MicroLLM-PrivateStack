import { Icon } from "./Icon";
import type { useWorkspace } from "./useWorkspace";

const NAV_ITEMS: { key: string; icon: string; label: string; hint?: string }[] = [
  { key: "explorer", icon: "i-folder", label: "Explorer" },
  { key: "search", icon: "i-search2", label: "Search", hint: "⌘F" },
  { key: "git", icon: "i-git", label: "Git" },
  { key: "terminal", icon: "i-terminal", label: "Terminal", hint: "⌘`" },
];

export function Sidebar({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const { sessions, activeSessionId, selectSession, newSession, sessionSearch, setSessionSearch, health } = ws;

  return (
    <aside className="sidebar">
      <div className="sidebar-search">
        <Icon id="i-search" size={14} />
        <input
          id="sessionSearch"
          type="text"
          placeholder="Search sessions"
          value={sessionSearch}
          onChange={(e) => setSessionSearch(e.target.value)}
        />
        <kbd>⌘K</kbd>
      </div>

      <button className="new-session-btn" onClick={newSession}>
        <Icon id="i-plus" size={14} />
        New Session
      </button>

      <div className="sidebar-section-label">Sessions</div>
      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div style={{ padding: "16px 10px", color: "var(--text-muted)", fontSize: "12.5px" }}>
            No sessions match &quot;{sessionSearch}&quot;
          </div>
        ) : (
          sessions.map((s) => (
            <button
              key={s.id}
              className={`session-item ${s.id === activeSessionId ? "active" : ""}`}
              onClick={() => selectSession(s.id)}
            >
              <span className="session-dot" />
              <span className="session-body">
                <div className="session-title">{s.title}</div>
                <div className="session-preview">{s.preview}</div>
                <div className="session-time">{s.time}</div>
              </span>
            </button>
          ))
        )}
      </div>

      <div className="sidebar-divider" />

      <nav className="workspace-nav">
        <div className="sidebar-section-label" style={{ paddingLeft: 10 }}>Workspace</div>
        {NAV_ITEMS.map((item) => (
          <button key={item.key} className="workspace-nav-item" onClick={() => ws.showToast("Not available yet")}>
            <Icon id={item.icon} size={15} /> {item.label}
            {item.hint && <span className="kbd-hint">{item.hint}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-status">
          <span className="local-dot" />
          <span className="sidebar-footer-text">
            <div className="sidebar-footer-title">{health.reachable ? "System Online" : "Backend Unreachable"}</div>
            <div className="sidebar-footer-sub">
              {health.reachable ? "All services running locally" : "Preview mode — backend not responding"}
            </div>
          </span>
        </div>
        <span className="sidebar-footer-version">v1.3.0</span>
      </div>
    </aside>
  );
}
