"""Admin dashboard endpoints — metrics, usage, cost."""
from datetime import datetime
from fastapi import APIRouter, Depends
from app.models.schemas import AdminMetrics
from app.core.security import get_current_user

router = APIRouter()


@router.get(
    "/metrics",
    response_model=AdminMetrics,
    summary="Get platform usage and health metrics",
)
async def get_metrics(current_user: dict = Depends(get_current_user)) -> AdminMetrics:
    # In production: query Azure Monitor / Application Insights
    # Returning realistic mock data for development
    return AdminMetrics(
        total_queries_today  = 3412,
        accuracy_rate        = 0.941,
        active_users         = 2847,
        avg_latency_p95_ms   = 2100,
        uptime_percent       = 99.97,
        cache_hit_rate       = 0.41,
        cost_per_query_usd   = 0.028,
        documents_indexed    = 4847,
        knowledge_gaps_count = 4,
    )


@router.get("/usage-by-domain", summary="Query volume broken down by knowledge domain")
async def usage_by_domain(current_user: dict = Depends(get_current_user)):
    return {
        "data": [
            {"domain": "Safety & EHS",          "queries": 987,  "pct": 28.9},
            {"domain": "Engineering",            "queries": 743,  "pct": 21.8},
            {"domain": "Quality & Mfg",          "queries": 612,  "pct": 17.9},
            {"domain": "Maintenance",            "queries": 489,  "pct": 14.3},
            {"domain": "HR & People",            "queries": 298,  "pct": 8.7},
            {"domain": "IT & Security",          "queries": 283,  "pct": 8.3},
        ],
        "as_of": datetime.utcnow().isoformat(),
    }


@router.get("/knowledge-gaps", summary="Queries that returned low-confidence answers")
async def knowledge_gaps(current_user: dict = Depends(get_current_user)):
    return {
        "gaps": [
            {"query": "Paroc panel fire rating",       "count": 14, "severity": "high"},
            {"query": "Foamglas sub-zero install SOP", "count": 9,  "severity": "medium"},
            {"query": "New SAP PM module process",     "count": 7,  "severity": "medium"},
            {"query": "EcoTouch vapor retarder spec",  "count": 4,  "severity": "low"},
        ]
    }


@router.get("/cost", summary="Azure OpenAI cost dashboard")
async def cost_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "spend_mtd_usd":         2841,
        "cost_per_query_usd":    0.028,
        "gpt4o_mini_routing_pct":19,
        "projected_monthly_usd": 5200,
        "budget_remaining_usd":  4800,
        "cache_hit_rate":        0.41,
    }
