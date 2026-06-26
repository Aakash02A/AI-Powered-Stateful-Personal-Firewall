import threading
import time
from typing import Callable, List, Dict

class JobScheduler:
    def __init__(self):
        self.jobs: List[Dict] = []
        self.running = False
        self.thread = None

    def register_job(self, func: Callable, interval_seconds: int):
        self.jobs.append({
            "func": func,
            "interval": interval_seconds,
            "last_run": time.time()
        })

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _run_loop(self):
        while self.running:
            now = time.time()
            for job in self.jobs:
                if now - job["last_run"] >= job["interval"]:
                    try:
                        job["func"]()
                    except Exception as e:
                        print(f"[Scheduler] Error running job {job['func'].__name__}: {e}")
                    job["last_run"] = time.time()
            time.sleep(1)
