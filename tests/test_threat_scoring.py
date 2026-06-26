from analytics.threat_scoring import ThreatScoringEngine


def test_threat_scoring_addition():
    engine = ThreatScoringEngine()
    engine.add_offense("10.0.0.1", "block")
    assert engine.scores["10.0.0.1"] == 10

    engine.add_offense("10.0.0.1", "port_scan")
    assert engine.scores["10.0.0.1"] == 35


def test_threat_scoring_cap():
    engine = ThreatScoringEngine()
    for _ in range(5):
        engine.add_offense("10.0.0.1", "brute_force")

    assert engine.scores["10.0.0.1"] == 100.0  # Should be capped


def test_threat_classification():
    engine = ThreatScoringEngine()
    assert engine.get_classification(10) == "Safe"
    assert engine.get_classification(40) == "Suspicious"
    assert engine.get_classification(60) == "Dangerous"
    assert engine.get_classification(90) == "Critical"


def test_decay():
    engine = ThreatScoringEngine()
    engine.add_offense("10.0.0.2", "block")
    assert engine.scores["10.0.0.2"] == 10

    engine.decay_scores()
    assert engine.scores["10.0.0.2"] < 10
