import { useEffect, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import { FaPlus, FaSearch, FaTrash } from "react-icons/fa";

export default function Sidebar({ selectedId, onSelect, onCreated, onDeleted }) {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async (query) => {
    setLoading(true);
    try {
      const token = await getToken();
      const params = new URLSearchParams();
      params.set("limit", "50");
      params.set("offset", "0");
      if (query?.trim()) params.set("q", query.trim());

      const res = await fetch(`${API_BASE}/api/v1/conversations?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setItems(Array.isArray(data?.items) ? data.items : []);
    } catch (e) {
      console.error(e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // debounce search
  useEffect(() => {
    const t = setTimeout(() => load(q), 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  const createConversation = async () => {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/v1/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: "New chat" }),
    });
    const c = await res.json();
    if (c?.id) {
      onCreated?.(c.id);
      load(q);
    }
  };

  const deleteConversation = async (id) => {
    if (!confirm("Delete this conversation?")) return;

    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE}/api/v1/conversations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Delete failed");

      onDeleted?.(id);
      load(q);
    } catch (e) {
      console.error(e);
      alert("Failed to delete conversation.");
    }
  };

  return (
    <div className="h-full flex flex-col border-r border-white/10 bg-black/30 backdrop-blur-xl">
      <div className="h-14 px-4 flex items-center justify-between border-b border-white/10">
        <div className="font-semibold text-sm tracking-wide">Chats</div>
        <button
          onClick={createConversation}
          className="p-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10"
          title="New chat"
        >
          <FaPlus />
        </button>
      </div>

      <div className="p-3 border-b border-white/10">
        <div className="flex items-center gap-2 rounded-xl bg-black/30 border border-white/10 px-3 py-2">
          <FaSearch className="text-white/50" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search chats…"
            className="w-full bg-transparent outline-none text-sm placeholder:text-white/40"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading ? <div className="text-xs text-white/45 p-3">Loading…</div> : null}

        {!loading && items.length === 0 ? (
          <div className="text-xs text-white/45 p-3">No conversations</div>
        ) : null}

        {items.map((c) => (
          <div
            key={c.id}
            className={`group flex items-center gap-2 rounded-xl px-3 py-2 border ${
              selectedId === c.id
                ? "bg-white/10 border-white/15"
                : "border-transparent hover:border-white/10 hover:bg-white/5"
            }`}
          >
            <button onClick={() => onSelect?.(c.id)} className="flex-1 min-w-0 text-left">
              <div className="text-sm truncate">{c.title || "New chat"}</div>
              <div className="text-[11px] text-white/45 truncate">
                {c.updated_at ? new Date(c.updated_at).toLocaleString() : ""}
              </div>
            </button>

            <button
              onClick={() => deleteConversation(c.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg hover:bg-white/10"
              title="Delete"
            >
              <FaTrash className="text-white/60" />
            </button>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-white/10 text-xs text-white/45">
        First message auto-renames the chat ✨
      </div>
    </div>
  );
}
