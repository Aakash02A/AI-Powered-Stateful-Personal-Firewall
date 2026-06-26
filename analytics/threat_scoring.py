import collections
from datetime import datetime, timedelta


class ThreatScoringEngine:
    def __init__(self):
        self.scores = collections.defaultdict(float)
        self.activity_logs = collections.defaultdict(list)

    def add_offense(self, ip: str, offense_type: str):
        severity_map = {
            "block": 10,
            "port_scan": 25,
            "syn_flood": 40,
            "brute_force": 50,
        }

        base_score = severity_map.get(offense_type, 0)

        now = datetime.now()
        self.activity_logs[ip].append(now)

        # Cleanup old logs (> 10 mins) for frequency calculation
        threshold = now - timedelta(minutes=10)
        self.activity_logs[ip] = [t for t in self.activity_logs[ip] if t > threshold]

        # Frequency weight
        frequency = len(self.activity_logs[ip])
        frequency_weight = 0
        if frequency > 3:
            frequency_weight = (frequency - 3) * 5

        self.scores[ip] += base_score + frequency_weight
        if self.scores[ip] > 100:
            self.scores[ip] = 100.0

    def decay_scores(self):
        # Subtract 5 every 24 hours of inactivity.
        # If scheduler calls this every hour, subtract 5/24
        decay_amount = 5.0 / 24.0
        for ip in list(self.scores.keys()):
            self.scores[ip] -= decay_amount
            if self.scores[ip] <= 0:
                del self.scores[ip]

    def get_classification(self, score: float) -> str:
        if score <= 20:
            return "Safe"
        elif score <= 50:
            return "Suspicious"
        elif score <= 80:
            return "Dangerous"
        else:
            return "Critical"
