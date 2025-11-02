"use client";

import React, { useState, useEffect } from "react";
import { Globe, ExternalLink, Copy, Check, Trash2 } from "lucide-react";
import {
  getSharedConversations,
  revokeShareLink,
  copyToClipboard,
  type ShareableConversation,
} from "@/app/lib/shareMockAPI";

export default function SharedConversationsList() {
  const [sharedConversations, setSharedConversations] = useState<
    ShareableConversation[]
  >([]);
  const [isLoading, setIsLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    loadSharedConversations();
  }, []);

  const loadSharedConversations = async () => {
    try {
      const conversations = await getSharedConversations();
      setSharedConversations(conversations);
    } catch (error) {
      console.error("Failed to load shared conversations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (url: string, id: string) => {
    const success = await copyToClipboard(url);
    if (success) {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const handleRevoke = async (conversationId: string) => {
    try {
      await revokeShareLink(conversationId);
      await loadSharedConversations();
    } catch (error) {
      console.error("Failed to revoke share link:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-gray-400 mt-3">Loading shared chats...</p>
      </div>
    );
  }

  if (sharedConversations.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="w-16 h-16 mx-auto bg-blue-900/20 rounded-2xl flex items-center justify-center mb-4">
          <Globe size={28} className="text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">
          No Shared Conversations
        </h3>
        <p className="text-sm text-gray-400">
          Share a conversation to see it here
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider flex items-center gap-2">
          <Globe size={16} />
          Shared Conversations ({sharedConversations.length})
        </h3>
      </div>

      {sharedConversations.map((conversation) => (
        <div
          key={conversation.id}
          className="p-4 rounded-xl bg-[#1a1f2e] border border-blue-500/20 hover:border-blue-500/40 transition-all group"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-white truncate mb-1">
                {conversation.name}
              </h4>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                <span>{conversation.message_count} messages</span>
                <span>•</span>
                <span>
                  {new Date(conversation.last_updated).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20 flex items-center gap-1.5">
              <Globe size={12} />
              Public
            </div>
          </div>

          {/* Share URL */}
          {conversation.share_url && (
            <div className="mb-3">
              <div className="flex items-center gap-2 px-3 py-2 bg-[#0f1419] border border-blue-500/20 rounded-lg">
                <ExternalLink size={14} className="text-blue-400 flex-shrink-0" />
                <span className="flex-1 text-xs font-mono text-gray-300 truncate">
                  {conversation.share_url}
                </span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() =>
                conversation.share_url &&
                handleCopy(conversation.share_url, conversation.id)
              }
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 transition-colors text-sm font-medium border border-blue-500/20"
            >
              {copiedId === conversation.id ? (
                <>
                  <Check size={14} />
                  Copied
                </>
              ) : (
                <>
                  <Copy size={14} />
                  Copy Link
                </>
              )}
            </button>
            <button
              onClick={() => handleRevoke(conversation.id)}
              className="px-3 py-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors border border-red-500/20"
              title="Revoke access"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
