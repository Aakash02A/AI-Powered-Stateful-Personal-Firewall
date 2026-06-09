"""
File Collector — monitors filesystem events using watchdog.
Detects ransomware patterns, malware droppers, and suspicious extensions.
"""
import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from sentinelx_agent.config import AgentConfig
    from sentinelx_agent.transport.http_client import TelemetryClient

logger = logging.getLogger("sentinelx.collector.file")

# Known ransomware extensions
RANSOMWARE_EXTENSIONS = {
    ".locked", ".encrypted", ".crypt", ".zepto", ".cerber", ".locky",
    ".wnry", ".wncry", ".wcry", ".cryptolocker", ".vault", ".zzzzz",
    ".aaa", ".abc", ".xyz", ".micro", ".xxx", ".ttt", ".mp3", ".ccc",
    ".vvv", ".zzz", ".666", ".coin", ".encrypted", ".ezz", ".exx",
}

# Suspicious script extensions dropped by malware
SUSPICIOUS_EXTENSIONS = {
    ".ps1", ".vbs", ".js", ".jse", ".wsf", ".hta", ".bat", ".cmd",
    ".scr", ".pif", ".jar", ".lnk",
}

# Directories to always ignore
IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "AppData\\Local\\Temp" if True else "/tmp",
}


class _SentinelXEventHandler(FileSystemEventHandler):
    def __init__(self, queue: "Queue[dict]") -> None:
        super().__init__()
        self._queue = queue

    def _should_ignore(self, path: str) -> bool:
        p = Path(path)
        return any(part in IGNORE_DIRS for part in p.parts)

    def _emit(self, event_type: str, path: str, dest: str | None = None) -> None:
        if self._should_ignore(path):
            return
        p = Path(path)
        self._queue.put({
            "event_type": event_type,
            "occurred_at": datetime.now(UTC).isoformat(),
            "payload": {
                "path": path,
                "name": p.name,
                "extension": p.suffix.lower(),
                "dest_path": dest,
                "is_ransomware_ext": p.suffix.lower() in RANSOMWARE_EXTENSIONS,
                "is_suspicious_ext": p.suffix.lower() in SUSPICIOUS_EXTENSIONS,
            },
        })

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._emit("file_create", event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._emit("file_delete", event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._emit("file_modify", event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._emit("file_rename", event.src_path, dest=event.dest_path)
            # Check if renamed TO a ransomware extension
            dest = Path(event.dest_path)
            if dest.suffix.lower() in RANSOMWARE_EXTENSIONS:
                logger.warning("Ransomware extension detected: %s → %s", event.src_path, event.dest_path)


class FileCollector:
    def __init__(self, config: "AgentConfig", client: "TelemetryClient") -> None:
        self._config = config
        self._client = client
        self._queue: Queue[dict] = Queue(maxsize=10000)

    async def start(self) -> None:
        """Start watchdog observer and drain queue."""
        handler = _SentinelXEventHandler(self._queue)
        observer = Observer()

        for watch_path in self._config.file_watch_paths:
            p = Path(watch_path)
            if p.exists():
                observer.schedule(handler, str(p), recursive=True)
                logger.info("Watching path: %s", p)

        thread = Thread(target=observer.start, daemon=True)
        thread.start()
        logger.info("File collector started, watching %d paths", len(self._config.file_watch_paths))

        # Drain the event queue asynchronously
        while True:
            try:
                event = self._queue.get_nowait()
                await self._client.enqueue(event)

                # Warn on ransomware patterns
                if event["payload"].get("is_ransomware_ext"):
                    logger.critical("RANSOMWARE PATTERN DETECTED: %s", event["payload"]["path"])

            except Empty:
                await asyncio.sleep(0.1)
            except Exception as exc:
                logger.error("File collector error: %s", exc)
                await asyncio.sleep(1)
