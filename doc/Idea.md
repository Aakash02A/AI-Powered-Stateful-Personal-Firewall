# AI-Powered Stateful Personal Firewall: Project Specification

## Executive Summary

Build a **Next-Generation Personal Firewall (NGFW)** that combines stateful packet inspection, rule-based intrusion detection, machine learning–based anomaly detection, and real-time monitoring. The system will capture and analyze network traffic in real-time, enforce firewall rules, detect threats, and provide actionable intelligence through an integrated monitoring dashboard.

**Target Users:** Security practitioners, network administrators, and developers requiring advanced network monitoring and threat detection.

**Architecture Philosophy:** Layered security (defense-in-depth) with clean separation between packet processing, threat detection, ML inference, and visualization.

---

## Project Phases

This project is structured in **three tiers**, with Tier 1 as the MVP and Tiers 2–3 as extensions.

### Phase 1: Tier 1 – Core Firewall & Stateful Inspection (Weeks 1–5)
**Goal:** Ship a functional firewall that captures packets, applies rules, detects basic attacks, and logs all activity.

### Phase 2: Tier 2 – ML Anomaly Detection & Analytics Dashboard (Weeks 6–8)
**Goal:** Integrate ML-based threat detection and build a real-time monitoring UI.

### Phase 3: Tier 3 – Advanced Features & Integration (Weeks 9–10, Optional)
**Goal:** Add threat intelligence feeds, alerting channels, and OS-level enforcement.

---

# TIER 1: CORE FIREWALL & STATEFUL INSPECTION

## 1.1 Functional Requirements

### Packet Capture and Parsing
- [ ] Capture incoming and outgoing packets on the local machine using **Scapy** or **PyShark**
- [ ] Parse L3 (IP) and L4 (TCP/UDP) headers to extract:
  - Source/destination IP addresses
  - Source/destination ports
  - Protocol type (TCP, UDP, ICMP)
  - Packet flags (SYN, ACK, FIN, etc. for TCP)
  - Payload size
  - Packet arrival timestamp

### Stateful Connection Tracking
- [ ] Maintain a **Connection State Table** that tracks active sessions:
  - Tuple: (src_ip, src_port, dst_ip, dst_port, protocol)
  - State: SYN_SENT, ESTABLISHED, FIN_WAIT, CLOSED
  - Timestamps: creation, last_activity
  - Packet counters: packets_in, packets_out, bytes_in, bytes_out
- [ ] Implement TCP state machine (3-way handshake, connection teardown)
- [ ] Auto-expire connections after inactivity timeout (e.g., 5 minutes for ESTABLISHED, 30 seconds for SYN_SENT)

### Rule Engine
- [ ] Define firewall rules as Python objects or JSON configs with the following structure:
  ```json
  {
    "rule_id": "rule_001",
    "priority": 100,
    "enabled": true,
    "protocol": "tcp|udp|icmp|any",
    "src_ip": "192.168.1.100|10.0.0.0/8|any",
    "src_port": "80|1024-2048|any",
    "dst_ip": "8.8.8.8|any",
    "dst_port": "443|53|any",
    "direction": "inbound|outbound|both",
    "action": "allow|block|drop|log",
    "description": "Allow HTTPS to Google DNS"
  }
  ```
- [ ] Implement rule matching logic:
  - Rules are evaluated in **priority order** (lower number = higher priority)
  - First matching rule determines action
  - Support wildcards and CIDR notation for IP addresses
  - Support port ranges
- [ ] Actions:
  - **allow**: Permit packet and log
  - **block**: Drop packet and send RST (TCP) or ICMP unreachable (UDP)
  - **drop**: Silently discard (no response)
  - **log**: Log without action (passthrough for monitoring)

### Threat Detection – Signature-Based IDS
Implement detection rules for common attacks:

#### Port Scan Detection
- [ ] Detect **SYN scans**: Multiple packets with SYN flag to different ports from same source IP within 10 seconds
  - Alert when: (unique_dst_ports > 10 in 10-second window from single src_ip)
- [ ] Log source IP, destination ports, and timestamp
- [ ] Action: Optional auto-block (configurable)

#### SYN Flood Detection
- [ ] Detect rapid SYN packets from multiple/single sources to same port
- [ ] Alert when: (SYN packets to same dst_ip:dst_port > 50 in 5-second window)
- [ ] Log source IPs, destination, and flood intensity
- [ ] Action: Optional auto-block with rate limiting

