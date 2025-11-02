"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useParams } from "next/navigation";
import { Bot, User, Copy, Check, Lock, ExternalLink } from "lucide-react";
import { copyToClipboard } from "@/app/lib/shareMockAPI";

type SharedMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  time: string;
};

// Mock data for shared conversation
const mockSharedConversation = {
  id: "shared-123",
  name: "Project Ideas Discussion",
  created_at: "2025-11-01T10:30:00Z",
  message_count: 15,
  messages: [
    {
      id: "msg-1",
      role: "user" as const,
      content: "Can you help me brainstorm some project ideas for a hackathon?",
      time: "10:30 AM",
    },
    {
      id: "msg-2",
      role: "assistant" as const,
      content:
        "I'd be happy to help! Here are some innovative project ideas:\n\n1. **AI Code Review Assistant** - A tool that analyzes code and provides intelligent suggestions\n2. **Smart Energy Monitor** - IoT solution for tracking and optimizing energy usage\n3. **Mental Health Chatbot** - An empathetic AI companion for mental wellness\n4. **Collaborative Code Editor** - Real-time coding platform with AI assistance\n\nWhat type of technology are you most interested in working with?",
      time: "10:31 AM",
    },
    {
      id: "msg-3",
      role: "user" as const,
      content: "The AI Code Review Assistant sounds interesting! Can you elaborate more on that?",
      time: "10:32 AM",
    },
    {
      id: "msg-4",
      role: "assistant" as const,
      content:
        "Great choice! Here's a detailed breakdown:\n\n**AI Code Review Assistant**\n\n**Core Features:**\n- Automatic code analysis using LLMs\n- Security vulnerability detection\n- Code style and best practices suggestions\n- Performance optimization recommendations\n\n**Tech Stack:**\n- Frontend: Next.js + TypeScript\n- Backend: Python (FastAPI) + LangChain\n- AI: OpenAI GPT-4 or Claude\n- Database: PostgreSQL\n\n**Key Differentiators:**\n- Context-aware suggestions\n- Learning from team's coding patterns\n- Integration with GitHub/GitLab\n\nWould you like me to help you plan the architecture?",
      time: "10:33 AM",
    },
  ],
};

export default function SharedConversationView() {
  const params = useParams();
  const shareId = params?.shareId as string;
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 800);
  }, []);

  const handleCopyLink = async () => {
    const url = window.location.href;
    const success = await copyToClipboard(url);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-400">Loading shared conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-[#1a1f2e] border-b border-blue-500/20 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image
                src="/logo2.png"
                alt="AlphaCode Logo"
                width={32}
                height={32}
                className="w-8 h-8 object-contain"
              />
              <div>
                <h1 className="font-bold text-lg text-white">AlphaCode</h1>
                <p className="text-xs text-gray-400">Shared Conversation</p>
              </div>
            </div>
            <button
              onClick={handleCopyLink}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
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
                  Copy Link
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Conversation Info Banner */}
      <div className="bg-blue-900/10 border-b border-blue-500/20">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h2 className="text-xl font-bold text-white mb-1">
                {mockSharedConversation.name}
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span className="flex items-center gap-1.5">
                  <ExternalLink size={14} />
                  {mockSharedConversation.message_count} messages
                </span>
                <span>•</span>
                <span>
                  Shared on{" "}
                  {new Date(mockSharedConversation.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div className="px-3 py-1.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 text-xs font-medium flex items-center gap-1.5">
              <Lock size={12} />
              View Only
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          {mockSharedConversation.messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div className="w-10 h-10 rounded-full bg-linear-to-br from-purple-600 to-blue-600 flex items-center justify-center flex-shrink-0">
                  <Bot size={20} className="text-white" />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-2xl px-5 py-3 ${
                  message.role === "user"
                    ? "bg-linear-to-br from-blue-600 to-blue-500 text-white"
                    : "bg-[#1a1f2e] text-white border border-blue-500/20"
                }`}
              >
                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </div>
                <div
                  className={`text-xs mt-2 ${
                    message.role === "user" ? "text-blue-100" : "text-gray-400"
                  }`}
                >
                  {message.time}
                </div>
              </div>
              {message.role === "user" && (
                <div className="w-10 h-10 rounded-full bg-linear-to-br from-blue-600 to-blue-500 flex items-center justify-center flex-shrink-0">
                  <User size={20} className="text-white" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-[#1a1f2e] border-t border-blue-500/20">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center">
          <p className="text-gray-400 text-sm mb-3">
            This is a read-only view of a shared conversation
          </p>
          <a
            href="/chat"
            className="inline-flex items-center gap-2 px-6 py-3 bg-linear-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:from-blue-500 hover:to-blue-400 transition-all font-medium shadow-lg shadow-blue-500/20"
          >
            Start Your Own Conversation
          </a>
        </div>
      </footer>
    </div>
  );
}
