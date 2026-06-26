import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from scapy.all import IP, TCP, UDP, ICMP, sniff
from scapy.packet import Packet as ScapyPacket

from analytics.flow_engine import FlowEngine
from firewall.models import Packet, Connection

logger = logging.getLogger(__name__)

class OfflineFlowEngine(FlowEngine):
    def __init__(self, timeout: int = 300, syn_timeout: int = 30):
        super().__init__(timeout, syn_timeout)
        self.completed_flows: List[Connection] = []

    def clean_expired(self, current_time: datetime):
        expired_keys = []
        for key, conn in self.active_connections.items():
            if conn.state == "SYN_SENT":
                if current_time - conn.last_activity > timedelta(seconds=self.syn_timeout):
                    expired_keys.append(key)
            elif conn.state == "CLOSED":
                if current_time - conn.last_activity > timedelta(seconds=10):
                    expired_keys.append(key)
            else:
                if current_time - conn.last_activity > timedelta(seconds=self.timeout):
                    expired_keys.append(key)

        for key in expired_keys:
            conn = self.active_connections.pop(key)
            conn.flow_end = current_time
            conn.duration = (conn.flow_end - conn.flow_start).total_seconds()
            self.completed_flows.append(conn)

    def process_offline_packet(self, packet: Packet):
        key = self._get_canonical_key(packet)
        now = packet.timestamp

        if key not in self.active_connections:
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

        if packet.src_ip == conn.src_ip:
            conn.packets_out += 1
            conn.bytes_out += packet.size
        else:
            conn.packets_in += 1
            conn.bytes_in += packet.size

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

def parse_scapy_packet(raw_packet: ScapyPacket) -> Packet | None:
    if IP not in raw_packet:
        return None

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

    return Packet(
        timestamp=datetime.fromtimestamp(float(raw_packet.time)),
        src_ip=ip_layer.src,
        src_port=src_port,
        dst_ip=ip_layer.dst,
        dst_port=dst_port,
        protocol=protocol,
        flags=flags,
        size=len(raw_packet),
    )

def process_pcap(pcap_path: str, output_csv: str):
    logger.info(f"Processing PCAP: {pcap_path}")
    engine = OfflineFlowEngine()
    
    packet_count = 0
    last_cleanup = None
    
    def handle_packet(raw_pkt):
        nonlocal packet_count, last_cleanup
        pkt = parse_scapy_packet(raw_pkt)
        if not pkt:
            return
            
        packet_count += 1
        if packet_count % 10000 == 0:
            logger.info(f"Processed {packet_count} packets...")
            
        engine.process_offline_packet(pkt)
        
        if last_cleanup is None or (pkt.timestamp - last_cleanup).total_seconds() > 10:
            engine.clean_expired(pkt.timestamp)
            last_cleanup = pkt.timestamp

    sniff(offline=pcap_path, prn=handle_packet, store=False)
    
    # Flush remaining
    logger.info("Flushing remaining active connections...")
    fake_now = datetime.max
    engine.clean_expired(fake_now)
    
    # Export to CSV
    export_dataset(engine.completed_flows, engine.active_connections.values(), output_csv)

def export_dataset(completed_flows: List[Connection], active_flows: List[Connection], output_path: str):
    all_flows = completed_flows + list(active_flows)
    logger.info(f"Exporting {len(all_flows)} flows to {output_path}")
    
    fieldnames = [
        "src_ip", "dst_ip", "src_port", "dst_port", "protocol",
        "duration", "packets_in", "packets_out", "bytes_in", "bytes_out",
        "avg_packet_size", "packet_rate", "byte_rate", "label"
    ]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for flow in all_flows:
            # Simple labeling heuristic: Mark anomalous if it matches known malicious patterns
            # Or if it's a massive SYN flood
            is_anomaly = False
            if flow.protocol == "TCP" and flow.state == "SYN_SENT" and flow.packets_out > 20 and flow.packets_in == 0:
                is_anomaly = True
            # For real datasets, we might use IP blacklists or Snort signatures to label here.
            
            writer.writerow({
                "src_ip": flow.src_ip,
                "dst_ip": flow.dst_ip,
                "src_port": flow.src_port,
                "dst_port": flow.dst_port,
                "protocol": flow.protocol,
                "duration": round(flow.duration, 4),
                "packets_in": flow.packets_in,
                "packets_out": flow.packets_out,
                "bytes_in": flow.bytes_in,
                "bytes_out": flow.bytes_out,
                "avg_packet_size": round(flow.avg_packet_size, 2),
                "packet_rate": round(flow.packet_rate, 2),
                "byte_rate": round(flow.byte_rate, 2),
                "label": 1 if is_anomaly else 0,
            })
    logger.info("Export complete.")

if __name__ == "__main__":
    import os
    from datetime import timedelta
    logging.basicConfig(level=logging.INFO)
    pcap_files = [
        "data/Sample.pcapng",
        "data/Sample2.pcapng", 
        "data/Sample3.pcapng"
    ]
    
    for idx, pcap in enumerate(pcap_files):
        if os.path.exists(pcap):
            process_pcap(pcap, f"ml/data/dataset_pcap_{idx}.csv")
        else:
            logger.warning(f"PCAP file {pcap} not found.")