#### ICMP Flooding Detection
- [ ] Detect rapid ICMP Echo Request packets (ping floods)
- [ ] Alert when: (ICMP packets > 100 in 5-second window)
- [ ] Log source and flood rate
- [ ] Action: Block source IP temporarily

#### Brute-Force Detection
- [ ] Detect repeated failed connection attempts (failed SYN/ACK handshakes)
  - Signature: SYN sent but no SYN-ACK received within timeout, repeated from same src_ip to same dst_ip:dst_port
- [ ] Alert when: (failed_attempts > 5 to same target within 30 seconds)
- [ ] Log source, target, and attempt count
- [ ] Action: Optional auto-block

#### Suspicious Traffic Patterns
- [ ] Detect connections to **non-standard ports** (optional):
  - SSH on port 12345, HTTP on port 8888, etc.
- [ ] Log and flag for manual review
- [ ] Support whitelist for known services

### Logging and Database Storage
- [ ] Create a **SQLite database** with the following tables:
  ```sql
  packets (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    src_ip TEXT, src_port INTEGER,
    dst_ip TEXT, dst_port INTEGER,
    protocol TEXT,
    packet_size INTEGER,
    flags TEXT
  );

  connections (
    id INTEGER PRIMARY KEY,
    src_ip TEXT, src_port INTEGER,
    dst_ip TEXT, dst_port INTEGER,
    protocol TEXT,
    state TEXT,
    start_time DATETIME,
    end_time DATETIME,
    packets_in INTEGER,
    packets_out INTEGER,
    bytes_in INTEGER,
    bytes_out INTEGER
  );

  firewall_events (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    rule_id TEXT,
    action TEXT,
    src_ip TEXT, src_port INTEGER,
    dst_ip TEXT, dst_port INTEGER,
    protocol TEXT,
    reason TEXT
  );

  alerts (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    alert_type TEXT,
    severity TEXT (low|medium|high|critical),
    src_ip TEXT,
    dst_ip TEXT,
    description TEXT,
    action_taken TEXT
  );
  ```
- [ ] Log **every packet** that matches a rule
- [ ] Log **every alert** generated by IDS
- [ ] Support structured logging (JSON format for easy parsing)
- [ ] Implement log rotation (e.g., new log file daily)

---

## 1.2 Technical Architecture – Tier 1

### System Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    Packet Stream (Raw)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │  Packet Capture     │
        │  (Scapy/PyShark)    │
        └─────────┬───────────┘
                  │
          ┌───────▼──────────┐
          │   Parse Packet   │
          │  (IP, TCP, UDP)  │
          └───────┬──────────┘
                  │
        ┌─────────▼───────────┐
        │  Update Connection  │
        │   State Table       │
        └─────────┬───────────┘
                  │
         ┌────────▼─────────┐
         │  Rule Matching   │
         │  (Priority order)│
         └────────┬─────────┘
                  │
        ┌─────────▼────────┐
        │  Action Executor │
        │ (allow/block/log)│
        └─────────┬────────┘
                  │
      ┌───────────▼──────────────┐
      │  IDS Detection Engine    │
      │ (Port Scan, SYN Flood..) │
      └───────────┬──────────────┘
                  │
      ┌───────────▼──────────────┐
      │  Logging & Persistence   │
      │  (SQLite DB)             │
      └──────────────────────────┘
```

### Core Components

#### 1. PacketCapture (Module: `firewall/packet_capture.py`)
```python
class PacketCapture:
    def __init__(self, interface: str = None):
        # Capture on all interfaces or specified interface
        pass
    
    def start_capture(self, callback: Callable):
        # Start sniffing packets, call callback for each packet
        pass
    
    def stop_capture(self):
        # Stop packet capture
        pass
    
    def parse_packet(self, raw_packet) -> Packet:
        # Return structured Packet object
        pass
```

#### 2. Packet & Connection Models (Module: `firewall/models.py`)
```python
@dataclass
class Packet:
    timestamp: datetime
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str  # TCP, UDP, ICMP
    flags: str  # TCP flags (SYN, ACK, FIN, RST)
    size: int

@dataclass
class Connection:
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    state: str  # SYN_SENT, ESTABLISHED, FIN_WAIT, CLOSED
    start_time: datetime
    last_activity: datetime
    packets_in: int
    packets_out: int
    bytes_in: int
    bytes_out: int
