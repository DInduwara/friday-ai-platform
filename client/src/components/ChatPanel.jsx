import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import MessageBubble from "./MessageBubble";

const PAGE_SIZE = 30;

export default function ChatPanel({
  conversationId,
  setAgentSteps,
  onNeedRefreshSidebar,
  onConversationCreated,
}) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);

  const bottomRef = useRef(null);
  const scrollToBottom = () => bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  const hasMore = messages.length < total;

  const mapApiItemsToUi = (items) => {
    // API returns newest-first. UI should show oldest-first.
    const mapped = (items || []).map((m) => ({
      role: m.role === "assistant" ? "ai" : "user",
      content: m.content,
      timestamp: Date.parse(m.created_at) || Date.now(),
    }));
    return mapped.reverse();
  };

  const loadPage = async ({ reset = false, nextOffset = 0 } = {}) => {
    setError("");
    if (!conversationId) {
      setMessages([]);
      setTotal(0);
      setOffset(0);
      return;
    }

    try {
      const token = await getToken();
      const params = new URLSearchParams();
      params.set("limit", String(PAGE_SIZE));
      params.set("offset", String(nextOffset));

      const res = await fetch(
        `${API_BASE}/api/v1/conversations/${conversationId}/messages?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = await res.json();
      const items = Array.isArray(data?.items) ? data.items : [];
      const uiPage = mapApiItemsToUi(items);

      setTotal(Number(data?.total || 0));
      setOffset(nextOffset);

      if (reset) {
        setMessages(uiPage);
        setTimeout(scrollToBottom, 60);
      } else {
        // Loading older => prepend
        setMessages((prev) => [...uiPage, ...prev]);
      }
    } catch (e) {
      console.error(e);
      setError("Failed to load messages.");
    }
  };

  useEffect(() => {
    setMessages([]);
    setAgentSteps([]);
    setTotal(0);
    setOffset(0);
    loadPage({ reset: true, nextOffset: 0 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  const createConversation = async () => {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/v1/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: "New chat" }),
    });
    const c = await res.json();
    if (c?.id) {
      onConversationCreated?.(c.id);
      return c.id;
    }
    throw new Error("Failed to create conversation");
  };

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    setError("");
    setIsSending(true);

    let cid = conversationId;

    try {
      if (!cid) cid = await createConversation();
    } catch {
      setError("Could not create a new conversation.");
      setIsSending(false);
      return;
    }


    const userText = input.trim();
    setInput("");

    const typingId = `typing_${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userText, timestamp: Date.now() },
      { role: "ai", content: "", timestamp: Date.now(), _typing: true, _id: typingId },
    ]);

    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ prompt: userText, conversation_id: cid }),
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

            if (Array.isArray(parsed?.step)) setAgentSteps(parsed.step);

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

      setMessages((prev) =>
        prev.map((m) =>
          m._id === typingId ? { role: "ai", content: finalText, timestamp: Date.now() } : m
        )
      );

      // IMPORTANT: refresh sidebar so auto-title appears
      onNeedRefreshSidebar?.();
    } catch (e) {
      console.error(e);
      setError(e?.message || "Chat error");

      setMessages((prev) =>
        prev.map((m) =>
          m._id === typingId
            ? { role: "ai", content: "⚠️ Failed to contact backend.", timestamp: Date.now() }
            : m
        )
      );
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="h-full flex flex-col min-w-0">
      <div className="px-4 py-3 border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="text-sm text-white/75">
          {conversationId ? "Conversation" : "Select a chat or click New"}
        </div>
        {error ? (
          <div className="mt-2 text-xs text-red-200 bg-red-900/30 border border-red-500/20 rounded-xl px-3 py-2">
            {error}
          </div>
        ) : null}
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-3">
        {conversationId && hasMore ? (
          <button
            className="mx-auto block text-xs px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10"
            onClick={() => loadPage({ reset: false, nextOffset: offset + PAGE_SIZE })}
          >
            Load older messages
          </button>
        ) : null}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-white/10 bg-black/25 backdrop-blur-xl">
        <div className="flex gap-3">
          <input
            className="flex-1 px-4 py-3 rounded-2xl bg-black/35 border border-white/10 outline-none
                       placeholder:text-white/35 focus:border-white/20"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={isSending ? "Waiting for response..." : "Type a message..."}
            disabled={isSending}
          />
          <button
            className="px-5 py-3 rounded-2xl bg-white/10 hover:bg-white/15 border border-white/10 disabled:opacity-60"
            onClick={sendMessage}
            disabled={isSending}
          >
            {isSending ? "Sending…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
