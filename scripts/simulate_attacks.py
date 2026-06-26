import time
import sqlite3
from datetime import datetime
from scapy.all import IP, TCP, ICMP
from firewall.firewall import PersonalFirewall
from firewall.models import Packet

def run_advanced_simulation():
    print("=" * 60)
    print("=== Firewall Attack Simulation & Validation Suite ===")
    print("=" * 60)
    
    print("[*] Initializing Personal Firewall (in-memory simulation)...")
    fw = PersonalFirewall(db_path="sqlite:///data/simulation.db")
    fw.start()
    time.sleep(1) # Wait for DB writer to initialize
    
    try:
        # --- 1. Baseline Metrics ---
        baseline = fw.get_stats()
        print(f"\n[*] Baseline stats: {baseline['active_connections']} active connections")
        
        # --- 2. Port Scan Detection & Latency ---
        print("\n[*] Simulating port scan (50 ports)...")
        start_time = time.time()
        for i in range(50):
            p = Packet(timestamp=datetime.now(), src_ip="192.168.1.50", src_port=50000+i, dst_ip="10.0.0.1", dst_port=1000+i, protocol="TCP", flags="S", size=60)
            fw._process_packet(p)
        latency_ms = (time.time() - start_time) / 50 * 1000
        print(f"    Average packet processing latency: {latency_ms:.2f}ms")
        assert latency_ms < 100, f"Processing too slow! {latency_ms}ms"
        
        # Wait for alerts to flush
        time.sleep(1.5)
        
        # --- 3. SYN Flood Detection ---
        print("\n[*] Simulating SYN flood (100 packets to port 443)...")
        for i in range(100):
            p = Packet(timestamp=datetime.now(), src_ip="192.168.1.51", src_port=50000+i, dst_ip="10.0.0.1", dst_port=443, protocol="TCP", flags="S", size=60)
            fw._process_packet(p)
        
        # --- 4. ICMP Flood Detection ---
        print("\n[*] Simulating ICMP flood (100 packets)...")
        for i in range(100):
            p = Packet(timestamp=datetime.now(), src_ip="192.168.1.52", src_port=0, dst_ip="10.0.0.1", dst_port=0, protocol="ICMP", flags="", size=60)
            fw._process_packet(p)
            
        time.sleep(2) # Wait for events to be written
        
        # --- 5. Verify Persistence ---
        print("\n[*] Verifying database persistence...")
        conn = sqlite3.connect("data/simulation.db")
        c = conn.cursor()
        
        c.execute("SELECT alert_type, COUNT(*) FROM alerts GROUP BY alert_type")
        results = dict(c.fetchall())
        
        assert results.get("port_scan", 0) > 0, "[!] Port scan not persisted!"
        assert results.get("syn_flood", 0) > 0, "[!] SYN flood not persisted!"
        assert results.get("icmp_flood", 0) > 0, "[!] ICMP flood not persisted!"
        
        print("[+] All attacks successfully detected and persisted to database:")
        for alert_type, count in results.items():
            print(f"  * {alert_type}: {count} alerts")
            
        conn.close()
        
        print("\n" + "=" * 60)
        print("[+] ALL ATTACK VALIDATION TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[!] TEST FAILED: {e}")
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        fw.stop()

if __name__ == '__main__':
    run_advanced_simulation()
