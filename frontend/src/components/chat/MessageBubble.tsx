"use client";
import { clsx } from "clsx";
import { Badge } from "@/components/shared/Badge";
import type { ChatMessage } from "@/types";

interface MessageBubbleProps {
  message:    ChatMessage;
  streamType: "internal" | "external";
}

export function MessageBubble({ message, streamType }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isInt  = streamType === "internal";

  return (
    <div className={clsx("flex gap-2 items-start", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-semibold text-white flex-shrink-0 mt-0.5"
        style={{ background: isUser ? (isInt ? "#2563A8" : "#1D9E75") : (isInt ? "#1B2E4A" : "#0E5C3A") }}
      >
        {isUser ? "AS" : "OC"}
      </div>

      {/* Bubble */}
      <div
        className={clsx(
          "max-w-[80%] px-3 py-2 rounded-xl text-xs leading-relaxed border",
          isUser
            ? isInt
              ? "bg-blue-50 border-blue-200 text-blue-900"
              : "bg-emerald-50 border-emerald-200 text-emerald-900"
            : "bg-white border-gray-100 text-gray-800"
        )}
      >
        {/* Content */}
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <div className="text-[9px] text-gray-400 mb-1">Sources</div>
            <div className="flex flex-wrap gap-1">
              {message.citations.map((c, i) => (
                <span
                  key={i}
                  title={`${c.document_name}${c.section ? " " + c.section : ""}${c.version ? " · " + c.version : ""}`}
                  className="inline-flex items-center gap-1 text-[9px] px-2 py-0.5 rounded-full border cursor-pointer bg-green-50 text-green-800 border-green-200 hover:bg-green-100 transition"
                >
                  <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  {c.document_name.length > 30 ? c.document_name.slice(0, 30) + "…" : c.document_name}
                  {c.section && ` ${c.section}`}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Confidence + latency footer */}
        {!isUser && message.confidence !== undefined && (
          <div className="mt-1.5 flex items-center gap-2">
            <div className="flex-1 h-0.5 bg-gray-100 rounded overflow-hidden">
              <div
                className="h-full bg-green-500 rounded"
                style={{ width: `${Math.round(message.confidence * 100)}%` }}
              />
            </div>
            <span className="text-[9px] text-gray-400">
              {Math.round(message.confidence * 100)}% confidence
              {message.latencyMs && ` · ${(message.latencyMs / 1000).toFixed(1)}s`}
            </span>
          </div>
        )}

        {/* Knowledge gap warning */}
        {!isUser && message.isKnowledgeGap && (
          <div className="mt-1.5 flex items-center gap-1 text-[9px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Knowledge gap flagged — no matching document found
          </div>
        )}
      </div>
    </div>
  );
}
