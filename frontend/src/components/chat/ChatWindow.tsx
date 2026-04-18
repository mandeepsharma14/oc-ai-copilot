"use client";
import { useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { ChatInput }     from "./ChatInput";
import { LoadingDots }   from "@/components/shared/LoadingDots";
import { useChat }       from "@/hooks/useChat";
import type { StreamType } from "@/types";

const INTERNAL_CHIPS = [
  "LOTO procedure for SC Doors assembly line",
  "New hire onboarding — automation engineer",
  "Injection molding PM schedule",
  "OT remote access & VPN policy",
  "CapEx approval thresholds — project managers",
];

const EXTERNAL_CHIPS = [
  "Duration Storm vs Duration Premium specs",
  "EcoTouch R-value for Climate Zone 5",
  "Duration shingle pricing — Lowe's program",
  "Thermafiber commercial fire rating",
  "EcoTouch attic installation steps",
];

interface ChatWindowProps {
  streamType:  StreamType;
  accentColor: string;
}

export function ChatWindow({ streamType, accentColor }: ChatWindowProps) {
  const {
    messages, isLoading, error, sendMessage,
    messagesEndRef, domainFilter, setDomainFilter,
  } = useChat({ streamType });

  const [chipsHidden, setChipsHidden] = useRef(false) as any;
  const chips = streamType === "internal" ? INTERNAL_CHIPS : EXTERNAL_CHIPS;
  const isInt = streamType === "internal";

  const handleChip = (chip: string) => {
    setChipsHidden(true);
    sendMessage(chip);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Domain / scope filter bar (internal only) */}
      {isInt && (
        <div className="flex items-center gap-1.5 px-3 py-2 border-b border-gray-100 flex-wrap">
          <span className="text-[9px] text-gray-400 mr-1">Domain:</span>
          {["All","Safety","Engineering","Quality","Maintenance","IT","HR","New Hire","Finance"].map((d) => (
            <button
              key={d}
              onClick={() => setDomainFilter(d === "All" ? null : d.toLowerCase())}
              className={`text-[10px] px-2 py-0.5 rounded-full border transition ${
                (d === "All" && !domainFilter) || domainFilter === d.toLowerCase()
                  ? "bg-blue-50 text-blue-800 border-blue-300"
                  : "border-gray-200 text-gray-500 hover:border-gray-400"
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-3">
        {/* Welcome */}
        {messages.length === 0 && (
          <div className="flex gap-2 items-start">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-semibold text-white flex-shrink-0"
              style={{ background: accentColor }}
            >
              OC
            </div>
            <div className="max-w-[80%] px-3 py-2 rounded-xl text-xs bg-white border border-gray-100 text-gray-800 leading-relaxed">
              {isInt
                ? "Hello! I have access to all 4,847 internal OC documents across 60 global sites — Safety, Engineering, Quality, Maintenance, IT, HR, New Hire, and Finance. What do you need?"
                : "Welcome to OC Product Advisor. I can help with product specifications, installation guides, R-values, fire ratings, and pricing across the full Owens Corning catalog. What are you looking for?"}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} streamType={streamType} />
        ))}

        {isLoading && (
          <div className="flex gap-2 items-start">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-semibold text-white flex-shrink-0"
              style={{ background: accentColor }}
            >
              OC
            </div>
            <div className="px-3 py-2 rounded-xl bg-white border border-gray-100">
              <LoadingDots />
            </div>
          </div>
        )}

        {error && (
          <div className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion chips */}
      {messages.length === 0 && (
        <div className="px-3 pb-2 flex flex-wrap gap-1.5">
          {chips.map((chip) => (
            <button
              key={chip}
              onClick={() => handleChip(chip)}
              className="text-[10px] px-2.5 py-1 border border-gray-200 rounded-full text-gray-500 hover:border-gray-400 hover:text-gray-700 transition"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      <ChatInput
        onSend={sendMessage}
        isLoading={isLoading}
        placeholder={
          isInt
            ? "Ask anything — SOPs, safety, maintenance, IT, HR, quality…"
            : "Ask about any OC product — specs, pricing, installation…"
        }
        accentColor={accentColor}
      />
    </div>
  );
}
