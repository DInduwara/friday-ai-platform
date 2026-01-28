import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import MessageBubble from "./MessageBubble";

export default function ChatPanel({ conversationId, onCreateConversation, setAgentSteps }) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);

  const scrollToBottom = () => bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  // Load history when conversation changes
  useEffect(() => {
    const load = async () => {
      setMessages([]);
      setAgentSteps([]);
      setError("");

      if (!conversationId) return;

      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE}/api/v1/conversations/${conversationId}/messages`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        const mapped = (Array.isArray(data) ? data : []).map((m) => ({
          role: m.role === "assistant" ? "ai" : "user",
          content: m.content,
          timestamp: Date.parse(m.created_at) || Date.now(),
        }));

        setMessages(mapped);
        setTimeout(scrollToBottom, 50);
      } catch (e) {
        console.error(e);
        setError("Failed to load messages.");
      }
    };

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    setError("");

    // If no conversation selected yet => create one first
    if (!conversationId) {
      await onCreateConversation();
      return;
    }

    setIsSending(true);

    const userInput = input.trim();
    setInput("");

    // add user msg
    setMessages((prev) => [...prev, { role: "user", content: userInput, timestamp: Date.now() }]);

    // add assistant placeholder (typing)
    const typingId = `typing_${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      { role: "ai", content: "…", timestamp: Date.now(), _typing: true, _id: typingId },
    ]);

    try {
      const token = await getToken();
      if (!token) throw new Error("No auth token. Please sign in again.");

      const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
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
      let finalText = "";

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
              finalText = parsed?.response?.data?.content || "";
            }

            if (parsed?.response?.kind === "error") {
              finalText = parsed?.response?.data?.message || "Something went wrong.";
            }
          } catch (err) {
            console.error("Bad SSE JSON:", err, jsonStr);
          }
        }
      }

      // Replace typing bubble with final
      setMessages((prev) =>
        prev.map((m) =>
          m._id === typingId ? { role: "ai", content: finalText, timestamp: Date.now() } : m
        )
      );
    } catch (err) {
      console.error("Chat error:", err);
      setError(err?.message || "Chat error");

      // Replace typing bubble with error
      setMessages((prev) =>
        prev.map((m) =>
          m._id === typingId
            ? {
                role: "ai",
                content: "⚠️ Failed to contact backend or auth failed. Check logs + Clerk setup.",
                timestamp: Date.now(),
              }
            : m
        )
      );
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900">
      {/* Header inside panel */}
      <div className="p-3 border-b border-white/10 bg-black/20">
        <div className="text-sm text-white/80">
          {conversationId ? `Conversation: ${conversationId}` : "Select a chat or click New"}
        </div>
        {error ? (
          <div className="mt-2 text-xs text-red-200 bg-red-900/30 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </div>
        ) : null}
      </div>

      {/* Messages */}
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
