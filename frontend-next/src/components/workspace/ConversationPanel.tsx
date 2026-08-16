"use client";

import { useEffect, useRef, useState } from "react";
import { Icon } from "./Icon";
import type { ChatMessage } from "./types";
import type { useWorkspace } from "./useWorkspace";

function MessageBubble({ m, onToast }: { m: ChatMessage; onToast: (msg: string) => void }) {
  const isUser = m.role === "user";
  const [liked, setLiked] = useState<"up" | "down" | null>(null);

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="message-meta">
        <span className="message-avatar">{isUser ? "U" : "M"}</span>
        <span className="message-author">{isUser ? "You" : "MicroLLM"}</span>
        <span className="message-time">{m.time}</span>
      </div>
      <div className="message-body" style={m.isError ? { color: "var(--error)" } : undefined}>
        {m.text}
      </div>

      {m.ragSources && m.ragSources.length > 0 && (
        <div className="result-panel">
          {m.ragSources.map((r, i) => (
            <div className="result-row" key={i}>
              <span className="result-indicator low" />
              <div className="result-content">
                <div className="result-top">
                  <span className="result-severity low">Source</span>
                  <span className="result-time">score {r.score}</span>
                </div>
                <div className="result-title">{r.source}</div>
                <div className="result-detail">{r.chunk}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!isUser && !m.isError && typeof m.tokensGenerated === "number" && (
        <div className="message-footer-note">
          <span>{m.tokensGenerated} tokens{typeof m.tookMs === "number" ? ` · ${m.tookMs}ms` : ""}</span>
          <span className="result-time">{m.time}</span>
        </div>
      )}

      {!isUser && (
        <div className="message-actions">
          <button
            className="message-action-btn"
            title="Copy"
            onClick={() => navigator.clipboard?.writeText(m.text).then(() => onToast("Copied to clipboard"))}
          >
            <Icon id="i-copy" size={14} />
          </button>
          <button
            className={`message-action-btn ${liked === "up" ? "active-like" : ""}`}
            title="Good response"
            onClick={() => setLiked((v) => (v === "up" ? null : "up"))}
          >
            <Icon id="i-thumbs-up" size={14} />
          </button>
          <button
            className={`message-action-btn ${liked === "down" ? "active-dislike" : ""}`}
            title="Bad response"
            onClick={() => setLiked((v) => (v === "down" ? null : "down"))}
          >
            <Icon id="i-thumbs-down" size={14} />
          </button>
          <button className="message-action-btn" title="More" onClick={() => onToast("Not available yet")}>
            <Icon id="i-more" size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

export function ConversationPanel({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const { activeSession, sending, composerText, setComposerText, sendMessage, models, activeModel, loadingHistoryId } = ws;
  const isLoadingHistory = activeSession != null && loadingHistoryId === activeSession.id;
  const messagesRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight });
  }, [activeSession?.messages.length, sending]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [composerText]);

  return (
    <main className="main-col">
      <div className="conv-header">
        <div className="conv-header-left">
          <div>
            <div className="conv-title">{activeSession?.title ?? "New Session"}</div>
            <div className="conv-subtitle">
              {activeSession ? `Session · ${activeSession.time}` : "No session selected"}
            </div>
          </div>
        </div>
        <div className="conv-header-right">
          <button className="btn-secondary" onClick={() => ws.showToast("Not available yet")}>Share</button>
          <button className="icon-btn" onClick={() => ws.showToast("Not available yet")} aria-label="More options">
            <Icon id="i-more" size={16} />
          </button>
        </div>
      </div>

      <div className="messages" ref={messagesRef}>
        {isLoadingHistory && (
          <div style={{ padding: "40px 20px", color: "var(--text-muted)", fontSize: 13, textAlign: "center" }}>
            Loading history...
          </div>
        )}
        {!isLoadingHistory && activeSession?.messages.length === 0 && (
          <div style={{ padding: "40px 20px", color: "var(--text-muted)", fontSize: 13, textAlign: "center" }}>
            Ask MicroLLM anything — inference runs locally against{" "}
            {activeModel ? activeModel.name : "the active model"}.
          </div>
        )}
        {activeSession?.messages.map((m) => (
          <MessageBubble key={m.id} m={m} onToast={ws.showToast} />
        ))}
        {sending && (
          <div className="typing-indicator">
            <span /><span /><span />
          </div>
        )}
      </div>

      <div className="composer-wrap">
        <div className="composer">
          <textarea
            ref={textareaRef}
            className="composer-input"
            rows={1}
            placeholder="Ask MicroLLM anything..."
            value={composerText}
            disabled={sending}
            onChange={(e) => setComposerText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />
          <div className="composer-toolbar">
            <button className="composer-tool-btn icon-only" title="Attach file" onClick={() => ws.showToast("Not available yet")}>
              <Icon id="i-clip" size={15} />
            </button>
            <button
              className="composer-tool-btn"
              title="Reference context"
              onClick={(e) => {
                e.stopPropagation();
                ws.setCommandPopoverOpen(false);
                ws.setContextPopoverOpen(!ws.contextPopoverOpen);
              }}
            >
              <Icon id="i-at" size={13} /> Context
            </button>
            <button
              className="composer-tool-btn"
              title="Slash commands"
              onClick={(e) => {
                e.stopPropagation();
                ws.setContextPopoverOpen(false);
                ws.setCommandPopoverOpen(!ws.commandPopoverOpen);
              }}
            >
              <Icon id="i-slash" size={13} /> Command
            </button>

            <div className={`composer-popover ${ws.contextPopoverOpen ? "open" : ""}`}>
              <button className="composer-popover-item" onClick={() => { ws.setContextPopoverOpen(false); ws.showToast("Not available yet"); }}>
                <Icon id="i-file" size={14} /> Current file
              </button>
              <button className="composer-popover-item" onClick={() => { ws.setContextPopoverOpen(false); ws.showToast("Not available yet"); }}>
                <Icon id="i-folder" size={14} /> Workspace
              </button>
              <button className="composer-popover-item" onClick={() => { ws.setContextPopoverOpen(false); ws.showToast("Not available yet"); }}>
                <Icon id="i-terminal" size={14} /> Terminal output
              </button>
            </div>
            <div className={`composer-popover ${ws.commandPopoverOpen ? "open" : ""}`}>
              {["/explain", "/fix", "/test"].map((cmd) => (
                <button key={cmd} className="composer-popover-item" onClick={() => { ws.setCommandPopoverOpen(false); ws.showToast("Not available yet"); }}>
                  {cmd}
                </button>
              ))}
            </div>

            <div className="composer-spacer" />
            <div className="composer-model-pill">
              <span className={`model-status-dot ${activeModel?.status ?? ""}`} />
              <span>{activeModel?.name ?? "No model"}</span>
            </div>
            <button
              className="composer-send-btn"
              aria-label="Send"
              disabled={composerText.trim().length === 0 || sending}
              onClick={sendMessage}
            >
              <Icon id="i-arrow-up" size={15} />
            </button>
          </div>
        </div>
        <div className="composer-meta">
          Local inference · {activeModel?.ctxMax.toLocaleString() ?? "—"} context · {activeModel?.quant ?? "—"} · llama.cpp
          {models.length === 0 && " · no models available"}
        </div>
      </div>

      <ConsolePanel ws={ws} />
    </main>
  );
}

function ConsolePanel({ ws }: { ws: ReturnType<typeof useWorkspace> }) {
  const bodyRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
  }, [ws.consoleLines.length]);

  return (
    <div className={`console-wrap ${ws.consoleCollapsed ? "collapsed" : ""}`}>
      <div className="console-header">
        <div className="console-header-left">
          <button onClick={() => ws.setConsoleCollapsed(!ws.consoleCollapsed)}>
            <Icon id="i-chevron-down" size={13} />
            <span className="console-title">SYSTEM CONSOLE</span>
          </button>
        </div>
        <button className="console-clear-btn" onClick={ws.clearConsole}>
          <Icon id="i-trash" size={12} /> Clear
        </button>
      </div>
      <div className="console-body" ref={bodyRef}>
        {ws.consoleLines.map((line) => (
          <div className="console-line" key={line.id}>
            <span className="console-ts">{line.ts}</span> <span className={`console-tag ${line.tag}`}>[{line.tag.toUpperCase()}]</span>{" "}
            <span className="console-msg">{line.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
