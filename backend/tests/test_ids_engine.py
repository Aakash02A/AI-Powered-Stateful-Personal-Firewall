from datetime import datetime

from analytics.flow_engine import FlowEngine
from firewall.ids_engine import IDSEngine
from firewall.models import Packet


def test_brute_force_detection():
    tracker = FlowEngine()
    ids = IDSEngine(tracker)

    alerts = []
    # Send 6 SYN packets without ACK
    for _ in range(6):
        p = Packet(
            timestamp=datetime.now(),
            src_ip="192.168.1.100",
            src_port=50000,
            dst_ip="10.0.0.1",
            dst_port=22,
            protocol="TCP",
            flags="S",
            size=60,
        )
        alerts.extend(ids.analyze_packet(p))

    # We should get a brute_force alert
    bf_alerts = [a for a in alerts if a.alert_type == "brute_force"]
    assert len(bf_alerts) == 1


def test_suspicious_port_detection():
    tracker = FlowEngine()
    ids = IDSEngine(tracker)

    p = Packet(
        timestamp=datetime.now(),
        src_ip="192.168.1.100",
        src_port=50000,
        dst_ip="10.0.0.1",
        dst_port=12345,
        protocol="TCP",
        flags="S",
        size=60,
    )
    alerts = ids.analyze_packet(p)

    assert len(alerts) == 1
    assert alerts[0].alert_type == "suspicious_port"
