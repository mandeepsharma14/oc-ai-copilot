# High-Level Design (HLD)
## OC AI Copilot — Enterprise Knowledge Assistant
**Version:** 1.0 | **Date:** April 2026 | **Owner:** Andy Sharma

---

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│              Azure Front Door + WAF + CDN                  │
│    (DDoS Shield · OWASP rules · 5M user scale)             │
└──────────────────┬────────────────────────────┬────────────┘
                   │ Internal                   │ External
      copilot.owenscorning.com       advisor.owenscorning.com
                   │                            │
      ┌────────────▼────────┐     ┌─────────────▼───────────┐
      │  Azure Entra ID SSO │     │  OAuth 2.0 / API Keys   │
      │  (OC employees only)│     │  (public + partner tier)│
      └────────────┬────────┘     └─────────────┬───────────┘
                   └──────────┬──────────────────┘
                              │
                  ┌───────────▼────────────┐
                  │  Azure API Management  │
                  │  Rate limiting · Auth  │
                  │  Request routing       │
                  └───────────┬────────────┘
                              │
          ┌───────────────────▼────────────────────┐
          │       AKS Cluster (auto-scale 3–200)    │
          │                                         │
          │  FastAPI Backend                        │
          │  ┌─────────────┐  ┌─────────────────┐  │
          │  │  LangGraph  │  │   RAG Engine     │  │
          │  │ Orchestrator│  │  LlamaIndex      │  │
          │  └─────────────┘  └─────────────────┘  │
          │  ┌─────────────┐  ┌─────────────────┐  │
          │  │  Ingestion  │  │  Auth / RBAC     │  │
          │  │  Pipeline   │  │  Service         │  │
          │  └─────────────┘  └─────────────────┘  │
          │                                         │
          │  Next.js Frontend (Internal + External) │
          └───────────────────┬────────────────────┘
                              │
   ┌──────────────────────────▼──────────────────────────┐
   │                   AI / LLM Layer                     │
   │  Azure OpenAI GPT-4o      Azure OpenAI GPT-4o-mini  │
   │  (internal stream)        (external — cost-optimized)│
   │  text-embedding-3-large   (shared — both streams)    │
   └──────────────────────────┬──────────────────────────┘
                              │
   ┌──────────────────────────▼──────────────────────────┐
   │                    Data Layer                        │
   │  Azure AI Search         Azure AI Search             │
   │  oc-internal-docs        oc-external-docs            │
   │  (4,847 docs)            (2,097 docs)                │
   │                                                      │
   │  Redis Cache   Cosmos DB (sessions)   Azure SQL (audit)│
   │  Azure Blob Storage (source documents)               │
   └──────────────────────────────────────────────────────┘
```

---

## 2. Architecture Principles

| Principle | Implementation |
|-----------|---------------|
| RAG-first | All answers grounded in retrieved OC documents — LLM never uses training knowledge alone |
| Security-first | Entra ID SSO, document-level RBAC, TLS 1.3, AES-256, WORM audit logs |
| Stream isolation | Separate search indexes, LLMs, and auth — data cannot cross streams by design |
| Modular | Each layer independently replaceable without full re-architecture |
| Cost-aware | GPT-4o-mini for external; CDN cache target 60%+; Redis for repeat queries |
| Observable | Every query, token count, latency, and cost tracked in Application Insights |

---

## 3. Stream Comparison

| Dimension | Internal | External |
|-----------|----------|---------|
| URL | copilot.owenscorning.com | advisor.owenscorning.com |
| Auth | Azure Entra ID SSO | OAuth 2.0 / API keys / public |
| LLM | GPT-4o | GPT-4o-mini |
| Search index | oc-internal-docs | oc-external-docs |
| Domains | Safety, Engineering, Quality, Maintenance, IT, HR, New Hire, Finance | Roofing, Insulation, Composites, Doors |
| Documents | 4,847 | 2,097 |
| RBAC | Document-level, AD group scoped | Product-line scoped; pricing tier for partners |
| Concurrent users | 18,000 tested | 5,000,000 design target |
| Latency p95 target | < 3 seconds | < 1.5 seconds (CDN-assisted) |
| Cost per query | ~$0.028 | ~$0.008 |
| Audit log | Immutable 3-year WORM | 90-day standard |
| Teams bot | Yes | No |

---

## 4. Security Architecture

```
Request
  → Azure Front Door WAF (OWASP rule set + rate 2000/5min/IP)
  → Azure API Management (JWT validation + rate limiting + IP allowlist)
  → FastAPI (RBAC enforcement + PII scrubbing + structured audit log)
  → Azure AI Search (filter-time permission scoping — never post-hoc)
  → Azure OpenAI (private endpoint — traffic never leaves Azure backbone)
  → Audit log (immutable write-once — no delete capability ever)
```

**Key controls:**
- Identity: Entra ID with MFA for all internal users
- Network: Azure Private Endpoints for all services; no public IPs on AKS nodes
- Encryption: AES-256 at rest (Key Vault managed keys); TLS 1.3 in transit
- Secrets: Azure Key Vault with 30-day automatic rotation for service credentials
- PII scrubbing: Azure AI Language PII detection applied to all queries before LLM submission
- Audit: Every interaction → immutable log → Azure Blob WORM (5-year retention)

---

## 5. Scalability Design

### Internal (25K employees)
- AKS HPA: 3–200 pods based on CPU > 70%
- Redis cache: 41% hit rate target on repeat queries per site
- Document-level RBAC enforced at query time via Azure AI Search metadata filters

### External (5M customers)
```
CloudFlare + Azure Front Door CDN (61% cache target)
  ├── Cached hits: product specs, install guides → serve from CDN, zero LLM cost
  └── Cache miss: novel queries
       → APIM → AKS (100–2,000 pods auto-scale)
       → GPT-4o-mini (87% cheaper than GPT-4o)
       → Redis session cache
```

### External cost model at full 5M users (3 queries/day each = 15M queries/day)
| Component | Daily queries | Unit cost | Daily cost |
|-----------|--------------|-----------|-----------|
| CDN hits (61%) | 9.15M | $0.00 | $0 |
| GPT-4o-mini queries (39%) | 5.85M | $0.008 | $46,800 |
| Embeddings | 5.85M | $0.0005 | $2,925 |
| Azure AI Search | 5.85M | $0.001 | $5,850 |
| AKS (2,000 pods) | — | $2.50/hr | ~$120,000 |
| **Total per query** | | | **~$0.006** |

---

## 6. Integration Map

| System | Integration | Purpose |
|--------|------------|---------|
| SharePoint Online | Microsoft Graph API webhooks | Auto-ingest on create/update |
| Azure Entra ID | OIDC / OAuth 2.0 | SSO + RBAC group lookup |
| Microsoft Teams | Bot Framework + Adaptive Cards | Internal chat interface |
| SAP (Phase 2) | OData API | Process documentation ingestion |
| Salesforce (Phase 3) | REST API | Customer account context |
| ServiceNow (Phase 3) | REST API | IT helpdesk knowledge base |

---

## 7. Disaster Recovery

| Target | Value |
|--------|-------|
| RTO | 4 hours |
| RPO | 1 hour |
| Platform SLA (internal) | 99.9% |
| Platform SLA (external) | 99.95% |
| AKS pod failure | Auto-replaced < 2 min |
| AZ failure | ALB routes to remaining AZs; Cosmos DB auto-failover < 30s |
| Region failure | Manual failover to East US via Terraform + DNS cutover |
| Azure OpenAI throttle | Retry with exponential backoff → cached response fallback |
