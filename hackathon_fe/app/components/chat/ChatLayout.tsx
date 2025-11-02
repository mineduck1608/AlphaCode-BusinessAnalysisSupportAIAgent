"use client";

import React, { useEffect, useRef, useState } from "react";
import ChatSidebar from "./ChatSidebar";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import PreviewPanel from "./PreviewPanel";
import { useWebSocket } from "@/app/lib/hooks/useWebSocket";
import { getCurrentUser, mockLogout } from "@/app/lib/authMock";
import { getWebSocketUrl, STORAGE_KEYS, UI_CONFIG } from "@/app/lib/constants";
import { PanelRightOpen, PanelRightClose } from "lucide-react";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  time?: string;
};

const STORAGE_KEY = STORAGE_KEYS.CHAT_HISTORY;

export default function ChatLayout() {
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [{ id: "m0", role: "assistant", content: UI_CONFIG.DEFAULT_GREETING, time: new Date().toLocaleTimeString() }];
      return JSON.parse(raw) as Message[];
    } catch {
      return [{ id: "m0", role: "assistant", content: UI_CONFIG.DEFAULT_GREETING, time: new Date().toLocaleTimeString() }];
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // WebSocket connection to backend
  const websocket = useWebSocket({
    url: getWebSocketUrl(),
    autoConnect: true,
    onMessage: (wsMessage) => {
      // Khi nhận message từ WebSocket, thêm vào chat
      if (wsMessage.type === 'system') {
        // System messages (welcome, etc.)
        const botMsg: Message = {
          id: 'ws' + Date.now(),
          role: 'assistant',
          content: `[System] ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else if (wsMessage.type === 'text') {
        // Regular text response from agent
        const botMsg: Message = {
          id: 'ws' + Date.now(),
          role: 'assistant',
          content: wsMessage.content,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
        setIsLoading(false);
      }
    },
    onOpen: () => {
      console.log('✅ Connected to AI Agent');
    },
    onClose: () => {
      console.log('❌ Disconnected from AI Agent');
    },
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    // auto scroll
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  // handle sending via WebSocket
  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    // Add user message to UI
    const id = Date.now().toString();
    const userMsg: Message = { 
      id, 
      role: "user", 
      content: text, 
      time: new Date().toLocaleTimeString() 
    };
    setMessages((s) => [...s, userMsg]);
    setIsLoading(true);

    // Mock: Show preview for demo (remove this in production)
    if (text.toLowerCase().includes("analyze") || text.toLowerCase().includes("improve")) {
      setTimeout(() => {
        setPreviewData({
          summary: {
            added: 1,
            modified: 2,
            deleted: 0,
            totalLines: { added: 47, deleted: 12 },
          },
          files: [
            {
              filename: "requirements/user-authentication.md",
              status: "modified",
              original: `# User Authentication\n\nThe system shall allow users to login with username and password.\nThe password must be at least 6 characters.`,
              modified: `# User Authentication\n\nThe system SHALL allow users to authenticate using email and password.\nThe password MUST be at least 8 characters and contain:\n- At least one uppercase letter\n- At least one number\n- At least one special character`,
            },
          ],
          issues: [
            {
              type: "warning",
              message: "Password requirements strengthened - may affect existing users",
              file: "user-authentication.md",
              line: 4,
            },
          ],
          message: "I've improved the authentication requirements following IEEE 830 standards.",
        });
        setShowPreview(true);
      }, 1000);
    }

    // Send via WebSocket if connected
    if (websocket.connected) {
      const success = websocket.sendMessage(text);
      if (!success) {
        // Nếu gửi thất bại, fallback về mock
        setIsLoading(false);
        const errorMsg: Message = {
          id: 'err' + Date.now(),
          role: 'assistant',
          content: '❌ Failed to send message. WebSocket not connected.',
          time: new Date().toLocaleTimeString(),
        };
        setMessages((s) => [...s, errorMsg]);
      }
      // Response sẽ được nhận qua onMessage callback
    } else {
      // Fallback: không có WebSocket connection
      setIsLoading(false);
      const offlineMsg: Message = {
        id: 'off' + Date.now(),
        role: 'assistant',
        content: '⚠️ WebSocket disconnected. Please check backend server at ws://localhost:8000/ws/chat',
        time: new Date().toLocaleTimeString(),
      };
      setMessages((s) => [...s, offlineMsg]);
    }
  };

  const handleLogout = () => {
    mockLogout();
    location.href = "/login";
  };

  const user = getCurrentUser();

  return (
    <div className="flex h-full w-full bg-[#0f1419] text-white overflow-hidden">
      <ChatSidebar onLogout={handleLogout} userEmail={user?.email} />
      
      {/* Main Chat Area */}
      <div className={`flex flex-col flex-1 h-full overflow-hidden transition-all duration-300 ${
        showPreview ? (isPreviewExpanded ? 'w-[40%]' : 'w-[60%]') : 'w-full'
      }`}>
        {/* Header with Preview Toggle */}
        <div className="flex items-center border-b border-blue-900/20 bg-[#0a0e13] shadow-lg shrink-0">
          <div className="flex-1">
            <ChatHeader connected={websocket.connected} connecting={websocket.connecting} />
          </div>
          
          {/* Preview Toggle Button - Inside header, not overlapping */}
          <div className="px-4">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className={`p-2.5 rounded-lg transition-all ${
                showPreview
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-blue-900/20 text-gray-400 hover:bg-blue-900/40 hover:text-gray-200'
              }`}
              title={showPreview ? 'Hide preview' : 'Show preview'}
            >
              {showPreview ? (
                <PanelRightClose className="w-5 h-5" />
              ) : (
                <PanelRightOpen className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <ChatMessageList messages={messages} isLoading={isLoading} bottomRef={bottomRef} />
        </div>
        <div className="shrink-0">
          <ChatInput onSend={handleSend} disabled={!websocket.connected} />
        </div>
      </div>

      {/* Preview Panel */}
      {showPreview && (
        <div className={`h-full transition-all duration-300 ${
          isPreviewExpanded ? 'w-[60%]' : 'w-[40%]'
        }`}>
          <PreviewPanel
            data={previewData}
            onClose={() => setShowPreview(false)}
            isExpanded={isPreviewExpanded}
            onToggleExpand={() => setIsPreviewExpanded(!isPreviewExpanded)}
          />
        </div>
      )}
    </div>
  );
}