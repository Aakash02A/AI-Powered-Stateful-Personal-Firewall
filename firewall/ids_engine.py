from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from analytics.flow_engine import FlowEngine
from firewall.event_bus import EventBus
from firewall.models import Alert, Packet


class IDSEngine:
    def __init__(self, flow_engine: FlowEngine):
        self.tracker = flow_engine
        self.port_scan_threshold = 10  # unique ports in 10 seconds
        self.syn_flood_threshold = 50  # SYN packets in 5 seconds
        self.icmp_flood_threshold = 100  # ICMP packets in 5 seconds
        self.brute_force_threshold = 5  # Failed attempts in 30 seconds
        self.whitelist = {"127.0.0.1"}
        self.event_bus = EventBus()

        # Tracking state
        self.syn_packets = defaultdict(list)
        self.icmp_packets = defaultdict(list)
        self.port_scans = defaultdict(set)
        self.brute_force = defaultdict(list)

        self.suspicious_ports = {
            12345: "SSH alternative",
            8888: "HTTP alternative",
            6667: "IRC",
        }

    def _cleanup_old_records(self, record_dict, time_window: int):
        now = datetime.now()
        threshold = now - timedelta(seconds=time_window)

        for key in list(record_dict.keys()):
            if isinstance(record_dict[key], list):
                # Filter old timestamps
                record_dict[key] = [
                    t
                    for t in record_dict[key]
                    if isinstance(t, datetime)
                    and t > threshold
                    or (isinstance(t, tuple) and t[0] > threshold)
                ]
                if not record_dict[key]:
                    del record_dict[key]
            elif isinstance(record_dict[key], set):
                # For port scans we store tuples of (timestamp, port)
                record_dict[key] = {
                    item for item in record_dict[key] if item[0] > threshold
                }
                if not record_dict[key]:
                    del record_dict[key]

    def detect_suspicious_ports(self, packet: Packet) -> Optional[Alert]:
        if packet.dst_port in self.suspicious_ports:
            return Alert(
                alert_type="suspicious_port",
                severity="low",
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                description=f"Connection to suspicious port {packet.dst_port} ({self.suspicious_ports[packet.dst_port]})",
                action_taken="log",
            )
        return None

    def detect_brute_force(self, packet: Packet) -> Optional[Alert]:
        # Simple heuristic: if we see multiple SYNs to the same target without ESTABLISHED state
        if packet.protocol != "TCP" or "S" not in packet.flags:
            return None

        key = (packet.src_ip, packet.dst_ip, packet.dst_port)
        self.brute_force[key].append(packet.timestamp)
        self._cleanup_old_records(self.brute_force, 30)

        if len(self.brute_force[key]) > self.brute_force_threshold:
            self.brute_force[key].clear()
            return Alert(
                alert_type="brute_force",
                severity="high",
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                description=f"Possible brute-force detected from {packet.src_ip} to {packet.dst_ip}:{packet.dst_port}",
                action_taken="log",
            )
        return None

    def detect_port_scan(self, packet: Packet) -> Optional[Alert]:
        if packet.protocol != "TCP" or "S" not in packet.flags:
            return None

        self.port_scans[packet.src_ip].add((packet.timestamp, packet.dst_port))
        self._cleanup_old_records(self.port_scans, 10)

        unique_ports = len({port for _, port in self.port_scans[packet.src_ip]})
        if unique_ports > self.port_scan_threshold:
            # Clear to prevent flood of alerts
            self.port_scans[packet.src_ip].clear()
            return Alert(
                alert_type="port_scan",
                severity="high",
                src_ip=packet.src_ip,
                description=f"Detected port scan from {packet.src_ip} ({unique_ports} ports in 10s)",
                action_taken="log",
            )
        return None

    def detect_syn_flood(self, packet: Packet) -> Optional[Alert]:
        if packet.protocol != "TCP" or "S" not in packet.flags:
            return None

        key = (packet.src_ip, packet.dst_ip, packet.dst_port)
        self.syn_packets[key].append(packet.timestamp)
        self._cleanup_old_records(self.syn_packets, 5)

        if len(self.syn_packets[key]) > self.syn_flood_threshold:
            self.syn_packets[key].clear()
            return Alert(
                alert_type="syn_flood",
                severity="critical",
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                description=f"SYN flood detected from {packet.src_ip} to {packet.dst_ip}:{packet.dst_port}",
                action_taken="log",
            )
        return None

    def detect_icmp_flood(self, packet: Packet) -> Optional[Alert]:
        if packet.protocol != "ICMP":
            return None

        self.icmp_packets[packet.src_ip].append(packet.timestamp)
        self._cleanup_old_records(self.icmp_packets, 5)

        if len(self.icmp_packets[packet.src_ip]) > self.icmp_flood_threshold:
            self.icmp_packets[packet.src_ip].clear()
            return Alert(
                alert_type="icmp_flood",
                severity="medium",
                src_ip=packet.src_ip,
                description=f"ICMP flood detected from {packet.src_ip}",
                action_taken="log",
            )
        return None

    def analyze_packet(self, packet: Packet) -> List[Alert]:
        alerts = []
        if packet.src_ip in self.whitelist:
            return alerts

        alert1 = self.detect_port_scan(packet)
        if alert1:
            alerts.append(alert1)

        alert2 = self.detect_syn_flood(packet)
        if alert2:
            alerts.append(alert2)

        alert3 = self.detect_icmp_flood(packet)
        if alert3:
            alerts.append(alert3)

        alert4 = self.detect_suspicious_ports(packet)
        if alert4:
            alerts.append(alert4)

        alert5 = self.detect_brute_force(packet)
        if alert5:
            alerts.append(alert5)

        for alert in alerts:
            self.event_bus.publish("alerts", alert)

        return alerts
