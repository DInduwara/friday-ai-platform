import { useEffect, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import { FaPlus, FaComments } from "react-icons/fa";

export default function Sidebar({ selectedId, onSelect, onNew }) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE}/api/v1/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setConversations(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Failed to load conversations", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col">
      {/* Header */}
      <div className="p-4 flex items-center justify-between border-b border-white/10">
        <div className="font-semibold text-sm">Chats</div>
        <button
          onClick={onNew}
          className="p-2 rounded-lg bg-white/10 hover:bg-white/20"
          title="New chat"
        >
          <FaPlus />
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading && <div className="text-xs text-white/40 p-2">Loading…</div>}

        {!loading && conversations.length === 0 && (
          <div className="text-xs text-white/40 p-2">No chats yet</div>
        )}

        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left
              ${
                selectedId === c.id
                  ? "bg-white/20"
                  : "hover:bg-white/10"
              }`}
          >
            <FaComments className="opacity-70" />
            <span className="truncate">{c.title || "New chat"}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
