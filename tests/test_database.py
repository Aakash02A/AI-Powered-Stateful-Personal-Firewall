import pytest
import os
from datetime import datetime
from firewall.models import Packet, Connection, FirewallEvent, Alert
from firewall.database import FirewallDatabase


@pytest.fixture
def db():
    # Use in-memory SQLite for testing
    database = FirewallDatabase("sqlite:///:memory:")
    return database


def test_log_packet(db):
    p = Packet(
        timestamp=datetime.now(),
        src_ip="1.1.1.1",
        src_port=123,
        dst_ip="2.2.2.2",
        dst_port=456,
        protocol="TCP",
        flags="S",
        size=100,
    )
    db.log_packet(p)
    # Just ensuring it doesn't crash


def test_query_connections(db):
    # This just tests the schema query
    conns = db.query_connections()
    assert isinstance(conns, list)


def test_log_and_query_alerts(db):
    a = Alert(
        timestamp=datetime.now(),
        alert_type="test",
        severity="low",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        description="test alert",
        action_taken="none",
    )
    db.log_alert(a)

    results = db.query_alerts(severity="low")
    assert len(results) == 1
    assert results[0]["alert_type"] == "test"
