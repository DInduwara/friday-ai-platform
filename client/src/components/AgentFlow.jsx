import { FaRobot, FaRoute, FaTools, FaBrain, FaDatabase, FaExclamationTriangle } from "react-icons/fa";

const kindIcon = {
  route: <FaRoute className="text-blue-300 w-5 h-5" />,
  tool: <FaTools className="text-green-300 w-5 h-5" />,
  agent: <FaBrain className="text-purple-300 w-5 h-5" />,
  memory: <FaDatabase className="text-yellow-300 w-5 h-5" />,
  error: <FaExclamationTriangle className="text-red-300 w-5 h-5" />,
  final: <FaRobot className="text-indigo-300 w-5 h-5" />,
};

function prettyData(data) {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

export default function AgentFlow({ steps }) {
  return (
    <div className="p-4 bg-gray-900/80 backdrop-blur-md rounded-xl shadow-xl">
      <h2 className="text-xl font-bold mb-6 text-white border-b border-gray-700 pb-2">
        Agent Flow
      </h2>

      {(!steps || steps.length === 0) ? (
        <p className="text-gray-400 italic text-center">Waiting for agent steps...</p>
      ) : (
        <div className="space-y-3">
          {steps.map((step, idx) => {
            const kind = step?.kind || "unknown";
            const data = step?.data ?? {};
            return (
              <div
                key={idx}
                className="flex items-start gap-3 p-4 rounded-xl bg-gradient-to-r from-gray-800 to-gray-900 shadow-lg border border-gray-700"
              >
                <div className="mt-1">
                  {kindIcon[kind] || <FaRobot className="w-5 h-5 text-gray-400" />}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <strong className="text-blue-300 text-base">{kind}</strong>
                    <span className="text-xs text-gray-400">#{idx + 1}</span>
                  </div>

                  <pre className="mt-2 text-xs text-gray-200 bg-black/30 border border-white/5 rounded-lg p-3 overflow-auto">
                    {prettyData(data)}
                  </pre>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
