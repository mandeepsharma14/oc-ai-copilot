# Low-Level Design (LLD)
## OC AI Copilot — Enterprise Knowledge Assistant
**Version:** 1.0 | **Date:** April 2026 | **Owner:** Andy Sharma

---

## 1. Azure AI Search Index Schema

```json
{
  "name": "oc-internal-docs",
  "fields": [
    { "name": "chunk_id",       "type": "Edm.String",              "key": true },
    { "name": "document_id",    "type": "Edm.String",              "filterable": true },
    { "name": "document_name",  "type": "Edm.String",              "searchable": true },
    { "name": "content",        "type": "Edm.String",              "searchable": true },
    { "name": "content_vector", "type": "Collection(Edm.Single)",  "dimensions": 3072,
      "vectorSearchProfile": "oc-hnsw-profile" },
    { "name": "section",        "type": "Edm.String",              "retrievable": true },
    { "name": "version",        "type": "Edm.String",              "retrievable": true },
    { "name": "approved_date",  "type": "Edm.String",              "retrievable": true },
    { "name": "domain",         "type": "Edm.String",              "filterable": true },
    { "name": "site",           "type": "Edm.String",              "filterable": true },
    { "name": "stream_type",    "type": "Edm.String",              "filterable": true }
  ],
  "vectorSearch": {
    "algorithms": [{
      "name": "oc-hnsw",
      "kind": "hnsw",
      "hnswParameters": { "m": 4, "efConstruction": 400, "metric": "cosine" }
    }],
    "profiles": [{ "name": "oc-hnsw-profile", "algorithm": "oc-hnsw" }]
  },
  "semantic": {
    "configurations": [{
      "name": "oc-semantic-config",
      "prioritizedFields": {
        "contentFields":  [{ "fieldName": "content" }],
        "keywordsFields": [{ "fieldName": "document_name" }, { "fieldName": "section" }]
      }
    }]
  }
}
```

---

## 2. Document Ingestion Pipeline

```
File detected (SharePoint webhook / Blob event / manual upload)
  │
  ▼
1. File type detection & routing
   PDF  → Azure Document Intelligence (layout-aware)
   DOCX → python-docx (headings, tables, lists preserved)
   XLSX → openpyxl (table-structured)
   TXT/MD → direct read

  │
  ▼
2. Metadata extraction
   name, version, approved_date, owner, domain/product_line, site, SharePoint path

  │
  ▼
3. Semantic chunking
   512-token chunks · 20% overlap · never split mid-table or mid-procedure

  │
  ▼
4. Embedding generation
   text-embedding-3-large (3072 dim) · batch 16 chunks/call

  │
  ▼
5. Index upsert (Azure AI Search)
   Idempotent by chunk_id — safe to re-run on document update

  │
  ▼
6. Ingestion audit record
   Written to Azure SQL — document ID, chunk count, timestamp, status
```

---

## 3. RAG Pipeline Detail

### 3.1 Query Processing

```python
async def process(query, user_context):
    # 1. Build RBAC filter from user's AD groups
    rbac_filter = {"domain": user_context.domain, "site": user_context.site}

    # 2. Hybrid search — BM25 + dense vector (RRF merge)
    candidates = await search(query, filter=rbac_filter, top_k=20)

    # 3. Cross-encoder reranking
    top_k = rerank(query, candidates, top_k=6)

    # 4. Check for knowledge gap
    is_gap = not top_k or top_k[0].score < 0.35

    # 5. Build prompt + generate
    messages = build_prompt(system_prompt, query, top_k, is_gap)
    answer   = await llm.generate(messages)

    return answer, citations(top_k), is_gap
```

### 3.2 Internal System Prompt

```
You are OC AI Copilot, an internal knowledge assistant for Owens Corning employees.

RULES:
1. Answer ONLY from the provided document context. Never use general knowledge.
2. Cite sources as: [Document Name, Section X.X, Version Y]
3. If context is insufficient: "I cannot find this in current approved documentation."
4. For safety-critical steps, add: "Verify with your site EHS lead before acting."
5. Format procedural answers as numbered steps.
```

### 3.3 External System Prompt

