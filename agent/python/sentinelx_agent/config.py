"""
Agent configuration — loaded from environment variables or a config file.
"""
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path


AGENT_VERSION = "0.1.0"


@dataclass
class AgentConfig:
    # ── API ──────────────────────────────────────────────────
    api_url: str = "http://localhost:8001"
    api_timeout: int = 10

    # ── Identity ─────────────────────────────────────────────
    agent_version: str = AGENT_VERSION
    hostname: str = field(default_factory=platform.node)
    os_type: str = field(default_factory=platform.system)
    os_version: str = field(default_factory=platform.version)

    # ── Storage ──────────────────────────────────────────────
    data_dir: Path = field(default_factory=lambda: Path.home() / ".sentinelx")
    token_file: str = "agent_token.dat"

    # ── Collection intervals (seconds) ───────────────────────
    process_interval: int = 5
    file_watch_paths: list[str] = field(default_factory=lambda: [
        str(Path.home()),
        "C:\\Windows\\System32" if platform.system() == "Windows" else "/etc",
        "C:\\Windows\\Temp" if platform.system() == "Windows" else "/tmp",
    ])
    network_interval: int = 10
    system_interval: int = 60
    heartbeat_interval: int = 60

    # ── Batching ─────────────────────────────────────────────
    batch_size: int = 100
    batch_flush_interval: int = 5

    # ── Detection thresholds ─────────────────────────────────
    suspicious_ports: list[int] = field(default_factory=lambda: [
        22, 23, 445, 1433, 3306, 3389, 5900, 6379, 9200,
    ])

    @classmethod
    def load(cls) -> "AgentConfig":
        """Load config from environment variables with defaults."""
        data_dir = Path(os.environ.get("SENTINELX_DATA_DIR", Path.home() / ".sentinelx"))
        data_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            api_url=os.environ.get("SENTINELX_API_URL", "http://localhost:8001"),
            api_timeout=int(os.environ.get("SENTINELX_API_TIMEOUT", "10")),
            data_dir=data_dir,
            process_interval=int(os.environ.get("SENTINELX_PROCESS_INTERVAL", "5")),
            heartbeat_interval=int(os.environ.get("SENTINELX_HEARTBEAT_INTERVAL", "60")),
            batch_size=int(os.environ.get("SENTINELX_BATCH_SIZE", "100")),
        )

    @property
    def token_path(self) -> Path:
        return self.data_dir / self.token_file
