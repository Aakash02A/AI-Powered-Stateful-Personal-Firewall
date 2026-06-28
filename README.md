# AI-Powered Stateful Personal Firewall 🛡️

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-18.x-brightgreen.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Backend CI](https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall/actions/workflows/ci.yml/badge.svg)](https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall/actions)

A Next-Generation Personal Firewall (NGFW) built in Python that combines stateful packet inspection, rule-based filtering, signature-based IDS, highly-concurrent database logging, and a robust REST API for dashboards.

For a detailed view of the architecture, please see [Architecture Documentation](ARCHITECTURE.md).

## 🚀 Features

*   **Stateful Packet Inspection**: Deep tracking of TCP connections, SYN/ACK sequences, and dynamic states.
*   **High-Performance Asynchronous Logging**: Lock-free multithreaded buffering using Python `Queue` to ensure zero packet drop during intensive IO.
*   **Intrusion Detection System (IDS)**: Detects network threats heuristically (Port Scans, SYN Floods, ICMP Floods, Brute-force).
*   **Machine Learning Anomaly Detection**: Uses Isolation Forest to detect Zero-Day anomalies based on traffic patterns (bytes/sec, connection duration, packet size variance).
*   **Active Auto-Mitigation**: Dynamically creates temporary `DROP` rules when heuristic, ML, or Threat Intelligence scores exceed thresholds.
*   **Threat Intelligence Integration**: Checks IPs against AlienVault OTX pulses for known malicious actors.
*   **Modern React Dashboard**: A sleek, dark-themed Vite/React UI with real-time charts (Recharts), dynamic DataTables, and WebSocket-driven Alert feeds.
*   **REST API & WebSockets**: Exposes endpoints for real-time traffic monitoring and metrics polling. Auto-documented at `/docs`.
*   **Prometheus Observability**: `/metrics` available for Grafana dashboards.
*   **Container Ready**: Includes a fully configured `Dockerfile` and `docker-compose.yml` serving both the backend and frontend.

---

## 🏗️ Architecture

The firewall architecture handles extremely high traffic gracefully using an event-driven queueing model. 

For an in-depth view of the asynchronous queuing and Thread Health Monitoring, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## ⚙️ Installation

1. **Prerequisites**: Python 3.9+ and Git. (On Windows, **Npcap** must be installed for raw packet capture).
2. **Clone the Repo**:
   ```bash
   git clone https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall.git
   cd AI-Powered-Stateful-Personal-Firewall
   ```
3. **Setup Environment**:
   ```bash
   cp .env.example .env
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Database Initialization**:
   ```bash
   python -m alembic upgrade head
   ```

---

## 💻 Usage

### 1. Standalone CLI
Run the daemon (Requires Root/Administrator capabilities):
```bash
python -m firewall.cli start
```

Other CLI commands:
- `python -m firewall.cli rules` (View loaded rules)
- `python -m firewall.cli alerts` (View generated IDS alerts)
- `python -m firewall.cli db-upgrade` (Manually run migrations)

### 2. Docker Deployment
We recommend using Docker Compose for an isolated, secure deployment. The container drops root privileges dynamically and retains only `NET_ADMIN`.
```bash
docker-compose up -d
```
See [DEPLOYMENT.md](DEPLOYMENT.md) for environment profile specifics.

---

## 🔌 API Examples

The core API runs locally on `http://127.0.0.1:8000`. By default, endpoints require an `X-API-Key` header (default: `default_dev_key`).
Interactive Swagger documentation is automatically available at **`http://localhost:8000/docs`**.

**1. Get Live Stats**
```bash
curl -H "X-API-Key: default_dev_key" http://localhost:8000/api/v1/stats
```
**2. Get Top Talkers**
```bash
curl -H "X-API-Key: default_dev_key" http://localhost:8000/api/v1/top-talkers
```
**3. Real-Time WebSockets**
Connect a client to `ws://localhost:8000/ws/alerts` for instantaneous JSON broadcasts whenever the IDS fires.

---

## 🗺️ Roadmap

- [x] Phase 1: Stateful Packet Inspection Engine
- [x] Phase 2: Rule Engines & CLI
- [x] Phase 3: REST API & Production Readiness
- [x] Phase 4: React / Next.js Admin Dashboard (UI)
- [x] Phase 5: Machine Learning Anomaly Detection & Auto-Mitigation
- [ ] Phase 6: eBPF / Kernel-Level Integration

---

## 🛡️ Contributing & Security

* Review the [CONTRIBUTING.md](CONTRIBUTING.md) to understand PR protocols.
* Review [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.
