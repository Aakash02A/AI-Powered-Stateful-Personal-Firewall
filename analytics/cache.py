import threading


class AnalyticsCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalyticsCache, cls).__new__(cls)
            cls._instance.lock = threading.Lock()
            cls._instance.data = {
                "top_talkers": [],
                "top_attackers": [],
                "threat_rankings": [],
                "protocol_statistics": {},
                "port_statistics": {},
                "traffic_summaries": {},
            }
        return cls._instance

    def get(self, key):
        with self.lock:
            return self.data.get(key, None)

    def set(self, key, value):
        with self.lock:
            self.data[key] = value
