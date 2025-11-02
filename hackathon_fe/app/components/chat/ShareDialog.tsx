"use client";

import React, { useState } from "react";
import { X, Link2, Check, Copy, Globe, Lock, ExternalLink } from "lucide-react";
import {
  generateShareLink,
  revokeShareLink,
  copyToClipboard,
  type ShareableConversation,
} from "@/app/lib/shareMockAPI";

type ShareDialogProps = {
  conversation: ShareableConversation | null;
  isOpen: boolean;
  onClose: () => void;
};

export default function ShareDialog({
  conversation,
  isOpen,
  onClose,
}: ShareDialogProps) {
  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState(conversation?.share_url || "");
  const [copied, setCopied] = useState(false);

  if (!isOpen || !conversation) return null;

  const handleGenerateLink = async () => {
    setIsSharing(true);
    try {
      const link = await generateShareLink(conversation.id);
      setShareUrl(link.share_url);
    } catch (error) {
      console.error("Failed to generate share link:", error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleRevokeLink = async () => {
    setIsSharing(true);
    try {
      await revokeShareLink(conversation.id);
      setShareUrl("");
    } catch (error) {
      console.error("Failed to revoke share link:", error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleCopy = async () => {
    const success = await copyToClipboard(shareUrl);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isShared = conversation.is_shared || !!shareUrl;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1f2e] rounded-2xl shadow-2xl max-w-md w-full border border-blue-500/20">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-blue-900/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <Link2 size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Share Conversation</h2>
              <p className="text-sm text-gray-400 mt-0.5">
                Share this chat with others
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-blue-900/20 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Conversation Info */}
          <div className="p-4 rounded-xl bg-[#0f1419] border border-blue-500/10">
            <div className="flex items-start gap-3">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white truncate">
                  {conversation.name}
                </h3>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                  <span>{conversation.message_count} messages</span>
                  <span>Session: {conversation.session.slice(0, 12)}...</span>
                </div>
              </div>
              <div
                className={`px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${
                  isShared
                    ? "bg-green-500/10 text-green-400 border border-green-500/20"
                    : "bg-gray-500/10 text-gray-400 border border-gray-500/20"
                }`}
              >
                {isShared ? (
                  <>
                    <Globe size={12} />
                    Shared
                  </>
                ) : (
                  <>
                    <Lock size={12} />
                    Private
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Share Link Section */}
          {isShared ? (
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <Link2 size={14} />
                Share Link
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={shareUrl}
                  readOnly
                  className="flex-1 px-4 py-3 bg-[#0f1419] border border-blue-500/30 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-blue-500 transition-colors"
                />
                <button
                  onClick={handleCopy}
                  className={`px-4 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                    copied
                      ? "bg-green-500 text-white"
                      : "bg-blue-600 hover:bg-blue-500 text-white"
                  }`}
                >
                  {copied ? (
                    <>
                      <Check size={16} />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy size={16} />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-400 flex items-center gap-1.5">
                <ExternalLink size={12} />
                Anyone with this link can view this conversation
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-blue-900/10 border border-blue-500/20">
              <p className="text-sm text-gray-300 text-center">
                Generate a share link to let others view this conversation
              </p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex gap-3 p-6 border-t border-blue-900/20">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 rounded-lg font-medium text-gray-300 hover:bg-blue-900/20 transition-colors border border-blue-500/20"
          >
            Close
          </button>
          {isShared ? (
            <button
              onClick={handleRevokeLink}
              disabled={isSharing}
              className="flex-1 px-4 py-3 rounded-lg font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors border border-red-500/20 disabled:opacity-50"
            >
              {isSharing ? "Revoking..." : "Revoke Link"}
            </button>
          ) : (
            <button
              onClick={handleGenerateLink}
              disabled={isSharing}
              className="flex-1 px-4 py-3 rounded-lg font-medium bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50"
            >
              {isSharing ? "Generating..." : "Generate Link"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
