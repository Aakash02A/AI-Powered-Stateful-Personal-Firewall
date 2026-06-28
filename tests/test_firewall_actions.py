import pytest
from datetime import datetime

from firewall.firewall import PersonalFirewall
from firewall.models import FirewallRule, Packet


@pytest.fixture
def fw(tmp_path):
    config_file = tmp_path / "rules.json"
    config_file.write_text('{"rules": []}')
    db_file = tmp_path / "test.db"

    fw_instance = PersonalFirewall(
        config_path=str(config_file), db_path=f"sqlite:///{db_file}"
    )
    yield fw_instance
    if fw_instance.db_writer and fw_instance.db_writer.db:
        fw_instance.db_writer.db.close()


def test_firewall_block_action(fw):
    fw.rule_engine.add_rule(
        FirewallRule(
            rule_id="test_block",
            priority=1,
            enabled=True,
            protocol="tcp",
            src_ip="any",
            src_port="any",
            dst_ip="any",
            dst_port="22",
            direction="both",
            action="block",
            description="Block SSH",
        )
    )

    p_tcp = Packet(
        timestamp=datetime.now(),
        src_ip="192.168.1.100",
        src_port=12345,
        dst_ip="10.0.0.1",
        dst_port=22,
        protocol="TCP",
        flags="S",
        size=60,
    )

    # Should attempt to send RST without crashing
    fw._process_packet(p_tcp)

    # Add UDP block rule
    fw.rule_engine.add_rule(
        FirewallRule(
            rule_id="test_block_udp",
            priority=2,
            enabled=True,
            protocol="udp",
            src_ip="any",
            src_port="any",
            dst_ip="any",
            dst_port="53",
            direction="both",
            action="block",
            description="Block DNS",
        )
    )
    p_udp = Packet(
        timestamp=datetime.now(),
        src_ip="192.168.1.100",
        src_port=12345,
        dst_ip="10.0.0.1",
        dst_port=53,
        protocol="UDP",
        flags="",
        size=60,
    )
    fw._process_packet(p_udp)


def test_firewall_drop_action(fw):
    fw.rule_engine.add_rule(
        FirewallRule(
            rule_id="test_drop",
            priority=1,
            enabled=True,
            protocol="tcp",
            src_ip="any",
            src_port="any",
            dst_ip="any",
            dst_port="any",
            direction="both",
            action="drop",
            description="Drop all",
        )
    )

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
