import sys
import os
import threading
import time
import math
import shutil
from pathlib import Path
import json
from datetime import datetime

from firewall.models import Connection
from ml.ml_detector import MLAnomalyDetector

def create_mock_conn(duration=10.0, pkts_in=10, pkts_out=10, bytes_in=1000, bytes_out=1000):
    conn = Connection(
        src_ip="192.168.1.1", src_port=12345, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", state="ESTABLISHED",
        creation_time=datetime.now(), last_activity=datetime.now()
    )
    conn.duration = duration
    conn.packets_in = pkts_in
    conn.packets_out = pkts_out
    conn.bytes_in = bytes_in
    conn.bytes_out = bytes_out
    conn.avg_packet_size = (bytes_in + bytes_out) / (pkts_in + pkts_out) if (pkts_in + pkts_out) > 0 else 0
    conn.packet_rate = (pkts_in + pkts_out) / duration if duration > 0 else 0
    conn.byte_rate = (bytes_in + bytes_out) / duration if duration > 0 else 0
    return conn

def test_missing_model():
    print("Testing missing model...")
    detector = MLAnomalyDetector(model_dir="invalid_dir_does_not_exist")
    conn = create_mock_conn()
    is_anomaly, score = detector.evaluate_connection(conn)
    if is_anomaly or score != 0.0:
        print("FAIL: Missing model did not fail gracefully.")
        return False
    print("PASS: Missing model handled gracefully.")
    return True

def test_corrupt_model():
    print("Testing corrupt model...")
    os.makedirs("ml/test_models", exist_ok=True)
    with open("ml/test_models/anomaly_detector_v1.0.joblib", "w") as f:
        f.write("corrupted data")
    with open("ml/test_models/scaler_v1.0.joblib", "w") as f:
        f.write("corrupted data")
    with open("ml/test_models/feature_schema.json", "w") as f:
        f.write("corrupted data")
        
    detector = MLAnomalyDetector(model_dir="ml/test_models")
    conn = create_mock_conn()
    is_anomaly, score = detector.evaluate_connection(conn)
    
    shutil.rmtree("ml/test_models")
    
    if is_anomaly or score != 0.0:
        print("FAIL: Corrupt model did not fail gracefully.")
        return False
    print("PASS: Corrupt model handled gracefully.")
    return True

def test_invalid_features():
    print("Testing invalid features...")
    detector = MLAnomalyDetector()
    conn = create_mock_conn(duration=float('inf'), pkts_in=float('nan'), bytes_in=-100)
    is_anomaly, score = detector.evaluate_connection(conn)
    # sklearn might throw ValueError, detector should catch it and return False, 0.0
    if is_anomaly or score != 0.0:
        print("FAIL: Invalid features did not fail gracefully.")
        return False
    print("PASS: Invalid features handled gracefully.")
    return True

def test_concurrent_inference():
    print("Testing concurrent inference...")
    detector = MLAnomalyDetector()
    conn = create_mock_conn()
    
    success = [True] * 50
    
    def worker(idx):
        try:
            is_anomaly, score = detector.evaluate_connection(conn)
        except Exception as e:
            print(f"Worker {idx} failed: {e}")
            success[idx] = False
            
    threads = []
    for i in range(50):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    if not all(success):
        print("FAIL: Concurrent inference failed.")
        return False
    print("PASS: Concurrent inference handled gracefully.")
    return True

def main():
    print("=== ML Robustness Testing ===")
    results = [
        test_missing_model(),
        test_corrupt_model(),
        test_invalid_features(),
        test_concurrent_inference()
    ]
    
    if all(results):
        print("PASS: All robustness tests passed.")
        sys.exit(0)
    else:
        print("FAIL: One or more robustness tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
