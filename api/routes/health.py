import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from analytics.cache import AnalyticsCache
from firewall.database import FirewallDatabase
from firewall.queue_manager import QueueManager

router = APIRouter(prefix="/health", tags=["Health"])

cache = AnalyticsCache()
queue_manager = QueueManager()
db = FirewallDatabase()
START_TIME = time.time()


@router.get("/threads", summary="Check background thread health")
async def health_threads(request: Request):
    if not hasattr(request.app.state, "firewall"):
        raise HTTPException(status_code=503, detail="Firewall not initialized")

    health = request.app.state.firewall.health_monitor.check_health()
    critical = ["PacketCapture", "DBWriter"]
    all_good = all(
        health.get(name, {}).get("alive", False) for name in critical if name in health
    )

    status_code = 200 if all_good else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_good else "degraded",
            "threads": health,
            "timestamp": datetime.now().isoformat(),
        },
    )


@router.get("/live", summary="Liveness Probe")
async def live(request: Request):
    if not hasattr(request.app.state, "firewall"):
        return {"status": "ok"}

    health = request.app.state.firewall.health_monitor.check_health()
    if health.get("PacketCapture", {}).get("alive", False):
        return {"status": "live"}
    else:
        raise HTTPException(status_code=503, detail="Packet capture thread dead")


@router.get("/ready", summary="Readiness Probe")
async def ready(request: Request):
    if hasattr(request.app.state, "firewall"):
        health = request.app.state.firewall.health_monitor.check_health()
        if not all(t["alive"] for t in health.values()):
            raise HTTPException(status_code=503, detail="Not all threads ready")

    # Check if DB is accessible by doing a quick query
    try:
        db.query_connections(limit=1)
        db_ok = True
    except Exception:
        db_ok = False

    if not db_ok:
        raise HTTPException(status_code=503, detail="Database not connected")

    return {"status": "ready", "database_connected": True}


@router.get("/startup", summary="Startup Probe")
def startup():
    # For now, just returns ok if the app is up. We can add background daemon checks later.
    return {"status": "started"}


@router.get("/metrics", summary="System Metrics")
def metrics():
    uptime = time.time() - START_TIME
    return {
        "uptime_seconds": uptime,
        "queue_size": queue_manager.qsize(),
        # For cache age, we'd need to store the last refresh timestamp in the cache singleton
    }
