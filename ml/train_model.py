import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path

def train_anomaly_detector(dataset_path: str, model_path: str):
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    feature_cols = [
        "duration", "packets_in", "packets_out", 
        "bytes_in", "bytes_out", "avg_packet_size", 
        "packet_rate", "byte_rate"
    ]
    
    X = df[feature_cols]
    y_true = df["label"] # 0 for normal, 1 for anomaly
    
    contamination_rate = sum(y_true) / len(y_true)
    if contamination_rate == 0:
        contamination_rate = 0.05
    elif contamination_rate > 0.5:
        contamination_rate = 0.5
    
    print(f"Training IsolationForest with contamination={contamination_rate:.3f}...")
    
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", IsolationForest(n_estimators=100, contamination=contamination_rate, random_state=42))
    ])
    
    pipeline.fit(X)
    
    print("Evaluating model...")
    # Predict: 1 (normal), -1 (anomaly)
    preds = pipeline.predict(X)
    
    # Convert predictions to our label format: 0 (normal), 1 (anomaly)
    y_pred = [1 if p == -1 else 0 for p in preds]
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    dataset_csv = Path("ml/data/dataset.csv")
    model_out = Path("ml/models/anomaly_detector.joblib")
    train_anomaly_detector(str(dataset_csv), str(model_out))
