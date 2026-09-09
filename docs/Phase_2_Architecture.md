# Phase 2 Architecture & Design Document

## 1. Project Context
**Phase 1 Retrospective**  
Phase 1 successfully delivered the core user-space firewall engine. It achieved stateful packet inspection, dynamic rule evaluations, foundational IDS heuristics (detecting port scans, SYN floods, and brute force), and SQLite persistence. 

**Limitations & Constraints**  
While functional, Phase 1 identified severe performance bottlenecks inherent to its architecture:
- **Python GIL & Synchronous I/O:** Logging every sniffed packet directly to SQLite blocks the main processing thread, capping throughput at roughly ~180 Packets Per Second (PPS).
- **User-Space Emulation:** As a user-space application, blocking is achieved actively (by forging `RST`/`ICMP` packets) rather than passively dropping traffic before the OS processes it.
- **Database Bloat:** Writing a new database row for every raw packet will cause rapid, unbounded database growth.

Phase 2 will pivot from core engine mechanics to high-performance analytics, data aggregation, and visualization.

---

## 2. Data Layer Design
Phase 2 shifts the focus from logging raw data to aggregating meaningful security telemetry.

**Data Consumption & Storage Strategy:**
- **Raw Packets:** We will **cease storing every raw packet** in the database. Packets will remain purely in-memory (short-lived) for rule evaluation and IDS analysis. Only packets that trigger an alert or a blocked event will have their raw headers logged.
- **Connections (Flows):** The core unit of storage becomes the bidirectional *flow* (Connection). These will be stored upon expiration or closure, containing aggregated byte/packet counters.
- **Alerts & Events:** Persistent storage of all rule matches and IDS triggers.

**Aggregated Statistics (Computed in-memory, persisted periodically):**
- Traffic volume per hour/day.
- Top source IPs by connection count and byte volume.
- Port/Protocol utilization percentages.

**Storage Boundaries:**
- **In-Memory (Fast):** Active connections, raw packet ring buffers, active IDS sliding windows.
- **SQLite (Durable):** Closed connections, alerts, events, daily aggregate rollups.

---

## 3. API Layer Design
The backend will expose a RESTful JSON API (likely using Flask or FastAPI) to serve the analytics dashboard.

### `GET /api/stats`
- **Purpose:** Provide top-level KPIs for dashboard widgets.
- **Parameters:** `?timeframe=24h`
- **Data Source:** Aggregation engine (querying connections and alerts).
- **Example Response:**
  ```json
  {
    "total_connections": 14502,
    "active_connections": 134,
    "total_blocked": 450,
    "active_alerts": 12,
    "bytes_transferred": 104857600
  }
  ```

### `GET /api/alerts`
- **Purpose:** Retrieve recent security alerts.
- **Parameters:** `?severity=high,critical&limit=50`
- **Data Source:** `AlertRecord` table.
- **Example Response:**
  ```json
  [
    {
      "timestamp": "2026-06-25T14:30:00Z",
      "alert_type": "syn_flood",
      "severity": "critical",
      "src_ip": "192.168.1.100",
      "description": "SYN flood detected from 192.168.1.100"
    }
  ]
  ```

### `GET /api/connections`
- **Purpose:** Paginated list of active and recent flows.
- **Parameters:** `?state=ESTABLISHED&limit=100`
- **Data Source:** In-memory `ConnectionTracker` + SQLite `connections` table.
- **Example Response:**
  ```json
  [
    {
      "src_ip": "10.0.0.5",
      "dst_ip": "8.8.8.8",
      "dst_port": 53,
      "state": "ESTABLISHED",
      "bytes_out": 512,
      "bytes_in": 1024
    }
  ]
  ```

### `GET /api/top-talkers`
- **Purpose:** Identifies hosts generating the most traffic or connections.
- **Parameters:** `?metric=bytes&limit=10`
- **Data Source:** Analytics Engine (daily aggregations).
- **Example Response:**
  ```json
  [
    {"ip": "192.168.1.50", "bytes": 50043920, "connections": 405},
    {"ip": "10.0.0.2", "bytes": 1024300, "connections": 12}
  ]
  ```

### `GET /api/protocols`
- **Purpose:** Break down traffic by protocol/port for pie charts.
- **Parameters:** `?timeframe=7d`
- **Data Source:** Aggregation Engine.
- **Example Response:**
  ```json
  {"TCP": 85, "UDP": 12, "ICMP": 3}
  ```

### `GET /api/timeline`
- **Purpose:** Timeseries data for line/bar charts (traffic and alerts over time).
- **Parameters:** `?interval=1h&limit=24`
- **Data Source:** SQLite grouped by truncated timestamps.
- **Example Response:**
  ```json
  [
    {"time": "2026-06-25T14:00:00Z", "bytes": 4500, "alerts": 2},
    {"time": "2026-06-25T15:00:00Z", "bytes": 9800, "alerts": 0}
  ]
  ```

