"""
Threat Scoring Engine.
Combines scores from rule engine, ML engine, and threat intel
into a unified 0–100 threat score.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Weight configuration (must sum to 1.0)
_WEIGHTS = {
    "rule_score": 0.35,
    "ml_score": 0.30,
    "threat_intel_score": 0.25,
    "behavior_score": 0.10,
}

_SEVERITY_MAP = {
    "critical": 95,
    "high": 75,
    "medium": 50,
    "low": 20,
    "info": 5,
}


def severity_to_score(severity: str) -> float:
    return _SEVERITY_MAP.get(severity.lower(), 0)


def score_to_severity(score: float) -> str:
    if score >= 81:
        return "critical"
    if score >= 51:
        return "high"
    if score >= 21:
        return "medium"
    return "low"


class ThreatScoringEngine:
    """
    Aggregates scores from multiple detection sources into a single threat score.

    Formula:
        threat_score = Σ(source_score × weight) clamped to [0, 100]
    """

    def compute(
        self,
        *,
        rule_matches: list[dict[str, Any]],
        ml_score: float = 0.0,
        threat_intel_matches: list[dict[str, Any]],
        behavior_score: float = 0.0,
    ) -> dict[str, Any]:
        """
        Compute a composite threat score.
        Returns score, severity, and contributing factors.
        """
        # Rule score: max severity among matching rules
        rule_score = 0.0
        if rule_matches:
            rule_score = max(
                severity_to_score(m.get("severity", "low")) for m in rule_matches
            )

        # Threat intel score: boost by 20 per match, capped at 100
        ti_score = min(len(threat_intel_matches) * 20, 100.0)

        # Weighted composite
        raw_score = (
            rule_score * _WEIGHTS["rule_score"]
            + ml_score * _WEIGHTS["ml_score"]
            + ti_score * _WEIGHTS["threat_intel_score"]
            + behavior_score * _WEIGHTS["behavior_score"]
        )

        final_score = round(min(max(raw_score, 0.0), 100.0), 2)

        return {
            "threat_score": final_score,
            "severity": score_to_severity(final_score),
            "components": {
                "rule_score": round(rule_score, 2),
                "ml_score": round(ml_score, 2),
                "threat_intel_score": round(ti_score, 2),
                "behavior_score": round(behavior_score, 2),
            },
        }
