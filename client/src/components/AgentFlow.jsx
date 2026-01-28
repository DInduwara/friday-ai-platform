import { FaRobot, FaUser, FaCheckCircle } from "react-icons/fa";

const iconMap = {
  ai: <FaRobot className="text-purple-400 w-5 h-5" />,
  user: <FaUser className="text-blue-400 w-5 h-5" />,
  supervisor: <FaCheckCircle className="text-green-400 w-6 h-6" />,
};

export default function AgentFlow({ steps }) {
  return (
    <div className="p-4 bg-gray-900/80 backdrop-blur-md rounded-xl shadow-xl">
      <h2 className="text-xl font-bold mb-6 text-white border-b border-gray-700 pb-2">
        Agent Flow
      </h2>

      {steps.length === 0 ? (
        <p className="text-gray-400 italic text-center">Waiting for agent steps...</p>
      ) : (
        <div className="space-y-4">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="flex items-start p-4 rounded-xl bg-gradient-to-r from-gray-800 to-gray-900 shadow-lg border border-gray-700 hover:scale-105 transition-transform"
            >
              {/* Icon */}
              <div className="mr-3">
                {iconMap[step.type?.toLowerCase()] || <FaRobot className="w-5 h-5 text-gray-400" />}
              </div>

              {/* Step content */}
              <div>
                <strong className="block text-blue-400 text-lg mb-1">{step.type}</strong>
                <p className="text-gray-200">{step.content}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}