---

## 4. Analytics Layer
The "Security Analytics Engine" acts as a background thread analyzing data produced by the firewall.

**Metrics & Computations:**
1. **Top Attackers:** Derived by counting distinct `AlertRecord` triggers per `src_ip`.
2. **Most Targeted Ports:** Aggregated by counting `dst_port` frequency on `FirewallEventRecord` where `action=block`.
3. **Traffic Volume Over Time:** Rollups of `bytes_in` + `bytes_out` from closed connections, bucketed by hour.
4. **Threat Scoring System:** 
   - Each external IP is assigned a "Threat Score" (0-100).
   - *Computation:* +10 for a blocked connection, +25 for a port scan alert, +50 for brute force. Decay score by 5 points every 24 hours of inactivity.
   - *Frequency:* Batch calculated every 5 minutes in a background thread.

---

## 5. System Architecture Overview
```text
[ Network Layer ]
       │
       ▼ (Raw PCAP)
[ Packet Capture Daemon ]
       │
       ├─► [ Connection Tracker ] ──► [ In-Memory State ]
       │
       ├─► [ Rule Engine ] ─────────► [ Actions (Allow/Block) ]
       │
       └─► [ IDS Engine ] ──────────► [ Alert Generation ]
       │
(Asynchronous Queue)
       │
       ▼
[ Storage & Aggregation Layer ]
       │
       ├─► [ SQLite DB ] (Persistent Logs)
       │
       └─► [ Analytics Engine ] (Metrics & Threat Scoring)
       │
       ▼
[ REST API Layer (Flask/FastAPI) ]
       │
       ▼ (JSON / HTTP)
[ Web Dashboard UI (React/Vue) ]
```

---

## 6. Data Flow Explanation
1. **Packet Capture:** `scapy` reads a raw frame from the network interface.
2. **State & Rules:** The `ConnectionTracker` updates flow bytes/state. The `RuleEngine` determines the firewall action.
3. **Threat Analysis:** The `IDS` window assesses the packet for heuristics.
4. **Storage (Async):** Instead of synchronous DB writes, the packet metadata is placed onto a thread-safe Queue. A separate worker thread pops the queue, aggregates it into current connection flows, and only commits closed flows or critical alerts to SQLite.
5. **Analytics:** The background Analytics Engine periodically runs queries on SQLite to update in-memory caches of "Top Talkers" and "Threat Scores".
6. **API & Dashboard:** The dashboard polls the API, which instantly returns the pre-computed in-memory analytics and paginated database views.

---

## 7. Database Design Updates
The Phase 1 schema must be evolved for Phase 2:
- **Deprecation:** The `packets` table will be truncated and removed (or strictly limited to a small ring-buffer of the last 1,000 packets) to solve the I/O bottleneck.
- **New Table (`threat_intelligence`):**
  - `ip_address` (String, PK)
  - `threat_score` (Integer)
  - `last_seen` (DateTime)
- **New Table (`hourly_traffic_aggregates`):**
  - `hour` (DateTime, PK)
  - `total_bytes` (Integer)
  - `total_connections` (Integer)
- **Indexing Strategy:** Already implemented in Phase 1.1 (`src_ip`, `dst_ip`, `timestamp`), which will natively support Phase 2 queries.

---

## 8. Phase 2 Roadmap
- **Phase 2A (Analytics Backend):** Rip out synchronous packet logging. Introduce the async queuing system, connection flow logging, and the Threat Scoring engine.
- **Phase 2B (API Layer):** Build the REST API endpoints and integrate Swagger/OpenAPI documentation.
- **Phase 2C (Dashboard UI):** Scaffold a modern frontend (e.g., React + Tailwind) featuring live charts, interactive rule management, and real-time alert notifications.
- **Phase 2D (Advanced & ML - Optional):** Introduce isolation forests or standard standard-deviation algorithms for traffic anomaly detection.

---

## 9. Risks and Limitations
- **Performance Bottlenecks:** Even with async DB writes, processing >10,000 PPS in pure Python will consume significant CPU.
- **Real-Time Websockets:** Polling the API (GET) might introduce latency. Implementing WebSockets for real-time alert streaming could increase backend complexity.
- **SQLite Concurrency:** SQLite restricts concurrent writes. The async worker must be the *exclusive* writer to the database to prevent locking exceptions.

---

## 10. Final Outcome Definition
Phase 2 is considered successful when:
1. The backend API serves all defined endpoints within <200ms latency under normal load.
2. The system throughput (PPS) improves by at least 10x due to the removal of raw packet logging.
3. A fully functional, styled Web Dashboard visually represents network telemetry, allows manual rule creation, and visualizes security alerts in a user-friendly manner.
