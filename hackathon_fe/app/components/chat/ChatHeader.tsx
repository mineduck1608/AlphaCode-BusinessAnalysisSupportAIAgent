// components/chat/ChatHeader.tsx
"use client";

import React from "react";
import { Bot, Sparkles } from "lucide-react";

export default function ChatHeader() {
  return (
    <div className="px-6 py-4 border-b border-border bg-background flex items-center justify-between flex-shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
          <Bot className="w-6 h-6 text-primary-foreground" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-foreground">AI Assistant</h2>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            GPT-5 Mock · Ready to help
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground bg-secondary px-3 py-1.5 rounded-full border border-border">
          Model: gpt-5-mock
        </span>
      </div>
    </div>
  );
}
