import time
from analytics.scheduler import JobScheduler
from analytics.cache import AnalyticsCache

def validate_cache_scheduler():
    print("=== CACHE & SCHEDULER VALIDATION ===")
    
    scheduler = JobScheduler()
    cache = AnalyticsCache()
    
    counters = {"runs": 0}
    
    def dummy_job():
        # Simulate a 500ms aggregation query
        time.sleep(0.5)
        cache.set("top_talkers", [{"ip": "1.1.1.1", "bytes": 5000}])
        counters["runs"] += 1
        
    scheduler.register_job(dummy_job, interval_seconds=1)
    
    start = time.time()
    scheduler.start()
    
    print("\n[Scheduler]")
    print("Waiting for 3 execution cycles...")
    time.sleep(3.5)
    scheduler.stop()
    
    end = time.time()
    
    print(f"Total time elapsed: {end - start:.2f}s")
    print(f"Job executions: {counters['runs']} (Expected ~3)")
    print(f"Scheduling Drift: {(end - start) - 3.5:.2f}s")
    
    print("\n[Cache]")
    # Simulate 100 cache hits
    hit_start = time.time()
    for _ in range(100):
        val = cache.get("top_talkers")
    hit_end = time.time()
    
    print(f"100 Cache Reads latency: {(hit_end - hit_start)*1000:.2f}ms")
    print(f"Cache Data Integrity: {val[0]['ip'] == '1.1.1.1'}")

if __name__ == '__main__':
    validate_cache_scheduler()
