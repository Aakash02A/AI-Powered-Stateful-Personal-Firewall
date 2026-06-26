from fastapi import APIRouter
from firewall.database import FirewallDatabase
from analytics.cache import AnalyticsCache
from firewall.queue_manager import QueueManager
import time

router = APIRouter(prefix="/health", tags=["Health"])

cache = AnalyticsCache()
queue_manager = QueueManager()
db = FirewallDatabase()
START_TIME = time.time()

@router.get("/live", summary="Liveness Probe")
def live():
    return {"status": "ok"}

@router.get("/ready", summary="Readiness Probe")
def ready():
    # Check if DB is accessible by doing a quick query
    try:
        db.query_connections(limit=1)
        db_ok = True
    except Exception:
        db_ok = False
        
    return {
        "status": "ready" if db_ok else "not_ready",
        "database_connected": db_ok,
    }

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
