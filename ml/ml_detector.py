import joblib
import logging
from typing import Optional
from pathlib import Path
import warnings

# Suppress sklearn warnings if it complains about feature names
warnings.filterwarnings("ignore", category=UserWarning)

from firewall.models import Connection

class MLAnomalyDetector:
    def __init__(self, model_path: str = "ml/models/anomaly_detector.joblib"):
        self.model_path = model_path
        self.model = None
        self.logger = logging.getLogger("system")
        self._load_model()

    def _load_model(self):
        try:
            if Path(self.model_path).exists():
                self.model = joblib.load(self.model_path)
                self.logger.info(f"Successfully loaded ML anomaly detector from {self.model_path}")
            else:
                self.logger.warning(f"ML model not found at {self.model_path}. ML detection disabled.")
        except Exception as e:
            self.logger.error(f"Failed to load ML model: {e}")

    def evaluate_connection(self, conn: Connection) -> bool:
        """
        Evaluates a single connection. Returns True if anomalous, False otherwise.
        """
        if self.model is None:
            return False

        # Extract features
        try:
            features = [
                conn.duration,
                conn.packets_in,
                conn.packets_out,
                conn.bytes_in,
                conn.bytes_out,
                conn.avg_packet_size,
                conn.packet_rate,
                conn.byte_rate
            ]
            
            # predict expects a 2D array: [n_samples, n_features]
            prediction = self.model.predict([features])
            
            # IsolationForest returns -1 for outliers, 1 for inliers
            return prediction[0] == -1
        except Exception as e:
            self.logger.error(f"ML evaluation error: {e}")
            return False
