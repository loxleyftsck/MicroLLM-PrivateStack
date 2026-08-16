"use client";

import "@/app/workspace/workspace.css";
import { ConversationPanel } from "./ConversationPanel";
import { ContextPanel } from "./ContextPanel";
import { IconSprite } from "./IconSprite";
import { RuntimeDrawer } from "./RuntimeDrawer";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { useWorkspace } from "./useWorkspace";

export function WorkspaceApp() {
  const ws = useWorkspace();

  if (ws.authStatus !== "authenticated") {
    return (
      <div style={{ display: "flex", minHeight: "100vh", alignItems: "center", justifyContent: "center", background: "#080B12" }}>
        <p style={{ color: "#7a8194", fontSize: 14 }}>Checking session...</p>
      </div>
    );
  }

  return (
    <>
      <IconSprite />
      <div
        className="scrim"
        onClick={ws.closeMobilePanels}
        style={{
          opacity: ws.sidebarOpen || ws.contextOpen ? 1 : 0,
          pointerEvents: ws.sidebarOpen || ws.contextOpen ? "auto" : "none",
        }}
      />

      <div
        className={`app-shell ${ws.sidebarOpen ? "sidebar-open" : ""} ${ws.contextOpen ? "context-open" : ""}`}
        onClick={ws.closeAllPopovers}
      >
        <TopBar ws={ws} />
        <Sidebar ws={ws} />
        <ConversationPanel ws={ws} />
        <ContextPanel ws={ws} />
      </div>

      <RuntimeDrawer ws={ws} />

      <div className={`toast ${ws.toast ? "show" : ""}`}>{ws.toast}</div>
    </>
  );
}
