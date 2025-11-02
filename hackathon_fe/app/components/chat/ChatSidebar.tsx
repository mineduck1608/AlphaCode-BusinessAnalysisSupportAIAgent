"use client";

import React from "react";
import { Plus, MessageSquare, Settings, LogOut } from "lucide-react";

export default function ChatSidebar({ onLogout, userEmail }: { onLogout?: () => void; userEmail?: string | undefined }) {
  return (
    <div className="w-72 bg-[#202123] flex flex-col p-4 border-r border-gray-800">
      <div className="mb-4">
        <button className="w-full flex items-center gap-2 text-sm text-neutral-100 bg-[#343541] px-3 py-2 rounded-md hover:bg-[#3e3f4b]">
          <Plus size={16} /> New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 text-sm">
        <div className="px-3 py-2 rounded-md hover:bg-[#2a2b32] cursor-pointer">Project ideas</div>
        <div className="px-3 py-2 rounded-md hover:bg-[#2a2b32] cursor-pointer">Study notes</div>
        <div className="px-3 py-2 rounded-md hover:bg-[#2a2b32] cursor-pointer">Recipes</div>
      </div>

      <div className="mt-4 border-t border-gray-800 pt-3">
        <div className="text-xs text-neutral-400 mb-2 px-1">{userEmail ?? "guest"}</div>
        <div className="flex gap-2">
          <button className="flex-1 flex items-center gap-2 text-sm text-neutral-300 hover:text-white px-2 py-2 rounded-md" onClick={() => alert("Settings (mock)")}>
            <Settings size={14} /> Settings
          </button>
          <button className="flex items-center gap-2 text-sm text-rose-300 hover:text-white px-2 py-2 rounded-md" onClick={onLogout}>
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </div>
  );
}
