import threading
from datetime import datetime
from typing import Callable, Optional

from scapy.all import ICMP, IP, TCP, UDP, sniff

from firewall.logger import thread_safe_run
from firewall.models import Packet


import os
import sys

class PacketCapture:
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _packet_handler(self, raw_packet, callback: Callable):
        if IP not in raw_packet:
            return True

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
        # Callback returns True to allow, False to block
        result = callback(packet)
        return result if result is not None else True

    def _start_sniffing(self, callback: Callable):
        if sys.platform == "win32":
            try:
                import pydivert
                print("[+] Starting Windows Filtering Platform (WFP) capture via pydivert...")
                with pydivert.WinDivert("ip or ipv6") as w:
                    while self.running:
                        try:
                            # Use timeout to allow checking self.running periodically
                            packet = w.recv(timeout=1000)
                            if packet is None:
                                continue
                            
                            # Convert pydivert packet to our format (roughly)
                            # Actually, we can use scapy to parse the raw bytes
                            from scapy.all import IP as ScapyIP
                            raw_bytes = packet.raw
                            scapy_pkt = ScapyIP(raw_bytes)
                            
                            allow = self._packet_handler(scapy_pkt, callback)
                            if allow:
                                w.send(packet)
                        except TimeoutError:
                            continue
            except ImportError:
                print("[!] pydivert not installed. Falling back to scapy.")
                self._fallback_scapy(callback)
            except PermissionError:
                print("[!] Permission Denied. You must run as Administrator for pydivert (WFP) to work.")
                self._fallback_scapy(callback)
        else:
            self._fallback_scapy(callback)

    def _fallback_scapy(self, callback: Callable):
        try:
            sniff(
                prn=lambda p: self._packet_handler(p, callback),
                store=False,
                stop_filter=lambda p: not self.running,
            )
        except Exception as e:
            if "winpcap is not installed" in str(e).lower() or "npcap" in str(e).lower():
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
