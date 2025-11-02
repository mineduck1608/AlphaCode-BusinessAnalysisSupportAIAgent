"use client";

import React from "react";
import DiffPreview from "./DiffPreview";
import ChangesSummary from "./ChangesSummary";
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
        <DiffPreview files={data.files} title="Modified Files" />
      </div>
    </div>
  );
}
