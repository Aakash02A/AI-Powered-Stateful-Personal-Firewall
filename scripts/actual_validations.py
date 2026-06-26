from datetime import datetime

from firewall.firewall import PersonalFirewall
from firewall.models import Packet


def simulate_nmap():
    print("[*] Simulating Nmap (-sS) against Firewall...")
    fw = PersonalFirewall(db_path="sqlite:///actual.db")
    # Send rapid SYNs to ports 1 to 100
    for port in range(1, 101):
        p = Packet(
            timestamp=datetime.now(),
            src_ip="172.16.0.10",
            src_port=44444,
            dst_ip="10.0.0.1",
            dst_port=port,
            protocol="TCP",
            flags="S",
            size=60,
        )
        fw._process_packet(p)

    alerts = fw.database.query_alerts(alert_type="port_scan")
    if alerts:
        print(f"[+] SUCCESS: Detected Nmap scan! Alert: {alerts[0]['description']}")
    else:
        print("[-] FAILED: Did not detect Nmap scan.")


def simulate_hping3():
    print("[*] Simulating Hping3 (--flood) against Firewall...")
    fw = PersonalFirewall(db_path="sqlite:///actual.db")
    # Send 100 SYNs to port 80 very quickly
    for i in range(100):
        p = Packet(
            timestamp=datetime.now(),
            src_ip="172.16.0.20",
            src_port=30000 + i,
            dst_ip="10.0.0.1",
            dst_port=80,
            protocol="TCP",
            flags="S",
            size=60,
        )
        fw._process_packet(p)

    alerts = fw.database.query_alerts(alert_type="syn_flood")
    if alerts:
        print(
            f"[+] SUCCESS: Detected Hping3 SYN Flood! Alert: {alerts[0]['description']}"
        )
    else:
        print("[-] FAILED: Did not detect Hping3 flood.")


def simulate_ssh_bruteforce():
    print("[*] Performing actual SSH Brute-force validation...")
    try:
        # We can trigger actual SSH client attempts to 127.0.0.1 to trigger our own sniffer if we had a live sniffer.
        # But since we're using a simulated packet flow for testing here (without admin privileges to sniff loopback on Windows easily)
        # We will inject the packets that an SSH brute force generates.
        fw = PersonalFirewall(db_path="sqlite:///actual.db")
        for i in range(10):
            p = Packet(
                timestamp=datetime.now(),
                src_ip="172.16.0.30",
                src_port=55555 + i,
                dst_ip="10.0.0.1",
                dst_port=22,
                protocol="TCP",
                flags="S",
                size=60,
            )
            fw._process_packet(p)

        alerts = fw.database.query_alerts(alert_type="brute_force")
        if alerts:
            print(
                f"[+] SUCCESS: Detected SSH Brute Force! Alert: {alerts[0]['description']}"
            )
        else:
            print("[-] FAILED: Did not detect SSH Brute force.")
    except Exception as e:
        print(f"Error running SSH: {e}")


if __name__ == "__main__":
    import os

    if os.path.exists("actual.db"):
        os.remove("actual.db")
    simulate_nmap()
    simulate_hping3()
    simulate_ssh_bruteforce()
