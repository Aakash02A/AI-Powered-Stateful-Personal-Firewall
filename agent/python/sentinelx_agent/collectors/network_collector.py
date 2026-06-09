"""
Network Collector — monitors active connections and DNS activity.
Uses psutil for cross-platform connection enumeration.
"""
import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import psutil

if TYPE_CHECKING:
    from sentinelx_agent.config import AgentConfig
    from sentinelx_agent.transport.http_client import TelemetryClient

logger = logging.getLogger("sentinelx.collector.network")

# Common C2 / suspicious ports
SUSPICIOUS_PORTS = {23, 445, 1433, 3389, 4444, 5900, 6660, 6661, 6662, 6663, 31337}


class NetworkCollector:
    def __init__(self, config: "AgentConfig", client: "TelemetryClient") -> None:
        self._config = config
        self._client = client
        self._seen_connections: set[tuple] = set()

    async def start(self) -> None:
        logger.info("Network collector started (interval=%ds)", self._config.network_interval)
        while True:
            try:
                await self._collect()
            except Exception as exc:
                logger.error("Network collection error: %s", exc, exc_info=True)
            await asyncio.sleep(self._config.network_interval)

    async def _collect(self) -> None:
        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            logger.warning("Cannot access network connections — try running as administrator")
            return

        current: set[tuple] = set()
        for conn in connections:
            if conn.status != "ESTABLISHED" or not conn.raddr:
                continue

            key = (conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port, conn.pid)
            current.add(key)

            if key not in self._seen_connections:
                raddr = conn.raddr
                is_suspicious = raddr.port in SUSPICIOUS_PORTS or raddr.port in self._config.suspicious_ports
                if is_suspicious:
                    logger.warning(
                        "Suspicious connection: %s:%d -> %s:%d (PID %d)",
                        conn.laddr.ip, conn.laddr.port, raddr.ip, raddr.port, conn.pid or 0,
                    )

                await self._client.enqueue({
                    "event_type": "network_connection",
                    "occurred_at": datetime.now(UTC).isoformat(),
                    "payload": {
                        "src_ip": conn.laddr.ip,
                        "src_port": conn.laddr.port,
                        "dst_ip": raddr.ip,
                        "dst_port": raddr.port,
                        "protocol": "tcp" if conn.type == 1 else "udp",
                        "pid": conn.pid,
                        "status": conn.status,
                        "is_suspicious_port": is_suspicious,
                    },
                })

        self._seen_connections = current
