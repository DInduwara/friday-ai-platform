import { motion } from "framer-motion";
import { FaRobot, FaUser } from "react-icons/fa";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  const time = new Date(message.timestamp || Date.now()).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const content = message._typing ? (message.content?.trim() ? message.content : "…") : message.content;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`
          max-w-[860px] w-fit px-4 py-3 rounded-2xl border border-white/10 shadow-lg
          ${isUser ? "bg-white/10" : "bg-black/30"}
        `}
      >
        <div className="flex items-center gap-2 mb-2 text-xs text-white/65">
          {isUser ? <FaUser /> : <FaRobot />}
          <span className="font-semibold">{isUser ? "You" : "FRIDAY"}</span>
          <span className="ml-auto text-[10px] text-white/45">{time}</span>
        </div>

        <div className="text-sm leading-relaxed whitespace-pre-wrap break-words overflow-hidden">
          {content}
        </div>
      </div>
    </motion.div>
  );
}
