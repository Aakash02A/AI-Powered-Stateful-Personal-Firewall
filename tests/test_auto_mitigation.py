import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from firewall.ids_engine import IDSEngine
from analytics.threat_scoring import ThreatScoringEngine
from firewall.rule_engine import RuleEngine
from analytics.flow_engine import FlowEngine
from firewall.models import Packet

@pytest.fixture
def engines():
    flow_engine = FlowEngine()
    rule_engine = RuleEngine()
    scoring_engine = ThreatScoringEngine()
    
    # Use a dummy config path so it falls back to defaults, then we override them manually
    ids_engine = IDSEngine(flow_engine, rule_engine, scoring_engine, "dummy_path.json")
    ids_engine.auto_block_enabled = True
    ids_engine.auto_block_threshold = 85.0
    ids_engine.auto_block_duration_minutes = 60
    
    return ids_engine, rule_engine, scoring_engine

def test_auto_mitigation_triggers_on_high_score(engines):
    ids_engine, rule_engine, scoring_engine = engines
    
    # Simulate a brute force attack (adds 50 to heuristic score)
    # Simulate high ML score (adds 30)
    # Simulate high TI score (adds 20)
    # Total = 100 > 85.0 threshold
    
    # We'll just call _trigger_mitigation directly for the core logic
    ids_engine._trigger_mitigation("10.0.0.5", 95.0, "High threat detected")
    
    # Verify rule was added
    assert len(rule_engine.rules) == 1
    rule = rule_engine.rules[0]
    
    assert rule.action == "drop"
    assert rule.src_ip == "10.0.0.5"
    assert rule.direction == "inbound"
    assert rule.priority == 1
    assert "Score: 95.0" in rule.description
    assert rule.expires_at is not None

def test_auto_mitigation_prevents_duplicate_rules(engines):
    ids_engine, rule_engine, scoring_engine = engines
    
    # Trigger twice for the same IP
    ids_engine._trigger_mitigation("192.168.1.100", 90.0, "Threat 1")
    ids_engine._trigger_mitigation("192.168.1.100", 92.0, "Threat 2")
    
    # Should only be one rule for this IP
    assert len(rule_engine.rules) == 1
    assert rule_engine.rules[0].src_ip == "192.168.1.100"

def test_auto_mitigation_disabled(engines):
    ids_engine, rule_engine, scoring_engine = engines
    ids_engine.auto_block_enabled = False
    
    ids_engine._trigger_mitigation("10.0.0.5", 99.0, "Threat")
    
    assert len(rule_engine.rules) == 0

def test_rule_expiration_cleanup():
    rule_engine = RuleEngine()
    
    from firewall.models import FirewallRule
    
    # Rule 1: Not expired (expires in 1 hour)
    future = (datetime.now() + timedelta(hours=1)).isoformat()
    rule_engine.add_rule(FirewallRule("rule1", 10, True, "any", "1.1.1.1", "any", "any", "any", "inbound", "drop", "test", expires_at=future))
    
    # Rule 2: Expired (expired 1 hour ago)
    past = (datetime.now() - timedelta(hours=1)).isoformat()
    rule_engine.add_rule(FirewallRule("rule2", 10, True, "any", "2.2.2.2", "any", "any", "any", "inbound", "drop", "test", expires_at=past))
    
    # Rule 3: No expiration
    rule_engine.add_rule(FirewallRule("rule3", 10, True, "any", "3.3.3.3", "any", "any", "any", "inbound", "drop", "test", expires_at=None))
    
    assert len(rule_engine.rules) == 3
    
    # Clean up
    rule_engine.cleanup_expired_rules()
    
    # Should only have 2 rules left (rule1 and rule3)
    assert len(rule_engine.rules) == 2
    assert "rule2" not in [r.rule_id for r in rule_engine.rules]
    assert "rule1" in [r.rule_id for r in rule_engine.rules]
    assert "rule3" in [r.rule_id for r in rule_engine.rules]