```

#### 3. Connection State Manager (Module: `firewall/connection_tracker.py`)
```python
class ConnectionTracker:
    def __init__(self, timeout: int = 300):  # 5 minutes
        self.active_connections = {}  # Key: (src_ip, src_port, dst_ip, dst_port, proto)
        self.timeout = timeout
    
    def update_state(self, packet: Packet) -> Connection:
        # Update or create connection state based on packet
        # Handle TCP state machine
        # Return Connection object
        pass
    
    def get_connection(self, packet: Packet) -> Optional[Connection]:
        # Retrieve existing connection or None
        pass
    
    def clean_expired(self):
        # Remove connections older than timeout
        pass
    
    def get_stats(self) -> dict:
        # Return summary: active_connections, top_talkers, protocols
        pass
```

#### 4. Rule Engine (Module: `firewall/rule_engine.py`)
```python
@dataclass
class FirewallRule:
    rule_id: str
    priority: int
    enabled: bool
    protocol: str  # tcp, udp, icmp, any
    src_ip: str    # IP, CIDR, wildcard
    src_port: str  # port, range, any
    dst_ip: str
    dst_port: str
    direction: str  # inbound, outbound, both
    action: str     # allow, block, drop, log
    description: str

class RuleEngine:
    def __init__(self):
        self.rules: List[FirewallRule] = []
    
    def load_rules_from_json(self, path: str):
        # Load rules from JSON file
        pass
    
    def evaluate_packet(self, packet: Packet) -> tuple[str, FirewallRule]:
        # Return (action, matched_rule) based on priority
        # First match wins
        pass
    
    def add_rule(self, rule: FirewallRule):
        pass
    
    def delete_rule(self, rule_id: str):
        pass
    
    def enable_rule(self, rule_id: str):
        pass
    
    def disable_rule(self, rule_id: str):
        pass
```

#### 5. IDS Detection Engine (Module: `firewall/ids_engine.py`)
```python
class IDSEngine:
    def __init__(self, connection_tracker: ConnectionTracker):
        self.tracker = connection_tracker
        self.alerts = []
        self.port_scan_threshold = 10  # unique ports in 10 seconds
        self.syn_flood_threshold = 50  # SYN packets in 5 seconds
        self.icmp_flood_threshold = 100  # ICMP packets in 5 seconds
    
    def detect_port_scan(self, packet: Packet) -> Optional[Alert]:
        # Check for port scan pattern
        pass
    
    def detect_syn_flood(self, packet: Packet) -> Optional[Alert]:
        # Check for SYN flood pattern
        pass
    
    def detect_icmp_flood(self, packet: Packet) -> Optional[Alert]:
        # Check for ICMP flood pattern
        pass
    
    def detect_brute_force(self, packet: Packet) -> Optional[Alert]:
        # Check for repeated failed connection attempts
        pass
    
    def analyze_packet(self, packet: Packet) -> Optional[Alert]:
        # Run all detection rules, return Alert if threat detected
        pass
