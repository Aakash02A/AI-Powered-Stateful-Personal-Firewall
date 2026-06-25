# AI-Powered Stateful Personal Firewall

A Next-Generation Personal Firewall (NGFW) built in Python that combines stateful packet inspection, rule-based filtering, signature-based IDS, and logging. 

## Features (Tier 1)

*   **Stateful Packet Inspection**: Tracks TCP connections through the 3-way handshake and connection teardown.
*   **Rule Engine**: Supports CIDR blocks, port ranges, wildcards, and directional matching (inbound/outbound) to evaluate traffic dynamically.
*   **Intrusion Detection System (IDS)**: Detects network threats heuristically:
    *   Port Scans
    *   SYN Floods
    *   ICMP Floods
    *   Brute-force connection attempts
    *   Suspicious port anomalies
*   **Structured Logging**: SQLite database logging for rules, packets, connections, and alerts, complemented by JSON file logging with daily rotation.
*   **CLI Dashboard**: Easily start, stop, query connections, and check alerts.

## Installation

1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

*(Note: Raw packet capture via Scapy on Windows may require Npcap to be installed).*

## Usage

### Start the Firewall Daemon
Must be run as an Administrator to sniff packets:
```bash
python -m firewall.cli start
```

### Check Rules
```bash
python -m firewall.cli rules
```

### View Recent Alerts
```bash
python -m firewall.cli alerts
```

### Query Active Connections
```bash
python -m firewall.cli queries --limit 10
```

## Testing

Run unit tests and generate the coverage report using Pytest:
```bash
pytest --cov=firewall tests/
```

For live attack simulations, see [ATTACK_SIMULATION.md](tests/ATTACK_SIMULATION.md).
