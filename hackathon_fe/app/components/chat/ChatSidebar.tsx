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
import { getCurrentUserId } from "@/app/lib/authMock";
import { toast } from "sonner";

export default function ChatSidebar({ onLogout, userEmail }: { onLogout?: () => void; userEmail?: string | null }) {
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<ShareableConversation | null>(null);
  const [activeTab, setActiveTab] = useState<"recent" | "shared">("recent");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null);
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

  const handleNewChat = async () => {
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

    
    try{
      const newConv = await conversationApi.create({
        name: "New Conversation",
        user_id: getCurrentUserId() || -1,
        is_shared: false
      });
      fetchConversations();
      router.push('/chat?id=' + newConv.id);
    }
    catch{

    }
  }

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent navigation when clicking delete
    setConversationToDelete(conversationId);
    setShowDeleteModal(true);
  }

  const confirmDelete = async () => {
    if (!conversationToDelete) return;

    // Use toast.promise for better UX
    toast.promise(
      async () => {
        await conversationApi.delete(conversationToDelete);
        // Remove from local state
        setConversations(prev => prev.filter(conv => conv.id !== conversationToDelete));
        // If currently viewing this conversation, redirect to chat
        if (window.location.pathname.includes(conversationToDelete)) {
          router.push('/chat');
        }
        setShowDeleteModal(false);
        setConversationToDelete(null);
      },
      {
        loading: 'Deleting conversation...',
        success: 'Conversation deleted successfully',
        error: 'Failed to delete conversation',
      }
    );
  }

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setConversationToDelete(null);
  }

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
        <button onClick={handleNewChat} className="w-full flex items-center justify-center gap-2 text-sm font-medium text-white bg-linear-to-r from-blue-600 to-blue-500 px-4 py-3 rounded-lg hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/20">
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
                    className="group px-3 py-2.5 rounded-lg hover:bg-blue-900/20 cursor-pointer transition-all border border-transparent hover:border-blue-500/20 relative"
                    title={conversation.name || conversation.summary || `Conversation ${conversation.id.slice(0, 8)}`}
                  >
                    <div className="flex items-center gap-2 text-sm text-gray-300 group-hover:text-white">
                      <MessageSquare size={14} className="text-blue-400 flex-shrink-0" />
                      <span className="truncate flex-1">
                        {conversation.name || conversation.summary || `Chat ${conversation.id.slice(0, 8)}`}
                      </span>
                      {/* Delete button - only show on hover */}
                      <button
                        onClick={(e) => handleDeleteConversation(conversation.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-900/30 rounded transition-all flex-shrink-0"
                        title="Delete conversation"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                          <path d="M3 6h18"/>
                          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
                          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                        </svg>
                      </button>
                    </div>
                    <div className="text-xs text-gray-500 mt-1 px-5">
                      {conversation.last_updated ? new Date(conversation.last_updated).toLocaleDateString() : 'No date'}
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

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={cancelDelete}>
          <div className="bg-[#1a1f2e] rounded-lg p-6 max-w-md w-full mx-4 border border-blue-900/20" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                  <path d="M3 6h18"/>
                  <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                  <line x1="10" x2="10" y1="11" y2="17"/>
                  <line x1="14" x2="14" y1="11" y2="17"/>
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Delete Conversation</h3>
                <p className="text-sm text-gray-400">This action cannot be undone</p>
              </div>
            </div>
            
            <p className="text-gray-300 mb-6">
              Are you sure you want to delete this conversation? All messages and history will be permanently removed.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={cancelDelete}
                className="flex-1 px-4 py-2.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="flex-1 px-4 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