```

#### 6. Logging & Persistence (Module: `firewall/database.py`)
```python
class FirewallDatabase:
    def __init__(self, db_path: str = "firewall.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        # Create tables if not exist
        pass
    
    def log_packet(self, packet: Packet):
        # Insert into packets table
        pass
    
    def log_event(self, event: FirewallEvent):
        # Insert into firewall_events table
        pass
    
    def log_alert(self, alert: Alert):
        # Insert into alerts table
        pass
    
    def query_connections(self, limit: int = 100) -> List[Connection]:
        # Retrieve recent connections
        pass
    
    def query_alerts(self, severity: str = None) -> List[Alert]:
        # Retrieve alerts, optionally filtered by severity
        pass
```

#### 7. Main Firewall Orchestrator (Module: `firewall/firewall.py`)
```python
class PersonalFirewall:
    def __init__(self, config_path: str):
        self.packet_capture = PacketCapture()
        self.rule_engine = RuleEngine()
        self.connection_tracker = ConnectionTracker()
        self.ids_engine = IDSEngine(self.connection_tracker)
        self.database = FirewallDatabase()
        self.running = False
        
        self.rule_engine.load_rules_from_json(config_path)
    
    def start(self):
        self.running = True
        self.packet_capture.start_capture(callback=self._process_packet)
        print("[*] Firewall started...")
    
    def stop(self):
        self.running = False
        self.packet_capture.stop_capture()
        print("[*] Firewall stopped.")
    
    def _process_packet(self, raw_packet):
        # Main packet processing pipeline
        packet = self.packet_capture.parse_packet(raw_packet)
        
        # Update connection state
        connection = self.connection_tracker.update_state(packet)
        
        # Evaluate against rules
        action, rule = self.rule_engine.evaluate_packet(packet)
        
        # Log firewall event
        self.database.log_event(FirewallEvent(...))
        
        # Run IDS
        alert = self.ids_engine.analyze_packet(packet)
        if alert:
            self.database.log_alert(alert)
            print(f"[!] ALERT: {alert.description}")
    
    def get_stats(self) -> dict:
        # Return live statistics
        pass
```

---

## 1.3 Implementation Requirements

### Dependencies
```
scapy>=2.5.0
pydantic>=2.0
sqlalchemy>=2.0
click>=8.0  # for CLI
```

### Project Structure
```
firewall/
├── __init__.py
├── models.py                 # Packet, Connection, FirewallRule, Alert
├── packet_capture.py         # PacketCapture class
├── connection_tracker.py      # ConnectionTracker class
├── rule_engine.py            # RuleEngine class
├── ids_engine.py             # IDSEngine class
├── database.py               # FirewallDatabase class
├── firewall.py               # PersonalFirewall orchestrator
├── cli.py                    # CLI interface
└── config/
    └── rules.json            # Sample rules

tests/
├── test_connection_tracker.py
├── test_rule_engine.py
├── test_ids_engine.py
├── test_database.py

README.md
requirements.txt
```

### Configuration File (rules.json)
```json
{
  "rules": [
    {
      "rule_id": "default_allow_established",
      "priority": 10,
      "enabled": true,
      "protocol": "any",
      "src_ip": "any",
      "src_port": "any",
      "dst_ip": "any",
      "dst_port": "any",
      "direction": "both",
      "action": "allow",
      "description": "Allow established connections"
    },
    {
      "rule_id": "block_ssh_external",
      "priority": 20,
      "enabled": true,
      "protocol": "tcp",
      "src_ip": "any",
      "src_port": "any",
      "dst_ip": "0.0.0.0/0",
      "dst_port": "22",
      "direction": "inbound",
      "action": "block",
      "description": "Block SSH from external IPs"
    }
  ]
}
```

### CLI Interface (Module: `firewall/cli.py`)
```
Usage: python -m firewall.cli [OPTIONS] COMMAND [ARGS]

Commands:
  start              Start the firewall
  stop               Stop the firewall
  status             Show firewall status and statistics
  rules              List/manage firewall rules
  alerts             Show recent alerts
  queries            Query database (connections, events)
  
Examples:
  python -m firewall.cli start --config config/rules.json
  python -m firewall.cli status
  python -m firewall.cli alerts --severity high
  python -m firewall.cli rules --list
```

---

## 1.4 Testing Strategy – Tier 1

### Unit Tests
- [ ] Test rule matching (IP ranges, ports, protocols)
- [ ] Test TCP state machine (SYN, ESTABLISHED, FIN_WAIT, CLOSED)
- [ ] Test IDS detection (port scans, SYN floods, etc.)
- [ ] Test database operations (insert, query, cleanup)

### Integration Tests
- [ ] Capture real packets from localhost
- [ ] Verify rule evaluation pipeline
- [ ] Verify alerts are logged correctly

### Attack Simulation Tests
You must validate that your firewall actually detects attacks. Use these tools:

#### Port Scan Detection
```bash
# Tool: nmap
nmap -sS -p 1-100 127.0.0.1
# Expected: Firewall detects multiple SYN packets to different ports
```

#### SYN Flood Detection
```bash
# Tool: hping3
sudo hping3 -S --flood -p 80 127.0.0.1
# Expected: Firewall detects rapid SYN packets and alerts
```

#### ICMP Flood Detection
```bash
# Tool: ping with high rate
ping -i 0.01 127.0.0.1
# Expected: Firewall detects ICMP flooding
```

#### Brute-Force Detection
```bash
# Tool: ssh with incorrect password, repeated attempts
for i in {1..10}; do sshpass -p wrong ssh user@localhost; done
# Expected: Firewall detects repeated failed connections
```

### Test Documentation
- [ ] Create a `tests/ATTACK_SIMULATION.md` with step-by-step instructions for each attack
- [ ] Include expected firewall output
- [ ] Include Wireshark/tcpdump verification steps

---

## 1.5 Deliverables – Tier 1

- [ ] **Codebase**: Fully functional firewall with all components
- [ ] **Configuration file**: Sample `rules.json` with 10+ example rules
- [ ] **CLI interface**: Functional command-line tool
- [ ] **SQLite database schema**: With tables and proper indexes
- [ ] **Unit & integration tests**: >70% code coverage
- [ ] **Attack simulation tests**: Validated against real attacks
- [ ] **README**: Setup, usage, architecture overview
- [ ] **Demo video**: 5 min showing firewall blocking port scan, SYN flood, ICMP flood with real attacks

---

---

# TIER 2: ML ANOMALY DETECTION & ANALYTICS DASHBOARD

*Note: Start Tier 2 after Tier 1 is feature-complete and tested.*

## 2.1 ML Anomaly Detection Module

### Overview
Train an ML model on "normal" network traffic to detect anomalies (previously unseen threats).

### Algorithm: Isolation Forest
- [ ] Why Isolation Forest?
  - Fast inference (suitable for real-time processing)
  - No need for labeled data (unsupervised)
  - Naturally detects outliers
  - Robust to high-dimensional data

### Features for Anomaly Detection
Extract features from a 5-minute **sliding window**:
1. **Packet Rate**: packets/second
2. **Bandwidth Usage**: bytes/second
3. **Protocol Distribution**: % TCP, UDP, ICMP
4. **Connection Diversity**: unique (src_ip, dst_ip) tuples
5. **Port Entropy**: Shannon entropy of destination ports
6. **Active Connections**: count of established connections
7. **Failed Connections**: count of connections with RST/timeout

### Training & Inference (Module: `firewall/ml_anomaly.py`)
```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle

class AnomalyDetector:
    def __init__(self, model_path: str = None, contamination: float = 0.05):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.trained = False
        self.feature_names = [
            'packet_rate', 'bandwidth_usage', 'protocol_diversity',
            'connection_diversity', 'port_entropy', 'active_connections',
            'failed_connections'
        ]
        
        if model_path:
            self.load(model_path)
    
    def extract_features(self, connection_tracker: ConnectionTracker, window_seconds: int = 300) -> dict:
        # Extract features from connection tracker stats
        # Return: {feature_name: value, ...}
        pass
    
    def train(self, traffic_history: List[dict], epochs: int = 1):
        # Train on normal traffic data
        # traffic_history: list of feature dicts from normal traffic capture
        features = [list(d.values()) for d in traffic_history]
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled)
        self.trained = True
    
    def predict(self, features: dict) -> tuple[int, float]:
        # Returns: (is_anomaly, anomaly_score)
        # is_anomaly: 1 if anomaly, -1 if normal
        # anomaly_score: 0 to 1, higher = more anomalous
        if not self.trained:
            return (-1, 0)
        
        feature_vector = [features[name] for name in self.feature_names]
        feature_scaled = self.scaler.transform([feature_vector])
        
        prediction = self.model.predict(feature_scaled)[0]
        anomaly_score = -self.model.score_samples(feature_scaled)[0]
        
        return (prediction, anomaly_score)
    
    def save(self, path: str):
        pickle.dump({'scaler': self.scaler, 'model': self.model}, open(path, 'wb'))
    
    def load(self, path: str):
        data = pickle.load(open(path, 'rb'))
        self.scaler = data['scaler']
        self.model = data['model']
        self.trained = True
