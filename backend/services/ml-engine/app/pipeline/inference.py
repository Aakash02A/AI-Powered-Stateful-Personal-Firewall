"""
ML Inference pipeline.
Runs anomaly detection and malware classification on normalized events.

Models:
- Anomaly: Isolation Forest (unsupervised, no labels needed)
- Classifier: XGBoost malware probability
"""
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# These will be loaded from serialized model files in production
# For now they are stubs that return 0.0
_anomaly_model = None
_classifier_model = None


def _extract_features(event: dict[str, Any]) -> np.ndarray:
    """
    Extract a fixed-length feature vector from an ECS event.
    Features are chosen to be model-agnostic numeric representations.
    """
    features = [
        # Process features
        len(event.get("process", {}).get("command_line", "") or ""),
        int(bool(event.get("process", {}).get("name"))),
        event.get("process", {}).get("pid", 0) or 0,
        # Network features
        int(bool(event.get("destination", {}).get("ip"))),
        event.get("destination", {}).get("port", 0) or 0,
        # File features
        len(event.get("file", {}).get("path", "") or ""),
        # Scoring features from prior engines
        event.get("sentinelx", {}).get("rule_score", 0.0),
    ]
    return np.array(features, dtype=np.float32)


async def run_inference(event: dict[str, Any]) -> dict[str, float]:
    """
    Run all ML models against an event and return scores.
    Returns:
        anomaly_score: 0.0-1.0 (higher = more anomalous)
        malware_probability: 0.0-1.0
    """
    features = _extract_features(event)

    # Anomaly detection (Isolation Forest)
    anomaly_score = 0.0
    if _anomaly_model is not None:
        raw = _anomaly_model.decision_function(features.reshape(1, -1))[0]
        # Isolation Forest scores: more negative = more anomalous
        # Normalize to [0, 1]
        anomaly_score = float(max(0.0, min(1.0, -raw)))

    # Malware classification (XGBoost)
    malware_probability = 0.0
    if _classifier_model is not None:
        proba = _classifier_model.predict_proba(features.reshape(1, -1))[0]
        malware_probability = float(proba[1])  # probability of class=1 (malicious)

    return {
        "anomaly_score": round(anomaly_score, 4),
        "malware_probability": round(malware_probability, 4),
        "ml_score": round(max(anomaly_score, malware_probability) * 100, 2),
    }
