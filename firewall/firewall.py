import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict

from scapy.all import ICMP, IP, TCP, send

from analytics.flow_engine import FlowEngine
from analytics.threat_scoring import ThreatScoringEngine
from firewall.db_writer import DBWriter
from firewall.event_bus import EventBus
from firewall.ids_engine import IDSEngine
from firewall.logger import ThreadHealthMonitor, setup_logger
from firewall.models import FirewallEvent
from firewall.packet_capture import PacketCapture
from firewall.queue_manager import QueueManager
from firewall.rule_engine import RuleEngine


class PersonalFirewall:
    def __init__(
        self,
        config_path: str = "firewall/config/rules.json",
        db_path: str = "sqlite:///data/firewall.db",
        packet_logger=None,
        event_logger=None,
    ):
        self.packet_capture = PacketCapture()
        self.rule_engine = RuleEngine()
        self.flow_engine = FlowEngine()
        self.scoring_engine = ThreatScoringEngine()
        self.ids_engine = IDSEngine(
            self.flow_engine, self.rule_engine, self.scoring_engine
        )
        self.queue_manager = QueueManager()
        self.event_bus = EventBus()
        self.db_writer = DBWriter(db_path=db_path)
        self.packet_logger = packet_logger or setup_logger(
            "packet_logger", "data/logs/packets.log"
        )
        self.event_logger = event_logger or setup_logger(
            "event_logger", "data/logs/events.log"
        )
        self.health_monitor = ThreadHealthMonitor()
        self.running = False

        # Stats
        self.packets_processed = 0
        self.bytes_processed = 0
        self.start_time = None

        try:
            self.rule_engine.load_rules_from_json(config_path)
            logging.getLogger("system").info(
                f"Loaded {len(self.rule_engine.rules)} rules from {config_path}"
            )
        except FileNotFoundError:
            logging.getLogger("system").warning(
                f"Config file {config_path} not found. Running with no rules."
            )

    def _restart_capture(self):
        logging.getLogger("system").critical("Restarting capture thread...")
        time.sleep(1)
        self.packet_capture.start_capture(
            callback=self._process_packet, on_crash=self._restart_capture
        )
        if self.packet_capture.thread:
            self.health_monitor.register("PacketCapture", self.packet_capture.thread)

    def _restart_db_writer(self):
        logging.getLogger("system").critical("Restarting db writer thread...")
        time.sleep(1)
        self.db_writer.start(on_crash=self._restart_db_writer)
        if self.db_writer.thread:
            self.health_monitor.register("DBWriter", self.db_writer.thread)

    def start(self):
        self.running = True
        self.start_time = datetime.now()

        # Start DB Writer
        self.db_writer.start(on_crash=self._restart_db_writer)
        if self.db_writer.thread:
            self.health_monitor.register("DBWriter", self.db_writer.thread)

        # Start cleanup thread for flow engine
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        self.health_monitor.register("CleanupLoop", self.cleanup_thread)

        logging.getLogger("system").info("Starting packet capture...")
        self.packet_capture.start_capture(
            callback=self._process_packet, on_crash=self._restart_capture
        )
        if self.packet_capture.thread:
            self.health_monitor.register("PacketCapture", self.packet_capture.thread)
        logging.getLogger("system").info("Firewall started and running in background.")

    def stop(self):
        self.running = False
        logging.getLogger("system").info("Stopping Firewall Core...")
        self.packet_capture.stop_capture()
        self.db_writer.stop()
        if hasattr(self, "cleanup_thread") and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2.0)
        logging.getLogger("system").info("Firewall stopped.")

    def _cleanup_loop(self):
        while self.running:
            try:
                self.flow_engine.clean_expired()
                self.rule_engine.cleanup_expired_rules()
                self.scoring_engine.decay_scores()
            except Exception as e:
                logging.getLogger("system").error(f"Cleanup loop error: {e}")
            time.sleep(10)

    def _process_packet(self, packet):
        self.packets_processed += 1
        self.bytes_processed += packet.size

        # Update connection state
        self.flow_engine.process_packet(packet)

        # Evaluate against rules
        action, rule = self.rule_engine.evaluate_packet(packet)
        rule_id = rule.rule_id if rule else "default"

        if action == "drop":
            # For a real firewall we'd actually drop it via iptables/NFQUEUE
            # Since this is a passive monitor right now, we just log it as dropped.
            pass
        elif action == "block":
            # Actively block by sending RST (TCP) or ICMP Unreachable (UDP)
            try:
                if packet.protocol == "TCP":
                    # Forge RST packet
                    rst = IP(src=packet.dst_ip, dst=packet.src_ip) / TCP(
                        sport=packet.dst_port, dport=packet.src_port, flags="R"
                    )
                    send(rst, verbose=False)
                elif packet.protocol == "UDP":
                    # Forge ICMP Port Unreachable
                    unreach = IP(src=packet.dst_ip, dst=packet.src_ip) / ICMP(
                        type=3, code=3
                    )
                    send(unreach, verbose=False)
            except Exception as e:
                # If running without privileges, sending might fail. Log it internally.
                self.event_logger.error(f"Failed to send block response: {e}")

        # Run IDS
        alerts = self.ids_engine.analyze_packet(packet)

        # Enqueue IDS alerts
        for alert in alerts:
            self.queue_manager.push(alert)
            logging.getLogger("system").warning(f"ALERT: {alert.description}")

        # Log firewall event if it was matched or blocked/logged
        if action != "allow" or rule_id != "default_allow_established":
            event = FirewallEvent(
                timestamp=packet.timestamp,
                rule_id=rule_id,
                action=action,
                src_ip=packet.src_ip,
                src_port=packet.src_port,
                dst_ip=packet.dst_ip,
                dst_port=packet.dst_port,
                protocol=packet.protocol,
                reason=rule.description if rule else "No matching rule",
            )
            self.queue_manager.push(event)
            if action == "block":
                self.event_bus.publish("events", event)

            self.event_logger.info(
                "Firewall Event",
                extra={
                    "extra_data": {
                        "rule_id": event.rule_id,
                        "action": event.action,
                        "src_ip": event.src_ip,
                        "src_port": event.src_port,
                        "dst_ip": event.dst_ip,
                        "dst_port": event.dst_port,
                        "protocol": event.protocol,
                        "reason": event.reason,
                    }
                },
            )

        # Limited Packet Retention (Only save if alert triggered or blocked)
        if len(alerts) > 0 or action == "block":
            self.queue_manager.push(packet)

        self.packet_logger.info(
            "Packet captured",
            extra={
                "extra_data": {
                    "src_ip": packet.src_ip,
                    "src_port": packet.src_port,
                    "dst_ip": packet.dst_ip,
                    "dst_port": packet.dst_port,
                    "protocol": packet.protocol,
                    "size": packet.size,
                    "flags": packet.flags,
                }
            },
        )

    def get_stats(self) -> Dict[str, Any]:
        uptime = (
            (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        )
        pps = self.packets_processed / uptime if uptime > 0 else 0
        mbps = (self.bytes_processed * 8 / 1_000_000) / uptime if uptime > 0 else 0

        return {
            "uptime_seconds": uptime,
            "packets_processed": self.packets_processed,
            "bytes_processed": self.bytes_processed,
            "pps": pps,
            "mbps": mbps,
            "active_connections": len(self.flow_engine.active_connections),
        }
