"use client";

import React, { useEffect, useRef, useState } from "react";
import ChatSidebar from "./ChatSidebar";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import { useWebSocket } from "@/app/lib/hooks/useWebSocket";
import { getCurrentUser, mockLogout } from "@/app/lib/authMock";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  time?: string;
};

const STORAGE_KEY = "chatgpt_clone_history_v1";

export default function ChatLayout() {
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [{ id: "m0", role: "assistant", content: "Hi there 👋 How can I help you today?", time: new Date().toLocaleTimeString() }];
      return JSON.parse(raw) as Message[];
    } catch {
      return [{ id: "m0", role: "assistant", content: "Hi there 👋 How can I help you today?", time: new Date().toLocaleTimeString() }];
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // WebSocket connection to backend
  const websocket = useWebSocket({
    url: 'ws://localhost:8000/ws/chat',
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
      <div className="flex flex-col flex-1 h-full overflow-hidden">
        <ChatHeader connected={websocket.connected} connecting={websocket.connecting} />
        <div className="flex-1 overflow-y-auto">
          <ChatMessageList messages={messages} isLoading={isLoading} bottomRef={bottomRef} />
        </div>
        <div className="shrink-0">
          <ChatInput onSend={handleSend} disabled={!websocket.connected} />
        </div>
      </div>
    </div>
  );
}