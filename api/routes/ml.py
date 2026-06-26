from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import os
import time

router = APIRouter(prefix="/ml", tags=["ML"])

class MLStatus(BaseModel):
    model_version: str
    status: str
    last_trained: float | None
    file_size_bytes: int | None

@router.get("/status", response_model=MLStatus)
def get_ml_status():
    model_path = Path("ml/models/anomaly_detector_v1.0.joblib")
    if model_path.exists():
        stat = model_path.stat()
        return MLStatus(
            model_version="v1.0",
            status="loaded",
            last_trained=stat.st_mtime,
            file_size_bytes=stat.st_size
        )
    else:
        return MLStatus(
            model_version="none",
            status="missing",
            last_trained=None,
            file_size_bytes=None
        )