```

### Integration into Firewall
Modify `PersonalFirewall._process_packet()`:
```python
def _process_packet(self, raw_packet):
    # ... existing code ...
    
    # Check for anomalies (every 300 packets)
    if packet_count % 300 == 0:
        features = self.anomaly_detector.extract_features(self.connection_tracker)
        is_anomaly, score = self.anomaly_detector.predict(features)
        
        if is_anomaly:
            alert = Alert(
                alert_type="anomaly",
                severity="medium" if score < 0.7 else "high",
                description=f"Network anomaly detected (score: {score:.2f})",
                features=features
            )
            self.database.log_alert(alert)
```

### Training Pipeline
Create `scripts/train_model.py`:
```python
import argparse
from firewall.ml_anomaly import AnomalyDetector
from firewall.database import FirewallDatabase

def collect_normal_traffic(duration_minutes: int = 60):
    """Run firewall for N minutes and collect traffic data"""
    # Run firewall, collect features every 5 minutes
    # Return list of feature dicts
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=60, help='Training duration in minutes')
    parser.add_argument('--output', default='models/anomaly_detector.pkl')
    args = parser.parse_args()
    
    print(f"[*] Collecting normal traffic for {args.duration} minutes...")
    traffic_history = collect_normal_traffic(args.duration)
    
    print(f"[*] Training Isolation Forest on {len(traffic_history)} samples...")
    detector = AnomalyDetector()
    detector.train(traffic_history)
    
    print(f"[*] Saving model to {args.output}")
    detector.save(args.output)
    print("[+] Training complete!")

