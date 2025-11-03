"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "./ChatLayout";
import { Bot, User } from "lucide-react";
import TypingIndicator from "./TypingIndicator";

export default function ChatMessageList({
  messages,
  isLoading,
  isAgentTyping,
  bottomRef,
  loadingMore,
  hasMore,
  onLoadMore,
}: {
  messages: Message[];
  isLoading: boolean;
  isAgentTyping?: boolean;
  bottomRef: React.RefObject<HTMLDivElement | null>;
  loadingMore?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const topSentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    console.log('💬 ChatMessageList render:', { isLoading, isAgentTyping, messageCount: messages.length });
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading, isAgentTyping]);

  // Intersection Observer for loading more messages when scrolling to top
  useEffect(() => {
    if (!onLoadMore || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loadingMore) {
          onLoadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (topSentinelRef.current) {
      observer.observe(topSentinelRef.current);
    }

    return () => observer.disconnect();
  }, [onLoadMore, hasMore, loadingMore]);

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-background">
      {/* Top sentinel for infinite scroll */}
      {hasMore && (
        <div ref={topSentinelRef} className="h-4 flex items-center justify-center">
          {loadingMore && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              Loading earlier messages...
            </div>
          )}
        </div>
      )}
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
          {/* Avatar */}
          <div className={`shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
            msg.role === "user" 
              ? "bg-linear-to-br from-blue-600 to-blue-500" 
              : "bg-linear-to-br from-purple-600 to-blue-600 border-2 border-blue-500/30"
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
                ? "bg-linear-to-r from-blue-600 to-blue-500 text-white" 
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

      {/* Agent Typing Indicator */}
      {isAgentTyping && <TypingIndicator />}

      {/* Loading fallback (if typing not triggered) */}
      {isLoading && !isAgentTyping && (
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
