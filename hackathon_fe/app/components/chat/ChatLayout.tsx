"use client";

import React, { useEffect, useRef, useState } from "react";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import { mockSendMessage } from "@/app/lib/chatMockAPI";

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

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    // auto scroll
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  // handle sending and typing animation
  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    const id = Date.now().toString();
    const userMsg: Message = { id, role: "user", content: text, time: new Date().toLocaleTimeString() };
    setMessages((s) => [...s, userMsg]);
    setIsLoading(true);

    const reply = await mockSendMessage(text); // full reply string

    // create a blank assistant message and animate
    const botId = "b" + Date.now().toString();
    setMessages((s) => [...s, { id: botId, role: "assistant", content: "", time: new Date().toLocaleTimeString() }]);

    // typing animation: reveal characters one by one
    let idx = 0;
    const interval = 24; // ms per char (tweak for speed)
    const timer = setInterval(() => {
      idx += 1;
      setMessages((prev) =>
        prev.map((m) => (m.id === botId ? { ...m, content: reply.slice(0, idx) } : m))
      );
      if (idx >= reply.length) {
        clearInterval(timer);
        setIsLoading(false);
      }
    }, interval);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-background border border-border rounded-xl overflow-hidden shadow-sm">
      <ChatHeader />
      <ChatMessageList messages={messages} isLoading={isLoading} bottomRef={bottomRef} />
      <ChatInput onSend={handleSend} />
    </div>
  );
}
