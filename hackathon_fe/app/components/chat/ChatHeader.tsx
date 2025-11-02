// components/chat/ChatHeader.tsx
"use client";

import React from "react";
import { Bot, Sparkles, Circle } from "lucide-react";

interface ChatHeaderProps {
  connected?: boolean;
  connecting?: boolean;
}

export default function ChatHeader({ connected = false, connecting = false }: ChatHeaderProps) {
  return (
    <div className="px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-linear-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center relative shadow-lg shadow-blue-500/20">
          <Bot className="w-7 h-7 text-white" />
          <Circle
            className={`absolute -bottom-1 -right-1 w-4 h-4 border-2 border-[#0a0e13] rounded-full ${
              connected ? 'fill-green-500 text-green-500' : 
              connecting ? 'fill-yellow-500 text-yellow-500 animate-pulse' : 
              'fill-red-500 text-red-500'
            }`}
          />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">AI Assistant</h2>
          <div className="text-xs text-gray-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            {connecting ? 'Đang kết nối...' : connected ? 'WebSocket Ready' : 'Offline'}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className={`text-xs font-medium px-4 py-2 rounded-full border shadow-lg ${
          connected ? 'bg-green-500/10 text-green-400 border-green-500/30' :
          connecting ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30 animate-pulse' :
          'bg-red-500/10 text-red-400 border-red-500/30'
        }`}>
          {connected ? '🟢 Online' : connecting ? '🟡 Connecting' : '🔴 Offline'}
        </span>
      </div>
    </div>
  );
}
