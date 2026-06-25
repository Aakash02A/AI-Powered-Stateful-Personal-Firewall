import json
import sqlite3
import time
from datetime import datetime
from firewall.firewall import PersonalFirewall
from firewall.models import Packet

# Helper to run simulated attacks and extract DB contents
def run_simulations():
    # 1. Setup instance in memory for testing
    fw = PersonalFirewall(db_path="sqlite:///simulation.db")
    
    # 2. Simulate Port Scan
    for i in range(15):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=50000+i, dst_ip="10.0.0.1", dst_port=1+i, protocol="TCP", flags="S", size=60)
        fw._process_packet(p)
        
    # 3. Simulate SYN Flood
    for i in range(60):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=50000+i, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", flags="S", size=60)
        fw._process_packet(p)
        
    # 4. Simulate ICMP Flood
    for i in range(110):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=0, dst_ip="10.0.0.1", dst_port=0, protocol="ICMP", flags="", size=60)
        fw._process_packet(p)
        
    # 5. Extract output
    conn = sqlite3.connect("simulation.db")
    c = conn.cursor()
    
    print("--- ALERTS GENERATED ---")
    c.execute("SELECT timestamp, severity, alert_type, description FROM alerts")
    for row in c.fetchall():
        print(row)
        
    print("\n--- SCHEMA ---")
    c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    for row in c.fetchall():
        print(row[0])
        print(row[1])
        print()
    
    conn.close()

if __name__ == '__main__':
    run_simulations()
