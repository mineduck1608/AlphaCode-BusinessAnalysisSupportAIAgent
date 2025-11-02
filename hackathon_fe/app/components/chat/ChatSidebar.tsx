"use client";

import React from "react";
import Image from "next/image";
import { Plus, MessageSquare, Settings, LogOut, User } from "lucide-react";

export default function ChatSidebar({ onLogout, userEmail }: { onLogout?: () => void; userEmail?: string | undefined }) {
  return (
    <div className="w-72 bg-[#0f1419] flex flex-col border-r border-blue-900/20">
      {/* Header với gradient và logo */}
      <div className="p-4 border-b border-blue-900/20 bg-gradient-to-r from-blue-600/10 to-purple-600/10">
        <div className="flex items-center gap-2 mb-3">
          <Image 
            src="/logo2.png" 
            alt="AlphaCode Logo" 
            width={28} 
            height={28}
            className="w-7 h-7 object-contain"
          />
          <span className="font-bold text-lg text-white">AlphaCode</span>
        </div>
        <button className="w-full flex items-center justify-center gap-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-500 px-4 py-3 rounded-lg hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/20">
          <Plus size={18} /> New Chat
        </button>
      </div>

      {/* Recent Chats */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="text-xs font-semibold text-blue-400 mb-3 px-2 uppercase tracking-wider">Recent Chats</div>
        <div className="space-y-1">
          <div className="group px-3 py-2.5 rounded-lg hover:bg-blue-900/20 cursor-pointer transition-all border border-transparent hover:border-blue-500/20">
            <div className="flex items-center gap-2 text-sm text-gray-300 group-hover:text-white">
              <MessageSquare size={14} className="text-blue-400" />
              <span className="truncate">Project ideas</span>
            </div>
          </div>
          <div className="group px-3 py-2.5 rounded-lg hover:bg-blue-900/20 cursor-pointer transition-all border border-transparent hover:border-blue-500/20">
            <div className="flex items-center gap-2 text-sm text-gray-300 group-hover:text-white">
              <MessageSquare size={14} className="text-blue-400" />
              <span className="truncate">Study notes</span>
            </div>
          </div>
          <div className="group px-3 py-2.5 rounded-lg hover:bg-blue-900/20 cursor-pointer transition-all border border-transparent hover:border-blue-500/20">
            <div className="flex items-center gap-2 text-sm text-gray-300 group-hover:text-white">
              <MessageSquare size={14} className="text-blue-400" />
              <span className="truncate">Recipes</span>
            </div>
          </div>
        </div>
      </div>

      {/* User Info Footer */}
      <div className="p-4 border-t border-blue-900/20 bg-[#0a0e13]">
        <div className="flex items-center gap-3 mb-3 px-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <User size={16} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-white truncate">{userEmail ?? "guest"}</div>
            <div className="text-xs text-gray-500">Free Plan</div>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            className="flex-1 flex items-center justify-center gap-2 text-xs text-gray-400 hover:text-white hover:bg-blue-900/20 px-3 py-2 rounded-lg transition-all border border-blue-900/20 hover:border-blue-500/30" 
            onClick={() => alert("Settings (mock)")}
          >
            <Settings size={14} />
            <span>Settings</span>
          </button>
          <button 
            className="flex items-center justify-center gap-2 text-xs text-red-400 hover:text-white hover:bg-red-900/20 px-3 py-2 rounded-lg transition-all border border-red-900/20 hover:border-red-500/30" 
            onClick={onLogout}
          >
            <LogOut size={14} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>
  );
}
