"""
Registry Collector — monitors Windows registry keys for persistence mechanisms.
Windows-only. Uses the winreg module.
"""
import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentinelx_agent.config import AgentConfig
    from sentinelx_agent.transport.http_client import TelemetryClient

logger = logging.getLogger("sentinelx.collector.registry")

# Keys commonly abused for persistence (T1547)
WATCH_KEYS = [
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM"),
    (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", "HKLM"),
    (r"SYSTEM\CurrentControlSet\Services", "HKLM"),
]


class RegistryCollector:
    def __init__(self, config: "AgentConfig", client: "TelemetryClient") -> None:
        self._config = config
        self._client = client
        self._snapshots: dict[str, dict] = {}

    async def start(self) -> None:
        logger.info("Registry collector started")
        while True:
            try:
                await self._scan()
            except Exception as exc:
                logger.error("Registry scan error: %s", exc, exc_info=True)
            await asyncio.sleep(30)  # Scan every 30 seconds

    async def _scan(self) -> None:
        try:
            import winreg
        except ImportError:
            return  # Not Windows

        hive_map = {
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
        }

        for key_path, hive_name in WATCH_KEYS:
            hive = hive_map.get(hive_name)
            if hive is None:
                continue

            snapshot_key = f"{hive_name}\\{key_path}"
            current: dict[str, str] = {}

            try:
                with winreg.OpenKey(hive, key_path) as reg_key:
                    i = 0
                    while True:
                        try:
                            name, data, _ = winreg.EnumValue(reg_key, i)
                            current[name] = str(data)
                            i += 1
                        except OSError:
                            break
            except OSError:
                continue

            # Compare with previous snapshot
            prev = self._snapshots.get(snapshot_key, {})

            for name, data in current.items():
                if name not in prev:
                    logger.warning("New registry persistence: %s\\%s = %s", snapshot_key, name, data)
                    await self._client.enqueue({
                        "event_type": "registry_set",
                        "occurred_at": datetime.now(UTC).isoformat(),
                        "payload": {
                            "hive": hive_name,
                            "key": key_path,
                            "value_name": name,
                            "value_data": data[:1024],
                            "action": "new_entry",
                            "is_persistence_key": True,
                        },
                    })
                elif prev[name] != data:
                    await self._client.enqueue({
                        "event_type": "registry_set",
                        "occurred_at": datetime.now(UTC).isoformat(),
                        "payload": {
                            "hive": hive_name,
                            "key": key_path,
                            "value_name": name,
                            "value_data": data[:1024],
                            "action": "modified",
                            "is_persistence_key": True,
                        },
                    })

            for name in prev:
                if name not in current:
                    await self._client.enqueue({
                        "event_type": "registry_delete",
                        "occurred_at": datetime.now(UTC).isoformat(),
                        "payload": {
                            "hive": hive_name,
                            "key": key_path,
                            "value_name": name,
                            "action": "deleted",
                        },
                    })

            self._snapshots[snapshot_key] = current
