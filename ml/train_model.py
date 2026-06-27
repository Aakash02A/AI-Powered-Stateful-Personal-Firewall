import os
import json
import hashlib
from datetime import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import sklearn
import joblib
import argparse
from glob import glob


def generate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def train_anomaly_detector(dataset_pattern: str, model_dir: str):
    print(f"Loading datasets matching {dataset_pattern}...")
    
    csv_files = glob(dataset_pattern)
    if not csv_files:
        print("No datasets found!")
        return
        
    dfs = []
    dataset_hashes = {}
    for f in csv_files:
        dfs.append(pd.read_csv(f))
        dataset_hashes[os.path.basename(f)] = generate_file_hash(f)
        
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total samples loaded: {len(df)}")
    
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
    
    print(f"Fitting StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"Training IsolationForest with contamination={contamination_rate:.3f}...")
    model = IsolationForest(n_estimators=100, contamination=contamination_rate, random_state=42)
    model.fit(X_scaled)
    
    print("Evaluating model...")
    preds = model.predict(X_scaled)
    y_pred = [1 if p == -1 else 0 for p in preds]
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))
    
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "anomaly_detector_v1.0.joblib")
    scaler_path = os.path.join(model_dir, "scaler_v1.0.joblib")
    feature_schema_path = os.path.join(model_dir, "feature_schema.json")
    metadata_path = os.path.join(model_dir, "metadata.json")
    
    # Save Models
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Model saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")
    
    # Save Feature Schema
    feature_schema = {
        "features": feature_cols,
        "types": ["float" for _ in feature_cols],
        "version": "1.0"
    }
    with open(feature_schema_path, "w") as f:
        json.dump(feature_schema, f, indent=4)
        
    # Generate Metadata
    metadata = {
        "model_version": "v1.0",
        "training_date": datetime.utcnow().isoformat() + "Z",
        "dataset_name": "PCAP Generated Multi-Dataset",
        "dataset_hash": dataset_hashes,
        "feature_count": len(feature_cols),
        "training_samples": len(X),
        "sklearn_version": sklearn.__version__,
        "contamination": contamination_rate,
        "random_state": 42,
        "model_hash": generate_file_hash(model_path),
        "scaler_hash": generate_file_hash(scaler_path)
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Metadata and Feature Schema saved to {model_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ML Anomaly Detector")
    parser.add_argument("--datasets", type=str, default="ml/data/dataset_pcap_*.csv", help="Glob pattern for dataset CSVs")
    parser.add_argument("--model-dir", type=str, default="ml/models", help="Output directory for model artifacts")
    
    args = parser.parse_args()
    
    train_anomaly_detector(args.datasets, args.model_dir)
