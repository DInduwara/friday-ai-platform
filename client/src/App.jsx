import { useState } from "react";
import { SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";

import ChatPanel from "./components/ChatPanel";
import AgentFlow from "./components/AgentFlow";

export default function App() {
  const [agentSteps, setAgentSteps] = useState([]);

  return (
    <div className="h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950 text-white">
      <SignedOut>
        <div className="h-full flex items-center justify-center p-6">
          {/* routing="hash" works great with Vite SPA */}
          <SignIn routing="hash" />
        </div>
      </SignedOut>

      <SignedIn>
        <div className="h-full flex">
          {/* Left: Chat */}
          <div className="flex-1 flex flex-col">
            {/* Top bar */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/20">
              <div className="font-semibold">FRIDAY</div>
              <UserButton />
            </div>

            <ChatPanel setAgentSteps={setAgentSteps} />
          </div>

          {/* Right: Agent Flow */}
          <div className="w-1/3 p-4 overflow-y-auto">
            <AgentFlow steps={agentSteps} />
          </div>
        </div>
      </SignedIn>
    </div>
  );
}
