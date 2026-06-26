import logging
import sqlite3
import threading
import time

from firewall.database import FirewallDatabase
from firewall.logger import thread_safe_run
from firewall.queue_manager import QueueManager


class DBWriter:
    def __init__(
        self,
        db_path: str = "sqlite:///data/firewall.db",
        batch_size: int = 100,
        flush_interval: int = 5,
    ):
        self.db = FirewallDatabase(db_path)
        self.queue_manager = QueueManager()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()
        self.running = False
        self.thread = None
        self.on_crash = None

    def start(self, on_crash=None):
        self.running = True
        self.on_crash = on_crash

        @thread_safe_run("DBWriter", on_crash=self.on_crash)
        def run_writer():
            self._run_loop()

        self.thread = threading.Thread(target=run_writer, daemon=False)
        self.thread.start()

    def _run_loop(self):
        while self.running:
            try:
                item = self.queue_manager.pop(timeout=1.0)
                if item:
                    self.buffer.append(item)

                now = time.time()
                if (
                    len(self.buffer) >= self.batch_size
                    or (now - self.last_flush) >= self.flush_interval
                ):
                    if self.buffer:
                        self._flush()
                    self.last_flush = now

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    # It's normal under heavy concurrent load, retry shortly
                    time.sleep(0.1)
                    continue
                raise
            except Exception as e:
                # Log and continue instead of crashing the whole thread
                logging.getLogger("system").error(
                    f"DB writer loop error: {e}", exc_info=True
                )
                time.sleep(1)
                continue

    def _flush(self):
        self.db.bulk_insert(self.buffer)
        self.buffer.clear()

    def stop(self):
        logging.getLogger("system").info("Stopping DBWriter and draining queues...")
        self.running = False
        self.on_crash = None
        if self.thread:
            self.thread.join(timeout=2.0)

        # Drain remaining items in queue
        while not self.queue_manager.empty():
            item = self.queue_manager.pop(timeout=0.1)
            if item:
                self.buffer.append(item)

        if self.buffer:
            self._flush()
        logging.getLogger("system").info("DBWriter stopped successfully.")
