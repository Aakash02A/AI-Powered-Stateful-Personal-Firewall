from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from firewall.models import Packet, Connection

class ConnectionTracker:
    def __init__(self, timeout: int = 300, syn_timeout: int = 30):
        self.active_connections: Dict[Tuple[str, int, str, int, str], Connection] = {}
        self.timeout = timeout
        self.syn_timeout = syn_timeout

    def _get_connection_key(self, packet: Packet) -> Tuple[str, int, str, int, str]:
        # Sort IPs and ports to ensure bidirectional matching
        if packet.src_ip < packet.dst_ip:
            return (packet.src_ip, packet.src_port, packet.dst_ip, packet.dst_port, packet.protocol)
        elif packet.src_ip > packet.dst_ip:
            return (packet.dst_ip, packet.dst_port, packet.src_ip, packet.src_port, packet.protocol)
        else:
            if packet.src_port <= packet.dst_port:
                return (packet.src_ip, packet.src_port, packet.dst_ip, packet.dst_port, packet.protocol)
            else:
                return (packet.dst_ip, packet.dst_port, packet.src_ip, packet.src_port, packet.protocol)

    def update_state(self, packet: Packet) -> Connection:
        key = self._get_connection_key(packet)
        now = datetime.now()
        
        if key not in self.active_connections:
            # Create new connection
            state = "NEW"
            if packet.protocol == "TCP":
                if "S" in packet.flags and "A" not in packet.flags:
                    state = "SYN_SENT"
            
            conn = Connection(
                src_ip=packet.src_ip,
                src_port=packet.src_port,
                dst_ip=packet.dst_ip,
                dst_port=packet.dst_port,
                protocol=packet.protocol,
                state=state,
                start_time=now,
                last_activity=now,
                packets_in=0,
                packets_out=0,
                bytes_in=0,
                bytes_out=0
            )
            self.active_connections[key] = conn

        conn = self.active_connections[key]
        conn.last_activity = now
        
        # Update metrics
        if packet.src_ip == conn.src_ip:
            conn.packets_out += 1
            conn.bytes_out += packet.size
        else:
            conn.packets_in += 1
            conn.bytes_in += packet.size
            
        # Update TCP State Machine
        if packet.protocol == "TCP":
            flags = packet.flags
            if conn.state == "SYN_SENT" and "S" in flags and "A" in flags:
                conn.state = "SYN_RECV"
            elif conn.state == "SYN_RECV" and "A" in flags and "S" not in flags:
                conn.state = "ESTABLISHED"
            elif conn.state in ("NEW", "SYN_SENT", "SYN_RECV") and "A" in flags and "S" not in flags:
                # Catch-all for established connections where we missed the handshake
                conn.state = "ESTABLISHED"
            elif "F" in flags or "R" in flags:
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
            del self.active_connections[key]

    def get_connections(self, limit: int = 100, offset: int = 0) -> list:
        # returns sorted by last activity
        conns = list(self.active_connections.values())
        conns.sort(key=lambda x: x.last_activity, reverse=True)
        return conns[offset:offset+limit]
