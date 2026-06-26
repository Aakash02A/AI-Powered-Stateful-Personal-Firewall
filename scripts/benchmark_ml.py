import sys
import time
import psutil
import os
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
    print("=== ML Benchmark ===")
    
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / (1024 * 1024)
    
    start_load = time.time()
    detector = MLAnomalyDetector()
    load_time = time.time() - start_load
    
    mem_after = process.memory_info().rss / (1024 * 1024)
    print(f"Model Loading Time: {load_time:.4f} seconds")
    print(f"Model Memory Footprint: {mem_after - mem_before:.2f} MB")
    
    if detector.model is None:
        print("FAIL: Model not loaded.")
        sys.exit(1)
        
    df = pd.read_csv("ml/data/dataset_pcap_0.csv", nrows=10000)
    conns = [create_mock_conn_from_row(row) for _, row in df.iterrows()]
    
    print("\n--- Single Inference Benchmark ---")
    start_single = time.time()
    for c in conns:
        detector.evaluate_connection(c)
    single_time = time.time() - start_single
    single_throughput = len(conns) / single_time
    print(f"Processed 10,000 flows sequentially in {single_time:.4f} seconds")
    print(f"Throughput: {single_throughput:.2f} flows/sec")
    
    print("\n--- Batch Inference Benchmark ---")
    start_batch = time.time()
    detector.evaluate_batch(conns)
    batch_time = time.time() - start_batch
    batch_throughput = len(conns) / batch_time
    print(f"Processed 10,000 flows in batch in {batch_time:.4f} seconds")
    print(f"Throughput: {batch_throughput:.2f} flows/sec")
    print(f"Speedup vs Single: {batch_throughput / single_throughput:.2f}x")
    
    print("\nPASS: Benchmarks completed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
