import logging
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime

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
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

from functools import wraps
import traceback

def log_exceptions(logger: logging.Logger):
    """Decorator to catch and log unhandled exceptions in threads/loops"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Unhandled exception in {func.__name__}: {str(e)}", extra={"extra_data": {"traceback": traceback.format_exc()}})
        return wrapper
    return decorator
