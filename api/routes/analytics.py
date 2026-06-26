from fastapi import APIRouter, Depends
from analytics.cache import AnalyticsCache
from api.models import StatsResponse, TopTalkersResponse, ProtocolStatsResponse
from api.security import get_api_key

router = APIRouter(prefix="/api/v1", tags=["Analytics"], dependencies=[Depends(get_api_key)])
cache = AnalyticsCache()

@router.get("/stats", response_model=StatsResponse, summary="Get Top-Level Stats")
def get_stats():
    traffic = cache.get("traffic_summaries") or {}
    return {
        "status": "success",
        "data": traffic
    }

@router.get("/top-talkers", response_model=TopTalkersResponse, summary="Get Top Talkers")
def get_top_talkers():
    return {
        "status": "success",
        "data": cache.get("top_talkers") or []
    }

@router.get("/top-attackers", response_model=TopTalkersResponse, summary="Get Top Attackers")
def get_top_attackers():
    return {
        "status": "success",
        "data": cache.get("top_attackers") or []
    }

@router.get("/threat-rankings", response_model=StatsResponse, summary="Get Threat Rankings")
def get_threat_rankings():
    return {
        "status": "success",
        "data": cache.get("threat_rankings") or []
    }

@router.get("/protocols", response_model=ProtocolStatsResponse, summary="Get Protocol Stats")
def get_protocols():
    return {
        "status": "success",
        "data": cache.get("protocol_statistics") or {}
    }

@router.get("/ports", response_model=ProtocolStatsResponse, summary="Get Port Stats")
def get_ports():
    return {
        "status": "success",
        "data": cache.get("port_statistics") or {}
    }
