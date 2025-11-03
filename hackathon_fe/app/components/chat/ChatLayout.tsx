"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import ChatSidebar from "./ChatSidebar";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import PreviewPanel from "./PreviewPanel";
import { analyzeStories, runPipeline } from '@/app/api/mcpApi';
import { useWebSocket } from "@/app/lib/hooks/useWebSocket";
import { getCurrentUserId, logout, getCurrentUserEmail } from "@/app/lib/authMock";
import { getWebSocketUrl, UI_CONFIG } from "@/app/lib/constants";
import { PanelRightOpen, PanelRightClose, MessageSquare, Plus } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { messageApi } from "@/app/api/messageApi";
import type { Message as APIMessage } from "@/app/types/message";

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
  const [hasMoreMessages, setHasMoreMessages] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [messagePage, setMessagePage] = useState(0);

  const [isLoading, setIsLoading] = useState(false);
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const messageContainerRef = useRef<HTMLDivElement | null>(null);
  const userEmail = getCurrentUserEmail();

  const MESSAGES_PER_PAGE = 50;

  // WebSocket connection
  const websocket = useWebSocket({
    url: getWebSocketUrl(),
    autoConnect: true,

    onMessage: (wsMessage) => {
      console.log("📨 Received WebSocket message:", wsMessage);

      // --- Handle typing indicator ---
      if (wsMessage.type === "typing") {
        let actualMetadata = wsMessage.metadata || {};
        if (typeof wsMessage.content === "string" && wsMessage.content.trim().startsWith("{")) {
          try {
            const parsed = JSON.parse(wsMessage.content);
            actualMetadata = parsed.metadata || actualMetadata;
          } catch (e) {
            console.warn("⚠️ Failed to parse typing content:", e);
          }
        }

        const isTyping = actualMetadata.is_typing === true || actualMetadata.isTyping === true;
        console.log("⌨️ Typing indicator:", isTyping);
        setIsAgentTyping(isTyping);
        if (isTyping) setIsLoading(false);
        return;
      }

      // --- System message ---
      if (wsMessage.type === "system") {
        // Bỏ qua welcome message và các system messages không cần thiết
        const contentStr = String(wsMessage.content || "");
        if (contentStr.includes("Welcome!") || contentStr.includes("session ID")) {
          return;
        }
        
        // Chỉ hiển thị system messages quan trọng (nếu cần)
        const botMsg: Message = {
          id: "ws-" + Date.now(),
          role: "assistant",
          content: `[System] ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
        return;
      }

      // --- Regular message ---
      if (wsMessage.type === "text") {
        setIsAgentTyping(false);
        const contentStr = String(wsMessage.content || "");

        const looksLikeMarkdown =
          /```|^#{1,6}\s|^\s*[-*]\s|\n#{1,6}\s|\*\*|\n\n/m.test(contentStr) ||
          contentStr.length > 300;

        if (looksLikeMarkdown) {
          setPreviewData({
            summary: { added: 0, modified: 0, deleted: 0, totalLines: { added: 0, deleted: 0 } },
            files: [],
            report: contentStr,
            message: "AI response preview",
          });
          setShowPreview(true);
        }

        const botMsg: Message = {
          id: "ws-" + Date.now(),
          role: "assistant",
          content: contentStr,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
        setIsLoading(false);

        // Lưu message từ agent vào database
        if (currentConversationId) {
          messageApi.createAgentMessage({
            conversation_id: currentConversationId,
            agent_id: "1", // TODO: Get actual agent_id from WebSocket or context
            content: contentStr,
            role: 1 // assistant role
          }).then(() => {
            console.log("✅ Agent message saved to database");
          }).catch((error) => {
            console.error("❌ Failed to save agent message:", error);
          });
        }
        return;
      }

      // --- Error message ---
      if (wsMessage.type === "error") {
        setIsAgentTyping(false);
        const errorMsg: Message = {
          id: "ws-" + Date.now(),
          role: "assistant",
          content: `⚠️ Error: ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
        setIsLoading(false);
      }
    },

    onOpen: () => console.log("✅ Connected to AI Agent"),
    onClose: () => console.log("❌ Disconnected from AI Agent"),
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
        setLoadingMessages(true);
        // Clear messages and reset pagination
        setMessages([]);
        setMessagePage(0);
        setHasMoreMessages(true);
        
        const apiMessages = await messageApi.getByConversationId(currentConversationId, 0, MESSAGES_PER_PAGE);
        
        if (apiMessages.length < MESSAGES_PER_PAGE) {
          setHasMoreMessages(false);
        }
        
        // Convert API messages to UI messages (reverse to show oldest first)
        const uiMessages: Message[] = apiMessages.reverse().map((msg: APIMessage) => ({
          id: msg.id.toString(),
          role: msg.user_id ? 'user' : 'assistant',
          content: msg.content,
          time: new Date(msg.created_at).toLocaleTimeString(),
        }));
        
        setMessages(uiMessages);
      } catch (error) {
        console.error('Failed to load messages:', error);
        
        // If conversation has no messages, show welcome message
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
          setHasMoreMessages(false);
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
        setLoadingMessages(false);
      }
    };

    loadMessages();
  }, [currentConversationId]);

  // Load more messages when scrolling to top
  const loadMoreMessages = useCallback(async () => {
    if (!currentConversationId || loadingMessages || !hasMoreMessages) return;

    setLoadingMessages(true);
    try {
      const nextPage = messagePage + 1;
      const skip = nextPage * MESSAGES_PER_PAGE;
      const apiMessages = await messageApi.getByConversationId(currentConversationId, skip, MESSAGES_PER_PAGE);
      
      if (apiMessages.length < MESSAGES_PER_PAGE) {
        setHasMoreMessages(false);
      }
      
      if (apiMessages.length > 0) {
        const uiMessages: Message[] = apiMessages.reverse().map((msg: APIMessage) => ({
          id: msg.id.toString(),
          role: msg.user_id ? 'user' : 'assistant',
          content: msg.content,
          time: new Date(msg.created_at).toLocaleTimeString(),
        }));
        
        // Prepend older messages to the beginning
        setMessages(prev => [...uiMessages, ...prev]);
        setMessagePage(nextPage);
      }
    } catch (error) {
      console.error('Failed to load more messages:', error);
    } finally {
      setLoadingMessages(false);
    }
  }, [currentConversationId, loadingMessages, hasMoreMessages, messagePage, MESSAGES_PER_PAGE]);

  // Auto scroll khi có messages mới
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ------------------- Handle Send -------------------
  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    // Kiểm tra phải có conversation
    if (!currentConversationId) {
      alert("Please select or create a conversation first!");
      return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
      alert("Please login first!");
      return;
    }

    const id = "u-" + Date.now();
    const userMsg: Message = { id, role: "user", content: text, time: new Date().toLocaleTimeString() };
    setMessages((s) => [...s, userMsg]);
    setIsLoading(true);
    setIsAgentTyping(true);

    console.log("🟢 Started typing indicator");

    // Lưu message vào database với đúng user_id và conversation_id
    messageApi.createUserMessage({
      conversation_id: currentConversationId,
      user_id: userId.toString(),
      content: text,
      role: 0 // user role
    }).then(() => {
      console.log("✅ User message saved to database");
    }).catch((error) => {
      console.error("❌ Failed to save user message:", error);
    });

    const isPipelineCommand =
      text.toLowerCase().includes("story:") ||
      text.toLowerCase().startsWith("/analyze") ||
      text.toLowerCase().startsWith("/pipeline");

    if (isPipelineCommand) {
      try {
        const resp = await runPipeline({ raw_text: text });
        const payload = resp || {};

        const analysisRaw = payload.analysis || {};
        const analysis = analysisRaw.analysis || analysisRaw;
        const report = payload.report || {};
        const requirements = payload.requirements || [];
        const prioritized = payload.prioritized || {};
        const prioritizedRequirements = prioritized.requirements || requirements;
        const issues =
          Array.isArray(analysis.issues) || Array.isArray(analysisRaw.issues)
            ? analysis.issues || analysisRaw.issues
            : [];

        const parts: string[] = [];

        if (analysis.summary) {
          const summary = analysis.summary;
          if (summary.total_stories)
            parts.push(`📊 Đã phân tích ${summary.total_stories} user story.`);
          if (summary.stories_with_issues)
            parts.push(`⚠️ ${summary.stories_with_issues} story có vấn đề.`);
        }

        if (issues.length > 0)
          parts.push(`📋 Tổng cộng ${issues.length} vấn đề đã được phát hiện.`);

        if (prioritizedRequirements.length > 0) {
          const topRequirements = prioritizedRequirements.slice(0, 3);
          parts.push(`📝 ${prioritizedRequirements.length} requirements đã được xác định.`);
          topRequirements.forEach((req: any, idx: number) => {
            parts.push(`  ${idx + 1}. ${req.title || req.summary} (Priority: ${req.priority || "N/A"})`);
          });
        }

        if (report.final_report_markdown)
          parts.push(`📄 Báo cáo chi tiết hiển thị trong Preview Panel.`);

        setPreviewData({
          issues,
          requirements,
          prioritizedRequirements,
          analysis: analysisRaw,
          report: report.final_report_markdown || "",
          summary: { added: 0, modified: 0, deleted: 0, totalLines: { added: 0, deleted: 0 } },
          files: [],
        });

        setMessages((s) => [
          ...s,
          {
            id: "a-" + Date.now(),
            role: "assistant",
            content: parts.join("\n"),
            time: new Date().toLocaleTimeString(),
          },
        ]);
      } catch (err: any) {
        setMessages((s) => [
          ...s,
          {
            id: "err-" + Date.now(),
            role: "assistant",
            content: `❌ Lỗi khi gọi API phân tích: ${err.message || String(err)}`,
            time: new Date().toLocaleTimeString(),
          },
        ]);
      } finally {
        setIsLoading(false);
        setIsAgentTyping(false);
      }
    } else {
      const sent = websocket.sendMessage(text);
      if (!sent) {
        setMessages((s) => [
          ...s,
          {
            id: "err-" + Date.now(),
            role: "assistant",
            content: "❌ Không thể kết nối tới AI Agent.",
            time: new Date().toLocaleTimeString(),
          },
        ]);
        setIsLoading(false);
        setIsAgentTyping(false);
      }
    }
  };

  const handleLogout = () => {
    logout();
    location.href = "/login";
  };

  const user = getCurrentUserId();

  return (
    <div className="flex h-full w-full bg-background text-white overflow-hidden">
      <ChatSidebar onLogout={handleLogout} userEmail={userEmail} />

      {/* --- Main Chat --- */}
      <div
        className={`flex flex-col flex-1 h-full overflow-hidden transition-all duration-300 ${
          showPreview ? (isPreviewExpanded ? "w-[60%]" : "w-[65%]") : "w-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center border-b border-blue-900/20 bg-[#0a0e13] shadow-lg shrink-0">
          <div className="flex-1">
            <ChatHeader connected={websocket.connected} connecting={websocket.connecting} />
          </div>

          {/* Preview toggle */}
          <div className="px-4">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className={`p-2.5 rounded-lg transition-all ${
                showPreview
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-blue-900/20 text-gray-400 hover:bg-blue-900/40 hover:text-gray-200"
              }`}
              title={showPreview ? "Hide preview" : "Show preview"}
            >
              {showPreview ? <PanelRightClose className="w-5 h-5" /> : <PanelRightOpen className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {!currentConversationId ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-8">
              <div className="max-w-2xl">
                <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-blue-600/20 flex items-center justify-center">
                  <MessageSquare className="w-12 h-12 text-blue-400" />
                </div>
                <h2 className="text-3xl font-bold mb-4 bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Welcome to AlphaCode Chat
                </h2>
                <p className="text-gray-400 text-lg mb-8">
                  Select a conversation from the sidebar or create a new one to start chatting with AI
                </p>
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={() => {
                      const newChatBtn = document.querySelector('[data-new-chat]') as HTMLButtonElement;
                      newChatBtn?.click();
                    }}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
                  >
                    <Plus className="w-5 h-5" />
                    New Conversation
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <ChatMessageList
              messages={messages}
              isLoading={isLoading}
              isAgentTyping={isAgentTyping}
              bottomRef={bottomRef}
              loadingMore={loadingMessages}
              hasMore={hasMoreMessages}
              onLoadMore={loadMoreMessages}
            />
          )}
        </div>

        <div className="shrink-0">
          <ChatInput onSend={handleSend} disabled={false} />
        </div>
      </div>

      {/* --- Preview Panel --- */}
      {showPreview && (
        <div
          className={`h-full transition-all duration-300 ${
            isPreviewExpanded ? "w-[40%]" : "w-[35%]"
          }`}
        >
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
