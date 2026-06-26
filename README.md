# AI-Powered Stateful Personal Firewall 🛡️

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)

A Next-Generation Personal Firewall (NGFW) built in Python that combines stateful packet inspection, rule-based filtering, signature-based IDS, highly-concurrent database logging, and a robust REST API for dashboards.

![Firewall Architecture Placeholder](https://via.placeholder.com/800x400?text=Architecture+Diagram+Placeholder)

## 🚀 Features

*   **Stateful Packet Inspection**: Deep tracking of TCP connections, SYN/ACK sequences, and dynamic states.
*   **High-Performance Asynchronous Logging**: Lock-free multithreaded buffering using Python `Queue` to ensure zero packet drop during intensive IO.
*   **Intrusion Detection System (IDS)**: Detects network threats heuristically:
    *   Port Scans
    *   SYN Floods
    *   ICMP Floods
    *   Brute-force connections
*   **REST API & WebSockets**: Exposes endpoints for real-time traffic monitoring and metrics polling.
*   **Prometheus Observability**: `/metrics` available for Grafana dashboards.
*   **Container Ready**: Includes a fully configured `Dockerfile` and `docker-compose.yml`.

---

## 🏗️ Architecture

The firewall architecture handles extremely high traffic gracefully using an event-driven queueing model. 

For an in-depth view of the asynchronous queuing and Thread Health Monitoring, see [ARCHITECTURE.md](doc/ARCHITECTURE.md).

---

## ⚙️ Installation

1. **Prerequisites**: Python 3.9+ and Git. (On Windows, **Npcap** must be installed for raw packet capture).
2. **Clone the Repo**:
   ```bash
   git clone https://github.com/your-username/ai-firewall.git
   cd ai-firewall
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
See [DEPLOYMENT.md](doc/DEPLOYMENT.md) for environment profile specifics.

---

## 🔌 API Examples

The core API runs locally on `http://127.0.0.1:8000`. By default, endpoints require an `X-API-Key` header (default: `default_dev_key`).

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
- [ ] Phase 4: React / Next.js Admin Dashboard (UI)
- [ ] Phase 5: Machine Learning Anomaly Detection
- [ ] Phase 6: eBPF / Kernel-Level Integration

---

## 🛡️ Contributing & Security

* Review the [CONTRIBUTING.md](CONTRIBUTING.md) to understand PR protocols.
* Review [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.