if __name__ == '__main__':
    main()
```

---

## 2.2 Threat Intelligence Integration

### Simple External API Integration
Instead of managing threat feeds, integrate a single free API: **AbuseIPDB**

```python
# firewall/threat_intel.py
import requests

class ThreatIntel:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.cache = {}  # Cache recent lookups
        self.cache_ttl = 3600  # 1 hour
    
    def check_ip_reputation(self, ip: str) -> dict:
        # Query AbuseIPDB API
        # Returns: {
        #   'ip': ip,
        #   'is_malicious': bool,
        #   'abuse_confidence_score': 0-100,
        #   'total_reports': int,
        #   'last_reported_at': datetime
        # }
        pass
    
    def is_malicious(self, ip: str, threshold: int = 75) -> bool:
        # Return True if abuse_confidence_score > threshold
        pass
```

**Usage in Firewall:**
```python
if packet.src_ip not in self.whitelist:
    rep = self.threat_intel.check_ip_reputation(packet.src_ip)
    if rep['is_malicious']:
        alert = Alert(
            alert_type="malicious_ip",
            severity="critical",
            src_ip=packet.src_ip,
            description=f"Known malicious IP (AbuseIPDB score: {rep['abuse_confidence_score']})"
        )
        self.database.log_alert(alert)
        # Auto-block if configured
```

---

## 2.3 Real-Time Monitoring Dashboard

### Technology Stack
- **Backend**: FastAPI (async)
- **Frontend**: React (or Streamlit for faster MVP)
- **Communication**: WebSockets for live updates
- **Data**: SQLite + in-memory cache for live stats

### Dashboard Pages

#### Page 1: Live Traffic Overview
- [ ] Real-time packet rate (packets/sec)
- [ ] Real-time bandwidth (Mbps in/out)
- [ ] Active connections count
- [ ] Top talkers (src IPs, dst IPs)
- [ ] Protocol distribution (pie chart: TCP %, UDP %, ICMP %)

#### Page 2: Active Connections
- [ ] Table of active connections:
  - Columns: src_ip, src_port, dst_ip, dst_port, protocol, state, duration, bytes_sent, bytes_recv
  - Sortable, filterable
  - Show first 100 connections, paginate

#### Page 3: Alerts & Incidents
- [ ] Alert feed (most recent first)
  - Columns: timestamp, alert_type, severity, src_ip, description
  - Color-coded severity (green=low, yellow=medium, orange=high, red=critical)
  - Filter by severity, type, date range

#### Page 4: Firewall Rules
- [ ] View all rules in table
  - Columns: rule_id, priority, enabled, action, src_ip, dst_ip, description
  - Enable/disable toggle
  - Edit/delete buttons
- [ ] Add new rule form

#### Page 5: Statistics & Reports
- [ ] Pie chart: Traffic by protocol
- [ ] Line chart: Packet rate over last 24 hours
- [ ] Line chart: Alert count over time
- [ ] Table: Top blocked IPs
- [ ] Summary stats: Total packets, total alerts, blocked packets, etc.

### FastAPI Backend (Module: `firewall/api.py`)
```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
import asyncio
import json

app = FastAPI()

# Reference to running firewall instance
firewall_instance = None

@app.get("/api/stats")
async def get_stats():
    """Return current firewall statistics"""
    return firewall_instance.get_stats()

@app.get("/api/connections")
async def get_connections(limit: int = 100, offset: int = 0):
    """Paginated list of active connections"""
    connections = firewall_instance.connection_tracker.get_connections(limit, offset)
    return {'connections': connections, 'total': len(connections)}

