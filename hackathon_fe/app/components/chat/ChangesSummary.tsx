"use client";

import React from "react";
import { FileText, FilePlus, FileX, FileEdit, AlertCircle, CheckCircle2, Info } from "lucide-react";

interface FileChangeSummary {
  added: number;
  modified: number;
  deleted: number;
  totalLines: {
    added: number;
    deleted: number;
  };
}

interface Issue {
  type: "error" | "warning" | "info";
  message: string;
  file?: string;
  line?: number;
}

interface ChangesSummaryProps {
  summary: FileChangeSummary;
  issues?: Issue[];
  message?: string;
}

export default function ChangesSummary({ summary, issues = [], message }: ChangesSummaryProps) {
  const totalFiles = summary.added + summary.modified + summary.deleted;

  return (
    <div className="space-y-3 my-4">
      {/* Message */}
      {message && (
        <div className="bg-[#1a1f2e]/70 border border-blue-900/30 rounded-lg px-4 py-3">
          <p className="text-sm text-gray-200 leading-relaxed">{message}</p>
        </div>
      )}

      {/* Summary Card */}
      <div className="bg-gradient-to-br from-[#1a1f2e] to-[#151922] border border-blue-900/30 rounded-xl p-4 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-400" />
            Changes Summary
          </h4>
          <span className="text-xs text-gray-400 bg-blue-900/20 px-3 py-1 rounded-full border border-blue-900/30">
            {totalFiles} {totalFiles === 1 ? "file" : "files"}
          </span>
        </div>

        {/* File Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {/* Added Files */}
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <FilePlus className="w-4 h-4 text-green-400" />
              <span className="text-xs text-gray-400">Added</span>
            </div>
            <div className="text-2xl font-bold text-green-400">{summary.added}</div>
          </div>

          {/* Modified Files */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <FileEdit className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-gray-400">Modified</span>
            </div>
            <div className="text-2xl font-bold text-blue-400">{summary.modified}</div>
          </div>

          {/* Deleted Files */}
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <FileX className="w-4 h-4 text-red-400" />
              <span className="text-xs text-gray-400">Deleted</span>
            </div>
            <div className="text-2xl font-bold text-red-400">{summary.deleted}</div>
          </div>
        </div>

        {/* Line Stats */}
        <div className="flex items-center justify-between pt-3 border-t border-blue-900/30">
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5 text-green-400">
              <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              <span className="font-mono">+{summary.totalLines.added}</span>
              <span className="text-gray-400">additions</span>
            </span>
            <span className="flex items-center gap-1.5 text-red-400">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              <span className="font-mono">-{summary.totalLines.deleted}</span>
              <span className="text-gray-400">deletions</span>
            </span>
          </div>
        </div>
      </div>

      {/* Issues */}
      {issues.length > 0 && (
        <div className="bg-[#1a1f2e]/50 border border-blue-900/30 rounded-xl overflow-hidden">
          <div className="px-4 py-3 bg-[#0f1419]/80 border-b border-blue-900/20">
            <h4 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-400" />
              Issues Found ({issues.length})
            </h4>
          </div>
          <div className="divide-y divide-blue-900/20">
            {issues.map((issue, index) => (
              <IssueItem key={index} issue={issue} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function IssueItem({ issue }: { issue: Issue }) {
  const getIcon = () => {
    switch (issue.type) {
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case "warning":
        return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case "info":
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getBgColor = () => {
    switch (issue.type) {
      case "error":
        return "bg-red-500/5 hover:bg-red-500/10";
      case "warning":
        return "bg-yellow-500/5 hover:bg-yellow-500/10";
      case "info":
        return "bg-blue-500/5 hover:bg-blue-500/10";
    }
  };

  const getTextColor = () => {
    switch (issue.type) {
      case "error":
        return "text-red-400";
      case "warning":
        return "text-yellow-400";
      case "info":
        return "text-blue-400";
    }
  };

  return (
    <div className={`px-4 py-3 transition-colors ${getBgColor()}`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{getIcon()}</div>
        <div className="flex-1">
          <p className={`text-sm ${getTextColor()} mb-1`}>{issue.message}</p>
          {(issue.file || issue.line) && (
            <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
              {issue.file && <span>{issue.file}</span>}
              {issue.line && (
                <>
                  <span>·</span>
                  <span>Line {issue.line}</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
