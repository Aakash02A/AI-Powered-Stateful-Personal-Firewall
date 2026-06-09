"""
AI Analysis router — incident summary, root cause, MITRE mapping.
"""
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.agents.soc_analyst import SOCAnalystAgent

logger = logging.getLogger(__name__)
router = APIRouter()
_agent = SOCAnalystAgent()


class AnalyzeRequest(BaseModel):
    incident_id: str
    alert_data: dict[str, Any]
    context: dict[str, Any] = {}


class AnalyzeResponse(BaseModel):
    incident_id: str
    summary: str
    root_cause: str
    mitre_tactics: list[str]
    mitre_techniques: list[str]
    attack_narrative: str
    recommended_actions: list[str]
    risk_level: str
    confidence: float


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze an incident with AI — generates summary, MITRE mapping, and recommendations",
)
async def analyze_incident(body: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = await _agent.analyze(
            incident_id=body.incident_id,
            alert_data=body.alert_data,
            context=body.context,
        )
        return AnalyzeResponse(**result)
    except Exception as exc:
        logger.error("AI analysis failed for incident %s: %s", body.incident_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis failed. Please retry.",
        )
