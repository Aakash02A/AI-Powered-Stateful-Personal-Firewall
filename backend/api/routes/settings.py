from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.config import settings
from api.security import get_api_key


router = APIRouter(
    prefix="/api/v1/settings",
    tags=["Settings"],
    dependencies=[Depends(get_api_key)],
)


class SettingsUpdate(BaseModel):
    monitor_only: bool = Field(...)
    rate_limit: str = Field(..., min_length=3)


def _settings_payload():
    return {
        "monitor_only": settings.MONITOR_ONLY,
        "rate_limit": settings.RATE_LIMIT,
        "ml_enabled": True,
        "threat_intel_configured": bool(getattr(settings, "ABUSEIPDB_API_KEY", "")),
    }


@router.get("")
def get_settings():
    return {"status": "success", "data": _settings_payload()}


@router.put("")
def update_settings(payload: SettingsUpdate):
    settings.MONITOR_ONLY = payload.monitor_only
    settings.RATE_LIMIT = payload.rate_limit
    return {"status": "success", "data": _settings_payload()}