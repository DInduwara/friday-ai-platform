import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import AgentFlow from "./components/AgentFlow";

function App() {
  const [agentSteps, setAgentSteps] = useState([]);

  return (
    <div className="h-screen flex bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950 text-white">
      {/* Chat Section */}
      <div className="flex-1 flex flex-col">
        <ChatPanel setAgentSteps={setAgentSteps} />
      </div>

      {/* Agent Flow Section */}
      <div className="w-1/3 p-4 overflow-y-auto">
        <AgentFlow steps={agentSteps} />
      </div>
    </div>
  );
}

export default App;
