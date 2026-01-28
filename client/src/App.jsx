import { useEffect, useState } from "react";
import { SignedIn, SignedOut, SignIn, UserButton, useAuth } from "@clerk/clerk-react";

import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import AgentFlow from "./components/AgentFlow";

export default function App() {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const { getToken } = useAuth();

  const [agentSteps, setAgentSteps] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);

  const createConversation = async () => {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/v1/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: "New chat" }),
    });
    const c = await res.json();
    if (c?.id) {
      setSelectedConversationId(c.id);
      localStorage.setItem("friday_selected_conversation", c.id);
      setAgentSteps([]);
    }
  };

  useEffect(() => {
    const saved = localStorage.getItem("friday_selected_conversation");
    if (saved) setSelectedConversationId(saved);
  }, []);

  const handleSelect = (id) => {
    setSelectedConversationId(id);
    if (id) localStorage.setItem("friday_selected_conversation", id);
    setAgentSteps([]);
  };

  return (
    <div className="h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950 text-white">
      <SignedOut>
        <div className="h-full flex items-center justify-center p-6">
          <SignIn routing="hash" />
        </div>
      </SignedOut>

      <SignedIn>
        <div className="h-full flex">
          <Sidebar selectedId={selectedConversationId} onSelect={handleSelect} onNew={createConversation} />

          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/20">
              <div className="font-semibold">FRIDAY</div>
              <UserButton />
            </div>

            <div className="flex flex-1">
              <div className="flex-1">
                <ChatPanel
                  conversationId={selectedConversationId}
                  onCreateConversation={createConversation}
                  setAgentSteps={setAgentSteps}
                />
              </div>

              <div className="w-1/3 p-4 overflow-y-auto border-l border-white/10 bg-black/15">
                <AgentFlow steps={agentSteps} />
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
    </div>
  );
}
