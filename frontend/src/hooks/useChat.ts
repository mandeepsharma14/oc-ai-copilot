/**
 * useChat — core hook for conversation state and query submission.
 */
import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { chatApi } from "@/utils/api";
import type { ChatMessage, ChatQueryRequest, StreamType, ChatQueryResponse } from "@/types";

interface UseChatOptions {
  streamType: StreamType;
}

export function useChat({ streamType }: UseChatOptions) {
  const [messages,    setMessages]    = useState<ChatMessage[]>([]);
  const [isLoading,   setIsLoading]   = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const [sessionId]                   = useState(uuidv4());
  const [domainFilter,setDomainFilter]= useState<string | null>(null);
  const messagesEndRef                = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }), 80);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;
    setError(null);

    const userMsg: ChatMessage = {
      id: uuidv4(), role: "user", content, timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    scrollToBottom();
    setIsLoading(true);

    try {
      const req: ChatQueryRequest = {
        query:         content,
        session_id:    sessionId,
        stream_type:   streamType,
        domain_filter: domainFilter as any ?? undefined,
      };
      const data = await chatApi.query(req) as ChatQueryResponse;

      const aiMsg: ChatMessage = {
        id:              data.query_id,
        role:            "assistant",
        content:         data.answer,
        citations:       data.citations,
        confidence:      data.confidence,
        isKnowledgeGap:  data.is_knowledge_gap,
        latencyMs:       data.latency_ms,
        timestamp:       new Date(data.timestamp),
      };
      setMessages((prev) => [...prev, aiMsg]);
      scrollToBottom();
    } catch (err: any) {
      setError(typeof err === "string" ? err : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId, streamType, domainFilter, scrollToBottom]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages, isLoading, error, sessionId,
    sendMessage, clearMessages, messagesEndRef,
    domainFilter, setDomainFilter,
  };
}
