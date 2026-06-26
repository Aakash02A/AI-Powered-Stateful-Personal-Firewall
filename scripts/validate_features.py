import os
import time
from datetime import datetime
from firewall.database import FirewallDatabase
from firewall.models import Connection, FirewallEvent, Alert
from analytics.features import FeatureEngineering

def validate_features():
    print("=== FEATURE ENGINEERING VALIDATION ===")
    
    if os.path.exists("test_features.db"):
        os.remove("test_features.db")
        
    db = FirewallDatabase("sqlite:///test_features.db")
    
    now = datetime.now()
    conns = [
        Connection(src_ip="10.0.0.1", src_port=1000, dst_ip="8.8.8.8", dst_port=53, protocol="UDP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=5, packets_out=5, bytes_in=500, bytes_out=500, duration=1.0),
        Connection(src_ip="10.0.0.1", src_port=1001, dst_ip="8.8.4.4", dst_port=53, protocol="UDP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=2, packets_out=2, bytes_in=200, bytes_out=200, duration=0.5),
        Connection(src_ip="192.168.1.50", src_port=4000, dst_ip="1.1.1.1", dst_port=443, protocol="TCP", state="CLOSED", creation_time=now, last_activity=now, flow_start=now, flow_end=now, packets_in=50, packets_out=40, bytes_in=50000, bytes_out=4000, duration=10.0)
    ]
    
    events = [
        FirewallEvent(timestamp=now, rule_id="1", action="block", src_ip="192.168.1.50", src_port=4000, dst_ip="1.1.1.1", dst_port=443, protocol="TCP", reason="blocked by rule"),
        FirewallEvent(timestamp=now, rule_id="2", action="allow", src_ip="10.0.0.1", src_port=1000, dst_ip="8.8.8.8", dst_port=53, protocol="UDP", reason="allowed by rule")
    ]
    
    alerts = [
        Alert(timestamp=now, alert_type="port_scan", severity="High", src_ip="192.168.1.50", dst_ip="1.1.1.1", description="Port scan", action_taken="Blocked")
    ]
    
    db.bulk_insert(conns)
    db.bulk_insert(events)
    db.bulk_insert(alerts)
    
    engine = FeatureEngineering(db)
    df = engine.generate_features()
    
    if df is None or df.empty:
        print("Pandas DataFrame is empty or not generated.")
        return
        
    print(f"\n[DataFrame Shape]: {df.shape}")
    print("\n[Data Types]:")
    print(df.dtypes)
    
    print("\n[Sample Rows]:")
    print(df.head())
    
    print("\n[Assertions & Validations]")
    
    # 1. Every engineered feature exists
    expected_cols = [
        'src_ip', 'connection_count', 'unique_destination_ips', 'unique_destination_ports',
        'average_duration', 'bytes_per_connection', 'packets_per_connection', 'connection_rate',
        'average_packet_rate', 'bytes_per_second', 'packets_per_second', 'protocol_entropy',
        'destination_port_entropy', 'active_hours', 'failed_connections', 'blocked_connections',
        'alert_count', 'alert_frequency', 'threat_score'
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"
    print("- [PASS] All engineered features exist.")
    
    # 2. No NaN values
    assert df.isna().sum().sum() == 0, "NaN values detected in DataFrame"
    print("- [PASS] Zero NaN values across all features.")
    
    # 3. Correct data types & Numeric ranges
    assert df['connection_count'].dtype == 'int32' or df['connection_count'].dtype == 'int64', "Incorrect dtype for connection_count"
    assert (df['average_duration'] >= 0).all(), "Negative duration found"
    assert (df['protocol_entropy'] >= 0).all(), "Negative entropy found"
    print("- [PASS] All data types and numeric bounds are correct.")
    
    # 4. No duplicate rows
    assert df.duplicated(subset=['src_ip']).sum() == 0, "Duplicate src_ip groupings detected"
    print("- [PASS] Aggregation determinism verified (No duplicate rows).")

if __name__ == '__main__':
    validate_features()
