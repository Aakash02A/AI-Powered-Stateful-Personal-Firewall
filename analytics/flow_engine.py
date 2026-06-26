from datetime import datetime, timedelta
from typing import Dict, Tuple

from firewall.models import Connection, Packet
from firewall.queue_manager import QueueManager


class FlowEngine:
    def __init__(self, timeout: int = 300, syn_timeout: int = 30):
        self.active_connections: Dict[Tuple[str, int, str, int, str], Connection] = {}
        self.timeout = timeout
        self.syn_timeout = syn_timeout
        self.queue_manager = QueueManager()

    def _get_canonical_key(self, packet: Packet) -> Tuple[str, int, str, int, str]:
        # Canonical bidirectional flow key
        if packet.src_ip < packet.dst_ip:
            return (
                packet.src_ip,
                packet.src_port,
                packet.dst_ip,
                packet.dst_port,
                packet.protocol,
            )
        elif packet.src_ip > packet.dst_ip:
            return (
                packet.dst_ip,
                packet.dst_port,
                packet.src_ip,
                packet.src_port,
                packet.protocol,
            )
        else:
            if packet.src_port <= packet.dst_port:
                return (
                    packet.src_ip,
                    packet.src_port,
                    packet.dst_ip,
                    packet.dst_port,
                    packet.protocol,
                )
            else:
                return (
                    packet.dst_ip,
                    packet.dst_port,
                    packet.src_ip,
                    packet.src_port,
                    packet.protocol,
                )

    def process_packet(self, packet: Packet) -> Connection:
        key = self._get_canonical_key(packet)
        now = datetime.now()

        if key not in self.active_connections:
            # Create new flow
            state = "NEW"
            if packet.protocol == "TCP":
                if "S" in packet.flags and "A" not in packet.flags:
                    state = "SYN_SENT"

            conn = Connection(
                src_ip=packet.src_ip,  # The initiator
                src_port=packet.src_port,
                dst_ip=packet.dst_ip,
                dst_port=packet.dst_port,
                protocol=packet.protocol,
                state=state,
                creation_time=now,
                last_activity=now,
                flow_start=now,
                packets_in=0,
                packets_out=0,
                bytes_in=0,
                bytes_out=0,
            )
            self.active_connections[key] = conn

        conn = self.active_connections[key]
        conn.last_activity = now

        # Ingress vs Egress relative to initiator
        if packet.src_ip == conn.src_ip:
            conn.packets_out += 1
            conn.bytes_out += packet.size
        else:
            conn.packets_in += 1
            conn.bytes_in += packet.size

        # Update metrics
        total_packets = (
            conn.packets_in + conn.conn_packets_out
            if hasattr(conn, "conn_packets_out")
            else conn.packets_in + conn.packets_out
        )
        total_bytes = conn.bytes_in + conn.bytes_out
        conn.avg_packet_size = total_bytes / total_packets if total_packets > 0 else 0

        duration = (now - conn.flow_start).total_seconds()
        conn.duration = duration
        if duration > 0:
            conn.packet_rate = total_packets / duration
            conn.byte_rate = total_bytes / duration

        # Update TCP State Machine
        if packet.protocol == "TCP":
            flags = packet.flags
            if conn.state == "SYN_SENT" and "S" in flags and "A" in flags:
                conn.state = "SYN_RECV"
            elif conn.state == "SYN_RECV" and "A" in flags and "S" not in flags:
                conn.state = "ESTABLISHED"
            elif (
                conn.state in ("NEW", "SYN_SENT", "SYN_RECV")
                and "A" in flags
                and "S" not in flags
            ):
                conn.state = "ESTABLISHED"
            elif "F" in flags:
                if conn.state == "ESTABLISHED":
                    conn.state = "FIN_WAIT"
                elif conn.state == "FIN_WAIT":
                    conn.state = "CLOSED"
            elif "R" in flags:
                conn.state = "CLOSED"

        return conn

    def clean_expired(self):
        now = datetime.now()
        expired_keys = []
        for key, conn in self.active_connections.items():
            if conn.state == "SYN_SENT":
                if now - conn.last_activity > timedelta(seconds=self.syn_timeout):
                    expired_keys.append(key)
            elif conn.state == "CLOSED":
                if now - conn.last_activity > timedelta(seconds=10):
                    expired_keys.append(key)
            else:
                if now - conn.last_activity > timedelta(seconds=self.timeout):
                    expired_keys.append(key)

        for key in expired_keys:
            conn = self.active_connections.pop(key)
            conn.flow_end = datetime.now()
            conn.duration = (conn.flow_end - conn.flow_start).total_seconds()
            # Push completed flow to DB queue
            self.queue_manager.push(conn)

    def get_connections(self, limit: int = 100, offset: int = 0) -> list:
        conns = list(self.active_connections.values())
        conns.sort(key=lambda x: x.last_activity, reverse=True)
        return conns[offset : offset + limit]
