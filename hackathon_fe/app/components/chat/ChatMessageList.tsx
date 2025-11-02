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
    <div ref={containerRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-background">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${msg.role === "user" ? "bg-primary" : "bg-secondary border border-border"}`}>
            {msg.role === "user" ? (
              <User className="w-5 h-5 text-primary-foreground" />
            ) : (
              <Bot className="w-5 h-5 text-muted-foreground" />
            )}
          </div>
          
          {/* Message Content */}
          <div className={`flex-1 max-w-[75%] ${msg.role === "user" ? "text-right" : "text-left"}`}>
            <div className={`inline-block whitespace-pre-wrap rounded-lg px-4 py-3 text-sm ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground border border-border"}`}>
              {msg.content || (msg.role === "assistant" ? "…" : "")}
            </div>
            {msg.time && (
              <div className={`text-xs text-muted-foreground mt-1 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                {msg.time}
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex gap-4">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-secondary border border-border">
            <Bot className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className="bg-secondary border border-border text-muted-foreground text-sm px-4 py-3 rounded-lg animate-pulse">
            Thinking...
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
