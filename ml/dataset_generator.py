import csv
import os
import random
from pathlib import Path


def generate_flow(is_anomaly=False):
    """
    Generates a synthetic network flow.
    Returns a dict with features matching our Connection model.
    """
    if not is_anomaly:
        # Normal traffic: Web browsing, API calls, media streaming
        duration = random.uniform(0.1, 300.0)
        packets_in = random.randint(5, 500)
        packets_out = random.randint(5, 500)
        bytes_in = packets_in * random.uniform(100, 1500)
        bytes_out = packets_out * random.uniform(60, 800)
    else:
        # Anomalous traffic
        anomaly_type = random.choice(["port_scan", "ddos", "exfiltration"])
        if anomaly_type == "port_scan":
            duration = random.uniform(0.01, 2.0)
            packets_in = 1
            packets_out = random.randint(0, 1)
            bytes_in = random.uniform(40, 60)
            bytes_out = random.uniform(0, 60)
        elif anomaly_type == "ddos":
            duration = random.uniform(1.0, 60.0)
            packets_in = random.randint(5000, 50000)
            packets_out = random.randint(0, 100)
            bytes_in = packets_in * random.uniform(40, 120)
            bytes_out = packets_out * random.uniform(40, 120)
        elif anomaly_type == "exfiltration":
            duration = random.uniform(60.0, 3600.0)
            packets_in = random.randint(100, 1000)
            packets_out = random.randint(10000, 500000)
            bytes_in = packets_in * random.uniform(60, 200)
            bytes_out = packets_out * random.uniform(1000, 1500)

    total_packets = packets_in + packets_out
    total_bytes = bytes_in + bytes_out
    
    # Avoid division by zero
    duration = max(duration, 0.001)
    total_packets = max(total_packets, 1)

    avg_packet_size = total_bytes / total_packets
    packet_rate = total_packets / duration
    byte_rate = total_bytes / duration

    return {
        "duration": round(duration, 4),
        "packets_in": packets_in,
        "packets_out": packets_out,
        "bytes_in": round(bytes_in, 2),
        "bytes_out": round(bytes_out, 2),
        "avg_packet_size": round(avg_packet_size, 2),
        "packet_rate": round(packet_rate, 2),
        "byte_rate": round(byte_rate, 2),
        "label": 1 if is_anomaly else 0,
    }


def generate_dataset(num_samples: int, anomaly_ratio: float, output_path: str):
    """
    Generates a dataset and saves it to a CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fieldnames = [
        "duration",
        "packets_in",
        "packets_out",
        "bytes_in",
        "bytes_out",
        "avg_packet_size",
        "packet_rate",
        "byte_rate",
        "label",
    ]
    
    num_anomalies = int(num_samples * anomaly_ratio)
    num_normal = num_samples - num_anomalies

    print(f"Generating {num_normal} normal flows and {num_anomalies} anomalous flows...")
    
    samples = []
    for _ in range(num_normal):
        samples.append(generate_flow(is_anomaly=False))
    for _ in range(num_anomalies):
        samples.append(generate_flow(is_anomaly=True))
        
    random.shuffle(samples)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(samples)
        
    print(f"Dataset saved to {output_path}")


if __name__ == "__main__":
    output_csv = Path("ml/data/dataset.csv")
    generate_dataset(num_samples=10000, anomaly_ratio=0.1, output_path=str(output_csv))
