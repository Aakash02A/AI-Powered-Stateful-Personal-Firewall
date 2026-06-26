from datetime import datetime
from firewall.models import Packet
from analytics.flow_engine import FlowEngine

def validate_flow_engine():
    print("=== FLOW ENGINE CANONICAL VALIDATION ===")
    
    engine = FlowEngine()
    
    print("\n--- Sending Packet 1: 10.0.0.5:5000 -> 8.8.8.8:53 ---")
    p1 = Packet(timestamp=datetime.now(), src_ip="10.0.0.5", src_port=5000, dst_ip="8.8.8.8", dst_port=53, protocol="UDP", flags="", size=100)
    c1 = engine.process_packet(p1)
    
    print("--- Sending Packet 2: 8.8.8.8:53 -> 10.0.0.5:5000 ---")
    p2 = Packet(timestamp=datetime.now(), src_ip="8.8.8.8", src_port=53, dst_ip="10.0.0.5", dst_port=5000, protocol="UDP", flags="", size=200)
    c2 = engine.process_packet(p2)
    
    print("\n[Results]")
    print(f"Total Unique Flows in Engine: {len(engine.active_connections)}")
    print(f"Connection 1 Identity == Connection 2 Identity: {c1 is c2}")
    print(f"Initiator IP: {c1.src_ip}:{c1.src_port}")
    print(f"Target IP: {c1.dst_ip}:{c1.dst_port}")
    print(f"Packets In (from 8.8.8.8): {c1.packets_in}")
    print(f"Packets Out (from 10.0.0.5): {c1.packets_out}")
    print(f"Bytes In: {c1.bytes_in}")
    print(f"Bytes Out: {c1.bytes_out}")
    print(f"Duration: {c1.duration}s")
    
if __name__ == '__main__':
    validate_flow_engine()
