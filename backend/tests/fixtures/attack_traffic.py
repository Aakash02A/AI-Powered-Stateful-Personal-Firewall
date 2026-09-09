from datetime import datetime

from firewall.models import Connection


def generate_normal_traffic(count=100):
    conns = []
    for _ in range(count):
        conn = Connection(
            src_ip="10.0.250.245",
            src_port=1732,
            dst_ip="193.84.4.4",
            dst_port=53,
            protocol="TCP",
            state="ESTABLISHED",
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            flow_start=datetime.now(),
            packets_in=4,
            packets_out=6,
            bytes_in=246,
            bytes_out=387,
        )
        conn.duration = 18.0857
        conn.avg_packet_size = 63.3
        conn.packet_rate = 92.39
        conn.byte_rate = 5848.28
        conns.append(conn)
    return conns


def generate_syn_flood(count=100):
    conns = []
    for _ in range(count):
        conn = Connection(
            src_ip="192.168.1.100",
            src_port=50000,
            dst_ip="10.0.0.1",
            dst_port=80,
            protocol="TCP",
            state="SYN_SENT",
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            flow_start=datetime.now(),
            packets_in=0,
            packets_out=5000,
            bytes_in=0,
            bytes_out=300000,
        )
        conn.duration = 1.0
        conn.avg_packet_size = 60.0
        conn.packet_rate = 5000.0
        conn.byte_rate = 300000.0
        conns.append(conn)
    return conns


def generate_port_scan(count=50):
    conns = []
    for _ in range(count):
        conn = Connection(
            src_ip="192.168.1.100",
            src_port=50000,
            dst_ip="10.0.0.1",
            dst_port=80,
            protocol="TCP",
            state="SYN_SENT",
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            flow_start=datetime.now(),
            packets_in=0,
            packets_out=1,
            bytes_in=0,
            bytes_out=60,
        )
        conn.duration = 0.001
        conn.avg_packet_size = 60.0
        conn.packet_rate = 1000.0
        conn.byte_rate = 60000.0
        conns.append(conn)
    return conns


def generate_icmp_flood(count=100):
    conns = []
    for _ in range(count):
        conn = Connection(
            src_ip="192.168.1.100",
            src_port=50000,
            dst_ip="10.0.0.1",
            dst_port=0,
            protocol="ICMP",
            state="NEW",
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            flow_start=datetime.now(),
            packets_in=0,
            packets_out=10000,
            bytes_in=0,
            bytes_out=640000,
        )
        conn.duration = 1.0
        conn.avg_packet_size = 64.0
        conn.packet_rate = 10000.0
        conn.byte_rate = 640000.0
        conns.append(conn)
    return conns
