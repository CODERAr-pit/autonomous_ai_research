'use client'
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'ai';
  content: string;
  time?: string | null;
  isStreaming?: boolean;
}

type AgentEvent = 
  | { type: "node_update"; node: string }
  | { type: "token"; text: string }
  | { type: "done"; report: string; attempts: number }
  | { type: "error"; message: string }
  | { type: "thread_started"; thread_id: string }

const NODE_EMOJI: Record<string, string> = {
  classifier:   "⟳",
  orchestrator: "◈",
  researcher:   "◉",
  writer:       "◎",
  critic:       "◆"
}

const NODE_MESSAGE: Record<string, string> = {
  classifier:   "Classifying query...",
  orchestrator: "Planning strategy...",
  researcher:   "Searching the web...",
  writer:       "Composing report...",
  critic:       "Evaluating quality..."
}

const NODE_COLOR: Record<string, string> = {
  classifier:   "#7B6EF6",
  orchestrator: "#4E9FE5",
  researcher:   "#48C78E",
  writer:       "#F5A623",
  critic:       "#FF6B6B"
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentNode, setCurrentNode] = useState<string>("");
  const [nodeHistory, setNodeHistory] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [threadId, setThreadId] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("thread_id") || "";
    }
    return "";
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
    }
  }, [input]);

  async function handleSend() {
    if (!input.trim() || isLoading) return;
    const userQuery = input;
    setInput("");
    setIsLoading(true);
    setCurrentNode("");
    setNodeHistory([]);

    setMessages(prev => [
      ...prev,
      { role: 'user', content: userQuery },
      { role: 'ai', content: "Initializing...", isStreaming: true }
    ]);

    try {
      const res = await fetch(`http://127.0.0.1:8000/run-agent-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: userQuery, thread_id: threadId })
      });

      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const streamMessages = buffer.split("\n\n");
        buffer = streamMessages.pop() || "";

        for (const message of streamMessages) {
          if (!message.startsWith("data: ")) continue;
          const jsonStr = message.slice(6).trim();
          if (!jsonStr) continue;
          const event: AgentEvent = JSON.parse(jsonStr);

          if (event.type === "thread_started") {
            localStorage.setItem("thread_id", event.thread_id);
            setThreadId(event.thread_id);
          }

          if (event.type === "node_update") {
            setCurrentNode(event.node);
            setNodeHistory(prev => [...prev, event.node]);
            const emoji = NODE_EMOJI[event.node] || "◌";
            const msgText = NODE_MESSAGE[event.node] || `Running ${event.node}...`;
            setMessages(prev => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1] = {
                role: 'ai',
                content: `${emoji} ${msgText}`,
                isStreaming: true
              };
              return newMsgs;
            });
          }

          if (event.type === "token") {
            setMessages(prev => {
              const newMsgs = [...prev];
              const lastIndex = newMsgs.length - 1;
              const currentText = newMsgs[lastIndex].content;
              const isStatusMsg = Object.values(NODE_MESSAGE).some(m => currentText.includes(m)) 
                || currentText === "Initializing...";
              newMsgs[lastIndex] = {
                role: 'ai',
                content: isStatusMsg ? event.text : currentText + event.text,
                isStreaming: true
              };
              return newMsgs;
            });
          }

          if (event.type === "done") {
            setCurrentNode("");
            setMessages(prev => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1] = {
                role: 'ai',
                content: event.report,
                isStreaming: false
              };
              return newMsgs;
            });
          }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          role: 'ai',
          content: `**Error:** ${err instanceof Error ? err.message : 'Unknown error'}`,
          isStreaming: false
        };
        return newMsgs;
      });
    } finally {
      setIsLoading(false);
      setCurrentNode("");
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestions = [
    "Compare React vs Vue for a startup",
    "Explain RAG systems in simple terms",
    "Best practices for FastAPI in production",
    "LangGraph vs CrewAI — which to choose?"
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg:        #0A0A0F;
          --bg2:       #111118;
          --bg3:       #18181F;
          --border:    rgba(255,255,255,0.07);
          --accent:    #7B6EF6;
          --accent2:   #4E9FE5;
          --text:      #E8E8F0;
          --text2:     #8888A0;
          --text3:     #55556A;
          --user-bg:   #1E1E2A;
          --radius:    16px;
        }

        body {
          background: var(--bg);
          color: var(--text);
          font-family: 'DM Mono', monospace;
          overflow: hidden;
        }

        .app { display: flex; flex-direction: column; height: 100vh; position: relative; }

        /* Ambient background */
        .ambient {
          position: fixed; inset: 0; pointer-events: none; z-index: 0;
          background:
            radial-gradient(ellipse 60% 40% at 20% 10%, rgba(123,110,246,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 50% 30% at 80% 80%, rgba(78,159,229,0.06) 0%, transparent 60%);
        }

        /* Header */
        .header {
          position: relative; z-index: 10;
          padding: 20px 28px;
          display: flex; align-items: center; justify-content: space-between;
          border-bottom: 1px solid var(--border);
          backdrop-filter: blur(20px);
        }

        .logo {
          font-family: 'Syne', sans-serif;
          font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
          background: linear-gradient(135deg, #fff 0%, var(--text2) 100%);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .header-status {
          display: flex; align-items: center; gap: 8px;
          font-size: 11px; color: var(--text3); letter-spacing: 0.5px;
        }

        .status-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: #48C78E;
          box-shadow: 0 0 8px #48C78E;
          animation: pulse-dot 2s ease-in-out infinite;
        }

        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }

        /* Agent pipeline */
        .pipeline {
          position: relative; z-index: 10;
          padding: 10px 28px;
          display: flex; align-items: center; gap: 6px;
          border-bottom: 1px solid var(--border);
          overflow-x: auto;
        }

        .pipeline-label {
          font-size: 10px; color: var(--text3);
          letter-spacing: 1px; text-transform: uppercase;
          margin-right: 4px; white-space: nowrap;
        }

        .pipeline-node {
          display: flex; align-items: center; gap: 5px;
          padding: 4px 10px; border-radius: 99px;
          font-size: 11px; font-family: 'DM Mono', monospace;
          border: 1px solid var(--border);
          color: var(--text3);
          transition: all 0.3s ease;
          white-space: nowrap;
        }

        .pipeline-node.active {
          color: #fff;
          border-color: transparent;
          animation: node-pulse 1.5s ease-in-out infinite;
        }

        .pipeline-node.done {
          color: var(--text2);
          border-color: rgba(255,255,255,0.1);
        }

        @keyframes node-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }

        .pipeline-arrow {
          color: var(--text3); font-size: 10px;
        }

        /* Messages */
        .messages {
          flex: 1; overflow-y: auto; padding: 28px;
          position: relative; z-index: 5;
          scrollbar-width: thin; scrollbar-color: var(--bg3) transparent;
        }

        .messages::-webkit-scrollbar { width: 4px; }
        .messages::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 4px; }

        /* Empty state */
        .empty {
          height: 100%;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          gap: 32px; text-align: center;
        }

        .empty-icon {
          width: 64px; height: 64px; border-radius: 20px;
          background: var(--bg3); border: 1px solid var(--border);
          display: flex; align-items: center; justify-content: center;
          font-size: 28px;
        }

        .empty-title {
          font-family: 'Syne', sans-serif;
          font-size: 28px; font-weight: 700; letter-spacing: -0.5px;
          color: var(--text);
        }

        .empty-sub {
          font-size: 13px; color: var(--text3); margin-top: 6px;
          max-width: 340px; line-height: 1.6;
        }

        .suggestions {
          display: grid; grid-template-columns: 1fr 1fr;
          gap: 8px; max-width: 520px; width: 100%;
        }

        .suggestion {
          padding: 12px 14px; border-radius: 12px;
          background: var(--bg2); border: 1px solid var(--border);
          color: var(--text2); font-size: 12px; line-height: 1.4;
          cursor: pointer; text-align: left;
          transition: all 0.2s ease;
          font-family: 'DM Mono', monospace;
        }

        .suggestion:hover {
          background: var(--bg3); border-color: rgba(123,110,246,0.3);
          color: var(--text);
        }

        /* Message rows */
        .msg-row {
          display: flex; margin-bottom: 20px;
          animation: fade-up 0.3s ease;
        }

        @keyframes fade-up {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .msg-row.user { justify-content: flex-end; }
        .msg-row.ai   { justify-content: flex-start; }

        .msg-bubble {
          max-width: 72%; padding: 14px 18px;
          border-radius: var(--radius);
          line-height: 1.65; font-size: 13.5px;
        }

        .msg-bubble.user {
          background: var(--user-bg);
          border: 1px solid rgba(123,110,246,0.2);
          color: var(--text);
          border-bottom-right-radius: 4px;
        }

        .msg-bubble.ai {
          background: var(--bg2);
          border: 1px solid var(--border);
          color: var(--text);
          border-bottom-left-radius: 4px;
        }

        .msg-bubble.ai.status {
          background: transparent;
          border: 1px solid var(--border);
          color: var(--text2);
          font-size: 12px; letter-spacing: 0.3px;
          display: flex; align-items: center; gap: 8px;
        }

        .status-spinner {
          width: 14px; height: 14px; border-radius: 50%;
          border: 2px solid var(--border);
          border-top-color: var(--accent);
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* Markdown styles */
        .msg-bubble.ai .prose h1,
        .msg-bubble.ai .prose h2,
        .msg-bubble.ai .prose h3 {
          font-family: 'Syne', sans-serif;
          color: var(--text); margin: 16px 0 8px;
          font-weight: 700;
        }

        .msg-bubble.ai .prose h1 { font-size: 18px; }
        .msg-bubble.ai .prose h2 { font-size: 15px; }
        .msg-bubble.ai .prose h3 { font-size: 13px; }

        .msg-bubble.ai .prose p {
          color: var(--text); margin-bottom: 10px;
          font-size: 13.5px; line-height: 1.7;
        }

        .msg-bubble.ai .prose ul,
        .msg-bubble.ai .prose ol {
          padding-left: 20px; margin-bottom: 10px;
        }

        .msg-bubble.ai .prose li {
          color: var(--text2); margin-bottom: 4px;
          font-size: 13px; line-height: 1.6;
        }

        .msg-bubble.ai .prose code {
          background: var(--bg3); color: var(--accent);
          padding: 2px 6px; border-radius: 4px;
          font-size: 12px; font-family: 'DM Mono', monospace;
        }

        .msg-bubble.ai .prose pre {
          background: var(--bg3); border: 1px solid var(--border);
          border-radius: 10px; padding: 14px; margin: 12px 0;
          overflow-x: auto;
        }

        .msg-bubble.ai .prose pre code {
          background: none; padding: 0; color: var(--text2);
        }

        .msg-bubble.ai .prose strong { color: #fff; font-weight: 600; }

        .msg-bubble.ai .prose blockquote {
          border-left: 3px solid var(--accent);
          padding-left: 12px; color: var(--text2);
          margin: 10px 0;
        }

        /* Cursor blink */
        .cursor {
          display: inline-block; width: 2px; height: 14px;
          background: var(--accent); margin-left: 2px;
          animation: blink 1s ease-in-out infinite;
          vertical-align: text-bottom;
        }

        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }

        /* Input area */
        .input-wrap {
          position: fixed; bottom: 0; width: 100%;
          padding: 16px 28px 20px;
          z-index: 20;
          background: linear-gradient(to top, var(--bg) 60%, transparent);
        }

        .input-inner {
          max-width: 760px; margin: 0 auto;
          background: var(--bg2);
          border: 1px solid var(--border);
          border-radius: 18px;
          display: flex; align-items: flex-end; gap: 8px;
          padding: 10px 10px 10px 18px;
          transition: border-color 0.2s;
        }

        .input-inner:focus-within {
          border-color: rgba(123,110,246,0.4);
        }

        .input-textarea {
          flex: 1; background: none; border: none; outline: none;
          resize: none; color: var(--text);
          font-family: 'DM Mono', monospace;
          font-size: 13.5px; line-height: 1.6;
          min-height: 24px; max-height: 160px;
          padding: 4px 0;
        }

        .input-textarea::placeholder { color: var(--text3); }

        .send-btn {
          width: 36px; height: 36px; border-radius: 10px;
          border: none; cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          transition: all 0.2s ease; flex-shrink: 0;
          background: var(--accent);
          color: white;
        }

        .send-btn:disabled {
          background: var(--bg3); color: var(--text3); cursor: not-allowed;
        }

        .send-btn:not(:disabled):hover {
          background: #6A5EE0; transform: scale(1.05);
        }

        .input-footer {
          max-width: 760px; margin: 8px auto 0;
          display: flex; align-items: center; justify-content: space-between;
        }

        .input-hint {
          font-size: 10px; color: var(--text3); letter-spacing: 0.3px;
        }

        .thread-badge {
          font-size: 10px; color: var(--text3);
          display: flex; align-items: center; gap: 4px;
        }

        .thread-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--accent); opacity: 0.6;
        }
      `}</style>

      <div className="app">
        <div className="ambient" />

        {/* Header */}
        <header className="header">
          <div className="logo">Xenum</div>
          <div className="header-status">
            <div className="status-dot" />
            ONLINE
          </div>
        </header>

        {/* Agent Pipeline */}
        {(isLoading || nodeHistory.length > 0) && (
          <div className="pipeline">
            <span className="pipeline-label">pipeline</span>
            {["classifier", "orchestrator", "researcher", "writer", "critic"].map((node, i, arr) => {
              const isDone   = nodeHistory.includes(node) && currentNode !== node;
              const isActive = currentNode === node;
              const color    = NODE_COLOR[node];
              return (
                <div key={node} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div
                    className={`pipeline-node ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
                    style={isActive ? { background: `${color}22`, borderColor: `${color}66`, color } : {}}
                  >
                    <span>{NODE_EMOJI[node]}</span>
                    <span>{node}</span>
                  </div>
                  {i < arr.length - 1 && <span className="pipeline-arrow">→</span>}
                </div>
              );
            })}
          </div>
        )}

        {/* Messages */}
        <div className="messages" style={{ paddingBottom: 100 }}>
          {messages.length === 0 ? (
            <div className="empty">
              <div>
                <div className="empty-icon">◈</div>
              </div>
              <div>
                <div className="empty-title">What do you want to research?</div>
                <div className="empty-sub">
                  Multi-agent AI that searches, writes, and critiques — until the answer is right.
                </div>
              </div>
              <div className="suggestions">
                {suggestions.map((s, i) => (
                  <button key={i} className="suggestion" onClick={() => setInput(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ maxWidth: 760, margin: '0 auto' }}>
              {messages.map((msg, index) => {
                const isStatusMsg = msg.isStreaming &&
                  (Object.values(NODE_MESSAGE).some(m => msg.content.includes(m)) ||
                   msg.content === "Initializing...");

                return (
                  <div key={index} className={`msg-row ${msg.role}`}>
                    <div className={`msg-bubble ${msg.role} ${isStatusMsg ? 'status' : ''}`}>
                      {isStatusMsg ? (
                        <>
                          <div className="status-spinner" />
                          <span>{msg.content}</span>
                        </>
                      ) : msg.role === 'user' ? (
                        <span style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</span>
                      ) : (
                        <div className="prose">
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                          {msg.isStreaming && <span className="cursor" />}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-wrap">
          <div className="input-inner">
            <textarea
              ref={textareaRef}
              className="input-textarea"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything to research..."
              rows={1}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
              </svg>
            </button>
          </div>
          <div className="input-footer">
            <span className="input-hint">↵ send · shift+↵ newline</span>
            {threadId && (
              <span className="thread-badge">
                <div className="thread-dot" />
                session active
              </span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}