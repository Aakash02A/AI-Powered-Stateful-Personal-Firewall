import os
import sys
import time
import socket
import platform
import requests
import datetime
import threading
import random
from scapy.all import sniff, IP, TCP, UDP

# Configuration
API_BASE_URL = "http://localhost:8000/api" # Change to production URL when hosted
AGENT_ID_FILE = "agent_id.txt"

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os_info": f"{platform.system()} {platform.release()}",
        "ip_address": socket.gethostbyname(socket.gethostname())
    }

def register_agent():
    if os.path.exists(AGENT_ID_FILE):
        with open(AGENT_ID_FILE, "r") as f:
            agent_id = f.read().strip()
            print(f"[*] Found existing Agent ID: {agent_id}")
            return agent_id
    
    print("[*] Registering new agent with GuardianWeb Cloud...")
    try:
        sys_info = get_system_info()
        response = requests.post(f"{API_BASE_URL}/agents/register", json=sys_info)
        response.raise_for_status()
        data = response.json()
        agent_id = data["agent_id"]
        
        with open(AGENT_ID_FILE, "w") as f:
            f.write(agent_id)
            
        print(f"[+] Successfully registered! Agent ID: {agent_id}")
        return agent_id
    except Exception as e:
        print(f"[-] Failed to register agent: {e}")
        sys.exit(1)

def packet_callback(packet, agent_id):
    if IP in packet:
        src = packet[IP].src
        dst = packet[IP].dst
        protocol = "UNKNOWN"
        port = 0
        
        if TCP in packet:
            protocol = "TCP"
            port = packet[TCP].dport
        elif UDP in packet:
            protocol = "UDP"
            port = packet[UDP].dport
            
        # Basic rules / threat intel simulation
        action = "allow"
        threat_detected = False
        threat_type = ""
        severity = "low"
        
        # Simulate detection of malicious ports or IPs
        if port in [23, 445, 3389] and random.random() < 0.05: # Randomly flag sensitive ports
            action = "block"
            threat_detected = True
            threat_type = "Suspicious Port Access"
            severity = "high"
        elif random.random() < 0.01: # Random malware IP simulation
            action = "block"
            threat_detected = True
            threat_type = "Known Malicious IP"
            severity = "critical"
            
        # 1. Send Log
        log_data = {
            "agent_id": agent_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "source_ip": src,
            "dest_ip": dst,
            "protocol": protocol,
            "port": port,
            "action": action
        }
        
        try:
            # We don't send EVERY packet to cloud to avoid flooding, we sample or batch in real life.
            # For demonstration, we send randomly 5% of traffic
            if random.random() < 0.05:
                requests.post(f"{API_BASE_URL}/logs", json=log_data, timeout=2)
        except:
            pass
            
        # 2. Send Threat Alert if detected
        if threat_detected:
            print(f"[!] Threat Detected! Blocked {src} -> {port} ({threat_type})")
            threat_data = {
                "agent_id": agent_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "threat_type": threat_type,
                "description": f"Blocked connection attempt to port {port} from {src}",
                "severity": severity,
                "source_ip": src
            }
            try:
                requests.post(f"{API_BASE_URL}/threats", json=threat_data, timeout=2)
            except:
                pass

def start_capture(agent_id):
    print(f"[*] Starting network capture engine...")
    # sniff blocks, so it runs indefinitely
    sniff(prn=lambda pkt: packet_callback(pkt, agent_id), store=0)

if __name__ == "__main__":
    print("========================================")
    print("    GuardianWeb - Local Security Agent  ")
    print("========================================")
    
    agent_id = register_agent()
    
    # Start packet capture in a separate thread
    capture_thread = threading.Thread(target=start_capture, args=(agent_id,))
    capture_thread.daemon = True
    capture_thread.start()
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[*] Stopping agent...")
        sys.exit(0)
