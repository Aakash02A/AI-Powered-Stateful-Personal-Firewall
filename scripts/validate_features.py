import os
from datetime import datetime
from firewall.database import FirewallDatabase
from firewall.models import Connection
from analytics.features import FeatureEngineering

def validate_features():
    print("=== FEATURE ENGINEERING VALIDATION ===")
    
    if os.path.exists("test_features.db"):
        os.remove("test_features.db")
        
    db = FirewallDatabase("sqlite:///test_features.db")
    
    # Inject dummy flows
    now = datetime.now()
    conns = [
        Connection(src_ip="10.0.0.1", src_port=1000, dst_ip="8.8.8.8", dst_port=53, protocol="UDP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=5, packets_out=5, bytes_in=500, bytes_out=500, duration=1.0),
        Connection(src_ip="10.0.0.1", src_port=1001, dst_ip="8.8.4.4", dst_port=53, protocol="UDP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=2, packets_out=2, bytes_in=200, bytes_out=200, duration=0.5),
        Connection(src_ip="192.168.1.50", src_port=4000, dst_ip="1.1.1.1", dst_port=443, protocol="TCP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=50, packets_out=40, bytes_in=50000, bytes_out=4000, duration=10.0)
    ]
    
    db.bulk_insert(conns)
    
    engine = FeatureEngineering(db)
    df = engine.generate_features()
    
    if df is None or df.empty:
        print("Pandas DataFrame is empty or not generated.")
        return
        
    print("\n[DataFrame Shape]")
    print(df.shape)
    
    print("\n[Data Types]")
    print(df.dtypes)
    
    print("\n[Sample Rows]")
    print(df.head())
    
    print("\n[NaN Check]")
    print(df.isna().sum())

if __name__ == '__main__':
    validate_features()
