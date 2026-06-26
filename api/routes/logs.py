from fastapi import APIRouter, Query, Depends
from firewall.database import FirewallDatabase
from typing import Optional
from api.models import AlertsResponse, ConnectionsResponse
from api.security import get_api_key

router = APIRouter(prefix="/api/v1", tags=["Logs"], dependencies=[Depends(get_api_key)])
db = FirewallDatabase()  # Uses singleton pattern if we set it up, else creates a new connection

@router.get("/alerts", response_model=AlertsResponse, summary="Get Paginated Alerts")
def get_alerts(severity: Optional[str] = Query(None), alert_type: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=1000)):
    alerts = db.query_alerts(severity=severity, alert_type=alert_type, limit=limit)
    return {
        "status": "success",
        "data": alerts
    }

@router.get("/connections", response_model=ConnectionsResponse, summary="Get Paginated Connections")
def get_connections(limit: int = Query(50, ge=1, le=1000)):
    connections = db.query_connections(limit=limit)
    return {
        "status": "success",
        "data": connections
    }
