from analytics.threat_scoring import ThreatScoringEngine


def validate_threat_scoring():
    print("=== THREAT SCORING VALIDATION ===")

    engine = ThreatScoringEngine()

    scenarios = [
        {
            "ip": "192.168.1.50",
            "events": [
                "port_scan",
                "port_scan",
                "brute_force",
                "block",
                "block",
                "block",
                "block",
                "block",
            ],
        },
        {"ip": "10.0.0.99", "events": ["syn_flood"]},
        {"ip": "172.16.0.5", "events": ["block", "block"]},
        {"ip": "8.8.8.8", "events": []},
        {
            "ip": "45.33.22.11",
            "events": ["brute_force", "brute_force", "brute_force", "brute_force"],
        },
    ]

    print(f"{'Source IP':<15} | {'Events':<30} | {'Score':<6} | {'Classification':<15}")
    print("-" * 75)

    for s in scenarios:
        for event in s["events"]:
            engine.add_offense(s["ip"], event)

        score = engine.scores.get(s["ip"], 0)
        classification = engine.get_classification(score)

        events_str = ", ".join(s["events"]) if s["events"] else "None"
        if len(events_str) > 27:
            events_str = events_str[:24] + "..."

        print(
            f"{s['ip']:<15} | {events_str:<30} | {score:<6.1f} | {classification:<15}"
        )


if __name__ == "__main__":
    validate_threat_scoring()
