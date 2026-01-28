import { useEffect, useMemo, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";

function newConversationId() {
  return `c_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export default function ChatPanel({ setAgentSteps }) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const [conversationId, setConversationId] = useState(() => {
    return localStorage.getItem("friday_conversation_id") || newConversationId();
  });

  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("friday_conversation_id", conversationId);
  }, [conversationId]);

  // ✅ auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const headerSubtitle = useMemo(() => {
    return conversationId ? `Session: ${conversationId}` : "";
  }, [conversationId]);

  const clearServerConversation = async (id) => {
    try {
      await fetch(`${API_BASE}/api/v1/chat/clear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation_id: id }),
      });
    } catch (e) {
      console.warn("Failed to clear server conversation:", e);
    }
  };

  const handleNewChat = async () => {
    const oldId = conversationId;
    const newId = newConversationId();

    await clearServerConversation(oldId);

    setConversationId(newId);
    setMessages([]);
    setAgentSteps([]);
    setError("");
  };

  const handleClearServer = async () => {
    await clearServerConversation(conversationId);
    setMessages([]);
    setAgentSteps([]);
    setError("");
  };

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    setError("");
    setIsSending(true);

    const userInput = input.trim();
    setInput("");

    // ✅ user message timestamp
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userInput, timestamp: Date.now() },
    ]);

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: userInput,
          conversation_id: conversationId,
        }),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status}. ${text}`);
      }
      if (!res.body) throw new Error("No response body from server.");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let buffer = "";
      let aiReply = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;

          const jsonStr = line.replace(/^data:\s?/, "");

          try {
            const parsed = JSON.parse(jsonStr);

            if (Array.isArray(parsed?.step)) {
              setAgentSteps(parsed.step);
            }

            if (parsed?.response?.kind === "final") {
              aiReply = parsed?.response?.data?.content || "";
            }

            if (parsed?.response?.kind === "error") {
              aiReply = parsed?.response?.data?.message || "Something went wrong.";
            }
          } catch (err) {
            console.error("Bad SSE JSON:", err, jsonStr);
          }
        }
      }

      if (aiReply) {
        // ✅ ai message timestamp (this was missing)
        setMessages((prev) => [
          ...prev,
          { role: "ai", content: aiReply, timestamp: Date.now() },
        ]);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError(err?.message || "Chat error");
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: "⚠️ Failed to contact backend. Check Docker logs and API URL.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full border-r border-gray-800 bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-800 to-purple-800 text-white p-4 shadow-md">
        <div className="flex items-center justify-between gap-3">
          <div className="text-center flex-1">
            <div className="font-bold text-lg">F.R.I.D.A.Y</div>
            <div className="text-xs text-indigo-200/90 mt-1 truncate">{headerSubtitle}</div>
          </div>

          <div className="flex gap-2">
            <button
              className="px-3 py-2 text-sm rounded-lg bg-white/10 hover:bg-white/15 border border-white/15"
              onClick={handleClearServer}
              title="Clear UI + clear server memory for this conversation"
              disabled={isSending}
            >
              Clear
            </button>
            <button
              className="px-3 py-2 text-sm rounded-lg bg-white/10 hover:bg-white/15 border border-white/15"
              onClick={handleNewChat}
              title="Start a new conversation (new conversation_id)"
              disabled={isSending}
            >
              New Chat
            </button>
          </div>
        </div>

        {error ? (
          <div className="mt-2 text-xs text-red-200 bg-red-900/30 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </div>
        ) : null}
      </div>

      {/* Scrollable messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex p-3 bg-gray-900/70 backdrop-blur-lg border-t border-gray-700">
        <input
          className="flex-1 p-2 rounded-lg bg-gray-800/80 text-white placeholder-gray-400 outline-none disabled:opacity-60"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder={isSending ? "Waiting for response..." : "Type a message..."}
          disabled={isSending}
        />
        <button
          className="ml-3 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-lg shadow-md hover:scale-105 transition-transform disabled:opacity-60 disabled:hover:scale-100"
          onClick={sendMessage}
          disabled={isSending}
        >
          {isSending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
