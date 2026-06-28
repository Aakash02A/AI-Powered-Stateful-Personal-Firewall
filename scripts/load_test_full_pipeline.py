import sys
import time
import os
import random
from datetime import datetime
from scapy.all import IP, TCP

from firewall.firewall import PersonalFirewall
from firewall.models import Packet

def main():
    print("=== Full Pipeline Load Test ===")
    
    fw = PersonalFirewall()
    fw.start()
    
    # Wait for engines to initialize
    time.sleep(2)
    
    num_packets = 50000
    print(f"Injecting {num_packets} packets into the pipeline...")
    
    packets = []
    for i in range(num_packets):
        # Simulate a SYN flood from a few IPs to trigger IDS, ML, and Mitigation
        src_ip = f"10.0.0.{random.randint(1, 10)}"
        
        # We don't need actual scapy raw bytes if packet_capture is bypassed, 
        # but the firewall queue consumes `scapy` objects usually.
        # Wait, Firewall._packet_processor expects `Packet` objects?
        # Let's check firewall.py: `self.queue_manager.pop("packet")` returns `packet`.
        # PacketCapture puts raw `scapy` packets or `Packet` models?
        scapy_pkt = IP(src=src_ip, dst="192.168.1.100") / TCP(sport=random.randint(1024, 65535), dport=80, flags="S")
        pkt = Packet(
            timestamp=datetime.now(),
            src_ip=src_ip,
            src_port=scapy_pkt[TCP].sport,
            dst_ip="192.168.1.100",
            dst_port=80,
            protocol="TCP",
            flags="S",
            size=len(scapy_pkt),
            raw=bytes(scapy_pkt)
        )
        packets.append(pkt)
        
    start_time = time.time()
    
    for pkt in packets:
        fw._process_packet(pkt)
        
    end_time = time.time()
    
    fw.stop()
    
    duration = end_time - start_time
    throughput = num_packets / duration
    
    print(f"\nProcessed {num_packets} packets in {duration:.4f} seconds")
    print(f"Throughput: {throughput:.2f} packets/sec")
    
    print("\nSystem State after load test:")
    print(f"Active Connections: {len(fw.flow_engine.active_connections)}")
    print(f"Active Rules: {len(fw.rule_engine.rules)}")
    
if __name__ == "__main__":
    main()
