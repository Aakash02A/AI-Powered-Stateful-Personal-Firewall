import time
import os
import threading
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from firewall.firewall import PersonalFirewall
from firewall.models import Packet, FirewallRule
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, queue):
        self.queue = queue
        self.running = False
        self.cpu_usage = []
        self.mem_usage = []
        self.q_depths = []
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
            
    def _monitor_loop(self):
        process = psutil.Process(os.getpid()) if HAS_PSUTIL else None
        while self.running:
            if process:
                self.cpu_usage.append(process.cpu_percent(interval=0.1))
                self.mem_usage.append(process.memory_info().rss / 1024 / 1024)
            self.q_depths.append(self.queue.qsize())
            time.sleep(0.1)

def run_benchmark(packet_count):
    if os.path.exists("bench.db"):
        os.remove("bench.db")
        
    fw = PersonalFirewall(db_path="sqlite:///bench.db")
    fw.rule_engine.add_rule(FirewallRule(
        rule_id="allow_all", priority=10, enabled=True, protocol="tcp",
        src_ip="any", src_port="any", dst_ip="any", dst_port="any",
        direction="both", action="allow", description="Allow All"
    ))
    
    p = Packet(timestamp=datetime.now(), src_ip="192.168.1.100", src_port=12345, dst_ip="10.0.0.1", dst_port=80, protocol="TCP", flags="S", size=60)
    
    fw.start()
    
    monitor = PerformanceMonitor(fw.queue_manager)
    monitor.start()
    
    start_time = time.time()
    for _ in range(packet_count):
        fw._process_packet(p)
        
    produce_time = time.time() - start_time
    
    while fw.queue_manager.qsize() > 0 or len(fw.db_writer.buffer) > 0:
        time.sleep(0.01)
        
    total_time = time.time() - start_time
    monitor.stop()
    fw.stop()
    
    print(f"\n--- Benchmark: {packet_count} Packets ---")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Packets Processed / Sec (PPS): {packet_count / total_time:.2f} pps")
    print(f"DB Writes / Sec: {packet_count / total_time:.2f}")
    if monitor.cpu_usage:
        avg_cpu = sum(monitor.cpu_usage) / len(monitor.cpu_usage)
        print(f"Average CPU Utilization: {avg_cpu:.1f}%")
        avg_mem = sum(monitor.mem_usage) / len(monitor.mem_usage)
        print(f"Average Memory Utilization: {avg_mem:.1f} MB")
        
    avg_q = sum(monitor.q_depths) / len(monitor.q_depths) if monitor.q_depths else 0
    print(f"Average Queue Depth Over Time: {avg_q:.1f}")

if __name__ == '__main__':
    print("=== EXPANDED BENCHMARK MONITORING ===")
    for count in [10000, 50000, 100000]:
        run_benchmark(count)
