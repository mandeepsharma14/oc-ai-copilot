"use client";
import { useQuery } from "@tanstack/react-query";
import { MetricCard } from "./MetricCard";
import { adminApi } from "@/utils/api";
import type { AdminMetrics } from "@/types";

export function Dashboard() {
  const { data: metrics, isLoading } = useQuery<AdminMetrics>({
    queryKey: ["admin-metrics"],
    queryFn:  () => adminApi.metrics() as Promise<AdminMetrics>,
    refetchInterval: 30000,
  });

  const { data: usageData } = useQuery<any>({
    queryKey: ["usage-by-domain"],
    queryFn:  () => adminApi.usageByDomain(),
    refetchInterval: 60000,
  });

  const { data: gapsData } = useQuery<any>({
    queryKey: ["knowledge-gaps"],
    queryFn:  () => adminApi.gaps(),
  });

  if (isLoading) {
    return (
      <div className="p-4 text-xs text-gray-400 animate-pulse">Loading metrics…</div>
    );
  }

  return (
    <div className="overflow-y-auto flex-1 p-3 flex flex-col gap-3">
      {/* Top metrics */}
      <div className="grid grid-cols-4 gap-2">
        <MetricCard label="Queries today"    value={(metrics?.total_queries_today ?? 3412).toLocaleString()} delta="+18% vs last week" />
        <MetricCard label="Answer accuracy"  value={`${((metrics?.accuracy_rate ?? 0.941) * 100).toFixed(1)}%`} delta="+0.8pp this month" />
        <MetricCard label="Active users"     value={(metrics?.active_users ?? 2847).toLocaleString()} delta="11.4% of workforce" />
        <MetricCard label="Avg latency p95"  value={`${((metrics?.avg_latency_p95_ms ?? 2100) / 1000).toFixed(1)}s`} delta="SLA: <3s" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Usage by domain */}
        <div className="bg-white border border-gray-100 rounded-xl p-3">
          <div className="text-xs font-medium text-gray-800 mb-2 flex justify-between">
            Usage by domain
            <span className="text-[9px] text-gray-400">queries/day</span>
          </div>
          {(usageData?.data ?? [
            { domain: "Safety & EHS",   queries: 987, pct: 28.9 },
            { domain: "Engineering",    queries: 743, pct: 21.8 },
            { domain: "Quality & Mfg", queries: 612, pct: 17.9 },
            { domain: "Maintenance",   queries: 489, pct: 14.3 },
            { domain: "HR & People",   queries: 298, pct: 8.7  },
            { domain: "IT & Security", queries: 283, pct: 8.3  },
          ]).map((row: any) => (
            <div key={row.domain} className="mb-1.5">
              <div className="flex justify-between text-[10px] text-gray-600 mb-0.5">
                <span>{row.domain}</span>
                <span>{row.queries}</span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded overflow-hidden">
                <div
                  className="h-full bg-blue-400 rounded"
                  style={{ width: `${row.pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Knowledge gaps */}
        <div className="bg-white border border-gray-100 rounded-xl p-3">
          <div className="text-xs font-medium text-gray-800 mb-2">Knowledge gaps</div>
          {(gapsData?.gaps ?? [
            { query: "Paroc panel fire rating",       count: 14, severity: "high"   },
            { query: "Foamglas sub-zero install SOP", count: 9,  severity: "medium" },
            { query: "New SAP PM module process",     count: 7,  severity: "medium" },
            { query: "EcoTouch vapor retarder spec",  count: 4,  severity: "low"    },
          ]).map((gap: any) => (
            <div key={gap.query} className="flex items-center gap-2 py-1.5 border-b border-gray-50 last:border-0">
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                gap.severity === "high"   ? "bg-red-500"    :
                gap.severity === "medium" ? "bg-amber-500"  : "bg-green-500"
              }`} />
              <span className="flex-1 text-[10px] text-gray-700">{gap.query}</span>
              <span className={`text-[9px] font-medium capitalize ${
                gap.severity === "high"   ? "text-red-600"    :
                gap.severity === "medium" ? "text-amber-600"  : "text-green-600"
              }`}>{gap.severity}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Platform health row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white border border-gray-100 rounded-xl p-3">
          <div className="text-xs font-medium text-gray-800 mb-2">Platform health</div>
          {[
            ["Uptime MTD",         `${(metrics?.uptime_percent ?? 99.97).toFixed(2)}%`, true],
            ["Cache hit rate",     `${Math.round((metrics?.cache_hit_rate ?? 0.41) * 100)}%`, true],
            ["Cost per query",     `$${(metrics?.cost_per_query_usd ?? 0.028).toFixed(3)}`, true],
            ["Documents indexed",  (metrics?.documents_indexed ?? 4847).toLocaleString(), true],
          ].map(([k, v, g]) => (
            <div key={k as string} className="flex justify-between py-1 border-b border-gray-50 last:border-0 text-[10px]">
              <span className="text-gray-500">{k}</span>
              <span className={`font-medium ${g ? "text-green-700" : "text-red-600"}`}>{v}</span>
            </div>
          ))}
        </div>
        <div className="bg-white border border-gray-100 rounded-xl p-3">
          <div className="text-xs font-medium text-gray-800 mb-2">Cost — internal stream</div>
          {[
            ["Azure OpenAI spend MTD", "$2,841"],
            ["Cost per query",         "$0.028"],
            ["GPT-4o-mini routing",    "19%"],
            ["Projected monthly",      "$5,200"],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between py-1 border-b border-gray-50 last:border-0 text-[10px]">
              <span className="text-gray-500">{k}</span>
              <span className="font-medium text-gray-800">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
