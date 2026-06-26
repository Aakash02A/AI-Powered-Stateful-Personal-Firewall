from datetime import datetime, timedelta

from firewall.connection_tracker import ConnectionTracker
from firewall.models import Packet


def test_connection_tracker_states():
    tracker = ConnectionTracker(timeout=300, syn_timeout=30)
    now = datetime.now()

    # 1. SYN -> SYN_SENT
    p1 = Packet(
        timestamp=now,
        src_ip="10.0.0.1",
        src_port=5000,
        dst_ip="10.0.0.2",
        dst_port=80,
        protocol="TCP",
        flags="S",
        size=60,
    )
    conn = tracker.update_state(p1)
    assert conn.state == "SYN_SENT"

    # 2. SYN-ACK -> SYN_RECV
    p2 = Packet(
        timestamp=now,
        src_ip="10.0.0.2",
        src_port=80,
        dst_ip="10.0.0.1",
        dst_port=5000,
        protocol="TCP",
        flags="SA",
        size=60,
    )
    conn = tracker.update_state(p2)
    assert conn.state == "SYN_RECV"

    # 3. ACK -> ESTABLISHED
    p3 = Packet(
        timestamp=now,
        src_ip="10.0.0.1",
        src_port=5000,
        dst_ip="10.0.0.2",
        dst_port=80,
        protocol="TCP",
        flags="A",
        size=60,
    )
    conn = tracker.update_state(p3)
    assert conn.state == "ESTABLISHED"

    # 4. FIN -> FIN_WAIT
    p4 = Packet(
        timestamp=now,
        src_ip="10.0.0.1",
        src_port=5000,
        dst_ip="10.0.0.2",
        dst_port=80,
        protocol="TCP",
        flags="FA",
        size=60,
    )
    conn = tracker.update_state(p4)
    assert conn.state == "FIN_WAIT"

    # 5. FIN-ACK from other -> CLOSED
    p5 = Packet(
        timestamp=now,
        src_ip="10.0.0.2",
        src_port=80,
        dst_ip="10.0.0.1",
        dst_port=5000,
        protocol="TCP",
        flags="FA",
        size=60,
    )
    conn = tracker.update_state(p5)
    assert conn.state == "CLOSED"


def test_connection_tracker_expiration():
    tracker = ConnectionTracker(timeout=300, syn_timeout=30)

    # Create SYN_SENT conn and artificially age it
    p1 = Packet(
        timestamp=datetime.now(),
        src_ip="10.0.0.1",
        src_port=5000,
        dst_ip="10.0.0.2",
        dst_port=80,
        protocol="TCP",
        flags="S",
        size=60,
    )
    conn = tracker.update_state(p1)

    # Verify last_activity updates
    initial_activity = conn.last_activity

    p2 = Packet(
        timestamp=p1.timestamp + timedelta(seconds=1),
        src_ip="10.0.0.2",
        src_port=80,
        dst_ip="10.0.0.1",
        dst_port=5000,
        protocol="TCP",
        flags="SA",
        size=60,
    )
    conn2 = tracker.update_state(p2)
    assert conn2.last_activity > initial_activity

    conn.last_activity -= timedelta(seconds=305)

    assert len(tracker.active_connections) == 1
    tracker.clean_expired()
    assert len(tracker.active_connections) == 0
