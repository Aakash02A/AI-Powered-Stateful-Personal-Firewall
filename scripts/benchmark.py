import time
import os
import sqlite3
from datetime import datetime
from firewall.firewall import PersonalFirewall
from firewall.models import Packet, FirewallRule
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def run_benchmarks():
    print("--- FIREWALL BENCHMARK SUITE ---")
    
    # Setup DB
    if os.path.exists("benchmark.db"):
        os.remove("benchmark.db")
    
    fw = PersonalFirewall(db_path="sqlite:///benchmark.db")
    fw.rule_engine.add_rule(FirewallRule(
        rule_id="allow_all", priority=10, enabled=True, protocol="tcp",
        src_ip="any", src_port="any", dst_ip="any", dst_port="any",
        direction="both", action="allow", description="Allow All"
    ))
    
    packet_count = 10000
    p = Packet(timestamp=datetime.now(), src_ip="192.168.1.100", src_port=12345, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", flags="S", size=60)
    
    start_time = time.time()
    for _ in range(packet_count):
        fw._process_packet(p)
    end_time = time.time()
    
    duration = end_time - start_time
    pps = packet_count / duration
    
    print(f"Packets Processed: {packet_count}")
    print(f"Time Taken: {duration:.2f} seconds")
    print(f"Packets Per Second (PPS): {pps:.2f} pps")
    
    # Memory profiling
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        print(f"Memory Usage: {mem_info.rss / 1024 / 1024:.2f} MB")
        
    # DB Growth rate
    db_size = os.path.getsize("benchmark.db")
    print(f"Database size after {packet_count} packets: {db_size / 1024:.2f} KB")
    
    if os.path.exists("benchmark.db"):
        os.remove("benchmark.db")

if __name__ == '__main__':
    run_benchmarks()
