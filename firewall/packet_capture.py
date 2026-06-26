import threading
from datetime import datetime
from typing import Callable, Optional

from scapy.all import ICMP, IP, TCP, UDP, sniff

from firewall.logger import thread_safe_run
from firewall.models import Packet


class PacketCapture:
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _packet_handler(self, raw_packet, callback: Callable):
        if IP not in raw_packet:
            return

        ip_layer = raw_packet[IP]
        protocol = "OTHER"
        src_port = 0
        dst_port = 0
        flags = ""

        if TCP in raw_packet:
            protocol = "TCP"
            src_port = raw_packet[TCP].sport
            dst_port = raw_packet[TCP].dport
            flags = raw_packet[TCP].flags.flagrepr()
        elif UDP in raw_packet:
            protocol = "UDP"
            src_port = raw_packet[UDP].sport
            dst_port = raw_packet[UDP].dport
        elif ICMP in raw_packet:
            protocol = "ICMP"

        packet = Packet(
            timestamp=datetime.now(),
            src_ip=ip_layer.src,
            src_port=src_port,
            dst_ip=ip_layer.dst,
            dst_port=dst_port,
            protocol=protocol,
            flags=flags,
            size=len(raw_packet),
            raw=bytes(raw_packet),
        )
        callback(packet)

    def _start_sniffing(self, callback: Callable):
        try:
            sniff(
                prn=lambda p: self._packet_handler(p, callback),
                store=False,
                stop_filter=lambda p: not self.running,
            )
        except Exception as e:
            if "winpcap is not installed" in str(e).lower():
                print(
                    "[!] Windows PCAP not found. Packet capture disabled. Use simulation script."
                )
            else:
                raise

    def start_capture(self, callback: Callable, on_crash=None):
        self.running = True

        @thread_safe_run("PacketCapture", on_crash=on_crash)
        def run_sniff():
            self._start_sniffing(callback)

        self.thread = threading.Thread(target=run_sniff, daemon=False)
        self.thread.start()

    def stop_capture(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
