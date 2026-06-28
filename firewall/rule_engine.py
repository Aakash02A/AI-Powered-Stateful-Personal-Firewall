import ipaddress
import json
import socket
from typing import List, Optional, Tuple

from firewall.models import FirewallRule, Packet


def get_local_ips():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return [host_ip, "127.0.0.1"]
    except Exception:
        return ["127.0.0.1"]


class RuleEngine:
    def __init__(self):
        self.rules: List[FirewallRule] = []
        self.config_path: Optional[str] = None

    def load_rules_from_json(self, path: str):
        self.config_path = path
        with open(path, "r") as f:
            data = json.load(f)
            for rule_data in data.get("rules", []):
                rule = FirewallRule(**rule_data)
                self.rules.append(rule)
        # Sort by priority (lower is higher priority)
        self.rules.sort(key=lambda x: x.priority)

    def save_rules(self):
        if not self.config_path:
            return
        data = {"rules": [r.__dict__ for r in self.rules]}
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=4)

    def _ip_matches(self, ip_str: str, rule_ip: str) -> bool:
        if rule_ip.lower() == "any":
            return True
        try:
            target_ip = ipaddress.ip_address(ip_str)
            if "/" in rule_ip:
                network = ipaddress.ip_network(rule_ip, strict=False)
                return target_ip in network
            else:
                return target_ip == ipaddress.ip_address(rule_ip)
        except ValueError:
            return False

    def _port_matches(self, port: int, rule_port: str) -> bool:
        if rule_port.lower() == "any":
            return True
        if "-" in rule_port:
            start, end = map(int, rule_port.split("-"))
            return start <= port <= end
        try:
            return port == int(rule_port)
        except ValueError:
            return False

    def evaluate_packet(self, packet: Packet) -> Tuple[str, Optional[FirewallRule]]:
        for rule in self.rules:
            if not rule.enabled:
                continue

            # Protocol check
            if (
                rule.protocol.lower() != "any"
                and rule.protocol.lower() != packet.protocol.lower()
            ):
                continue

            # Direction check
            is_src_local = packet.src_ip in get_local_ips()
            is_dst_local = packet.dst_ip in get_local_ips()

            if rule.direction.lower() == "inbound" and not is_dst_local:
                # For inbound, dst_ip must be local (or we assume it is inbound if src is not local)
                # To simplify: if it's explicitly inbound, dst is local or src is external
                continue
            elif rule.direction.lower() == "outbound" and not is_src_local:
                # For outbound, src_ip must be local
                continue

            if not self._ip_matches(packet.src_ip, rule.src_ip):
                continue
            if not self._ip_matches(packet.dst_ip, rule.dst_ip):
                continue
            if not self._port_matches(packet.src_port, rule.src_port):
                continue
            if not self._port_matches(packet.dst_port, rule.dst_port):
                continue

            # Matched
            return rule.action.lower(), rule

        return "allow", None  # Default action if no rules match

    def add_rule(self, rule: FirewallRule):
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority)
        self.save_rules()

    def delete_rule(self, rule_id: str):
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        self.save_rules()

    def update_rule(self, rule_id: str, **kwargs):
        for rule in self.rules:
            if rule.rule_id == rule_id:
                for k, v in kwargs.items():
                    if hasattr(rule, k):
                        setattr(rule, k, v)
        self.rules.sort(key=lambda x: x.priority)
        self.save_rules()

    def cleanup_expired_rules(self):
        from datetime import datetime

        now = datetime.now()
        original_count = len(self.rules)

        valid_rules = []
        for rule in self.rules:
            if rule.expires_at:
                try:
                    expires = datetime.fromisoformat(rule.expires_at)
                    if now > expires:
                        continue  # Skip expired rule
                except Exception:
                    pass  # Keep if invalid format
            valid_rules.append(rule)

        if len(valid_rules) < original_count:
            self.rules = valid_rules
            self.save_rules()
