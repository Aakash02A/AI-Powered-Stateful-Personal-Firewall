import os
from datetime import datetime

from firewall.firewall import PersonalFirewall
from firewall.logger import setup_logger
from firewall.models import Packet


def test_firewall_integration_packet_processing(tmp_path):
    config_file = tmp_path / "rules.json"
    config_file.write_text('{"rules": []}')
    db_file = tmp_path / "test.db"

    packet_log = tmp_path / "packets.log"
    event_log = tmp_path / "events.log"
    p_logger = setup_logger("test_packet_logger", str(packet_log))
    e_logger = setup_logger("test_event_logger", str(event_log))

    fw = PersonalFirewall(
        config_path=str(config_file),
        db_path=f"sqlite:///{db_file}",
        packet_logger=p_logger,
        event_logger=e_logger,
    )

    # Process a packet manually without starting the sniffer
    p = Packet(
        timestamp=datetime.now(),
        src_ip="192.168.1.100",
        src_port=12345,
        dst_ip="10.0.0.1",
        dst_port=80,
        protocol="TCP",
        flags="S",
        size=60,
    )
    fw._process_packet(p)

    stats = fw.get_stats()
    assert stats["packets_processed"] == 1
    assert stats["active_connections"] == 1

    # Check DB
    conns = fw.db_writer.db.query_connections()
    assert len(conns) == 0  # DB doesn't store active connections immediately

    # Send another packet to trigger brute force
    for _ in range(6):
        fw._process_packet(p)

    import time

    start_time = time.time()
    alerts = []
    while time.time() - start_time < 5:
        alerts = fw.db_writer.db.query_alerts()
        if len(alerts) >= 1:
            break
        time.sleep(0.1)

    # Properly stop the firewall to drain queues and flush DB synchronously
    fw.stop()

    alerts = fw.db_writer.db.query_alerts()
    assert len(alerts) >= 1

    # Ensure logs were written to the injected paths
    assert os.path.exists(str(packet_log))
    assert os.path.exists(str(event_log))
