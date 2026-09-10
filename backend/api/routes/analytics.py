from fastapi import APIRouter, Depends

from api.models import ProtocolStatsResponse, StatsResponse, TopTalkersResponse
from api.security import get_api_key
from firewall.database import FirewallDatabase
from api.config import settings

router = APIRouter(
    prefix="/api/v1", tags=["Analytics"], dependencies=[Depends(get_api_key)]
)
db = FirewallDatabase(db_path=settings.DATABASE_URL)


def _connections():
    return db.query_connections(limit=10000)


def _alerts():
    return db.query_alerts(limit=10000)


@router.get("/stats", response_model=StatsResponse, summary="Get Top-Level Stats")
def get_stats():
    connections = _connections()
    alerts = _alerts()
    blocked = sum(
        1 for alert in alerts if alert.get("action_taken", "").lower() in {"block", "blocked", "drop", "dropped"}
    )
    return {
        "status": "success",
        "data": {
            "active_connections": sum(1 for connection in connections if not connection.get("end_time")),
            "total_connections": len(connections),
            "blocked_connections": blocked,
            "total_alerts": len(alerts),
        },
    }


@router.get(
    "/top-talkers", response_model=TopTalkersResponse, summary="Get Top Talkers"
)
def get_top_talkers():
    totals = {}
    for connection in _connections():
        src_ip = connection.get("src_ip")
        totals[src_ip] = totals.get(src_ip, 0) + (connection.get("bytes_out") or 0)
    data = [
        {"src_ip": ip, "total_bytes": total}
        for ip, total in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:10]
    ]
    return {"status": "success", "data": data}


@router.get(
    "/top-attackers", response_model=TopTalkersResponse, summary="Get Top Attackers"
)
def get_top_attackers():
    totals = {}
    for alert in _alerts():
        src_ip = alert.get("src_ip")
        totals[src_ip] = totals.get(src_ip, 0) + 1
    return {
        "status": "success",
        "data": [{"src_ip": ip, "alert_count": count} for ip, count in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:10]],
    }


@router.get(
    "/threat-rankings", response_model=StatsResponse, summary="Get Threat Rankings"
)
def get_threat_rankings():
    return get_top_attackers()


@router.get(
    "/protocols", response_model=ProtocolStatsResponse, summary="Get Protocol Stats"
)
def get_protocols():
    protocols = {}
    for connection in _connections():
        protocol = connection.get("protocol", "unknown")
        protocols[protocol] = protocols.get(protocol, 0) + 1
    return {"status": "success", "data": protocols}


@router.get("/ports", response_model=ProtocolStatsResponse, summary="Get Port Stats")
def get_ports():
    ports = {}
    for connection in _connections():
        port = str(connection.get("dst_port", "unknown"))
        ports[port] = ports.get(port, 0) + 1
    return {"status": "success", "data": ports}
