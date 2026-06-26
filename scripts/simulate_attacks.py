import sqlite3
import time
from datetime import datetime
from firewall.firewall import PersonalFirewall
from firewall.models import Packet

# Helper to run simulated attacks and extract DB contents without relying on WinPcap
def run_simulations():
    print("=== Automated Attack Validation (Mock Mode) ===")
    print("[*] Initializing Personal Firewall (in-memory simulation)...")
    
    # Setup instance in memory for testing
    fw = PersonalFirewall(db_path="sqlite:///data/simulation.db")
    fw.start()
    time.sleep(1) # wait for db writer
    
    # 1. Simulate Port Scan
    print("\n[+] Injecting Port Scan packets...")
    for i in range(15):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=50000+i, dst_ip="10.0.0.1", dst_port=1+i, protocol="TCP", flags="S", size=60)
        fw._process_packet(p)
        
    # 2. Simulate SYN Flood
    print("[+] Injecting SYN Flood packets...")
    for i in range(60):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=50000+i, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", flags="S", size=60)
        fw._process_packet(p)
        
    # 3. Simulate ICMP Flood
    print("[+] Injecting ICMP Flood packets...")
    for i in range(110):
        p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=0, dst_ip="10.0.0.1", dst_port=0, protocol="ICMP", flags="", size=60)
        fw._process_packet(p)
        
    time.sleep(2) # wait for events to be written
    fw.stop()
    
    # 4. Extract output
    conn = sqlite3.connect("data/simulation.db")
    c = conn.cursor()
    
    print("\n--- VALIDATION RESULTS (ALERTS) ---")
    c.execute("SELECT timestamp, severity, alert_type, description FROM alerts")
    alerts = c.fetchall()
    
    if len(alerts) > 0:
        for row in alerts:
            print(f"[{row[1].upper()}] {row[2]} - {row[3]}")
    else:
        print("[-] No alerts detected! Validation failed.")
        
    conn.close()

if __name__ == '__main__':
    run_simulations()
