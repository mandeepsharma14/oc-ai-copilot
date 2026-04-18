# Business Requirements Document (BRD)
## OC AI Copilot — Enterprise Knowledge Assistant
**Version:** 1.0 | **Date:** April 2026 | **Owner:** Andy Sharma — Sr. Engineering Leader, Owens Corning

---

## 1. Executive Summary

OC AI Copilot is a secure, enterprise-grade Retrieval-Augmented Generation (RAG) platform serving two distinct user populations on a shared cloud infrastructure:

| Stream | Users | Scale Target | Purpose |
|--------|-------|-------------|---------|
| Internal | 25,000 employees · 60 sites | 18K concurrent | SOPs, safety, engineering, HR, IT, quality, maintenance, onboarding |
| External | Retailers, contractors, builders, homeowners | 500K–5M concurrent | Product specs, pricing, installation guides, fire ratings |

**Projected Year-1 ROI:** 660%–1,423% based on: knowledge retrieval time savings ($1.46M), SME interruption reduction ($737K), onboarding acceleration ($520K), safety risk avoidance ($170K+).

---

## 2. Problem Statement

### Internal (Employee) Problems
- **Knowledge fragmentation:** 4,847+ documents scattered across SharePoint, network drives, SAP, and email — no unified search layer
- **Version control risk:** Employees routinely reference outdated SOPs and superseded standards — direct safety and quality liability
- **SME bottleneck:** Subject matter experts spend 30–40% of time answering repeat questions that documentation already answers
- **Onboarding inefficiency:** New hires take 8–12 weeks to reach productivity; knowledge navigation is the primary bottleneck
- **Multi-site inconsistency:** 60 global sites apply engineering and safety standards inconsistently

### External (Customer) Problems
- **Product selection friction:** Contractors and builders spend significant time locating spec sheets, fire ratings, and installation guides
- **Support cost:** High volume of routine product questions handled by expensive human support channels ($15–40 per call)
- **Revenue leakage:** Customers unable to find information in time choose competitor products
- **Retailer enablement:** Lowe's and Home Depot floor staff need instant access to OC product data at point of sale

---

## 3. Business Objectives

1. Reduce internal knowledge retrieval time from 20 minutes average to under 60 seconds
2. Reduce SME interruption burden by 60–70%
3. Accelerate new employee time-to-productivity from 10 weeks to 6 weeks
4. Deflect 40%+ of routine external product queries to AI self-service
5. Deploy a governed, auditable AI platform meeting all OC IT security and compliance requirements
6. Scale external customer platform to 5 million concurrent users without re-architecture

---

## 4. Scope

### Phase 1 — Internal Pilot (Q2–Q3 2026)
- 500 pilot users at 3 sites: Charlotte NC, Gastonia NC, Aiken SC
- 8 knowledge domains indexed
- Microsoft Teams bot integration
- 4,847 target documents

### Phase 2 — External Launch + Internal Rollout (Q4 2026)
- External customer portal: all 4 product lines
- 4 customer segments: Retail, Contractor, Builder, Homeowner
- Internal: 20 additional sites enrolled
- SAP process documentation added

### Phase 3 — Enterprise Scale (2027)
- Full 60-site internal rollout (25,000 users)
- 5M external user capacity
- Spanish language support
- Live SAP data queries (inventory, pricing, order status)
- Salesforce and ServiceNow API integrations

### Out of Scope
- Proprietary formulation or trade-secret documents
- Real-time ERP data (Phase 3 only)
- Customer order management or transactions

---

## 5. Stakeholders

| Stakeholder | Role | Primary Interest |
|------------|------|-----------------|
| VP Engineering | Executive sponsor | ROI, SME burden reduction |
| Plant Operations Managers | Primary internal users | Faster answers, safety compliance |
| EHS Director | Safety content owner | Version-controlled safety guidance |
| HR Director | HR content owner | Consistent policy delivery |
| IT Security Director | Infrastructure approver | SSO, data residency, security controls |
| Sales & Marketing | External stream sponsor | Customer satisfaction, revenue |
| Lowe's / Home Depot | External retail partners | Product information availability |
| Legal / Compliance | Risk reviewer | Audit trail, IP protection |
| Andy Sharma | Platform owner & tech lead | End-to-end delivery |

---

## 6. Functional Requirements

### FR-01: Natural Language Query Interface
- Users submit questions in plain English via web browser, mobile, and Microsoft Teams
- System returns answers within 3 seconds p95 (internal); 1.5 seconds p95 (external/CDN)
- Every answer includes inline source citations with document name, section, version, approval date

### FR-02: Dual-Stream Data Isolation
- Internal stream: accessible only via Azure Entra ID SSO (OC employee credentials)
- External stream: public access with optional account tiers for partner/pricing content
- Enforced at index level — internal documents never reachable through external API

### FR-03: Document-Level RBAC
- Internal: Azure AD group memberships gate which documents a user can receive answers from
- Site-specific isolation: operators at one site cannot access another site's confidential procedures
- Permission evaluated at retrieval time — never cached or bypassed

### FR-04: Knowledge Base Management
- Admin portal: ingestion status, content approval, freshness monitoring, gap detection
- Supported formats: PDF, DOCX, XLSX, PPTX, TXT, Markdown
- Auto-ingestion from SharePoint via Microsoft Graph API webhooks
- Queries returning low-confidence answers flagged automatically as knowledge gaps

### FR-05: Audit & Compliance
- Every query, retrieved document set, and generated answer logged immutably
- Logs retained minimum 3 years in WORM Azure Blob Storage
- Compliance dashboard for EHS and Legal review of AI-guided safety interactions

---

## 7. Non-Functional Requirements

| Requirement | Internal Target | External Target |
|-------------|----------------|-----------------|
| Availability | 99.9% | 99.95% |
| Query latency p95 | < 3 seconds | < 1.5 seconds (CDN) |
| Concurrent users | 18,000 tested | 5,000,000 design capacity |
| LLM | GPT-4o | GPT-4o-mini |
| Cost per query | < $0.035 | < $0.010 |
| Answer accuracy | > 92% | > 90% |
| Hallucination rate | < 2% | < 2% |

---

## 8. Success Metrics

| KPI | Phase 1 Target | Phase 2 Target |
|-----|---------------|----------------|
| Answer relevance score | > 90% | > 92% |
| Daily active users / enrolled | > 70% | > 65% |
| SME interruptions per site/week | < 25 (from ~80) | < 15 |
| New hire time-to-productivity | 6 weeks (from 10) | 5 weeks |
| External customer satisfaction | — | > 4.2 / 5.0 |
| Customer support deflection | — | > 40% |

---

## 9. Risk Register

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Azure OpenAI enterprise agreement delay | High | Evaluate AWS Bedrock Claude as fallback |
| IT SharePoint API access delay | Medium | Start with bulk manual upload; automate in Phase 1B |
| Low pilot adoption | Medium | Site champions program + executive mandate |
| Answer quality below threshold | Medium | Chunking tuning + SME feedback loop |
| Sensitive document ingestion | High | Legal-approved exclusion list + DLP scan on ingest |
| Cost overrun at 5M user scale | Medium | CDN caching + GPT-4o-mini routing + monthly budget gates |
