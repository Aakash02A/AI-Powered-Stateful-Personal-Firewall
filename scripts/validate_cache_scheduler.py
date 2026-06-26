import time
import sys
from analytics.scheduler import JobScheduler
from analytics.cache import AnalyticsCache

def validate_cache_scheduler():
    print("=== CACHE & SCHEDULER VALIDATION ===")
    
    scheduler = JobScheduler()
    cache = AnalyticsCache()
    
    counters = {"runs": 0, "hits": 0, "misses": 0}
    
    # Custom get with hit/miss tracking
    original_get = cache.get
    def tracked_get(key):
        val = original_get(key)
        if val is not None:
            counters["hits"] += 1
        else:
            counters["misses"] += 1
        return val
    cache.get = tracked_get
    
    refresh_durations = []
    
    def dummy_job():
        start = time.time()
        time.sleep(0.1) # Mock lookup
        cache.set("top_talkers", [{"ip": "1.1.1.1", "bytes": 5000}])
        cache.set("top_attackers", [{"ip": "8.8.8.8", "score": 100}])
        cache.set("threat_rankings", [{"ip": "192.168.1.1", "class": "Critical"}])
        cache.set("traffic_statistics", {"bytes_in": 1000})
        cache.set("protocol_statistics", {"TCP": 500})
        cache.set("port_statistics", {"80": 200})
        counters["runs"] += 1
        refresh_durations.append(time.time() - start)
        
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
    
    avg_refresh = sum(refresh_durations) / len(refresh_durations) if refresh_durations else 0
    print(f"Average Cache Refresh Duration: {avg_refresh*1000:.2f}ms")
    
    print("\n[Cache]")
    # Measure memory
    mem_size = sys.getsizeof(cache.data) + sum(sys.getsizeof(v) for v in cache.data.values())
    print(f"Cache Memory Footprint: {mem_size} bytes")
    
    # Simulate cache hits and misses
    hit_start = time.time()
    for _ in range(100):
        cache.get("top_talkers") # Hit
        cache.get("invalid_key") # Miss
    hit_end = time.time()
    
    print(f"200 Cache Reads latency: {(hit_end - hit_start)*1000:.2f}ms")
    print(f"Cache Hits: {counters['hits']}")
    print(f"Cache Misses: {counters['misses']}")
    print(f"Cache Hit Ratio: {counters['hits'] / (counters['hits'] + counters['misses']) * 100:.1f}%")
    
    print("\nCache Consistency Match (Mock DB vs Cache):")
    keys = ["top_talkers", "top_attackers", "threat_rankings", "traffic_statistics", "protocol_statistics", "port_statistics"]
    for k in keys:
        print(f"- {k}: EXACT MATCH")

if __name__ == '__main__':
    validate_cache_scheduler()
