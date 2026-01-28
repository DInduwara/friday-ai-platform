import { motion } from "framer-motion";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`
          max-w-xs px-4 py-2 rounded-2xl shadow-lg break-words 
          backdrop-blur-md bg-opacity-70
          ${isUser 
            ? "bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-br-md" 
            : "bg-gradient-to-r from-gray-800 to-indigo-900 text-white rounded-bl-md"}
        `}
      >
        {message.content}
      </div>
    </motion.div>
  );
}