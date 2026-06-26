import pytest
from scapy.all import IP, TCP, UDP, ICMP
from firewall.packet_capture import PacketCapture

def test_packet_handler():
    capture = PacketCapture()
    captured_packets = []
    
    def callback(packet):
        captured_packets.append(packet)
        
    # Test TCP
    tcp_pkt = IP(src="1.2.3.4", dst="5.6.7.8") / TCP(sport=1000, dport=80, flags="S")
    capture._packet_handler(tcp_pkt, callback)
    
    assert len(captured_packets) == 1
    assert captured_packets[0].protocol == "TCP"
    assert captured_packets[0].src_ip == "1.2.3.4"
    assert "S" in captured_packets[0].flags
    
    # Test UDP
    udp_pkt = IP(src="1.2.3.4", dst="5.6.7.8") / UDP(sport=1000, dport=53)
    capture._packet_handler(udp_pkt, callback)
    
    assert len(captured_packets) == 2
    assert captured_packets[1].protocol == "UDP"
    
    # Test ICMP
    icmp_pkt = IP(src="1.2.3.4", dst="5.6.7.8") / ICMP(type=8)
    capture._packet_handler(icmp_pkt, callback)
    
    assert len(captured_packets) == 3
    assert captured_packets[2].protocol == "ICMP"
