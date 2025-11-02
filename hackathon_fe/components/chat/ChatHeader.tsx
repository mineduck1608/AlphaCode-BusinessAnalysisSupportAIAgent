// components/chat/ChatHeader.tsx
"use client";

import React from "react";

export default function ChatHeader() {
  return (
    <div className="p-4 border-b border-gray-800 bg-[#1e1f24] flex items-center justify-between">
      <div>
        <h2 className="text-lg font-semibold">ChatGPT</h2>
        <div className="text-xs text-neutral-400">GPT-5 Mock · Local</div>
      </div>
      <div className="text-sm text-neutral-400">Model: gpt-5-mock</div>
    </div>
  );
}
