import pytest
from ml.ml_detector import MLAnomalyDetector
from tests.fixtures.attack_traffic import (
    generate_normal_traffic,
    generate_syn_flood,
    generate_port_scan,
    generate_icmp_flood,
)


@pytest.fixture(scope="module")
def detector():
    d = MLAnomalyDetector()
    return d


def test_detects_port_scan_50_ports(detector):
    flows = generate_port_scan(50)
    detected = sum(1 for flow in flows if detector.evaluate_connection(flow)[0])
    rate = (detected / 50) * 100
    print(
        f"\nPort Scan Detection Results:\n  Total flows: 50\n  Detected as anomalous: {detected}\n  Detection rate: {rate}%\n"
    )
    assert rate > 80.0


def test_detects_syn_flood_100_packets(detector):
    flows = generate_syn_flood(100)
    detected = sum(1 for flow in flows if detector.evaluate_connection(flow)[0])
    rate = (detected / 100) * 100
    print(
        f"\nSYN Flood Detection Results:\n  Total flows: 100\n  Detected as anomalous: {detected}\n  Detection rate: {rate}%\n"
    )
    assert rate > 80.0


def test_detects_icmp_flood_100_packets(detector):
    flows = generate_icmp_flood(100)
    detected = sum(1 for flow in flows if detector.evaluate_connection(flow)[0])
    rate = (detected / 100) * 100
    print(
        f"\nICMP Flood Detection Results:\n  Total flows: 100\n  Detected as anomalous: {detected}\n  Detection rate: {rate}%\n"
    )
    assert rate > 80.0


def test_normal_web_browsing_no_alert(detector):
    flows = generate_normal_traffic(100)
    detected = sum(1 for flow in flows if detector.evaluate_connection(flow)[0])
    fp_rate = (detected / 100) * 100
    print(
        f"\nNormal Traffic Results:\n  Total flows: 100\n  Detected as anomalous (False Positives): {detected}\n  False Positive rate: {fp_rate}%\n"
    )
    assert fp_rate < 5.0


def test_attack_vs_normal_separation(detector):
    # Verify attacks score lower (more anomalous) than normal traffic
    normal_flow = generate_normal_traffic(1)[0]
    attack_flow = generate_syn_flood(1)[0]

    _, normal_score = detector.evaluate_connection(normal_flow)
    _, attack_score = detector.evaluate_connection(attack_flow)

    # Lower score is more anomalous in Isolation Forest
    assert attack_score < normal_score
