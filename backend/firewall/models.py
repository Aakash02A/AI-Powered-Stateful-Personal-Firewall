from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Packet:
    timestamp: datetime
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str  # TCP, UDP, ICMP, etc.
    flags: str  # TCP flags, e.g., 'S', 'SA', 'F', 'PA'
    size: int
    raw: Optional[bytes] = None


@dataclass
class Connection:
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    state: str  # SYN_SENT, ESTABLISHED, FIN_WAIT, CLOSED
    creation_time: datetime
    last_activity: datetime
    packets_in: int = 0
    packets_out: int = 0
    bytes_in: int = 0
    bytes_out: int = 0

    # Phase 2 Analytics Fields
    flow_start: Optional[datetime] = None
    flow_end: Optional[datetime] = None
    duration: float = 0.0
    avg_packet_size: float = 0.0
    packet_rate: float = 0.0
    byte_rate: float = 0.0


@dataclass
class FirewallRule:
    rule_id: str
    priority: int
    enabled: bool
    protocol: str  # tcp, udp, icmp, any
    src_ip: str  # IP, CIDR, wildcard (any)
    src_port: str  # port, range, any
    dst_ip: str
    dst_port: str
    direction: str  # inbound, outbound, both
    action: str  # allow, block, drop, log
    description: str
    expires_at: Optional[str] = None


@dataclass
class FirewallEvent:
    timestamp: datetime
    rule_id: str
    action: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    reason: str


@dataclass
class Alert:
    timestamp: datetime = field(default_factory=datetime.now)
    alert_type: str = "general"
    severity: str = "low"  # low, medium, high, critical
    src_ip: str = ""
    dst_ip: str = ""
    description: str = ""
    action_taken: str = "none"
    details: Optional[dict] = None
