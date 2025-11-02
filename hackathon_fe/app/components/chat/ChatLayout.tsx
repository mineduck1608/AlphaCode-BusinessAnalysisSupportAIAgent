"use client";

import React, { useEffect, useRef, useState } from "react";
import ChatSidebar from "./ChatSidebar";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import PreviewPanel from "./PreviewPanel";
import { useWebSocket } from "@/app/lib/hooks/useWebSocket";
import { getCurrentUserId, logout } from "@/app/lib/authMock";
import { getWebSocketUrl, UI_CONFIG } from "@/app/lib/constants";
import { PanelRightOpen, PanelRightClose } from "lucide-react";
import { messageApi } from "@/app/api/messageApi";
import type { Message as APIMessage } from "@/app/types/message";
import { useSearchParams } from "next/navigation";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  time?: string;
};

export default function ChatLayout() {
  const searchParams = useSearchParams();
  const conversationIdFromUrl = searchParams.get('id');
  
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversationIdFromUrl);
  const [messages, setMessages] = useState<Message[]>([]);
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
          id: `ws-system-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: `[System] ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else if (wsMessage.type === 'text') {
        // Regular text response from agent
        const botMsg: Message = {
          id: `ws-text-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
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

  // Sync conversation ID từ URL
  useEffect(() => {
    if (conversationIdFromUrl && conversationIdFromUrl !== currentConversationId) {
      setCurrentConversationId(conversationIdFromUrl);
    }
  }, [conversationIdFromUrl, currentConversationId]);

  // Load messages khi conversation ID thay đổi
  useEffect(() => {
    const loadMessages = async () => {
      if (!currentConversationId) {
        // Không có conversation, hiển thị welcome message
        setMessages([{ 
          id: "welcome", 
          role: "assistant", 
          content: UI_CONFIG.DEFAULT_GREETING, 
          time: new Date().toLocaleTimeString() 
        }]);
        return;
      }
      
      try {
        setIsLoading(true);
        // Clear messages cũ trước khi load
        setMessages([]);
        
        const apiMessages = await messageApi.getByConversationId(currentConversationId);
        
        // Convert API messages to UI messages
        const uiMessages: Message[] = apiMessages.map((msg: APIMessage) => ({
          id: msg.id.toString(),
          role: msg.user_id ? 'user' : 'assistant', // Nếu có user_id thì là user message
          content: msg.content,
          time: new Date(msg.created_at).toLocaleTimeString(),
        }));
        
        setMessages(uiMessages);
      } catch (error) {
        console.error('Failed to load messages:', error);
        
        // Nếu conversation chưa có messages, hiển thị welcome message
        const errorMessage = error instanceof Error ? error.message : '';
        const errorDetail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        
        if (errorDetail === "No messages found for this conversation" || 
            errorMessage.includes("No messages found")) {
          setMessages([{ 
            id: "welcome", 
            role: "assistant", 
            content: "👋 Start a new conversation! Send your first message below.", 
            time: new Date().toLocaleTimeString() 
          }]);
        } else {
          // Lỗi thật sự thì mới hiển thị error message
          setMessages([{ 
            id: "error", 
            role: "assistant", 
            content: "❌ Failed to load conversation messages.", 
            time: new Date().toLocaleTimeString() 
          }]);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadMessages();
  }, [currentConversationId]);

  // Auto scroll khi có messages mới
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  // handle sending via WebSocket
  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    // Add user message to UI with unique ID
    const id = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
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
          id: `err-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
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
        id: `off-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: 'assistant',
        content: '⚠️ WebSocket disconnected. Please check backend server at ws://localhost:8000/ws/chat',
        time: new Date().toLocaleTimeString(),
      };
      setMessages((s) => [...s, offlineMsg]);
    }
  };

  const handleLogout = () => {
    logout();
    location.href = "/login";
  };

  const user = getCurrentUserId();

  // Function để set conversation hiện tại
  const handleSelectConversation = (conversationId: string) => {
    setCurrentConversationId(conversationId);
  };

  return (
    <div className="flex h-full w-full bg-background text-white overflow-hidden">
      <ChatSidebar onLogout={handleLogout} />
      
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