"""Pydantic request/response schemas for all API endpoints."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StreamType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class KnowledgeDomain(str, Enum):
    SAFETY      = "safety"
    ENGINEERING = "engineering"
    QUALITY     = "quality"
    MAINTENANCE = "maintenance"
    IT          = "it"
    HR          = "hr"
    NEW_HIRE    = "new_hire"
    FINANCE     = "finance"


class ProductLine(str, Enum):
    ROOFING    = "roofing"
    INSULATION = "insulation"
    COMPOSITES = "composites"
    DOORS      = "doors"


class CustomerSegment(str, Enum):
    RETAIL      = "retail"
    CONTRACTOR  = "contractor"
    BUILDER     = "builder"
    HOMEOWNER   = "homeowner"


class SourceCitation(BaseModel):
    document_name: str
    section:       Optional[str] = None
    version:       Optional[str] = None
    approved_date: Optional[str] = None
    confidence:    float = Field(ge=0.0, le=1.0)


class ChatQueryRequest(BaseModel):
    query:            str = Field(min_length=3, max_length=2000)
    session_id:       Optional[str] = None
    stream_type:      StreamType
    domain_filter:    Optional[KnowledgeDomain] = None
    product_filter:   Optional[ProductLine] = None
    customer_segment: Optional[CustomerSegment] = None
    site_filter:      Optional[str] = None


class ChatQueryResponse(BaseModel):
    answer:           str
    citations:        List[SourceCitation]
    session_id:       str
    query_id:         str
    confidence:       float
    is_knowledge_gap: bool = False
    latency_ms:       int
    stream_type:      StreamType
    timestamp:        datetime


class DocumentIngestRequest(BaseModel):
    source_type:  str   # "sharepoint" | "blob" | "upload"
    source_url:   Optional[str] = None
    stream_type:  StreamType
    domain:       Optional[KnowledgeDomain] = None
    product_line: Optional[ProductLine] = None
    site:         Optional[str] = None
    metadata:     Optional[dict] = None


class DocumentIngestResponse(BaseModel):
    document_id:    str
    document_name:  str
    chunks_created: int
    stream_type:    str
    status:         str


class DocumentRecord(BaseModel):
    id:            str
    name:          str
    version:       Optional[str] = None
    approved_date: Optional[str] = None
    owner:         Optional[str] = None
    domain:        Optional[str] = None
    product_line:  Optional[str] = None
    stream_type:   str
    status:        str  # "live" | "review" | "archived"
    chunk_count:   int
    ingested_at:   datetime


class AdminMetrics(BaseModel):
    total_queries_today:  int
    accuracy_rate:        float
    active_users:         int
    avg_latency_p95_ms:   int
    uptime_percent:       float
    cache_hit_rate:       float
    cost_per_query_usd:   float
    documents_indexed:    int
    knowledge_gaps_count: int


class HealthResponse(BaseModel):
    status:      str
    version:     str
    environment: str
    timestamp:   datetime
