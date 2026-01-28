import { useCallback, useEffect, useState } from "react";
import { SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";

import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import AgentFlow from "./components/AgentFlow";

export default function App() {
  const [agentSteps, setAgentSteps] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  const refreshSidebar = useCallback(() => {
    setSidebarRefreshKey((k) => k + 1);
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("friday_selected_conversation");
    if (saved) setSelectedConversationId(saved);
  }, []);

  const handleSelect = (id) => {
    setSelectedConversationId(id);
    if (id) localStorage.setItem("friday_selected_conversation", id);
    setAgentSteps([]);
  };

  const handleCreated = (id) => {
    setSelectedConversationId(id);
    localStorage.setItem("friday_selected_conversation", id);
    setAgentSteps([]);
    refreshSidebar();
  };

  const handleDeleted = (id) => {
    if (id === selectedConversationId) {
      setSelectedConversationId(null);
      localStorage.removeItem("friday_selected_conversation");
      setAgentSteps([]);
    }
    refreshSidebar();
  };

  return (
    <div className="min-h-screen friday-bg text-white">
      <SignedOut>
        <div className="min-h-screen flex items-center justify-center p-6">
          <div className="w-full max-w-md rounded-2xl border border-white/10 bg-black/40 p-6 backdrop-blur-xl shadow-2xl">
            <div className="text-xl font-semibold mb-2">FRIDAY</div>
            <div className="text-sm text-white/60 mb-6">Sign in to continue</div>
            <SignIn routing="hash" />
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="h-screen flex">
          <div className="w-[320px] shrink-0">
            <Sidebar
              key={sidebarRefreshKey}
              selectedId={selectedConversationId}
              onSelect={handleSelect}
              onCreated={handleCreated}
              onDeleted={handleDeleted}
            />
          </div>

          <div className="flex-1 flex flex-col min-w-0">
            <div className="h-14 px-5 flex items-center justify-between border-b border-white/10 bg-black/20 backdrop-blur-xl">
              <div className="font-semibold tracking-wide">FRIDAY</div>
              <UserButton />
            </div>

            <div className="flex-1 min-h-0 flex">
              <div className="flex-1 min-w-0">
                <ChatPanel
                  conversationId={selectedConversationId}
                  setAgentSteps={setAgentSteps}
                  onNeedRefreshSidebar={refreshSidebar}
                  onConversationCreated={handleCreated}
                />
              </div>

              <div className="w-[420px] shrink-0 border-l border-white/10 bg-black/15 backdrop-blur-xl p-4 overflow-y-auto">
                <AgentFlow steps={agentSteps} />
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
    </div>
  );
}
