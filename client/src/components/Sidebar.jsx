import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import { FaPlus, FaComments, FaTrash } from "react-icons/fa";

export default function Sidebar({ selectedId, onSelect, onNew }) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");

  const loadConversations = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE}/api/v1/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setConversations(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Failed to load conversations", e);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Refresh list after creating a new chat
  const handleNew = async () => {
    await onNew();
    await loadConversations();
  };

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return conversations;
    return conversations.filter((c) => (c.title || "").toLowerCase().includes(s));
  }, [conversations, q]);

  return (
    <div className="w-72 bg-black/40 border-r border-white/10 flex flex-col backdrop-blur-xl">
      <div className="p-4 flex items-center justify-between border-b border-white/10">
        <div className="font-semibold text-sm">Chats</div>
        <button
          onClick={handleNew}
          className="p-2 rounded-xl bg-white/10 hover:bg-white/15 transition"
          title="New chat"
        >
          <FaPlus />
        </button>
      </div>

      <div className="p-3">
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search chats..."
            className="w-full bg-transparent outline-none text-sm text-white/90 placeholder:text-white/40"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-3 space-y-1">
        {loading && <div className="text-xs text-white/40 p-2">Loading...</div>}

        {!loading && filtered.length === 0 && (
          <div className="text-xs text-white/40 p-2">No conversations</div>
        )}

        {filtered.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-left transition
              ${selectedId === c.id ? "bg-white/15 border border-white/10" : "hover:bg-white/10"}`}
          >
            <FaComments className="opacity-70" />
            <span className="truncate">{c.title || "New chat"}</span>
          </button>
        ))}
      </div>

      <div className="px-3 pb-3">
        <div className="text-[11px] text-white/35">
          First message auto-renames the chat
        </div>
      </div>
    </div>
  );
}
