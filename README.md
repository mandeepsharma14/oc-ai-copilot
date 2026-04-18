# OC AI Copilot — Enterprise Knowledge Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)

> **Enterprise-scale dual-stream AI knowledge platform** for Owens Corning.
> Serves 25,000+ internal employees (SOPs, safety, engineering, HR) and up to 5 million
> external customers (product specs, pricing, installation guides).

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/mandeepsharma14/oc-ai-copilot.git
cd oc-ai-copilot

# 2. Setup
bash infrastructure/scripts/setup.sh

# 3. Edit .env with your Azure credentials
cp .env.example .env && nano .env

# 4. Run locally
docker-compose up --build

# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
# API Docs → http://localhost:8000/docs
```

---

## Project Structure

```
oc-ai-copilot/
├── backend/                    Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/   REST route handlers
│   │   ├── core/               Config, security, logging
│   │   ├── models/             Pydantic schemas + DB models
│   │   ├── services/           Chat, document, audit services
│   │   ├── rag/                RAG pipeline, retriever, reranker
│   │   └── ingestion/          Document ingestion pipeline
│   └── tests/                  Pytest test suite
├── frontend/                   Next.js 14 TypeScript frontend
│   └── src/
│       ├── components/         Chat, admin, KB, shared UI
│       ├── pages/              Next.js pages
│       ├── hooks/              Custom React hooks
│       ├── store/              Zustand state
│       └── types/              TypeScript definitions
├── docs/
│   ├── brd/BRD.md              Business Requirements Document
│   ├── hld/HLD.md              High-Level Architecture
│   ├── lld/LLD.md              Low-Level Architecture
│   └── DEPLOYMENT.md           Step-by-step deployment guide
├── infrastructure/
│   ├── terraform/              Azure IaC (all resources)
│   ├── kubernetes/             K8s deployment manifests
│   └── scripts/                Setup and seed scripts
├── .github/workflows/          CI/CD pipelines
├── docker-compose.yml          Local development
└── .env.example                Environment variables template
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI Orchestration | LangGraph, LangChain |
| RAG | LlamaIndex, Azure AI Search (hybrid BM25 + vector) |
| LLM | Azure OpenAI GPT-4o (internal) / GPT-4o-mini (external) |
| Embeddings | Azure OpenAI text-embedding-3-large |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Auth Internal | Azure Entra ID + MSAL |
| Auth External | OAuth 2.0 / API keys |
| Cache | Redis (Azure Cache for Redis) |
| Session DB | Azure Cosmos DB |
| Audit DB | Azure SQL (immutable ledger) |
| Storage | Azure Blob Storage |
| Orchestration | Azure Kubernetes Service (AKS) |
| CI/CD | GitHub Actions |
| IaC | Terraform |
| Monitoring | Azure Monitor + Application Insights |

---

## Documentation

| File | Description |
|------|-------------|
| [BRD](docs/brd/BRD.md) | Business requirements, stakeholders, ROI model |
| [HLD](docs/hld/HLD.md) | Architecture, security, scalability design |
| [LLD](docs/lld/LLD.md) | Index schema, RAG pipeline, API spec, DB schema |
| [Deployment](docs/DEPLOYMENT.md) | Full 12-step Azure deployment guide |

---

## License

MIT License — see [LICENSE](LICENSE)

**Built by Andy Sharma** · Sr. Engineering Leader, Owens Corning
[linkedin.com/in/mandeepsharma14](https://linkedin.com/in/mandeepsharma14)
