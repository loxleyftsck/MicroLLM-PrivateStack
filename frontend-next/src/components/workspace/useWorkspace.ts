"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type {
  ChatMessage,
  CurrentUser,
  HealthSnapshot,
  ModelStatus,
  RagSource,
  Session,
  TtftStats,
  WorkspaceModel,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_MICROLLM_API_URL ?? "http://localhost:8000";

type AuthStatus = "checking" | "authenticated" | "unauthenticated";

interface ConsoleLine {
  id: string;
  ts: string;
  tag: "info" | "user" | "error";
  msg: string;
}

function pad2(n: number) {
  return String(n).padStart(2, "0");
}
function nowHHMM() {
  const d = new Date();
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}
function nowHHMMSS() {
  const d = new Date();
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
}
function fmtSize(gb: number) {
  return gb >= 1 ? `${gb.toFixed(1)} GB` : `${Math.round(gb * 1024)} MB`;
}
function uid() {
  return Math.random().toString(36).slice(2, 10);
}

// SQLite CURRENT_TIMESTAMP comes back as naive UTC "YYYY-MM-DD HH:MM:SS" —
// force UTC parsing rather than letting the engine guess local time.
function parseServerTimestamp(ts: string): Date {
  return new Date(ts.replace(" ", "T") + "Z");
}
function formatHHMM(ts: string): string {
  const d = parseServerTimestamp(ts);
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}
function formatRelativeLabel(ts: string): string {
  const d = parseServerTimestamp(ts);
  const diffMin = Math.floor((Date.now() - d.getTime()) / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  const diffD = Math.floor(diffH / 24);
  if (diffD < 7) return `${diffD}d ago`;
  return d.toLocaleDateString();
}

interface ApiWorkspace {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

interface ApiChatMessage {
  id: string;
  role: "user" | "assistant";
  message: string;
  timestamp: string;
}

function workspaceToSession(w: ApiWorkspace): Session {
  return {
    id: w.id,
    title: w.name,
    preview: w.description || "No messages yet",
    time: formatRelativeLabel(w.created_at),
    messages: [],
    historyLoaded: false,
  };
}

export function useWorkspace() {
  const router = useRouter();

  const [authStatus, setAuthStatus] = useState<AuthStatus>("checking");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const tokenRef = useRef<string | null>(null);

  const [models, setModels] = useState<WorkspaceModel[]>([]);
  const [activeModelId, setActiveModelId] = useState<string>("");
  const [switchingModel, setSwitchingModel] = useState(false);

  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>("");
  const [sessionSearch, setSessionSearch] = useState("");
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [loadingHistoryId, setLoadingHistoryId] = useState<string | null>(null);

  const [composerText, setComposerText] = useState("");
  const [sending, setSending] = useState(false);

  const [consoleLines, setConsoleLines] = useState<ConsoleLine[]>([]);
  const [consoleCollapsed, setConsoleCollapsed] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [contextPopoverOpen, setContextPopoverOpen] = useState(false);
  const [commandPopoverOpen, setCommandPopoverOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [totalTokens, setTotalTokens] = useState(0);
  const [ctxUsed, setCtxUsed] = useState(0);
  const [tokensPerSec, setTokensPerSec] = useState<number | null>(null);
  const [ttft, setTtft] = useState<TtftStats>({ p50Ms: null, samples: 0 });
  const [health, setHealth] = useState<HealthSnapshot>({ reachable: false });

  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const startedAt = useRef(Date.now());
  const [uptime, setUptime] = useState("00:00:00");

  const addConsoleLine = useCallback((tag: ConsoleLine["tag"], msg: string) => {
    setConsoleLines((prev) => [...prev, { id: uid(), ts: nowHHMMSS(), tag, msg }].slice(-200));
  }, []);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2200);
  }, []);

  function authHeaders(): HeadersInit {
    return tokenRef.current ? { Authorization: `Bearer ${tokenRef.current}` } : {};
  }

  // ------------------------------------------------------------------
  // Auth verification
  // ------------------------------------------------------------------
  useEffect(() => {
    async function verifySession() {
      const token = window.localStorage.getItem("microllm_token");
      if (!token) {
        setAuthStatus("unauthenticated");
        return;
      }
      tokenRef.current = token;
      try {
        const res = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("invalid_session");
        const data = await res.json();
        setUser(data.user);
        setAuthStatus("authenticated");
      } catch {
        window.localStorage.removeItem("microllm_token");
        setAuthStatus("unauthenticated");
      }
    }
    verifySession();
  }, []);

  useEffect(() => {
    if (authStatus === "unauthenticated") {
      router.replace("/");
    }
  }, [authStatus, router]);

  function logout() {
    window.localStorage.removeItem("microllm_token");
    router.replace("/");
  }

  // ------------------------------------------------------------------
  // Models
  // ------------------------------------------------------------------
  const loadModels = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/models/list`, { headers: authHeaders() });
      if (!res.ok) throw new Error("models_list_failed");
      const data = await res.json();
      const list: WorkspaceModel[] = (data.models ?? []).map(
        (m: {
          id: string;
          name: string;
          parameters: string;
          quantization: string;
          size_mb?: number;
          context_length: number;
          active: boolean;
          available: boolean;
        }) => ({
          id: m.id,
          name: m.name,
          params: m.parameters,
          quant: m.quantization,
          sizeGb: m.size_mb ? m.size_mb / 1024 : 0,
          ctxMax: m.context_length || 4096,
          status: (m.active ? "running" : m.available ? "available" : "unavailable") as ModelStatus,
        })
      );
      setModels(list);
      const active = list.find((m) => m.status === "running");
      setActiveModelId(active ? active.id : list[0]?.id ?? "");
      addConsoleLine("info", `Loaded ${list.length} models from /api/models/list`);
    } catch {
      addConsoleLine("error", "Failed to load model catalogue");
    }
  }, [addConsoleLine]);

  const loadHistory = useCallback(
    async (sessionId: string) => {
      setLoadingHistoryId(sessionId);
      try {
        const res = await fetch(`${API_URL}/api/chat/history/${sessionId}`, { headers: authHeaders() });
        if (!res.ok) throw new Error("history_failed");
        const data = await res.json();
        const rows: ApiChatMessage[] = data.history ?? [];
        const messages: ChatMessage[] = rows.map((m) => ({
          id: m.id,
          role: m.role,
          time: formatHHMM(m.timestamp),
          text: m.message,
        }));
        const last = messages[messages.length - 1];
        setSessions((prev) =>
          prev.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  messages,
                  historyLoaded: true,
                  preview: last ? last.text : s.preview,
                  time: last ? formatRelativeLabel(rows[rows.length - 1].timestamp) : s.time,
                }
              : s
          )
        );
        addConsoleLine("info", `Loaded ${messages.length} messages from /api/chat/history`);
      } catch {
        addConsoleLine("error", "Failed to load chat history for session");
      } finally {
        setLoadingHistoryId((current) => (current === sessionId ? null : current));
      }
    },
     
    [addConsoleLine]
  );

  const createWorkspace = useCallback(
    async (name: string): Promise<Session | null> => {
      try {
        const res = await fetch(`${API_URL}/api/workspaces`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify({ name }),
        });
        if (!res.ok) throw new Error("create_workspace_failed");
        const data = await res.json();
        const session: Session = {
          id: data.workspace_id,
          title: name,
          preview: "No messages yet",
          time: "just now",
          messages: [],
          historyLoaded: true,
        };
        return session;
      } catch {
        addConsoleLine("error", "Failed to create workspace");
        showToast("Could not create a new session");
        return null;
      }
    },
     
    [addConsoleLine, showToast]
  );

  const loadWorkspaces = useCallback(async () => {
    setSessionsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/workspaces`, { headers: authHeaders() });
      if (!res.ok) throw new Error("workspaces_failed");
      const data = await res.json();
      const rows: ApiWorkspace[] = data.workspaces ?? [];

      let list = rows.map(workspaceToSession);
      if (list.length === 0) {
        const created = await createWorkspace("New Session");
        if (created) list = [created];
      }

      setSessions(list);
      if (list.length > 0) {
        setActiveSessionId(list[0].id);
        if (list[0].historyLoaded === false) {
          await loadHistory(list[0].id);
        }
      }
      addConsoleLine("info", `Loaded ${list.length} session(s) from /api/workspaces`);
    } catch {
      addConsoleLine("error", "Failed to load workspaces — sessions unavailable");
    } finally {
      setSessionsLoading(false);
    }
     
  }, [addConsoleLine, createWorkspace, loadHistory]);

  useEffect(() => {
    async function bootstrap() {
      if (authStatus !== "authenticated") return;
      addConsoleLine("info", "System initialized");
      await Promise.all([loadModels(), loadWorkspaces()]);
    }
    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authStatus]);

  async function switchModel(modelId: string) {
    if (switchingModel) return;
    const target = models.find((m) => m.id === modelId);
    if (!target || target.status === "running" || target.status === "unavailable") return;

    setSwitchingModel(true);
    setModels((prev) => prev.map((m) => (m.id === modelId ? { ...m, status: "loading" } : m)));
    addConsoleLine("info", `Switching model to: ${target.name} (${target.params})`);

    try {
      const res = await fetch(`${API_URL}/api/models/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ model_id: modelId }),
      });
      if (!res.ok) throw new Error("switch_failed");
      const data = await res.json();
      setModels((prev) =>
        prev.map((m) => ({
          ...m,
          status: m.id === modelId ? "running" : m.status === "running" ? "available" : m.status,
        }))
      );
      setActiveModelId(modelId);
      setCtxUsed(0);
      addConsoleLine("info", `Model switched: ${data.name} — ready for inference`);
    } catch {
      setModels((prev) => prev.map((m) => (m.id === modelId ? { ...m, status: "available" } : m)));
      addConsoleLine("error", `Failed to switch to ${target.name}`);
      showToast("Model switch failed");
    } finally {
      setSwitchingModel(false);
    }
  }

  // ------------------------------------------------------------------
  // Health / metrics polling (real backend telemetry)
  // ------------------------------------------------------------------
  useEffect(() => {
    if (authStatus !== "authenticated") return;

    async function pollHealth() {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (!res.ok) throw new Error("unhealthy");
        const data = await res.json();
        setHealth((prev) => ({
          ...prev,
          reachable: true,
          gpuPercent: data.gpu_percent,
          modelLoaded: data.model?.model?.loaded,
        }));
      } catch {
        setHealth((prev) => ({ ...prev, reachable: false }));
      }
    }

    async function pollMetrics() {
      try {
        const res = await fetch(`${API_URL}/api/metrics/system`, { headers: authHeaders() });
        if (!res.ok) return;
        const data = await res.json();
        setHealth((prev) => ({
          ...prev,
          cpuPercent: data.cpu_percent,
          ramPercent: data.ram_percent,
          ramTotalGb: data.ram_total_gb,
          ramUsedGb: data.ram_used_gb,
        }));
      } catch {
        /* non-fatal */
      }
    }

    pollHealth();
    pollMetrics();
    const healthTimer = setInterval(pollHealth, 5000);
    const metricsTimer = setInterval(pollMetrics, 5000);
    return () => {
      clearInterval(healthTimer);
      clearInterval(metricsTimer);
    };
  }, [authStatus]);

  async function refreshTtft() {
    try {
      const res = await fetch(`${API_URL}/api/perf/ttft`, { headers: authHeaders() });
      if (!res.ok) return;
      const data = await res.json();
      setTtft({ p50Ms: data.p50_ms ?? null, samples: data.samples ?? 0 });
    } catch {
      /* non-fatal */
    }
  }

  // ------------------------------------------------------------------
  // Uptime tick
  // ------------------------------------------------------------------
  useEffect(() => {
    const timer = setInterval(() => {
      const secs = Math.floor((Date.now() - startedAt.current) / 1000);
      const h = pad2(Math.floor(secs / 3600));
      const m = pad2(Math.floor((secs % 3600) / 60));
      const s = pad2(secs % 60);
      setUptime(`${h}:${m}:${s}`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // ------------------------------------------------------------------
  // Sessions (backed by /api/workspaces + /api/chat/history)
  // ------------------------------------------------------------------
  async function newSession() {
    const created = await createWorkspace("New Session");
    if (!created) return;
    setSessions((prev) => [created, ...prev]);
    setActiveSessionId(created.id);
    closeMobilePanels();
  }

  function selectSession(id: string) {
    setActiveSessionId(id);
    closeMobilePanels();
    const target = sessions.find((s) => s.id === id);
    if (target && !target.historyLoaded) {
      loadHistory(id);
    }
  }

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? sessions[0];
  const activeModel = models.find((m) => m.id === activeModelId);

  const filteredSessions = sessions.filter((s) => {
    const q = sessionSearch.trim().toLowerCase();
    if (!q) return true;
    return s.title.toLowerCase().includes(q) || s.preview.toLowerCase().includes(q);
  });

  // ------------------------------------------------------------------
  // Sending messages — real POST /api/chat
  // ------------------------------------------------------------------
  async function sendMessage() {
    const text = composerText.trim();
    if (!text || sending) return;
    if (!activeSessionId) {
      showToast("No session available — try again in a moment");
      return;
    }

    const userMsg: ChatMessage = { id: uid(), role: "user", time: nowHHMM(), text };
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSessionId
          ? {
              ...s,
              messages: [...s.messages, userMsg],
              preview: text,
              title: s.messages.length === 0 ? (text.length > 40 ? text.slice(0, 40) + "…" : text) : s.title,
            }
          : s
      )
    );
    setComposerText("");
    setSending(true);
    addConsoleLine("user", text.length > 60 ? text.slice(0, 60) + "…" : text);

    const startedRequestAt = performance.now();

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ message: text, max_tokens: 128, workspace_id: activeSessionId }),
      });
      const elapsedMs = Math.round(performance.now() - startedRequestAt);
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      const ragSources: RagSource[] | undefined = data.rag?.grounded ? data.rag.sources : undefined;
      const assistantMsg: ChatMessage = {
        id: uid(),
        role: "assistant",
        time: nowHHMM(),
        text: data.response ?? "(empty response)",
        ragSources,
        tokensGenerated: data.tokens_generated,
        tookMs: elapsedMs,
      };
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, messages: [...s.messages, assistantMsg] } : s))
      );

      if (typeof data.tokens_generated === "number") {
        setTotalTokens((t) => t + data.tokens_generated);
        setCtxUsed((c) => c + Math.round(text.length / 3) + data.tokens_generated);
        if (elapsedMs > 0) setTokensPerSec(Math.round((data.tokens_generated / elapsedMs) * 1000 * 10) / 10);
      }
      addConsoleLine("info", `Response received (${data.tokens_generated ?? "?"} tokens, ${elapsedMs}ms)`);
      refreshTtft();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Request failed";
      const errorMsg: ChatMessage = {
        id: uid(),
        role: "assistant",
        time: nowHHMM(),
        text: `Request failed: ${message}`,
        isError: true,
      };
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSessionId ? { ...s, messages: [...s.messages, errorMsg] } : s))
      );
      addConsoleLine("error", message);
    } finally {
      setSending(false);
    }
  }

  // ------------------------------------------------------------------
  // Panel toggles
  // ------------------------------------------------------------------
  function closeMobilePanels() {
    setSidebarOpen(false);
    setContextOpen(false);
  }
  function closeAllPopovers() {
    setDropdownOpen(false);
    setContextPopoverOpen(false);
    setCommandPopoverOpen(false);
  }

  useEffect(() => {
    function onKeydown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        closeAllPopovers();
        setDrawerOpen(false);
        closeMobilePanels();
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        document.getElementById("sessionSearch")?.focus();
      }
    }
    document.addEventListener("keydown", onKeydown);
    return () => document.removeEventListener("keydown", onKeydown);
  }, []);

  return {
    API_URL,
    authStatus,
    user,
    models,
    activeModel,
    activeModelId,
    switchingModel,
    switchModel,
    sessions: filteredSessions,
    sessionsLoading,
    loadingHistoryId,
    activeSession,
    activeSessionId,
    selectSession,
    newSession,
    sessionSearch,
    setSessionSearch,
    composerText,
    setComposerText,
    sending,
    sendMessage,
    consoleLines,
    consoleCollapsed,
    setConsoleCollapsed,
    clearConsole: () => setConsoleLines([]),
    sidebarOpen,
    contextOpen,
    dropdownOpen,
    setDropdownOpen,
    contextPopoverOpen,
    setContextPopoverOpen,
    commandPopoverOpen,
    setCommandPopoverOpen,
    drawerOpen,
    setDrawerOpen,
    toggleSidebar: () => setSidebarOpen((v) => !v),
    toggleContext: () => setContextOpen((v) => !v),
    closeMobilePanels,
    closeAllPopovers,
    totalTokens,
    ctxUsed,
    tokensPerSec,
    ttft,
    health,
    uptime,
    toast,
    showToast,
    logout,
    fmtSize,
  };
}
