"""
System Collector — collects CPU, RAM, disk usage, running services.
"""
import asyncio
import logging
import platform
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import psutil

if TYPE_CHECKING:
    from sentinelx_agent.config import AgentConfig
    from sentinelx_agent.transport.http_client import TelemetryClient

logger = logging.getLogger("sentinelx.collector.system")


class SystemCollector:
    def __init__(self, config: "AgentConfig", client: "TelemetryClient") -> None:
        self._config = config
        self._client = client

    async def start(self) -> None:
        logger.info("System collector started (interval=%ds)", self._config.system_interval)
        while True:
            try:
                await self._collect()
            except Exception as exc:
                logger.error("System collection error: %s", exc, exc_info=True)
            await asyncio.sleep(self._config.system_interval)

    async def _collect(self) -> None:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        payload = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(vm.total / 1e9, 2),
            "ram_used_gb": round(vm.used / 1e9, 2),
            "ram_percent": vm.percent,
            "disk_total_gb": round(disk.total / 1e9, 2),
            "disk_used_gb": round(disk.used / 1e9, 2),
            "disk_percent": disk.percent,
            "net_bytes_sent": net.bytes_sent,
            "net_bytes_recv": net.bytes_recv,
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": platform.node(),
        }

        await self._client.enqueue({
            "event_type": "system_health",
            "occurred_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        })
