import cProfile
import pstats
import io
import time
import random
from datetime import datetime
from scapy.all import IP, TCP

from firewall.firewall import PersonalFirewall
from firewall.models import Packet

def profile_pipeline():
    fw = PersonalFirewall()
    # Don't start the background threads (db writer, cleanup) to isolate the packet processor
    
    # Generate mock packets
    print("Generating mock packets for profiling...")
    packets = []
    for _ in range(5000):
        src_ip = f"10.0.0.{random.randint(1, 10)}"
        scapy_pkt = IP(src=src_ip, dst="192.168.1.100") / TCP(sport=random.randint(1024, 65535), dport=80, flags="S")
        pkt = Packet(
            timestamp=datetime.now(),
            src_ip=src_ip,
            src_port=scapy_pkt[TCP].sport,
            dst_ip="192.168.1.100",
            dst_port=80,
            protocol="TCP",
            flags="S",
            size=len(scapy_pkt),
            raw=bytes(scapy_pkt)
        )
        packets.append(pkt)

    print("Profiling `_process_packet` for 5,000 packets...")
    
    pr = cProfile.Profile()
    pr.enable()
    
    for pkt in packets:
        fw._process_packet(pkt)
        
    pr.disable()
    
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(30) # Print top 30 functions
    
    print(s.getvalue())

if __name__ == "__main__":
    profile_pipeline()
