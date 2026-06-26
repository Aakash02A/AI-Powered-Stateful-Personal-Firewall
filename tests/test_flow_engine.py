import pytest
from datetime import datetime, timedelta
from firewall.models import Packet
from analytics.flow_engine import FlowEngine

def test_canonical_flow():
    engine = FlowEngine()
    now = datetime.now()
    p1 = Packet(timestamp=now, src_ip="10.0.0.1", src_port=5000, dst_ip="8.8.8.8", dst_port=53, protocol="UDP", flags="", size=100)
    p2 = Packet(timestamp=now, src_ip="8.8.8.8", src_port=53, dst_ip="10.0.0.1", dst_port=5000, protocol="UDP", flags="", size=200)
    
    conn1 = engine.process_packet(p1)
    conn2 = engine.process_packet(p2)
    
    # Assert they resolve to the exact same connection object
    assert conn1 is conn2
    assert len(engine.active_connections) == 1
    assert conn1.packets_out == 1
    assert conn1.packets_in == 1
    assert conn1.bytes_out == 100
    assert conn1.bytes_in == 200

def test_tcp_state_machine():
    engine = FlowEngine()
    now = datetime.now()
    
    # SYN
    p1 = Packet(timestamp=now, src_ip="1.1.1.1", src_port=1000, dst_ip="2.2.2.2", dst_port=80, protocol="TCP", flags="S", size=60)
    conn = engine.process_packet(p1)
    assert conn.state == "SYN_SENT"
    
    # SYN-ACK
    p2 = Packet(timestamp=now, src_ip="2.2.2.2", src_port=80, dst_ip="1.1.1.1", dst_port=1000, protocol="TCP", flags="SA", size=60)
    conn = engine.process_packet(p2)
    assert conn.state == "SYN_RECV"
    
    # ACK
    p3 = Packet(timestamp=now, src_ip="1.1.1.1", src_port=1000, dst_ip="2.2.2.2", dst_port=80, protocol="TCP", flags="A", size=60)
    conn = engine.process_packet(p3)
    assert conn.state == "ESTABLISHED"
    
def test_flow_expiration():
    engine = FlowEngine(syn_timeout=1)
    # Clear singleton queue
    while engine.queue_manager.qsize() > 0:
        engine.queue_manager.pop()
        
    now = datetime.now()
    p = Packet(timestamp=now, src_ip="1.1.1.1", src_port=1000, dst_ip="2.2.2.2", dst_port=80, protocol="TCP", flags="S", size=60)
    
    conn = engine.process_packet(p)
    assert len(engine.active_connections) == 1
    
    # Artificially age it
    conn.last_activity = now - timedelta(seconds=5)
    engine.clean_expired()
    
    assert len(engine.active_connections) == 0
    # The flow should be pushed to queue
    assert engine.queue_manager.qsize() == 1
    engine.queue_manager.pop()
