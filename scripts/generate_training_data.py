import csv
import random
import os


def generate_benign_traffic(num_samples):
    data = []
    for _ in range(num_samples):
        # Normal web browsing (short to medium duration, higher bytes out (download))
        duration = random.uniform(0.1, 120.0)
        packets_in = random.randint(5, 500)
        packets_out = random.randint(5, 1000)
        bytes_in = packets_in * random.uniform(40, 200)  # Mostly ACKs/Requests
        bytes_out = packets_out * random.uniform(200, 1500)  # Payloads

        # Calculate derived features
        total_packets = packets_in + packets_out
        total_bytes = bytes_in + bytes_out
        bytes_per_packet = total_bytes / total_packets if total_packets > 0 else 0
        packets_per_second = total_packets / duration if duration > 0 else 0

        data.append([
            duration, bytes_in, bytes_out, packets_in, packets_out,
            bytes_per_packet, packets_per_second, 0
        ])
    return data


def generate_malicious_traffic(num_samples):
    data = []
    for _ in range(num_samples):
        attack_type = random.choice(["port_scan", "ddos", "exfiltration"])

        if attack_type == "port_scan":
            duration = random.uniform(0.01, 1.0)
            packets_in = random.randint(1, 3)
            packets_out = 0
            bytes_in = packets_in * random.uniform(40, 60)
            bytes_out = 0
        elif attack_type == "ddos":
            duration = random.uniform(0.1, 5.0)
            packets_in = random.randint(1000, 5000)
            packets_out = random.randint(0, 100)
            bytes_in = packets_in * random.uniform(40, 100)
            bytes_out = packets_out * random.uniform(40, 100)
        elif attack_type == "exfiltration":
            duration = random.uniform(10.0, 3600.0)
            packets_in = random.randint(100, 5000)
            packets_out = random.randint(100, 500)
            bytes_in = packets_in * random.uniform(1000, 1500)  # Heavy outbound (from internal perspective)
            bytes_out = packets_out * random.uniform(40, 200)

        total_packets = packets_in + packets_out
        total_bytes = bytes_in + bytes_out
        bytes_per_packet = total_bytes / total_packets if total_packets > 0 else 0
        packets_per_second = total_packets / duration if duration > 0 else 0

        data.append([
            duration, bytes_in, bytes_out, packets_in, packets_out,
            bytes_per_packet, packets_per_second, 1
        ])
    return data


def main():
    os.makedirs('data', exist_ok=True)
    filepath = 'data/training_dataset.csv'

    benign = generate_benign_traffic(5000)
    malicious = generate_malicious_traffic(500)

    dataset = benign + malicious
    random.shuffle(dataset)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'duration_seconds', 'bytes_in', 'bytes_out',
            'packets_in', 'packets_out', 'bytes_per_packet',
            'packets_per_second', 'is_anomaly'
        ])
        writer.writerows(dataset)

    print(f"Generated {len(dataset)} samples saved to {filepath}")


if __name__ == "__main__":
    main()