@app.get("/api/alerts")
async def get_alerts(severity: str = None, limit: int = 100):
    """Get recent alerts"""
    alerts = firewall_instance.database.query_alerts(severity=severity, limit=limit)
    return {'alerts': alerts}

@app.get("/api/rules")
async def get_rules():
    """Get all firewall rules"""
    return {'rules': firewall_instance.rule_engine.rules}

@app.post("/api/rules")
async def create_rule(rule_data: dict):
    """Create new firewall rule"""
    rule = FirewallRule(**rule_data)
    firewall_instance.rule_engine.add_rule(rule)
    return {'success': True, 'rule_id': rule.rule_id}

@app.put("/api/rules/{rule_id}")
async def update_rule(rule_id: str, rule_data: dict):
    """Update firewall rule"""
    firewall_instance.rule_engine.update_rule(rule_id, **rule_data)
    return {'success': True}

@app.websocket("/ws/live-stats")
async def websocket_live_stats(websocket: WebSocket):
    """WebSocket for live updates"""
    await websocket.accept()
    try:
        while True:
            stats = firewall_instance.get_stats()
            await websocket.send_text(json.dumps(stats))
            await asyncio.sleep(2)  # Update every 2 seconds
    except Exception as e:
        print(f"WebSocket error: {e}")

# Serve React frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True))
```

### React Frontend (Module: `firewall/frontend/`)
```
frontend/
├── src/
│   ├── components/
│   │   ├── LiveStats.jsx
│   │   ├── ActiveConnections.jsx
│   │   ├── AlertFeed.jsx
│   │   ├── RulesManager.jsx
│   │   └── Analytics.jsx
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Connections.jsx
│   │   ├── Alerts.jsx
│   │   ├── Rules.jsx
│   │   └── Analytics.jsx
│   ├── App.jsx
│   └── index.js
├── package.json
└── build/  (output)
```

**Key Libraries:**
- `react-router-dom`: Routing
- `axios`: HTTP client
- `recharts`: Charts
- `tailwindcss`: Styling

### Streamlit Alternative (Faster MVP)
If you want a quick dashboard MVP without React:
```python
# firewall/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Firewall Dashboard", layout="wide")

st.title("🔥 Personal Firewall Dashboard")

# Live stats in columns
col1, col2, col3, col4 = st.columns(4)
stats = firewall_instance.get_stats()
col1.metric("Packet Rate", f"{stats['pps']:.0f} pps")
col2.metric("Bandwidth", f"{stats['mbps']:.2f} Mbps")
col3.metric("Active Connections", stats['active_connections'])
col4.metric("High Severity Alerts", stats['high_alerts'])

# Connections table
st.subheader("Active Connections")
connections_df = pd.DataFrame(firewall_instance.get_connections())
st.dataframe(connections_df, use_container_width=True)

# Alert feed
st.subheader("Recent Alerts")
alerts = firewall_instance.database.query_alerts(limit=50)
alerts_df = pd.DataFrame([{
    'timestamp': a.timestamp,
    'type': a.alert_type,
    'severity': a.severity,
    'src_ip': a.src_ip,
    'description': a.description
} for a in alerts])
st.dataframe(alerts_df.sort_values('timestamp', ascending=False), use_container_width=True)

# Charts
col1, col2 = st.columns(2)
with col1:
    fig = px.pie(values=stats['protocol_counts'].values(), names=stats['protocol_counts'].keys())
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Alerts over time
    alert_timeline = firewall_instance.database.get_alert_timeline(hours=24)
    fig = px.line(alert_timeline, x='hour', y='count', title='Alerts over 24h')
    st.plotly_chart(fig, use_container_width=True)
```

---

## 2.4 Deliverables – Tier 2

- [ ] **Anomaly Detection Module**: Trained Isolation Forest model
- [ ] **Training Script**: Collects normal traffic and trains model
- [ ] **Threat Intel Integration**: AbuseIPDB API client
- [ ] **FastAPI Backend**: RESTful + WebSocket endpoints
- [ ] **React/Streamlit Dashboard**: Multi-page UI with live updates
- [ ] **Integration Tests**: Test API endpoints, WebSocket communication
- [ ] **Dashboard Demo**: 5 min video showing live traffic, alerts, anomalies
- [ ] **Updated README**: Dashboard setup, training instructions

---

---

# TIER 3: ADVANCED FEATURES & INTEGRATION (OPTIONAL)

## 3.1 Email & Telegram Alerting

```python
# firewall/alerting.py
import smtplib
import requests
from email.mime.text import MIMEText

