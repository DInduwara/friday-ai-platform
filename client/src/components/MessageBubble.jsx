import { motion } from "framer-motion";
import { FaRobot, FaUser } from "react-icons/fa";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  const time = new Date(message.timestamp || Date.now()).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`
          max-w-[75%] px-4 py-3 rounded-2xl shadow-lg break-words
          backdrop-blur-md border border-white/10
          ${
            isUser
              ? "bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-br-md"
              : "bg-gradient-to-r from-gray-800 to-indigo-900 text-white rounded-bl-md"
          }
        `}
      >
        <div className="flex items-center gap-2 mb-1 opacity-80 text-xs">
          {isUser ? (
            <FaUser className="text-blue-200" />
          ) : (
            <FaRobot className="text-purple-300" />
          )}
          <span className="font-semibold">{isUser ? "You" : "FRIDAY"}</span>
          <span className="ml-auto text-[10px] text-white/60">{time}</span>
        </div>

        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    </motion.div>
  );
}
