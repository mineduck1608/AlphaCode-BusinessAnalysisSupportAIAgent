"use client";

import React from "react";
import { Bot } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="flex gap-4 items-start">
      {/* Avatar */}
      <div className="w-10 h-10 rounded-full bg-linear-to-br from-purple-600 to-blue-600 flex items-center justify-center shrink-0">
        <Bot size={20} className="text-white" />
      </div>

      {/* Typing bubble */}
      <div className="bg-[#1a1f2e] rounded-2xl px-5 py-4 border border-blue-500/20">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
        </div>
      </div>
    </div>
  );
}
