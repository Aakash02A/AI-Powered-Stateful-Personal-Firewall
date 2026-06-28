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

    # Score should never exceed the maximum
    assert engine.scores["10.0.0.1"] == 100.0


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


def test_combined_score():
    engine = ThreatScoringEngine()

    # 50% heuristic (from 10), 30% ML (from 0.8), 20% TI (from 50)
    engine.add_offense("8.8.8.8", "block")  # heuristic = 10

    ml_score = 0.8  # scaled to 80 -> 30% of 80 = 24
    ti_score = 50  # 20% of 50 = 10
    # heuristic -> 50% of 10 = 5
    # Total = 5 + 24 + 10 = 39

    combined = engine.get_combined_score(
        "8.8.8.8", ml_score=ml_score, ti_score=ti_score
    )
    assert combined == 39.0

    # Test bounds
    combined_high = engine.get_combined_score("8.8.8.8", ml_score=1.5, ti_score=150)
    # ML capped at 100 -> 30, TI capped at 100 -> 20, Heuristic -> 5. Total = 55.0
    assert combined_high == 55.0
