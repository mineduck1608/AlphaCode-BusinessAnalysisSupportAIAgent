"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Plus, MessageSquare, Settings, LogOut, User, Share2, Clock, Globe } from "lucide-react";
import ShareDialog from "./ShareDialog";
import SharedConversationsList from "./SharedConversationsList";
import { getAllConversations, type ShareableConversation } from "@/app/lib/shareMockAPI";
import { conversationApi } from "@/app/api/conversationApi";
import { Conversation } from "@/app/types/conversation";
import { useRouter } from "next/navigation";

export default function ChatSidebar({ onLogout, userEmail }: { onLogout?: () => void; userEmail?: string | undefined }) {
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<ShareableConversation | null>(null);
  const [activeTab, setActiveTab] = useState<"recent" | "shared">("recent");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const router = useRouter();

  // Fetch conversations when component mounts
  useEffect(() => {
    const fetchConversations = async () => {
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        setConversations([]);
        return;
      }

      setLoadingConversations(true);
      try {
        const data = await conversationApi.getByUserId(userId);
        setConversations(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
        setConversations([]);
      } finally {
        setLoadingConversations(false);
      }
    };

    fetchConversations();
  }, []);

  const handleShareClick = async () => {
    // Get first conversation for demo (trong thực tế sẽ get conversation hiện tại)
    const conversations = await getAllConversations();
    if (conversations.length > 0) {
      setSelectedConversation(conversations[0]);
      setShowShareDialog(true);
    }
  };

  const handleConversationClick = (conversationId: string) => {
    router.push(`/chat?id=${conversationId}`);
  };
  return (
    <div className="w-72 bg-background flex flex-col border-r border-blue-900/20">
      {/* Header với gradient và logo */}
      <div className="p-4 border-b border-blue-900/20 bg-linear-to-r from-blue-600/10 to-purple-600/10">
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
        <button className="w-full flex items-center justify-center gap-2 text-sm font-medium text-white bg-linear-to-r from-blue-600 to-blue-500 px-4 py-3 rounded-lg hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/20">
          <Plus size={18} /> New Chat
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-blue-900/20 bg-[#0a0e13]">
        <button
          onClick={() => setActiveTab("recent")}
          className={`flex-1 px-4 py-3 text-xs font-medium transition-all relative flex items-center justify-center gap-2 ${
            activeTab === "recent"
              ? "text-blue-400"
              : "text-gray-400 hover:text-gray-300"
          }`}
        >
          <Clock size={14} />
          Recent
          {activeTab === "recent" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"></div>
          )}
        </button>
        <button
          onClick={() => setActiveTab("shared")}
          className={`flex-1 px-4 py-3 text-xs font-medium transition-all relative flex items-center justify-center gap-2 ${
            activeTab === "shared"
              ? "text-blue-400"
              : "text-gray-400 hover:text-gray-300"
          }`}
        >
          <Globe size={14} />
          Shared
          {activeTab === "shared" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"></div>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === "recent" ? (
          <div className="p-3">
            <div className="text-xs font-semibold text-blue-400 mb-3 px-2 uppercase tracking-wider">Recent Chats</div>
            <div className="space-y-1">
              {loadingConversations ? (
                <div className="px-3 py-2 text-xs text-gray-400">Loading conversations...</div>
              ) : conversations.length > 0 ? (
                conversations.map((conversation) => (
                  <div 
                    key={conversation.id}
                    onClick={() => handleConversationClick(conversation.id)}
                    className="group px-3 py-2.5 rounded-lg hover:bg-blue-900/20 cursor-pointer transition-all border border-transparent hover:border-blue-500/20"
                    title={conversation.name || conversation.summary || `Conversation ${conversation.id.slice(0, 8)}`}
                  >
                    <div className="flex items-center gap-2 text-sm text-gray-300 group-hover:text-white">
                      <MessageSquare size={14} className="text-blue-400" />
                      <span className="truncate">
                        {conversation.name || conversation.summary || `Chat ${conversation.id.slice(0, 8)}`}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1 px-5">
                      {new Date(conversation.last_updated).toLocaleDateString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-3 py-2 text-xs text-gray-400">No conversations yet</div>
              )}
            </div>
          </div>
        ) : (
          <SharedConversationsList />
        )}
      </div>

      {/* User Info Footer */}
      <div className="p-4 border-t border-blue-900/20 bg-[#0a0e13]">
        <div className="flex items-center gap-3 mb-3 px-2">
          <div className="w-8 h-8 rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <User size={16} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-white truncate">{userEmail ?? "guest"}</div>
            <div className="text-xs text-gray-500">Free Plan</div>
          </div>
        </div>
        <div className="flex gap-2 mb-2">
          <button 
            className="flex-1 flex items-center justify-center gap-2 text-xs text-blue-400 hover:text-white hover:bg-blue-900/20 px-3 py-2 rounded-lg transition-all border border-blue-900/20 hover:border-blue-500/30" 
            onClick={handleShareClick}
          >
            <Share2 size={14} />
            <span>Share Chat</span>
          </button>
          <button 
            className="flex items-center justify-center gap-2 text-xs text-gray-400 hover:text-white hover:bg-blue-900/20 px-3 py-2 rounded-lg transition-all border border-blue-900/20 hover:border-blue-500/30" 
            onClick={() => alert("Settings (mock)")}
          >
            <Settings size={14} />
          </button>
        </div>
        <div className="flex gap-2">
          <button 
            className="flex-1 flex items-center justify-center gap-2 text-xs text-red-400 hover:text-white hover:bg-red-900/20 px-3 py-2 rounded-lg transition-all border border-red-900/20 hover:border-red-500/30" 
            onClick={onLogout}
          >
            <LogOut size={14} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Share Dialog */}
      <ShareDialog 
        conversation={selectedConversation}
        isOpen={showShareDialog}
        onClose={() => setShowShareDialog(false)}
      />
    </div>
  );
}
