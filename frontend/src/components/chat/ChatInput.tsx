"use client";
import { useState, KeyboardEvent } from "react";
import { clsx } from "clsx";

interface ChatInputProps {
  onSend:      (message: string) => void;
  isLoading:   boolean;
  placeholder: string;
  accentColor: string;
}

export function ChatInput({ onSend, isLoading, placeholder, accentColor }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="px-3 py-2 border-t border-gray-100">
      <div className={clsx(
        "flex items-center gap-2 border rounded-xl px-3 py-2 bg-white transition-shadow",
        "border-gray-200 focus-within:border-gray-400 focus-within:ring-1 focus-within:ring-gray-200"
      )}>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder={placeholder}
          disabled={isLoading}
          className="flex-1 bg-transparent text-xs text-gray-800 placeholder-gray-400 outline-none disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={!value.trim() || isLoading}
          className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 disabled:opacity-40 transition-opacity"
          style={{ background: accentColor }}
        >
          <svg className="w-3 h-3 text-white" viewBox="0 0 24 24" fill="white">
            <path d="M22 2L11 13"/>
            <path d="M22 2L15 22 11 13 2 9l20-7z"/>
          </svg>
        </button>
      </div>
      <p className="text-center text-[9px] text-gray-400 mt-1">
        Answers grounded in approved OC documentation only.
      </p>
    </div>
  );
}