class AlertingService:
    def __init__(self, config: dict):
        self.email_config = config.get('email')
        self.telegram_config = config.get('telegram')
    
    def send_email_alert(self, alert: Alert):
        # Send via SMTP
        msg = MIMEText(f"Alert: {alert.description}\nIP: {alert.src_ip}")
        # ... implementation
    
    def send_telegram_alert(self, alert: Alert):
        # Send via Telegram Bot API
        # ... implementation
```

---

## 3.2 iptables Integration (Optional, Linux-only)

```python
# firewall/iptables_integration.py
import subprocess

class iptablesManager:
    @staticmethod
    def block_ip(ip: str):
        # Add iptables rule
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
    
    @staticmethod
    def allow_ip(ip: str):
        # Remove iptables rule
        subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])
```

---

## 3.3 Advanced ML Features
- Multi-class classification (attack type prediction)
- LSTM-based temporal anomaly detection
- Active learning (user feedback on alerts)

---

---

# IMPLEMENTATION TIMELINE

| Phase | Duration | Goals | Status |
|-------|----------|-------|--------|
| **Tier 1** | Weeks 1–5 | Core firewall, rule engine, basic IDS | Foundational |
| **Tier 2** | Weeks 6–8 | ML anomaly detection, analytics dashboard | Portfolio-ready |
| **Tier 3** | Weeks 9–10 | Alerting, iptables, advanced ML | Nice-to-have |

---

# SUCCESS CRITERIA

## Tier 1 (MVP)
- [ ] Firewall captures packets and applies rules correctly
- [ ] Firewall successfully detects and alerts on real attacks (port scan, SYN flood, ICMP flood)
- [ ] All events logged to SQLite database
- [ ] CLI interface functional
- [ ] >70% test coverage
- [ ] **No false positives on normal traffic**

## Tier 2 (Production)
- [ ] ML model trained on normal traffic, detects anomalies
- [ ] Dashboard displays live traffic, connections, alerts
- [ ] API endpoints working, WebSockets live
- [ ] Threat intel integration working (AbuseIPDB queries)
- [ ] **Full end-to-end demo**: capture attack → IDS detects → alert logged → dashboard shows

## Tier 3 (Polish)
- [ ] Email/Telegram alerts sent on critical events
- [ ] iptables integration auto-blocks malicious IPs
- [ ] Performance benchmarked (handles >10K pps)

---

# EVALUATION RUBRIC

### For Placement Interviews
- **Architecture**: Can you explain the stateful inspection pipeline?
- **Trade-offs**: Why Isolation Forest? What about false positives in IDS?
- **Real-world testing**: Demo with actual attacks (port scan, SYN flood).
- **Code quality**: Clean separation of concerns, testability.
- **Problem-solving**: How did you handle X challenge?

---

# REFERENCES & RESOURCES

### Packet Capture
- Scapy documentation: https://scapy.readthedocs.io/
- PyShark: https://github.com/KimikoMaying/pyshark

### Network Security
- NIST Firewall Guide: https://csrc.nist.gov/publications/fips
- OWASP Network Segmentation: https://owasp.org/

### ML Anomaly Detection
- Scikit-learn Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- SANS: Network Anomaly Detection: https://www.sans.org/

### Dashboard
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Streamlit: https://streamlit.io/

---

# APPENDIX: Sample Attack Simulation Commands

```bash
# Port Scan (Nmap)
nmap -sS -p 1-1000 127.0.0.1

# SYN Flood (hping3)
sudo hping3 -S --flood -p 80 192.168.1.100

# ICMP Flood (ping)
ping -i 0.01 192.168.1.100 # on Linux, use -i 0.01

# Brute Force SSH (Paramiko + sshpass)
for i in {1..10}; do sshpass -p wrongpass ssh user@localhost; done

# UDP Flood (netcat)
nc -u -b -w1 -z 192.168.1.100 80

# Verify with Wireshark
tshark -i eth0 -f "tcp.flags.syn==1"  # Show SYN packets
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-25  
**Status:** Ready for Implementation