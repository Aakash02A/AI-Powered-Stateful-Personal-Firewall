# Architecture Document for Tier 1 Personal Firewall

## System Overview
The AI-Powered Stateful Personal Firewall is a Python-based security tool designed to monitor, filter, and inspect network traffic in real-time. Tier 1 implements the foundational components required for a stateful inspection engine, including a rule-based engine, an Intrusion Detection System (IDS), connection tracking, and comprehensive logging.

## Core Components
### 1. PacketCapture (`packet_capture.py`)
Uses `scapy` to sniff packets asynchronously. Extracts L3 and L4 headers (IP, TCP, UDP, ICMP), standardizes them into a robust `Packet` dataclass, and passes them to a registered callback.

### 2. ConnectionTracker (`connection_tracker.py`)
Maintains a state table of active connections based on the 5-tuple signature. Implements a partial TCP State Machine handling transitions (`SYN_SENT`, `SYN_RECV`, `ESTABLISHED`, `FIN_WAIT`, `CLOSED`) and tracks ingress/egress bytes. Expiration is managed in a separate thread.

### 3. RuleEngine (`rule_engine.py`)
A prioritized evaluation engine that checks packet signatures (source/destination IP, port, protocol, and directional local matching) against JSON-configured rules. Uses exact match, port ranges, CIDR subnets, and `any` wildcards.

### 4. IDSEngine (`ids_engine.py`)
A signature and heuristic-based anomaly detector monitoring for:
- **Port Scans:** High volume of unique ports targeted within 10 seconds.
- **SYN Floods:** High volume of SYNs sent to the same destination without completing handshakes.
- **ICMP Floods:** Massive influx of ping requests.
- **Brute Force Attacks:** Repeated failed connections/SYNs from a single source.
- **Suspicious Ports:** Connections to known risky alternative ports (e.g., 12345).

### 5. Logging and Database (`database.py` & `logger.py`)
All events, alerts, and captured packets are durably logged to a SQLite database via SQLAlchemy. Additionally, a structured JSON file log natively rotates daily for seamless integration into SIEM tools.

## Data Flow Pipeline
1. `scapy.sniff` captures a packet on the network interface.
2. `PacketCapture` normalizes the raw data into a `Packet` object.
3. `PersonalFirewall` (Orchestrator) receives the `Packet`.
4. `ConnectionTracker` updates TCP state and byte counts.
5. `RuleEngine` evaluates the packet. If action is `block`, Scapy actively forges and sends a TCP RST or ICMP Port Unreachable packet.
6. `IDSEngine` assesses the packet context for signatures and generates `Alert` records if thresholds are breached.
7. `Database` & `JSON Logger` persists the evaluation results and logs.

## Known Limitations
- Sending raw packets (`scapy.send()`) for `block` actions requires elevated administrative privileges and may conflict with the host OS's native TCP/IP stack (especially on Windows).
- Passive listening (without NFQUEUE or iptables) means the firewall cannot drop packets before they reach the OS layer. It can only send resets after the fact.
- `scapy` packet capture is inherently CPU-bound and struggles with >10,000 packets per second in Python.
