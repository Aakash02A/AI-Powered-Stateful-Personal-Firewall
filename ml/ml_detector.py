import joblib
import logging
import json

from pathlib import Path
import warnings

# Suppress sklearn warnings if it complains about feature names
warnings.filterwarnings("ignore", category=UserWarning)

from firewall.models import Connection

class MLAnomalyDetector:
    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_schema = None
        self.logger = logging.getLogger("system")
        self._load_artifacts()

    def _load_artifacts(self):
        try:
            model_path = self.model_dir / "anomaly_detector_v1.0.joblib"
            scaler_path = self.model_dir / "scaler_v1.0.joblib"
            schema_path = self.model_dir / "feature_schema.json"
            
            if model_path.exists() and scaler_path.exists() and schema_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                with open(schema_path, "r") as f:
                    self.feature_schema = json.load(f)
                self.logger.info(f"Successfully loaded ML anomaly detector from {self.model_dir}")
            else:
                self.logger.warning(f"ML artifacts missing in {self.model_dir}. ML detection disabled.")
        except Exception as e:
            self.logger.error(f"Failed to load ML artifacts: {e}")

    def evaluate_connection(self, conn: Connection) -> tuple[bool, float]:
        """
        Evaluates a single connection. Returns (is_anomalous, anomaly_score).
        """
        if self.model is None or self.scaler is None or self.feature_schema is None:
            return False, 0.0

        # Extract features enforcing strict schema ordering
        try:
            features = []
            for feat_name in self.feature_schema["features"]:
                if not hasattr(conn, feat_name):
                    self.logger.error(f"Missing feature {feat_name} on Connection object.")
                    return False, 0.0
                features.append(float(getattr(conn, feat_name)))
            
            # predict expects a 2D array: [n_samples, n_features]
            scaled_features = self.scaler.transform([features])
            prediction = self.model.predict(scaled_features)
            
            # IsolationForest returns -1 for outliers, 1 for inliers
            is_anomaly = prediction[0] == -1
            
            # Score is negative for anomalies, positive for normal
            score = 0.0
            if hasattr(self.model, "decision_function"):
                score = float(self.model.decision_function(scaled_features)[0])
                
            return is_anomaly, score
        except Exception as e:
            self.logger.error(f"ML evaluation error: {e}")
            return False, 0.0

    def evaluate_batch(self, conns: list[Connection]) -> list[tuple[bool, float]]:
        """
        Evaluates a batch of connections for performance testing.
        """
        if self.model is None or self.scaler is None or self.feature_schema is None:
            return [(False, 0.0) for _ in conns]
            
        try:
            batch_features = []
            for conn in conns:
                features = []
                for feat_name in self.feature_schema["features"]:
                    features.append(float(getattr(conn, feat_name, 0.0)))
                batch_features.append(features)
                
            scaled_features = self.scaler.transform(batch_features)
            predictions = self.model.predict(scaled_features)
            scores = self.model.decision_function(scaled_features) if hasattr(self.model, "decision_function") else [0.0]*len(conns)
            
            results = []
            for p, s in zip(predictions, scores):
                results.append((p == -1, float(s)))
            return results
        except Exception as e:
            self.logger.error(f"ML batch evaluation error: {e}")
            return [(False, 0.0) for _ in conns]
