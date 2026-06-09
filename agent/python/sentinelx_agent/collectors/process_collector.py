"""
Process Collector — monitors running processes for suspicious activity.
Uses psutil for cross-platform process enumeration.
"""
import asyncio
import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import psutil

if TYPE_CHECKING:
    from sentinelx_agent.config import AgentConfig
    from sentinelx_agent.transport.http_client import TelemetryClient

logger = logging.getLogger("sentinelx.collector.process")

# Known LOLBins (Living Off the Land Binaries) that are commonly abused
LOLBINS = {
    "certutil.exe", "bitsadmin.exe", "mshta.exe", "regsvr32.exe",
    "rundll32.exe", "wscript.exe", "cscript.exe", "wmic.exe",
    "msiexec.exe", "installutil.exe", "regasm.exe", "regsvcs.exe",
    "msbuild.exe", "cmstp.exe", "forfiles.exe", "pcalua.exe",
    "bash.exe", "explorer.exe", "schtasks.exe", "at.exe",
}

# Credential dumping indicators
CRED_DUMP_KEYWORDS = {
    "lsass", "mimikatz", "sekurlsa", "wce.exe", "procdump",
    "comsvcs", "minidum", "ntdsa", "ntdsutil",
}


class ProcessCollector:
    def __init__(self, config: "AgentConfig", client: "TelemetryClient") -> None:
        self._config = config
        self._client = client
        self._seen_pids: set[int] = set()

    async def start(self) -> None:
        """Run the process collection loop."""
        logger.info("Process collector started (interval=%ds)", self._config.process_interval)
        while True:
            try:
                await self._collect_processes()
            except Exception as exc:
                logger.error("Process collection error: %s", exc, exc_info=True)
            await asyncio.sleep(self._config.process_interval)

    async def _collect_processes(self) -> None:
        current_pids: set[int] = set()

        for proc in psutil.process_iter(
            attrs=["pid", "ppid", "name", "exe", "cmdline", "username", "create_time"]
        ):
            try:
                info = proc.info
                pid = info["pid"]
                current_pids.add(pid)

                # Only report new processes
                if pid in self._seen_pids:
                    continue

                event = self._build_event(info)
                if event:
                    await self._client.enqueue(event)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Detect terminated processes
        terminated = self._seen_pids - current_pids
        for pid in terminated:
            await self._client.enqueue({
                "event_type": "process_terminate",
                "occurred_at": datetime.now(UTC).isoformat(),
                "payload": {"pid": pid},
            })

        self._seen_pids = current_pids

    def _build_event(self, info: dict) -> dict | None:
        name = (info.get("name") or "").lower()
        cmdline = " ".join(info.get("cmdline") or [])
        exe = info.get("exe") or ""

        # Hash the executable (if accessible)
        sha256 = self._hash_file(exe) if exe else None

        payload = {
            "process_name": name,
            "pid": info["pid"],
            "parent_pid": info["ppid"],
            "command_line": cmdline[:4096],  # Truncate to avoid huge payloads
            "executable": exe,
            "user": info.get("username"),
            "sha256": sha256,
        }

        # Enrich with detection flags
        flags = []
        if name in LOLBINS:
            flags.append("lolbin")
        if any(kw in cmdline.lower() for kw in CRED_DUMP_KEYWORDS):
            flags.append("credential_access")
        if "powershell" in name and any(
            kw in cmdline.lower() for kw in ("-enc", "-encodedcommand", "downloadstring", "iex")
        ):
            flags.append("powershell_abuse")

        if flags:
            payload["detection_flags"] = flags
            logger.warning("Suspicious process detected: %s flags=%s", name, flags)

        return {
            "event_type": "process_create",
            "occurred_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        }

    @staticmethod
    def _hash_file(path: str) -> str | None:
        """SHA-256 hash of a file. Returns None on error."""
        try:
            p = Path(path)
            if not p.is_file() or p.stat().st_size > 100 * 1024 * 1024:  # Skip files > 100MB
                return None
            sha256 = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (PermissionError, OSError):
            return None
