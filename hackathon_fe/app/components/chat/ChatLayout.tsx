"use client";

import React, { useEffect, useRef, useState } from "react";
import ChatSidebar from "./ChatSidebar";
import ChatHeader from "./ChatHeader";
import ChatMessageList from "./ChatMessageList";
import ChatInput from "./ChatInput";
import PreviewPanel from "./PreviewPanel";
import { analyzeStories, runPipeline } from '@/app/api/mcpApi';
import { useWebSocket } from "@/app/lib/hooks/useWebSocket";
import { getCurrentUserId, logout, getCurrentUserEmail } from "@/app/lib/authMock";
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
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const userEmail = getCurrentUserEmail();

  // WebSocket connection to backend
  const websocket = useWebSocket({
    url: getWebSocketUrl(),
    autoConnect: true,
    onMessage: (wsMessage) => {
      console.log('📨 Received WebSocket message:', wsMessage);
      
      // Handle typing indicator
      if (wsMessage.type === 'typing') {
        setIsAgentTyping(wsMessage.metadata?.isTyping || false);
        setIsLoading(false); // Stop loading when agent starts typing
        return;
      }
      
      // Handle system messages (welcome, etc.)
      if (wsMessage.type === 'system') {
        const botMsg: Message = {
          id: 'ws' + Date.now(),
          role: 'assistant',
          content: `[System] ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else if (wsMessage.type === 'text') {
        // Regular text response from agent
        setIsAgentTyping(false); // Stop typing indicator
        
        const botMsg: Message = {
          id: 'ws' + Date.now(),
          role: 'assistant',
          content: wsMessage.content,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botMsg]);
        setIsLoading(false);
      } else if (wsMessage.type === 'error') {
        // Handle error messages
        setIsAgentTyping(false);
        
        const errorMsg: Message = {
          id: 'ws' + Date.now(),
          role: 'assistant',
          content: `⚠️ Error: ${wsMessage.content}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
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

  // handle sending: if message contains "Story:" -> pipeline, else -> WebSocket chat
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

    // Check if message is requirements analysis (contains "Story:" or command)
    const isRequirementsAnalysis = text.toLowerCase().includes('story:') || 
                                   text.toLowerCase().startsWith('/analyze') ||
                                   text.toLowerCase().startsWith('/pipeline');
    
    if (isRequirementsAnalysis) {
      // Route to pipeline for requirements analysis
      try {
        // Use raw_text instead of stories to let collector extract multiple stories from input
        // Collector will automatically detect and split on "Story:" markers
        const resp = await runPipeline({ raw_text: text });
        const payload = resp || {};

      // Extract data from pipeline response
      // Handle nested analysis structure: analysis.analysis.summary or analysis.summary
      const analysisRaw = payload.analysis || {};
      const analysis = analysisRaw.analysis || analysisRaw; // Support both nested and flat structure
      const report = payload.report || {};
      const requirements = payload.requirements || [];
      const prioritized = payload.prioritized || {};
      const prioritizedRequirements = prioritized.requirements || requirements;

      // Build chat message: show analysis summary and report preview
      const parts: string[] = [];
      
      // Analysis summary
      if (analysis.summary) {
        const summary = analysis.summary;
        if (summary.total_stories) {
          parts.push(`📊 Phân tích hoàn tất: ${summary.total_stories} user story được xử lý`);
          if (summary.stories_with_issues > 0) {
            parts.push(`⚠️ ${summary.stories_with_issues} story có vấn đề (${summary.total_issues} vấn đề tổng cộng)`);
          } else {
            parts.push(`✅ Không phát hiện vấn đề`);
          }
        }
      }

      // Issues summary - check both analysis.issues and analysisRaw.issues
      const issues = Array.isArray(analysis.issues) ? analysis.issues : 
                     Array.isArray(analysisRaw.issues) ? analysisRaw.issues : [];
      if (issues.length > 0) {
        const criticalIssues = issues.filter((i: any) => i.type === 'conflict' || i.severity === 'high').length;
        if (criticalIssues > 0) {
          parts.push(`🔴 ${criticalIssues} vấn đề nghiêm trọng cần xử lý`);
        }
        parts.push(`📋 Tổng cộng ${issues.length} vấn đề đã được phát hiện. Xem chi tiết trong Preview Panel.`);
      }

      // Requirements summary
      if (prioritizedRequirements.length > 0) {
        const reqCount = prioritizedRequirements.length;
        parts.push(`📝 ${reqCount} requirement${reqCount > 1 ? 's' : ''} đã được xác định và ưu tiên hóa`);
        
        const topRequirements = prioritizedRequirements.slice(0, 3);
        if (topRequirements.length > 0 && topRequirements.length <= 3) {
          if (topRequirements.length === 1) {
            // Nếu chỉ có 1 requirement, hiển thị trực tiếp
            const req = topRequirements[0];
            const title = req.title || req.summary || req.id || `Requirement`;
            const priority = req.priority || req.priority_score || 'N/A';
            parts.push(`\n🎯 Requirement: ${title} (Priority: ${priority})`);
          } else {
            // Nếu có nhiều hơn 1, hiển thị top list
            parts.push(`\nTop ${topRequirements.length} requirements ưu tiên cao:`);
            topRequirements.forEach((req: any, idx: number) => {
              const title = req.title || req.summary || req.id || `Requirement ${idx + 1}`;
              const priority = req.priority || req.priority_score || 'N/A';
              parts.push(`  ${idx + 1}. ${title} (Priority: ${priority})`);
            });
          }
        }
      }

      // Report preview
      if (report.final_report_markdown) {
        parts.push(`📄 Báo cáo đã được tạo. Xem chi tiết trong Preview Panel bên phải.`);
      }

      if (!parts.length) {
        parts.push('✅ Pipeline đã chạy xong. Không có vấn đề nào được phát hiện.');
      }

      // Update preview data with full pipeline results
      setPreviewData({
        summary: {
          added: 0,
          modified: 0,
          deleted: 0,
          totalLines: { added: 0, deleted: 0 }
        },
        files: [],
        issues: issues.map((it: any) => ({
          type: (it.type === 'conflict' ? 'error' : it.severity === 'high' ? 'error' : it.severity === 'medium' ? 'warning' : 'info') as 'error' | 'warning' | 'info',
          message: it.description || it.message || JSON.stringify(it),
          file: it.file || it.story_id,
          line: it.line,
        })),
        requirements: requirements,
        prioritizedRequirements: prioritizedRequirements,
        analysis: analysisRaw, // Pass full analysis structure to preview
        report: report.final_report_markdown || '',
        actionItems: report.action_items || [],
        stakeholderQuestions: report.stakeholder_questions || [],
        mermaid: report.final_report_mermaid || '',
      });

        const botMsg: Message = {
          id: 'm' + Date.now(),
          role: 'assistant',
          content: parts.join('\n'),
          time: new Date().toLocaleTimeString(),
        };
        setMessages((s) => [...s, botMsg]);
      } catch (err: any) {
        const errMsg: Message = {
          id: 'err' + Date.now(),
          role: 'assistant',
          content: `❌ Lỗi khi gọi API phân tích: ${err?.message || String(err)}`,
          time: new Date().toLocaleTimeString(),
        };
        setMessages((s) => [...s, errMsg]);
      } finally {
        setIsLoading(false);
      }
    } else {
      // Route to WebSocket for chat with Gemini agent
      const sent = websocket.sendMessage(text);
      if (!sent) {
        // If WebSocket not connected, show error
        const errMsg: Message = {
          id: 'err' + Date.now(),
          role: 'assistant',
          content: '❌ Không thể kết nối đến AI Agent. Vui lòng kiểm tra kết nối WebSocket.',
          time: new Date().toLocaleTimeString(),
        };
        setMessages((s) => [...s, errMsg]);
        setIsLoading(false);
      }
      // Loading will be set to false when WebSocket message is received (handled in onMessage callback)
    }
  };

  const handleLogout = () => {
    logout();
    location.href = "/login";
  };

  const user = getCurrentUserId();

  return (
    <div className="flex h-full w-full bg-[#0f1419] text-white overflow-hidden">
      <ChatSidebar onLogout={handleLogout} userEmail={userEmail}  />

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
          <ChatMessageList 
            messages={messages} 
            isLoading={isLoading}
            isAgentTyping={isAgentTyping}
            bottomRef={bottomRef} 
          />
        </div>
        <div className="shrink-0">
          <ChatInput onSend={handleSend} disabled={false} />
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
