from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.models import AlertsResponse, ConnectionsResponse
from api.security import get_api_key
from firewall.database import FirewallDatabase

router = APIRouter(prefix="/api/v1", tags=["Logs"], dependencies=[Depends(get_api_key)])
db = (
    FirewallDatabase()
)  # Uses singleton pattern if we set it up, else creates a new connection


@router.get("/alerts", response_model=AlertsResponse, summary="Get Paginated Alerts")
def get_alerts(
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
):
    alerts = db.query_alerts(severity=severity, alert_type=alert_type, limit=limit)
    return {"status": "success", "data": alerts}


@router.get(
    "/connections",
    response_model=ConnectionsResponse,
    summary="Get Paginated Connections",
)
def get_connections(limit: int = Query(50, ge=1, le=1000)):
    connections = db.query_connections(limit=limit)
    return {"status": "success", "data": connections}

@router.post("/alerts/{alert_id}/false-positive")
def mark_false_positive(alert_id: int):
    success = db.mark_alert_false_positive(alert_id)
    if success:
        return {"status": "success", "message": "Alert marked as false positive"}
    return {"status": "error", "message": "Alert not found"}, 404
