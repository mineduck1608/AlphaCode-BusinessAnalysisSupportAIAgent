"use client";

import React, { useState } from "react";
import { FileText, ChevronDown, ChevronRight, Copy, Check, Download } from "lucide-react";
import * as Diff from "diff";

interface FileChange {
  filename: string;
  language?: string;
  original: string;
  modified: string;
  status: "added" | "modified" | "deleted";
}

interface DiffPreviewProps {
  files: FileChange[];
  title?: string;
}

export default function DiffPreview({ files, title = "File Changes" }: DiffPreviewProps) {
  return (
    <div className="w-full my-4">
      {title && (
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-400" />
            {title}
          </h3>
        </div>
      )}
      <div className="space-y-3">
        {files.map((file, index) => (
          <FileChangeCard key={index} file={file} />
        ))}
      </div>
    </div>
  );
}

function FileChangeCard({ file }: { file: FileChange }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [viewMode, setViewMode] = useState<"unified" | "split">("unified");
  const [copied, setCopied] = useState(false);

  const diff = React.useMemo(() => {
    return Diff.diffLines(file.original, file.modified);
  }, [file.original, file.modified]);

  const stats = React.useMemo(() => {
    let added = 0;
    let removed = 0;
    diff.forEach((part) => {
      if (part.added) added += part.count || 0;
      if (part.removed) removed += part.count || 0;
    });
    return { added, removed };
  }, [diff]);

  const getStatusColor = () => {
    switch (file.status) {
      case "added":
        return "text-green-400 border-green-500/30 bg-green-500/5";
      case "deleted":
        return "text-red-400 border-red-500/30 bg-red-500/5";
      case "modified":
        return "text-blue-400 border-blue-500/30 bg-blue-500/5";
    }
  };

  const getStatusIcon = () => {
    switch (file.status) {
      case "added":
        return "+";
      case "deleted":
        return "-";
      case "modified":
        return "M";
    }
  };

  const copyContent = () => {
    navigator.clipboard.writeText(file.modified);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadFile = () => {
    const blob = new Blob([file.modified], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="border border-blue-900/30 rounded-xl overflow-hidden bg-[#1a1f2e]/50 backdrop-blur-sm shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
        <div className="flex items-center gap-3 flex-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-200 transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded border ${getStatusColor()}`}
            >
              {getStatusIcon()}
            </span>
            <span className="text-sm font-medium text-gray-200 font-mono">
              {file.filename}
            </span>
          </div>

          {file.status === "modified" && (
            <div className="flex items-center gap-3 text-xs text-gray-400 ml-3">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                +{stats.added}
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                -{stats.removed}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          {file.status === "modified" && (
            <div className="flex items-center gap-1 bg-[#0a0e13] rounded-lg p-1 border border-blue-900/30">
              <button
                onClick={() => setViewMode("unified")}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === "unified"
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:text-gray-200"
                }`}
              >
                Unified
              </button>
              <button
                onClick={() => setViewMode("split")}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  viewMode === "split"
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:text-gray-200"
                }`}
              >
                Split
              </button>
            </div>
          )}

          {/* Action Buttons */}
          <button
            onClick={copyContent}
            className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-blue-900/20 rounded transition-colors"
            title="Copy content"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-400" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={downloadFile}
            className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-blue-900/20 rounded transition-colors"
            title="Download file"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="max-h-[400px] overflow-auto">
          {file.status === "added" && (
            <AddedFileView content={file.modified} language={file.language} />
          )}
          {file.status === "deleted" && (
            <DeletedFileView content={file.original} language={file.language} />
          )}
          {file.status === "modified" && (
            <>
              {viewMode === "unified" ? (
                <UnifiedDiffView diff={diff} />
              ) : (
                <SplitDiffView
                  original={file.original}
                  modified={file.modified}
                />
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

// Added File View
function AddedFileView({ content, language }: { content: string; language?: string }) {
  const lines = content.split("\n");
  return (
    <div className="font-mono text-xs bg-green-500/5">
      {lines.map((line, index) => (
        <div
          key={index}
          className="flex hover:bg-green-500/10 transition-colors border-l-2 border-green-500"
        >
          <span className="px-3 py-1 text-gray-500 select-none bg-[#0a0e13]/50 border-r border-blue-900/20 min-w-[50px] text-right">
            {index + 1}
          </span>
          <span className="px-3 py-1 text-green-400 flex-1">
            <span className="text-green-500 mr-2">+</span>
            {line}
          </span>
        </div>
      ))}
    </div>
  );
}

// Deleted File View
function DeletedFileView({ content, language }: { content: string; language?: string }) {
  const lines = content.split("\n");
  return (
    <div className="font-mono text-xs bg-red-500/5">
      {lines.map((line, index) => (
        <div
          key={index}
          className="flex hover:bg-red-500/10 transition-colors border-l-2 border-red-500"
        >
          <span className="px-3 py-1 text-gray-500 select-none bg-[#0a0e13]/50 border-r border-blue-900/20 min-w-[50px] text-right">
            {index + 1}
          </span>
          <span className="px-3 py-1 text-red-400 flex-1">
            <span className="text-red-500 mr-2">-</span>
            {line}
          </span>
        </div>
      ))}
    </div>
  );
}

// Unified Diff View
function UnifiedDiffView({ diff }: { diff: Diff.Change[] }) {
  let lineNumber = 0;

  return (
    <div className="font-mono text-xs">
      {diff.map((part, partIndex) => {
        const lines = part.value.split("\n").filter((_, i, arr) => i < arr.length - 1 || part.value.endsWith("\n"));
        
        return lines.map((line, lineIndex) => {
          const currentLine = ++lineNumber;
          const bgColor = part.added
            ? "bg-green-500/10 border-l-2 border-green-500"
            : part.removed
            ? "bg-red-500/10 border-l-2 border-red-500"
            : "border-l-2 border-transparent";
          const textColor = part.added
            ? "text-green-400"
            : part.removed
            ? "text-red-400"
            : "text-gray-300";
          const prefix = part.added ? "+ " : part.removed ? "- " : "  ";
          const prefixColor = part.added ? "text-green-500" : part.removed ? "text-red-500" : "text-gray-600";

          return (
            <div
              key={`${partIndex}-${lineIndex}`}
              className={`flex hover:bg-blue-900/10 transition-colors ${bgColor}`}
            >
              <span className="px-3 py-1 text-gray-500 select-none bg-[#0a0e13]/50 border-r border-blue-900/20 min-w-[50px] text-right">
                {!part.added && !part.removed ? currentLine : ""}
              </span>
              <span className={`px-3 py-1 flex-1 ${textColor}`}>
                <span className={`${prefixColor} mr-2 select-none`}>{prefix}</span>
                {line}
              </span>
            </div>
          );
        });
      })}
    </div>
  );
}

// Split Diff View
function SplitDiffView({
  original,
  modified,
}: {
  original: string;
  modified: string;
}) {
  const originalLines = original.split("\n");
  const modifiedLines = modified.split("\n");
  const maxLines = Math.max(originalLines.length, modifiedLines.length);

  return (
    <div className="grid grid-cols-2 divide-x divide-blue-900/30">
      {/* Original */}
      <div className="font-mono text-xs">
        <div className="bg-[#0a0e13]/80 px-4 py-2 text-xs font-semibold text-gray-400 border-b border-blue-900/20 sticky top-0">
          Original
        </div>
        {originalLines.map((line, index) => (
          <div
            key={index}
            className="flex hover:bg-red-500/5 transition-colors"
          >
            <span className="px-3 py-1 text-gray-500 select-none bg-[#0a0e13]/30 border-r border-blue-900/20 min-w-[50px] text-right">
              {index + 1}
            </span>
            <span className="px-3 py-1 text-gray-300 flex-1">{line}</span>
          </div>
        ))}
      </div>

      {/* Modified */}
      <div className="font-mono text-xs">
        <div className="bg-[#0a0e13]/80 px-4 py-2 text-xs font-semibold text-gray-400 border-b border-blue-900/20 sticky top-0">
          Modified
        </div>
        {modifiedLines.map((line, index) => (
          <div
            key={index}
            className="flex hover:bg-green-500/5 transition-colors"
          >
            <span className="px-3 py-1 text-gray-500 select-none bg-[#0a0e13]/30 border-r border-blue-900/20 min-w-[50px] text-right">
              {index + 1}
            </span>
            <span className="px-3 py-1 text-gray-300 flex-1">{line}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
