import { useCallback, useEffect, useMemo, useState } from "react";
import { SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";
import { FaBars, FaTimes } from "react-icons/fa";

import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import AgentFlow from "./components/AgentFlow";

function useIsMobile(breakpointPx = 1024) {
  const [isMobile, setIsMobile] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.innerWidth < breakpointPx;
  });

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpointPx - 1}px)`);
    const handler = (e) => setIsMobile(e.matches);
    handler(mq); // init
    mq.addEventListener?.("change", handler);
    return () => mq.removeEventListener?.("change", handler);
  }, [breakpointPx]);

  return isMobile;
}

export default function App() {
  const [agentSteps, setAgentSteps] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  // mobile UI state
  const isMobile = useIsMobile(1024); // lg breakpoint behavior
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileTab, setMobileTab] = useState("chat"); // "chat" | "agent"

  const refreshSidebar = useCallback(() => {
    setSidebarRefreshKey((k) => k + 1);
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("friday_selected_conversation");
    if (saved) setSelectedConversationId(saved);
  }, []);

  // close drawer if we switch to desktop
  useEffect(() => {
    if (!isMobile) setSidebarOpen(false);
  }, [isMobile]);

  const handleSelect = (id) => {
    setSelectedConversationId(id);
    if (id) localStorage.setItem("friday_selected_conversation", id);
    setAgentSteps([]);
    // mobile: close drawer after selecting
    if (isMobile) setSidebarOpen(false);
    // ensure we show chat
    if (isMobile) setMobileTab("chat");
  };

  const handleCreated = (id) => {
    setSelectedConversationId(id);
    localStorage.setItem("friday_selected_conversation", id);
    setAgentSteps([]);
    refreshSidebar();
    if (isMobile) {
      setSidebarOpen(false);
      setMobileTab("chat");
    }
  };

  const handleDeleted = (id) => {
    if (id === selectedConversationId) {
      setSelectedConversationId(null);
      localStorage.removeItem("friday_selected_conversation");
      setAgentSteps([]);
    }
    refreshSidebar();
  };

  const sidebarNode = useMemo(
    () => (
      <Sidebar
        key={sidebarRefreshKey}
        selectedId={selectedConversationId}
        onSelect={handleSelect}
        onCreated={handleCreated}
        onDeleted={handleDeleted}
      />
    ),
    [sidebarRefreshKey, selectedConversationId]
  );

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
        {/* MOBILE LAYOUT */}
        {isMobile ? (
          <div className="h-screen flex flex-col">
            {/* Top bar */}
            <div className="h-14 px-4 flex items-center justify-between border-b border-white/10 bg-black/20 backdrop-blur-xl">
              <button
                className="p-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10"
                onClick={() => setSidebarOpen(true)}
                aria-label="Open sidebar"
              >
                <FaBars />
              </button>

              <div className="font-semibold tracking-wide">FRIDAY</div>

              <UserButton />
            </div>

            {/* Tabs */}
            <div className="px-4 py-3 border-b border-white/10 bg-black/10 backdrop-blur-xl">
              <div className="inline-flex w-full rounded-2xl border border-white/10 bg-black/20 p-1">
                <button
                  onClick={() => setMobileTab("chat")}
                  className={`flex-1 px-4 py-2 rounded-2xl text-sm ${
                    mobileTab === "chat" ? "bg-white/10" : "hover:bg-white/5"
                  }`}
                >
                  Chat
                </button>
                <button
                  onClick={() => setMobileTab("agent")}
                  className={`flex-1 px-4 py-2 rounded-2xl text-sm ${
                    mobileTab === "agent" ? "bg-white/10" : "hover:bg-white/5"
                  }`}
                >
                  Agent
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="flex-1 min-h-0">
              {mobileTab === "chat" ? (
                <ChatPanel
                  conversationId={selectedConversationId}
                  setAgentSteps={setAgentSteps}
                  onNeedRefreshSidebar={refreshSidebar}
                  onConversationCreated={handleCreated}
                />
              ) : (
                <div className="h-full p-4 overflow-y-auto">
                  <AgentFlow steps={agentSteps} />
                </div>
              )}
            </div>

            {/* Sidebar Drawer */}
            {sidebarOpen ? (
              <div className="fixed inset-0 z-50">
                {/* overlay */}
                <div
                  className="absolute inset-0 bg-black/60"
                  onClick={() => setSidebarOpen(false)}
                />
                {/* panel */}
                <div className="absolute inset-y-0 left-0 w-[88%] max-w-[360px]">
                  <div className="h-14 px-4 flex items-center justify-between border-b border-white/10 bg-black/40 backdrop-blur-xl">
                    <div className="font-semibold">Chats</div>
                    <button
                      className="p-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10"
                      onClick={() => setSidebarOpen(false)}
                      aria-label="Close sidebar"
                    >
                      <FaTimes />
                    </button>
                  </div>
                  <div className="h-[calc(100vh-56px)] bg-black/30 backdrop-blur-xl">
                    {sidebarNode}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        ) : (
          /* DESKTOP LAYOUT (same as yours) */
          <div className="h-screen flex">
            <div className="w-[320px] shrink-0">{sidebarNode}</div>

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
        )}
      </SignedIn>
    </div>
  );
}
