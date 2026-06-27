import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from analytics.flow_engine import FlowEngine
from firewall.event_bus import EventBus
from firewall.models import Alert, Packet
from ml.ml_detector import MLAnomalyDetector


class IDSEngine:
    def __init__(self, flow_engine: FlowEngine, config_path: str = "firewall/config/ids_config.json"):
        self.tracker = flow_engine
        self.event_bus = EventBus()
        self.ml_detector = MLAnomalyDetector()
        
        self.config_path = config_path
        self._init_state()
        self._load_config()

        self.whitelist = {"127.0.0.1"}

    def _load_config(self):
        try:
            path = Path(self.config_path)
            if path.exists():
                with open(path, "r") as f:
                    config = json.load(f)
                self.port_scan_threshold = config.get("port_scan_threshold", 10)
                self.syn_flood_threshold = config.get("syn_flood_threshold", 50)
                self.icmp_flood_threshold = config.get("icmp_flood_threshold", 100)
                self.brute_force_threshold = config.get("brute_force_threshold", 5)
                
                windows = config.get("time_windows", {})
                self.window_port_scan = windows.get("port_scan", 10)
                self.window_syn_flood = windows.get("syn_flood", 5)
                self.window_icmp_flood = windows.get("icmp_flood", 5)
                self.window_brute_force = windows.get("brute_force", 30)
            else:
                self._set_default_config()
        except Exception:
            self._set_default_config()

    def _set_default_config(self):
        self.port_scan_threshold = 10
        self.syn_flood_threshold = 50
        self.icmp_flood_threshold = 100
        self.brute_force_threshold = 5
        self.window_port_scan = 10
        self.window_syn_flood = 5
        self.window_icmp_flood = 5
        self.window_icmp_flood = 5
        self.window_brute_force = 30

    def _init_state(self):
        # Tracking state
        self.syn_packets = defaultdict(list)
        self.icmp_packets = defaultdict(list)
        self.port_scans = defaultdict(set)
        self.brute_force = defaultdict(list)
        self.ml_last_eval = {}
        self.ml_last_cleanup = datetime.now()

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
        self._cleanup_old_records(self.brute_force, self.window_brute_force)

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
        self._cleanup_old_records(self.port_scans, self.window_port_scan)

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
        self._cleanup_old_records(self.syn_packets, self.window_syn_flood)

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
        self._cleanup_old_records(self.icmp_packets, self.window_icmp_flood)

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

    def detect_ml_anomaly(self, packet: Packet) -> Optional[Alert]:
        if hasattr(self.tracker, "_get_canonical_key"):
            key = self.tracker._get_canonical_key(packet)
        elif hasattr(self.tracker, "_get_connection_key"):
            key = self.tracker._get_connection_key(packet)
        else:
            return None

        conn = self.tracker.active_connections.get(key)
        if not conn:
            return None

        now = datetime.now()

        if (now - self.ml_last_cleanup).total_seconds() > 60:
            self.ml_last_eval = {k: v for k, v in self.ml_last_eval.items() if k in self.tracker.active_connections}
            self.ml_last_cleanup = now

        last_eval = self.ml_last_eval.get(key)
        total_packets = (
            conn.packets_in + conn.conn_packets_out
            if hasattr(conn, "conn_packets_out")
            else conn.packets_in + conn.packets_out
        )

        if total_packets < 10:
            return None

        if last_eval and (now - last_eval).total_seconds() < 1.0:
            return None

        self.ml_last_eval[key] = now

        is_anomalous, score = self.ml_detector.evaluate_connection(conn)
        if is_anomalous:
            return Alert(
                alert_type="ml_anomaly",
                severity="high",
                src_ip=conn.src_ip,
                dst_ip=conn.dst_ip,
                description=f"ML Anomaly (score: {score:.3f}) detected for flow {conn.src_ip}:{conn.src_port} -> {conn.dst_ip}:{conn.dst_port}",
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

        alert6 = self.detect_ml_anomaly(packet)
        if alert6:
            alerts.append(alert6)

        for alert in alerts:
            self.event_bus.publish("alerts", alert)

        return alerts
