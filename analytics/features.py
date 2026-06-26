try:
    import pandas as pd
except ImportError:
    pd = None

class FeatureEngineering:
    def __init__(self, db):
        self.db = db

    def generate_features(self):
        if not pd:
            print("[!] Pandas not installed, skipping feature generation.")
            return None
            
        query = "SELECT * FROM connections"
        df = pd.read_sql(query, self.db.engine)
        if df.empty:
            return pd.DataFrame()
            
        # Group by src_ip to build ML-ready features
        features = df.groupby('src_ip').agg(
            connection_count=('id', 'count'),
            unique_destination_ips=('dst_ip', 'nunique'),
            unique_destination_ports=('dst_port', 'nunique'),
            average_duration=('duration', 'mean'),
            bytes_per_connection=('bytes_out', 'mean'),
            packets_per_connection=('packets_out', 'mean'),
            connection_rate=('duration', lambda x: len(x) / (x.sum() or 1)),
        ).reset_index()
        
        # In a real implementation, we would also join alert_counts and threat_scores here.
        return features
