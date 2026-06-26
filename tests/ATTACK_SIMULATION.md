# Attack Simulation Guide

This document outlines how to test the AI-Powered Stateful Personal Firewall against common attack patterns. Because the target OS is Windows, some commands use Python scripts or Windows equivalents to simulate attacks.

## 1. Port Scan Detection

The IDS detects port scans when multiple SYN packets are sent to different ports from a single source within a 10-second window.

**Simulation with Nmap (if installed):**
```bash
nmap -sS -p 1-100 127.0.0.1
```

**Expected Result:**
The firewall will log an alert with severity `high` indicating a `port_scan` from `127.0.0.1`.

## 2. SYN Flood Detection

The IDS detects SYN floods when numerous SYN packets hit the same destination port in rapid succession (e.g., >50 packets in 5 seconds).

**Simulation with Python:**
```python
import socket
target_ip = "127.0.0.1"
target_port = 80
# Send multiple SYN-like packets if using scapy, or just attempt rapid connections
for _ in range(100):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)
    try:
        s.connect((target_ip, target_port))
    except:
        pass
```
*Note: True SYN flooding requires Scapy to forge raw SYN packets.*

**Expected Result:**
The firewall will log an alert with severity `critical` indicating a `syn_flood`.

## 3. ICMP Flood Detection

The IDS triggers when a rapid influx of ICMP packets arrives.

**Simulation:**
Open PowerShell and run an aggressive ping loop:
```powershell
while ($true) { ping 127.0.0.1 -n 1 -w 1 }
```
(Or use Scapy to blast ICMP faster).

**Expected Result:**
The firewall logs an alert with severity `medium` for `icmp_flood`.

## 4. Brute Force Detection

The IDS tracks repeated SYN attempts that do not complete the TCP handshake (i.e., failed connections) to detect brute-forcing.

**Simulation:**
Attempt to connect to a closed port 10+ times within 30 seconds.

**Expected Result:**
The firewall logs an alert with severity `high` for `brute_force`.

## 5. Suspicious Port Detection

The IDS flags connections to known suspicious ports (e.g., 12345 for SSH alternative, 8888, 6667).

**Simulation:**
```bash
curl http://127.0.0.1:12345
```

**Expected Result:**
The firewall logs an alert with severity `low` for `suspicious_port`.
