from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Any
import os
import time

from api.security import get_api_key
from firewall.database import FirewallDatabase

router = APIRouter(prefix="/api/v1/ml", tags=["ML"], dependencies=[Depends(get_api_key)])
db = FirewallDatabase()

class MLStatus(BaseModel):
    model_version: str
    status: str
    last_trained: float | None
    file_size_bytes: int | None
    enabled: bool

@router.get("/status", response_model=MLStatus)
def get_ml_status():
    """Get ML model status"""
    model_path = Path("ml/models/anomaly_detector_v1.0.joblib")
    if model_path.exists():
        stat = model_path.stat()
        return MLStatus(
            model_version="v1.0",
            status="loaded",
            last_trained=stat.st_mtime,
            file_size_bytes=stat.st_size,
            enabled=True
        )
    else:
        return MLStatus(
            model_version="none",
            status="missing",
            last_trained=None,
            file_size_bytes=None,
            enabled=False
        )

@router.get("/metrics")
def get_ml_metrics():
    """Get ML performance metrics"""
    # For now, we mock the overall historical metrics since we don't have an evaluation table.
    # In a full deployment, these could be updated dynamically from robust evaluation runs.
    return {
        "status": "success",
        "data": {
            "anomaly_detection_rate": 0.87,
            "false_positive_rate": 0.032,
            "average_latency_ms": 12.5,
        }
    }

@router.get("/anomaly-scores")
def get_anomaly_scores(hours: int = 24):
    """Get recent anomaly scores from database"""
    # Query alerts table for "ml_anomaly" type
    alerts = db.query_alerts(alert_type="ml_anomaly", limit=100)
    
    # Extract the score from the description or details. 
    # Current ML alerts description format: "ML Anomaly (score: 0.950) detected..."
    scores = []
    for alert in alerts:
        score = 0.0
        desc = alert.get("description", "")
        if "(score: " in desc:
            try:
                # Extract score like "0.950" from "ML Anomaly (score: 0.950) detected..."
                score_str = desc.split("(score: ")[1].split(")")[0]
                score = float(score_str)
            except Exception:
                pass
        
        scores.append({
            "timestamp": alert.get("timestamp"),
            "score": score,
            "src_ip": alert.get("src_ip"),
            "dst_ip": alert.get("dst_ip"),
        })
    
    # Reverse to have chronological order for charts
    scores.reverse()
    
    return {
        "status": "success",
        "data": scores
    }
