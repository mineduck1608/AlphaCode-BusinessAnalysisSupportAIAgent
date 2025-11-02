// components/chat/ChatMessageList.tsx
"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "./ChatLayout";

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
    <div ref={containerRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-neutral-900">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={`max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm ${msg.role === "user" ? "bg-[#4b5563] text-white" : "bg-[#2a2b32] text-neutral-100"}`}>
            {msg.content || (msg.role === "assistant" ? "…" : "")}
            <div className="text-xs text-neutral-400 mt-2 text-right">{msg.time}</div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-[#2a2b32] text-neutral-400 text-sm px-4 py-2 rounded-2xl animate-pulse">Thinking...</div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
