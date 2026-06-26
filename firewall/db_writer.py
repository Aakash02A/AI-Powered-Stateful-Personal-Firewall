import threading
import time
from firewall.queue_manager import QueueManager
from firewall.database import FirewallDatabase
from firewall.models import Packet, Connection, FirewallEvent, Alert

class DBWriter(threading.Thread):
    def __init__(self, db_path: str = "sqlite:///firewall.db", batch_size: int = 100, flush_interval: int = 5):
        super().__init__(daemon=True)
        self.db = FirewallDatabase(db_path)
        self.queue_manager = QueueManager()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()
        self.running = True

    def run(self):
        while self.running:
            item = self.queue_manager.pop(timeout=1.0)
            if item:
                self.buffer.append(item)
                
            now = time.time()
            if len(self.buffer) >= self.batch_size or (now - self.last_flush) >= self.flush_interval:
                if self.buffer:
                    self._flush()
                self.last_flush = now
                
    def _flush(self):
        self.db.bulk_insert(self.buffer)
        self.buffer.clear()
        
    def stop(self):
        self.running = False
        if self.buffer:
            self._flush()
