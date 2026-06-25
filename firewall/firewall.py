import threading
import time
from datetime import datetime
from typing import Dict, Any

from firewall.packet_capture import PacketCapture
from firewall.connection_tracker import ConnectionTracker
from firewall.rule_engine import RuleEngine
from firewall.ids_engine import IDSEngine
from firewall.database import FirewallDatabase
from firewall.models import FirewallEvent

class PersonalFirewall:
    def __init__(self, config_path: str = "firewall/config/rules.json", db_path: str = "sqlite:///firewall.db"):
        self.packet_capture = PacketCapture()
        self.rule_engine = RuleEngine()
        self.connection_tracker = ConnectionTracker()
        self.ids_engine = IDSEngine(self.connection_tracker)
        self.database = FirewallDatabase(db_path=db_path)
        self.running = False
        
        # Stats
        self.packets_processed = 0
        self.bytes_processed = 0
        self.start_time = None
        
        try:
            self.rule_engine.load_rules_from_json(config_path)
            print(f"[*] Loaded {len(self.rule_engine.rules)} rules from {config_path}")
        except FileNotFoundError:
            print(f"[!] Warning: Config file {config_path} not found. Running with no rules.")

    def start(self):
        self.running = True
        self.start_time = datetime.now()
        
        # Start cleanup thread for tracker
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        print("[*] Starting packet capture...")
        self.packet_capture.start_capture(callback=self._process_packet)
        print("[*] Firewall started and running in background.")

    def stop(self):
        self.running = False
        self.packet_capture.stop_capture()
        print("[*] Firewall stopped.")

    def _cleanup_loop(self):
        while self.running:
            self.connection_tracker.clean_expired()
            time.sleep(10)

    def _process_packet(self, packet):
        self.packets_processed += 1
        self.bytes_processed += packet.size
        
        # Update connection state
        connection = self.connection_tracker.update_state(packet)
        
        # Evaluate against rules
        action, rule = self.rule_engine.evaluate_packet(packet)
        rule_id = rule.rule_id if rule else "default"
        
        if action == "drop":
            # For a real firewall we'd actually drop it via iptables/NFQUEUE
            # Since this is a passive monitor right now, we just log it as dropped.
            pass
        elif action == "block":
            # Send RST (not implemented in MVP)
            pass
            
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
                reason=rule.description if rule else "No matching rule"
            )
            # Depending on load, might want to batch writes
            # self.database.log_event(event)

        # Log packet (optional, can be very heavy)
        # self.database.log_packet(packet)

        # Run IDS
        alerts = self.ids_engine.analyze_packet(packet)
        for alert in alerts:
            self.database.log_alert(alert)
            print(f"[!] ALERT: {alert.description}")

    def get_stats(self) -> Dict[str, Any]:
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        pps = self.packets_processed / uptime if uptime > 0 else 0
        mbps = (self.bytes_processed * 8 / 1_000_000) / uptime if uptime > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "packets_processed": self.packets_processed,
            "bytes_processed": self.bytes_processed,
            "pps": pps,
            "mbps": mbps,
            "active_connections": len(self.connection_tracker.active_connections)
        }
