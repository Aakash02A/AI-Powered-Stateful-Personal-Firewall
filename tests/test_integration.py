import pytest
import time
from datetime import datetime
from firewall.firewall import PersonalFirewall
from firewall.models import Packet

def test_firewall_integration_packet_processing(tmp_path):
    config_file = tmp_path / "rules.json"
    config_file.write_text('{"rules": []}')
    db_file = tmp_path / "test.db"
    
    fw = PersonalFirewall(config_path=str(config_file), db_path=f"sqlite:///{db_file}")
    
    # Process a packet manually without starting the sniffer
    p = Packet(timestamp=datetime.now(), src_ip="192.168.1.100", src_port=12345, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", flags="S", size=60)
    fw._process_packet(p)
    
    stats = fw.get_stats()
    assert stats['packets_processed'] == 1
    assert stats['active_connections'] == 1
    
    # Check DB
    conns = fw.db_writer.db.query_connections()
    assert len(conns) == 0 # DB doesn't store active connections immediately unless we implement connection logging
    
    # Send another packet to trigger brute force
    for _ in range(6):
        fw._process_packet(p)
        
    alerts = fw.db_writer.db.query_alerts()
    assert len(alerts) >= 1
    
    # Ensure logs were written
    import os
    assert os.path.exists("data/logs/packets.log")
    assert os.path.exists("data/logs/events.log")
