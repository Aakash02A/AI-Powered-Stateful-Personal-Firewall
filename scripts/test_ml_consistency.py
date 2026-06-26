import sys
import pandas as pd
from datetime import datetime
from ml.ml_detector import MLAnomalyDetector
from firewall.models import Connection

def create_mock_conn_from_row(row):
    conn = Connection(
        src_ip="1.1.1.1", src_port=123, dst_ip="2.2.2.2", dst_port=456, protocol="TCP", state="ESTABLISHED",
        creation_time=datetime.now(), last_activity=datetime.now()
    )
    for k, v in row.items():
        if hasattr(conn, k):
            setattr(conn, k, v)
    return conn

def main():
    print("=== ML Consistency Testing ===")
    
    detector1 = MLAnomalyDetector()
    if detector1.model is None:
        print("FAIL: Model not loaded.")
        sys.exit(1)
        
    df = pd.read_csv("ml/data/dataset_pcap_0.csv", nrows=100)
    conns = [create_mock_conn_from_row(row) for _, row in df.iterrows()]
    
    print("Evaluating with first detector instance...")
    results1 = [detector1.evaluate_connection(c) for c in conns]
    
    print("Reloading model (second detector instance)...")
    detector2 = MLAnomalyDetector()
    
    print("Evaluating with second detector instance...")
    results2 = [detector2.evaluate_connection(c) for c in conns]
    
    mismatches = 0
    for i, (r1, r2) in enumerate(zip(results1, results2)):
        if r1[0] != r2[0] or abs(r1[1] - r2[1]) > 1e-6:
            print(f"Mismatch at index {i}: {r1} != {r2}")
            mismatches += 1
            
    if mismatches > 0:
        print(f"FAIL: Found {mismatches} inconsistent predictions.")
        sys.exit(1)
        
    print("PASS: Predictions are 100% consistent across model reloads.")
    sys.exit(0)

if __name__ == "__main__":
    main()
