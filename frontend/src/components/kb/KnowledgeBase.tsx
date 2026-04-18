"use client";
import { useState } from "react";
import { useQuery }  from "@tanstack/react-query";
import { documentsApi } from "@/utils/api";
import type { DocumentRecord } from "@/types";

const DOMAIN_COLORS: Record<string, string> = {
  safety:      "#85B7EB",
  engineering: "#5DCAA5",
  quality:     "#AFA9EC",
  maintenance: "#F0997B",
  it:          "#97C459",
  hr:          "#FAC775",
  new_hire:    "#5DCAA5",
  finance:     "#85B7EB",
  roofing:     "#85B7EB",
  insulation:  "#5DCAA5",
  composites:  "#AFA9EC",
  doors:       "#F0997B",
};

interface KnowledgeBaseProps {
  streamType: "internal" | "external";
}

export function KnowledgeBase({ streamType }: KnowledgeBaseProps) {
  const [search, setSearch] = useState("");

  const { data: docs = [], isLoading } = useQuery<DocumentRecord[]>({
    queryKey: ["documents", streamType],
    queryFn:  () => documentsApi.list(streamType) as Promise<DocumentRecord[]>,
  });

  const filtered = docs.filter((d) =>
    !search || d.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full">
      {/* Search bar */}
      <div className="px-3 py-2 border-b border-gray-100 flex items-center gap-2">
        <div className="flex-1 flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5">
          <svg className="w-3 h-3 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents…"
            className="flex-1 bg-transparent text-xs text-gray-700 placeholder-gray-400 outline-none"
          />
        </div>
        <span className="text-[10px] text-gray-400">{filtered.length} documents</span>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2 flex flex-col gap-2">
        {isLoading && (
          <div className="text-xs text-gray-400 animate-pulse py-4 text-center">Loading knowledge base…</div>
        )}

        {!isLoading && filtered.length === 0 && (
          <div className="text-xs text-gray-400 py-8 text-center">No documents match your search.</div>
        )}

        {filtered.map((doc) => {
          const colorKey = doc.domain || doc.product_line || "engineering";
          const color    = DOMAIN_COLORS[colorKey] || "#85B7EB";
          return (
            <div
              key={doc.id}
              className="flex items-center gap-2.5 px-3 py-2 border border-gray-100 rounded-lg hover:bg-gray-50 transition cursor-pointer"
            >
              <div
                className="w-5 h-5 rounded flex-shrink-0 flex items-center justify-center"
                style={{ background: color + "22" }}
              >
                <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-gray-800 truncate">{doc.name}</div>
                <div className="text-[9px] text-gray-400">
                  {doc.version && `${doc.version} · `}
                  {doc.approved_date && `Approved ${doc.approved_date} · `}
                  {doc.chunk_count} chunks
                </div>
              </div>
              <span
                className={`text-[9px] px-2 py-0.5 rounded-full flex-shrink-0 ${
                  doc.status === "live"
                    ? "bg-green-50 text-green-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {doc.status === "live" ? "Live" : "Review"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
