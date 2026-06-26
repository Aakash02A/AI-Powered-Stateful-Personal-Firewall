import logging
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime
import functools
import threading
import traceback

logger = logging.getLogger(__name__)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.utcnow().isoformat() + "Z",
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
        return json.dumps(log_record)

def setup_logger(name: str, log_file: str) -> logging.Logger:
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(logging.INFO)
    
    if not custom_logger.handlers:
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
        handler.setFormatter(JSONFormatter())
        custom_logger.addHandler(handler)
        
    return custom_logger


def thread_safe_run(name: str, on_crash=None):
    """
    Decorator for thread target functions.
    Ensures exceptions don't kill threads silently.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"[{name}] Thread started successfully")
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                logger.info(f"[{name}] Thread interrupted (Ctrl+C)")
            except Exception as e:
                logger.critical(
                    f"[{name}] Thread crashed with unhandled exception: {type(e).__name__}: {e}",
                    exc_info=True
                )
                if on_crash and callable(on_crash):
                    try:
                        on_crash()
                    except:
                        logger.error(f"[{name}] Crash handler failed", exc_info=True)
                raise
            finally:
                logger.info(f"[{name}] Thread stopped")
        return wrapper
    return decorator

class ThreadHealthMonitor:
    """Monitor thread health and detect crashes"""
    
    def __init__(self):
        self.threads = {}
        self.crashed = {}
    
    def register(self, name: str, thread: threading.Thread):
        """Register a thread for monitoring"""
        self.threads[name] = thread
        self.crashed[name] = False
    
    def check_health(self) -> dict:
        """Return health status of all threads"""
        health = {}
        for name, thread in self.threads.items():
            health[name] = {
                "alive": thread.is_alive(),
                "crashed": self.crashed.get(name, False)
            }
        return health
    
    def mark_crashed(self, name: str):
        """Mark thread as crashed"""
        self.crashed[name] = True
        logger.critical(f"Thread '{name}' marked as crashed")
