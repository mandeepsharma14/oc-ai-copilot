/** Core TypeScript types for OC AI Copilot */

export type StreamType      = "internal" | "external";
export type KnowledgeDomain = "safety" | "engineering" | "quality" | "maintenance" | "it" | "hr" | "new_hire" | "finance";
export type ProductLine     = "roofing" | "insulation" | "composites" | "doors";
export type CustomerSegment = "retail" | "contractor" | "builder" | "homeowner";

export interface SourceCitation {
  document_name:  string;
  section?:       string;
  version?:       string;
  approved_date?: string;
  confidence:     number;
}

export interface ChatMessage {
  id:               string;
  role:             "user" | "assistant";
  content:          string;
  citations?:       SourceCitation[];
  confidence?:      number;
  isKnowledgeGap?:  boolean;
  latencyMs?:       number;
  timestamp:        Date;
}

export interface ChatQueryRequest {
  query:             string;
  session_id?:       string;
  stream_type:       StreamType;
  domain_filter?:    KnowledgeDomain;
  product_filter?:   ProductLine;
  customer_segment?: CustomerSegment;
  site_filter?:      string;
}

export interface ChatQueryResponse {
  answer:           string;
  citations:        SourceCitation[];
  session_id:       string;
  query_id:         string;
  confidence:       number;
  is_knowledge_gap: boolean;
  latency_ms:       number;
  stream_type:      StreamType;
  timestamp:        string;
}

export interface AdminMetrics {
  total_queries_today:   number;
  accuracy_rate:         number;
  active_users:          number;
  avg_latency_p95_ms:    number;
  uptime_percent:        number;
  cache_hit_rate:        number;
  cost_per_query_usd:    number;
  documents_indexed:     number;
  knowledge_gaps_count:  number;
}

export interface DocumentRecord {
  id:             string;
  name:           string;
  version?:       string;
  approved_date?: string;
  owner?:         string;
  domain?:        string;
  product_line?:  string;
  stream_type:    string;
  status:         "live" | "review" | "archived";
  chunk_count:    number;
  ingested_at:    string;
}
