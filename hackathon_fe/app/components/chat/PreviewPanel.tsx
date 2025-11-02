"use client";

import React from "react";
import DiffPreview from "./DiffPreview";
import ChangesSummary from "./ChangesSummary";

// Enhanced markdown -> HTML converter with table support
function simpleMarkdownToHtml(md: string) {
  if (!md) return "";
  
  // Split into lines for better processing
  const lines = md.split('\n');
  const result: string[] = [];
  let inCodeBlock = false;
  let codeBlockContent: string[] = [];
  let inTable = false;
  let tableRows: string[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Handle code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // Close code block
        result.push(`<pre class="markdown-code">${codeBlockContent.join('\n').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`);
        codeBlockContent = [];
        inCodeBlock = false;
      } else {
        // Start code block
        inCodeBlock = true;
      }
      continue;
    }
    
    if (inCodeBlock) {
      codeBlockContent.push(line);
      continue;
    }
    
    // Handle tables - look ahead to detect separator
    const isTableRow = line.trim().startsWith('|') && line.trim().endsWith('|');
    const isTableSeparator = isTableRow && /^\s*\|[\s\|\-:]+\|\s*$/.test(line);
    
    if (isTableRow && !isTableSeparator) {
      // Check if next line is a separator (which means this is a header)
      const nextLine = i + 1 < lines.length ? lines[i + 1] : '';
      const nextIsSeparator = nextLine.trim().startsWith('|') && /^\s*\|[\s\|\-:]+\|\s*$/.test(nextLine);
      const isHeaderRow = nextIsSeparator;
      
      if (!inTable) {
        inTable = true;
        tableRows = [];
      }
      
      // Parse table row
      const cells = line.split('|').map(c => c.trim()).filter(c => c);
      const formattedCells = cells.map(cell => {
        // Escape HTML but preserve inline formatting
        let formatted = cell
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
        
        // Apply inline formatting
        formatted = formatted
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/`([^`]+)`/g, '<code>$1</code>');
        
        const tag = isHeaderRow ? 'th' : 'td';
        return `<${tag}>${formatted}</${tag}>`;
      });
      
      tableRows.push(`<tr>${formattedCells.join('')}</tr>`);
      
      // If this was a header and we just processed the separator on next iteration, skip it
      // But we'll handle that in the next iteration
      
      continue;
    } else if (isTableSeparator) {
      // Skip separator rows
      continue;
    } else if (inTable) {
      // Close table if we exit table mode
      if (tableRows.length > 0) {
        const headerRow = tableRows.find(row => row.includes('<th>'));
        const bodyRows = tableRows.filter(row => !row.includes('<th>'));
        
        if (headerRow) {
          result.push(`<table class="markdown-table border-collapse border border-blue-900/30 w-full my-4"><thead>${headerRow}</thead><tbody>${bodyRows.join('')}</tbody></table>`);
        } else {
          result.push(`<table class="markdown-table border-collapse border border-blue-900/30 w-full my-4"><tbody>${tableRows.join('')}</tbody></table>`);
        }
      }
      tableRows = [];
      inTable = false;
    }
    
    // Skip empty lines (will be handled by paragraph logic)
    if (line.trim() === '') {
      result.push('');
      continue;
    }
    
    // Headings
    if (line.startsWith('### ')) {
      result.push(`<h3 class="text-lg font-semibold text-gray-200 mt-4 mb-2">${line.substring(4).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</h3>`);
      continue;
    }
    if (line.startsWith('## ')) {
      result.push(`<h2 class="text-xl font-semibold text-gray-200 mt-5 mb-3">${line.substring(3).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</h2>`);
      continue;
    }
    if (line.startsWith('# ')) {
      result.push(`<h1 class="text-2xl font-bold text-gray-200 mt-6 mb-4">${line.substring(2).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</h1>`);
      continue;
    }
    
    // Inline code
    let processedLine = line.replace(/`([^`]+)`/g, '<code class="markdown-inline bg-blue-900/20 px-1 py-0.5 rounded text-sm">$1</code>');
    
    // Bold and italic
    processedLine = processedLine.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
    processedLine = processedLine.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
    
    // Escape HTML
    processedLine = processedLine.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    // Unescape our formatting tags
    processedLine = processedLine.replace(/&lt;(code|strong|em)/g, '<$1');
    processedLine = processedLine.replace(/\/(code|strong|em)&gt;/g, '</$1>');
    
    // Paragraph
    result.push(`<p class="text-gray-300 mb-2 leading-relaxed">${processedLine}</p>`);
  }
  
  // Close any remaining code block or table
  if (inCodeBlock && codeBlockContent.length > 0) {
    result.push(`<pre class="markdown-code">${codeBlockContent.join('\n').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`);
  }
  if (inTable && tableRows.length > 0) {
    const headerRow = tableRows.find(row => row.includes('<th>'));
    const bodyRows = tableRows.filter(row => !row.includes('<th>'));
    
    if (headerRow) {
      result.push(`<table class="markdown-table border-collapse border border-blue-900/30 w-full my-4"><thead>${headerRow}</thead><tbody>${bodyRows.join('')}</tbody></table>`);
    } else {
      result.push(`<table class="markdown-table border-collapse border border-blue-900/30 w-full my-4"><tbody>${tableRows.join('')}</tbody></table>`);
    }
  }
  
  // Process lists
  let output = result.join('\n');
  
  // Ordered lists
  output = output.replace(/(<p>)?(\d+\.\s+.*?)(<\/p>)?/g, (match, p1, content) => {
    const listItems: string[] = [];
    const lines = output.split('\n');
    for (const line of lines) {
      if (/^\d+\.\s+/.test(line)) {
        const item = line.replace(/^\d+\.\s+/, '').replace(/<p>|<\/p>/g, '');
        listItems.push(`<li>${item}</li>`);
      }
    }
    return listItems.length > 0 ? `<ol class="list-decimal list-inside my-2 space-y-1">${listItems.join('')}</ol>` : match;
  });
  
  // Unordered lists (better handling)
  output = output.replace(/(<p>)?(-\s+.*?)(<\/p>)?/g, (match) => {
    const item = match.replace(/<p>|<\/p>/g, '').replace(/^-\s+/, '');
    return `<li class="ml-4">${item}</li>`;
  });
  
  // Wrap consecutive <li> into <ul>
  output = output.replace(/(<li[^>]*>[\s\S]*?<\/li>)([\s\S]*?<li[^>]*>[\s\S]*?<\/li>)+/g, (match) => {
    return `<ul class="list-disc list-inside my-2 space-y-1 ml-4">${match}</ul>`;
  });
  
  return output;
}
import { X, Maximize2, Minimize2 } from "lucide-react";

interface FileChange {
  filename: string;
  language?: string;
  original: string;
  modified: string;
  status: "added" | "modified" | "deleted";
}

interface PreviewData {
  summary: {
    added: number;
    modified: number;
    deleted: number;
    totalLines: {
      added: number;
      deleted: number;
    };
  };
  files: FileChange[];
  issues?: Array<{
    type: "error" | "warning" | "info";
    message: string;
    file?: string;
    line?: number;
  }>;
  message?: string;
  report?: string;
  // Pipeline data
  requirements?: any[];
  prioritizedRequirements?: any[];
  analysis?: any;
  actionItems?: Array<{ who?: string; action: string; due?: string | null }>;
  stakeholderQuestions?: string[];
  mermaid?: string;
}

interface PreviewPanelProps {
  data: PreviewData | null;
  onClose: () => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export default function PreviewPanel({
  data,
  onClose,
  isExpanded = false,
  onToggleExpand,
}: PreviewPanelProps) {
  if (!data) {
    return (
      <div className="h-full flex items-center justify-center bg-[#0a0e13] border-l border-blue-900/20">
        <div className="text-center text-gray-500 px-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-blue-900/10 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p className="text-sm mb-1">No preview available</p>
          <p className="text-xs">
            File changes will appear here after AI analysis
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#0a0e13] border-l border-blue-900/20">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-blue-900/20 bg-[#0f1419]/50 backdrop-blur-sm shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <h3 className="text-sm font-semibold text-gray-200">Changes Preview</h3>
        </div>
        <div className="flex items-center gap-1">
          {onToggleExpand && (
            <button
              onClick={onToggleExpand}
              className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-blue-900/20 rounded transition-colors"
              title={isExpanded ? "Normal view" : "Expand panel"}
            >
              {isExpanded ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-blue-900/20 rounded transition-colors"
            title="Close preview"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <ChangesSummary
          summary={data.summary}
          issues={data.issues}
          message={data.message}
        />

        {/* Prioritized Requirements */}
        {data.prioritizedRequirements && data.prioritizedRequirements.length > 0 && (
          <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
              <h4 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Prioritized Requirements ({data.prioritizedRequirements.length})
              </h4>
            </div>
            <div className="divide-y divide-blue-900/20 max-h-[300px] overflow-y-auto">
              {data.prioritizedRequirements.slice(0, 10).map((req: any, idx: number) => (
                <div key={idx} className="px-4 py-3 hover:bg-blue-900/10 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono text-blue-400">#{idx + 1}</span>
                        <span className="text-sm font-medium text-gray-200">
                          {req.title || req.summary || req.id || `Requirement ${idx + 1}`}
                        </span>
                      </div>
                      {req.description && (
                        <p className="text-xs text-gray-400 mt-1">{req.description}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        {req.priority && (
                          <span className="px-2 py-0.5 bg-blue-900/30 rounded">
                            Priority: {req.priority}
                          </span>
                        )}
                        {req.priority_score && (
                          <span className="px-2 py-0.5 bg-purple-900/30 rounded">
                            Score: {req.priority_score}
                          </span>
                        )}
                        {req.recommended_action && (
                          <span className="px-2 py-0.5 bg-green-900/30 rounded">
                            {req.recommended_action}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Items */}
        {data.actionItems && data.actionItems.length > 0 && (
          <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
              <h4 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Action Items ({data.actionItems.length})
              </h4>
            </div>
            <div className="divide-y divide-blue-900/20">
              {data.actionItems.map((item: any, idx: number) => (
                <div key={idx} className="px-4 py-3 hover:bg-green-900/10 transition-colors">
                  <div className="flex items-start gap-2">
                    <span className="text-xs text-green-400 mt-0.5">•</span>
                    <div className="flex-1">
                      <p className="text-sm text-gray-200">{item.action}</p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        {item.who && <span>👤 {item.who}</span>}
                        {item.due && <span>📅 {item.due}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stakeholder Questions */}
        {data.stakeholderQuestions && data.stakeholderQuestions.length > 0 && (
          <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
              <h4 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                <svg className="w-4 h-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Stakeholder Questions ({data.stakeholderQuestions.length})
              </h4>
            </div>
            <div className="divide-y divide-blue-900/20">
              {data.stakeholderQuestions.map((q: string, idx: number) => (
                <div key={idx} className="px-4 py-3 hover:bg-yellow-900/10 transition-colors">
                  <p className="text-sm text-gray-200">❓ {q}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mermaid Diagram */}
        {data.mermaid && (
          <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
              <h4 className="text-sm font-semibold text-gray-200">Requirements Graph</h4>
            </div>
            <div className="p-4">
              <pre className="text-xs text-gray-300 font-mono bg-[#0a0e13] p-3 rounded overflow-x-auto">
                {data.mermaid}
              </pre>
            </div>
          </div>
        )}

        {/* Report (Markdown) */}
        {data.report && (
          <div className="pt-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-gray-200">Full Report</h4>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    const reportText = data.report || "";
                    const blob = new Blob([reportText], { type: 'text/markdown;charset=utf-8' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'report.md';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);
                  }}
                  className="text-xs px-2 py-1 bg-blue-700/30 hover:bg-blue-700/50 rounded transition-colors"
                >
                  Download .md
                </button>
              </div>
            </div>

            <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl p-4 overflow-x-auto">
              <div 
                className="text-gray-100 markdown-content"
                dangerouslySetInnerHTML={{ __html: simpleMarkdownToHtml(data.report) }}
                style={{
                  maxHeight: '70vh',
                  overflowY: 'auto',
                }}
              />
              <style jsx>{`
                .markdown-content :global(table) {
                  width: 100%;
                  border-collapse: collapse;
                  margin: 1rem 0;
                }
                .markdown-content :global(table th),
                .markdown-content :global(table td) {
                  border: 1px solid rgba(59, 130, 246, 0.3);
                  padding: 0.5rem;
                  text-align: left;
                }
                .markdown-content :global(table th) {
                  background-color: rgba(59, 130, 246, 0.1);
                  font-weight: 600;
                }
                .markdown-content :global(table tr:nth-child(even)) {
                  background-color: rgba(59, 130, 246, 0.05);
                }
                .markdown-content :global(pre) {
                  background-color: rgba(10, 14, 19, 0.8);
                  padding: 1rem;
                  border-radius: 0.5rem;
                  overflow-x: auto;
                  margin: 1rem 0;
                }
                .markdown-content :global(code) {
                  font-family: 'Courier New', monospace;
                }
              `}</style>
            </div>
          </div>
        )}

        {/* Legacy: File Changes (if present) */}
        {data.files && data.files.length > 0 && (
          <DiffPreview files={data.files} title="Modified Files" />
        )}
      </div>
    </div>
  );
}