```
You are OC Product Advisor, helping customers with Owens Corning products.

RULES:
1. Answer ONLY from provided product documentation.
2. For pricing: "Pricing is MSRP guidance — contact your OC rep for final pricing."
3. For installation: "Consult local codes and a licensed contractor."
4. If unable to answer: "Visit owenscorning.com or call 1-800-GET-PINK."
```

---

## 4. API Specification

### POST /api/v1/chat/query

**Request:**
```json
{
  "query":         "What is the LOTO procedure for Line 3?",
  "session_id":    "uuid-optional",
  "stream_type":   "internal",
  "domain_filter": "safety",
  "site_filter":   "Charlotte"
}
```

**Response:**
```json
{
  "answer":           "For Line 3 conveyors at Charlotte...",
  "citations": [
    {
      "document_name":  "EHS-LOTO-003",
      "section":        "§4.2",
      "version":        "Rev 4",
      "approved_date":  "2025-10-01",
      "confidence":     0.96
    }
  ],
  "session_id":       "uuid",
  "query_id":         "uuid",
  "confidence":       0.96,
  "is_knowledge_gap": false,
  "latency_ms":       1847,
  "stream_type":      "internal",
  "timestamp":        "2026-04-18T14:23:11Z"
}
```

---

## 5. Database Schemas

### Azure SQL — Audit Log (Immutable)

```sql
CREATE TABLE query_audit_log (
    id               UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    query_id         NVARCHAR(36)     NOT NULL,
    session_id       NVARCHAR(36)     NOT NULL,
    user_id          NVARCHAR(255)    NOT NULL,
    stream_type      NVARCHAR(20)     NOT NULL,
    query_text       NVARCHAR(MAX)    NOT NULL,
    answer_text      NVARCHAR(MAX)    NOT NULL,
    citations_json   NVARCHAR(MAX),
    confidence       DECIMAL(5,4),
    is_knowledge_gap BIT              DEFAULT 0,
    latency_ms       INT,
    domain_filter    NVARCHAR(50),
    site_filter      NVARCHAR(100),
    created_at       DATETIME2        DEFAULT GETUTCDATE()
);
-- Enable SQL ledger for immutability (Azure SQL feature)
```

### Cosmos DB — Sessions Container

```json
{
  "id":          "session-uuid",
  "user_id":     "andy.sharma@owenscorning.com",
  "stream_type": "internal",
  "messages":    [
    { "role": "user",      "content": "...", "timestamp": "..." },
    { "role": "assistant", "content": "...", "query_id": "...", "citations": [] }
  ],
  "created_at":  "2026-04-18T14:22:00Z",
  "ttl":         86400
}
```

---

## 6. Infrastructure Sizing

| Pool | VM Size | Min pods | Max pods | Purpose |
|------|---------|----------|----------|---------|
| system | Standard_D4s_v3 | 2 | 10 | K8s system workloads |
| apppool | Standard_D8s_v3 | 3 | 200 | Backend + frontend pods |

### Azure OpenAI Capacity

| Deployment | Model | Capacity | Stream |
|-----------|-------|----------|--------|
| gpt-4o | GPT-4o | 40K TPM | Internal |
| gpt-4o-mini | GPT-4o-mini | 120K TPM | External |
| text-embedding-3-large | Embedding | 30K RPM | Both |

---

## 7. Testing Strategy

```
tests/
├── unit/
│   ├── test_pipeline.py     RAG pipeline with mocked Azure calls
│   ├── test_retriever.py    Retriever logic and mock fallback
│   ├── test_chunker.py      Chunking size, overlap, short-text filtering
│   ├── test_prompts.py      Prompt construction and knowledge gap handling
│   └── test_schemas.py      Pydantic validation for all request/response types
├── integration/
│   ├── test_chat_api.py     Full API endpoint tests (TestClient)
│   ├── test_ingestion.py    End-to-end ingestion with temp files
│   └── test_rbac.py         Permission scoping filter tests
└── accuracy/
    ├── internal_test_set.json   200 Q&A pairs for internal benchmark
    └── external_test_set.json   200 Q&A pairs for external benchmark
```

**Accuracy benchmark target:** > 92% answer relevance (internal), > 90% (external), run monthly.
