import time
import os
from analytics.scheduler import JobScheduler
from firewall.queue_manager import QueueManager
from firewall.db_writer import DBWriter

def validate_failures():
    print("=== FAILURE INJECTION VALIDATION ===")
    
    print("\n[Test 1: Scheduler Exception Recovery]")
    scheduler = JobScheduler()
    counters = {"success": 0}
    
    def bad_job():
        # Force a division by zero exception every time
        x = 1 / 0
        
    def good_job():
        counters["success"] += 1
        
    scheduler.register_job(bad_job, interval_seconds=1)
    scheduler.register_job(good_job, interval_seconds=1)
    
    scheduler.start()
    time.sleep(2.5)
    scheduler.stop()
    
    print("Expected: bad_job crashes silently with log, good_job continues.")
    print(f"Good Job Executions: {counters['success']} (Should be >0)")
    
    print("\n[Test 2: Database Writer Recovery (Simulated)]")
    # Simulate DB unavailability by passing an invalid path
    try:
        writer = DBWriter(db_path="sqlite:////invalid/path/db.db", batch_size=10, flush_interval=1)
        writer.start()
        
        qm = QueueManager()
        for i in range(5):
            qm.push("dummy_event")
            
        time.sleep(1.5)
        writer.stop()
        print("DBWriter gracefully caught the bad path or flushed cleanly without crashing the main process.")
    except Exception as e:
        print(f"DBWriter crashed: {e}")

if __name__ == '__main__':
    validate_failures()
