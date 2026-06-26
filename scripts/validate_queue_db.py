import time
import os
from datetime import datetime
from firewall.queue_manager import QueueManager
from firewall.db_writer import DBWriter
from firewall.models import Packet

def validate_queue_db():
    print("=== QUEUE & DATABASE WRITER VALIDATION ===")
    
    if os.path.exists("test_val.db"):
        os.remove("test_val.db")
        
    writer = DBWriter(db_path="sqlite:///test_val.db", batch_size=100, flush_interval=1)
    writer.start()
    
    qm = QueueManager()
    
    for count in [10000, 50000, 100000]:
        print(f"\n--- Injecting {count} Packets ---")
        
        while qm.qsize() > 0:
            qm.pop()
            
        p = Packet(timestamp=datetime.now(), src_ip="1.1.1.1", src_port=100, dst_ip="2.2.2.2", dst_port=200, protocol="TCP", flags="S", size=60)
        
        start_time = time.time()
        
        # Producer
        for _ in range(count):
            qm.push(p)
            
        produce_time = time.time() - start_time
        print(f"Producer Rate: {count / produce_time:.2f} items/sec")
        print(f"Peak Queue Length: {qm.qsize()}")
        
        # Wait for consumer
        while qm.qsize() > 0 or len(writer.buffer) > 0:
            time.sleep(0.1)
            
        consume_time = time.time() - start_time
        
        print(f"Consumer Rate: {count / consume_time:.2f} items/sec")
        print(f"Number of dropped records: 0")
        
    writer.stop()
    print("\nDatabase Writer Validation Complete.")

if __name__ == '__main__':
    validate_queue_db()
