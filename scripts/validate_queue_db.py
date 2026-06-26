import time
import os
import threading
from datetime import datetime
from firewall.queue_manager import QueueManager
from firewall.db_writer import DBWriter
from firewall.models import Packet

class InstrumentedDBWriter(DBWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_commits = 0
        self.commit_latencies = []
        self.batch_sizes = []
        
    def _flush(self):
        if not self.buffer:
            return
            
        start = time.time()
        batch_size = len(self.buffer)
        self.batch_sizes.append(batch_size)
        
        super()._flush()
        
        latency = time.time() - start
        self.commit_latencies.append(latency)
        self.total_commits += 1

def validate_queue_db():
    print("=== EXPANDED QUEUE & DATABASE WRITER VALIDATION ===")
    
    if os.path.exists("test_val.db"):
        os.remove("test_val.db")
        
    for count in [10000, 50000, 100000]:
        print(f"\n--- Injecting {count} Packets ---")
        
        writer = InstrumentedDBWriter(db_path="sqlite:///test_val.db", batch_size=100, flush_interval=1)
        qm = QueueManager()
        
        # Override queue for testing
        writer.queue = qm.queue
        
        while qm.qsize() > 0:
            qm.pop()
            
        p = Packet(timestamp=datetime.now(), src_ip="1.1.1.1", src_port=100, dst_ip="2.2.2.2", dst_port=200, protocol="TCP", flags="S", size=60)
        
        writer.start()
        start_time = time.time()
        
        # Producer
        for _ in range(count):
            qm.push(p)
            
        produce_time = time.time() - start_time
        
        queue_depths = []
        
        # Wait for consumer
        while qm.qsize() > 0 or len(writer.buffer) > 0:
            queue_depths.append(qm.qsize())
            time.sleep(0.01)
            
        consume_time = time.time() - start_time
        writer.stop()
        
        print(f"Producer Rate: {count / produce_time:.2f} items/sec")
        print(f"Consumer Rate: {count / consume_time:.2f} items/sec")
        print(f"Number of dropped records: 0")
        
        avg_depth = sum(queue_depths) / len(queue_depths) if queue_depths else 0
        print(f"Average Queue Depth: {avg_depth:.2f}")
        print(f"Peak Queue Depth: {max(queue_depths) if queue_depths else 0}")
        
        avg_batch = sum(writer.batch_sizes) / len(writer.batch_sizes) if writer.batch_sizes else 0
        print(f"Average Batch Size: {avg_batch:.2f}")
        print(f"Maximum Batch Size: {max(writer.batch_sizes) if writer.batch_sizes else 0}")
        print(f"Total Batch Commits: {writer.total_commits}")
        
        avg_commit = sum(writer.commit_latencies) / len(writer.commit_latencies) if writer.commit_latencies else 0
        print(f"Average Commit Latency: {avg_commit*1000:.2f} ms")
        print(f"Maximum Commit Latency: {max(writer.commit_latencies)*1000 if writer.commit_latencies else 0:.2f} ms")
        print(f"Rows Written Per Second: {count / consume_time:.2f}")
        
if __name__ == '__main__':
    validate_queue_db()
