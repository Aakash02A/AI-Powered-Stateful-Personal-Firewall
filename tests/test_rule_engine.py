import pytest
from datetime import datetime
from firewall.models import Packet, FirewallRule
from firewall.rule_engine import RuleEngine
import firewall.rule_engine

@pytest.fixture
def rule_engine():
    engine = RuleEngine()
    engine.add_rule(FirewallRule(
        rule_id="1", priority=10, enabled=True, protocol="tcp",
        src_ip="192.168.1.0/24", src_port="any", dst_ip="any", dst_port="443",
        direction="outbound", action="allow", description="Allow HTTPS"
    ))
    return engine

def test_rule_matching(rule_engine):
    p1 = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=12345, dst_ip="8.8.8.8", dst_port=443, protocol="tcp", flags="S", size=64)
    # Patch local IP to mock outbound check
    firewall.rule_engine.get_local_ips = lambda: ["192.168.1.50"]
    action, rule = rule_engine.evaluate_packet(p1)
    assert action == "allow"
    assert rule.rule_id == "1"

    # Outbound direction check fail
    firewall.rule_engine.get_local_ips = lambda: ["8.8.8.8"]
    action, rule = rule_engine.evaluate_packet(p1)
    assert action == "allow"
    assert rule is None # Default action allow returned if no match

def test_ip_matching(rule_engine):
    assert rule_engine._ip_matches("192.168.1.50", "192.168.1.0/24") == True
    assert rule_engine._ip_matches("10.0.0.1", "192.168.1.0/24") == False
    assert rule_engine._ip_matches("192.168.1.50", "any") == True
    assert rule_engine._ip_matches("10.0.0.1", "10.0.0.1") == True
    # Test invalid CIDR silently fails and returns false
    assert rule_engine._ip_matches("192.168.1.50", "invalid_ip") == False

def test_port_matching(rule_engine):
    assert rule_engine._port_matches(80, "80") == True
    assert rule_engine._port_matches(80, "any") == True
    assert rule_engine._port_matches(443, "100-500") == True
    assert rule_engine._port_matches(80, "100-500") == False
    assert rule_engine._port_matches(80, "invalid") == False
    
def test_direction_matching():
    engine = RuleEngine()
    engine.add_rule(FirewallRule(
        rule_id="inbound_block", priority=10, enabled=True, protocol="tcp",
        src_ip="any", src_port="any", dst_ip="any", dst_port="22",
        direction="inbound", action="block", description="Block Inbound SSH"
    ))
    
    p = Packet(timestamp=datetime.now(), src_ip="8.8.8.8", src_port=12345, dst_ip="10.0.0.2", dst_port=22, protocol="tcp", flags="S", size=60)
    
    # Mock local IPs so 10.0.0.2 is local, meaning traffic is indeed inbound
    firewall.rule_engine.get_local_ips = lambda: ["10.0.0.2"]
    action, rule = engine.evaluate_packet(p)
    assert action == "block"
    assert rule.rule_id == "inbound_block"
    
    # Mock local IPs so 10.0.0.2 is NOT local, meaning it's not inbound for us
    firewall.rule_engine.get_local_ips = lambda: ["192.168.1.50"]
    action, rule = engine.evaluate_packet(p)
    assert action == "allow" # Falls through to default allow

def test_protocol_and_misc_matching():
    engine = RuleEngine()
    engine.add_rule(FirewallRule(
        rule_id="proto_udp", priority=10, enabled=True, protocol="udp",
        src_ip="any", src_port="any", dst_ip="any", dst_port="53",
        direction="both", action="allow", description="UDP DNS"
    ))
    
    p = Packet(timestamp=datetime.now(), src_ip="8.8.8.8", src_port=53, dst_ip="10.0.0.2", dst_port=53, protocol="tcp", flags="S", size=60)
    
    # TCP packet should not match UDP rule
    action, rule = engine.evaluate_packet(p)
    assert action == "allow" # default allow
    assert rule is None
    
    # UDP packet should match
    p_udp = Packet(timestamp=datetime.now(), src_ip="8.8.8.8", src_port=53, dst_ip="10.0.0.2", dst_port=53, protocol="udp", flags="", size=60)
    action, rule = engine.evaluate_packet(p_udp)
    assert action == "allow"
    assert rule.rule_id == "proto_udp"
    
    # Port mismatch
    p_udp2 = Packet(timestamp=datetime.now(), src_ip="8.8.8.8", src_port=53, dst_ip="10.0.0.2", dst_port=123, protocol="udp", flags="", size=60)
    action, rule = engine.evaluate_packet(p_udp2)
    assert rule is None
