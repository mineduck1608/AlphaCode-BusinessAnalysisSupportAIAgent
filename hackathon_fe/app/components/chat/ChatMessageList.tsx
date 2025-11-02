"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "./ChatLayout";
import { Bot, User } from "lucide-react";

export default function ChatMessageList({
  messages,
  isLoading,
  bottomRef,
}: {
  messages: Message[];
  isLoading: boolean;
  bottomRef: React.RefObject<HTMLDivElement | null>;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#0f1419]">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
          {/* Avatar */}
          <div className={`shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
            msg.role === "user" 
              ? "bg-gradient-to-br from-blue-600 to-blue-500" 
              : "bg-gradient-to-br from-purple-600 to-blue-600 border-2 border-blue-500/30"
          }`}>
            {msg.role === "user" ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className="w-5 h-5 text-white" />
            )}
          </div>
          
          {/* Message Content */}
          <div className={`flex-1 max-w-[75%] ${msg.role === "user" ? "text-right" : "text-left"}`}>
            <div className={`inline-block whitespace-pre-wrap rounded-2xl px-5 py-3 text-sm shadow-lg ${
              msg.role === "user" 
                ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white" 
                : "bg-[#1a1f2e] text-gray-100 border border-blue-900/30"
            }`}>
              {msg.content || (msg.role === "assistant" ? "…" : "")}
            </div>
            {msg.time && (
              <div className={`text-xs text-gray-500 mt-2 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                {msg.time}
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex gap-4">
          <div className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-linear-to-br from-purple-600 to-blue-600 border-2 border-blue-500/30 shadow-lg">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div className="bg-[#1a1f2e] border border-blue-900/30 text-gray-300 text-sm px-5 py-3 rounded-2xl animate-pulse shadow-lg">
            <span className="inline-flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              <span className="ml-2">Thinking...</span>
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
