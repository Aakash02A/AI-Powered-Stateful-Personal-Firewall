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

## ⚙️ System Requirements

### Backend
- Python 3.9 or higher
- SQLite3 (included with Python)
- For Windows packet capture: Npcap (https://npcap.com/)
- For Linux packet capture: libpcap development headers

### Frontend
- Node.js 18.x or higher
- npm or yarn package manager

### Optional
- Docker and Docker Compose (for containerized deployment)
- AbuseIPDB API key (for threat intelligence integration)

---

## 📦 Installation

### Quick Setup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall.git
   cd AI-Powered-Stateful-Personal-Firewall
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```
   
   This will:
   - Create necessary directories
   - Generate secure API keys
   - Create `.env` configuration files
   - Initialize the database

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Manual Setup

If you prefer manual configuration:

1. **Create backend environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your secure API key:
   ```
   API_KEY=your_secure_api_key_here
   ```

2. **Create frontend environment file**:
   ```bash
   cp frontend/.env.example frontend/.env
   ```
   Edit `frontend/.env` and set the same API key:
   ```
   VITE_API_KEY=your_secure_api_key_here
   ```

3. **Create necessary directories**:
   ```bash
   mkdir -p data/logs ml/models ml/data
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   ```

5. **Initialize database**:
   ```bash
   python -m alembic upgrade head
   ```

---

## � Starting the Application

### Development Mode

1. **Start the backend API**:
   ```bash
   python -m api.main
   ```
   The API will be available at `http://127.0.0.1:8000`

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`

### Production Mode

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Start the backend**:
   ```bash
   python -m api.main
   ```
   The application will serve both the API and the built frontend at `http://127.0.0.1:8000`

### Docker Deployment

```bash
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
- `API_KEY`: Secure API key for authentication (required)
- `HOST`: API host address (default: 127.0.0.1)
- `PORT`: API port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DATABASE_URL`: Database connection string (default: sqlite:///data/firewall.db)
- `MONITOR_ONLY`: When true, logs packets without dropping (default: true)
- `CORS_ORIGINS`: Allowed CORS origins (default: ["*"])
- `ABUSEIPDB_API_KEY`: Optional API key for threat intelligence

#### Frontend (frontend/.env)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000/api/v1)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:8000/api/v1/ws/stream)
- `VITE_API_KEY`: API key for authentication (must match backend)

### Firewall Rules

Edit `firewall/config/rules.json` to customize firewall rules. The system includes sensible defaults for common traffic patterns.

### IDS Configuration

Edit `firewall/config/ids_config.json` to adjust intrusion detection thresholds for:
- Port scan detection
- SYN flood detection
- ICMP flood detection
- Brute force detection

---

## 🔌 API Usage

### Authentication

All API endpoints require an `X-API-Key` header with your configured API key.

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/stats
```

### Interactive Documentation

Interactive Swagger documentation is available at:
- **`http://localhost:8000/docs`** (Swagger UI)
- **`http://localhost:8000/redoc`** (ReDoc)

### Common Endpoints

**Get Live Stats**
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/stats
```

**Get Top Talkers**
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/top-talkers
```

**Get Recent Alerts**
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/alerts?limit=10
```

**Get Active Connections**
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/connections?limit=10
```

### WebSocket Connection

Connect to the WebSocket for real-time alerts:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream?api_key=YOUR_API_KEY');
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/test_api.py -v
pytest tests/test_ids_engine.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🛠️ CLI Commands

### Start Firewall
```bash
python -m firewall.cli start
```

### View Rules
```bash
python -m firewall.cli rules
```

### View Alerts
```bash
python -m firewall.cli alerts
```

### Query Connections
```bash
python -m firewall.cli queries --limit=10
```

### Database Migration
```bash
python -m firewall.cli db-upgrade
```

---

## 🔒 Security Considerations

### Important Security Notes

1. **API Key Security**: Never commit your `.env` file to version control. Always use strong, randomly generated API keys.

2. **Monitor Mode**: The firewall defaults to `MONITOR_ONLY=true` for safety. Set to `false` only when you're ready for active packet blocking.

3. **Network Access**: The firewall requires administrator/root privileges for packet capture. Only run trusted code with these privileges.

4. **CORS Configuration**: In production, restrict `CORS_ORIGINS` to specific domains instead of using wildcard `["*"]`.

5. **Database Security**: The default SQLite database is suitable for single-user deployments. For multi-user scenarios, consider PostgreSQL or MySQL.

### Production Deployment Checklist

- [ ] Set strong API keys in environment variables
- [ ] Configure appropriate CORS origins
- [ ] Set `MONITOR_ONLY=false` for active blocking
- [ ] Use HTTPS/TLS for API communication
- [ ] Configure firewall rules for your network
- [ ] Set up regular database backups
- [ ] Configure log rotation
- [ ] Monitor system resources
- [ ] Test failover procedures

---

## 🐛 Troubleshooting

### Common Issues

**API fails to start with "API_KEY not set" error**
- Ensure your `.env` file contains a valid `API_KEY` value
- Run `python setup.py` to regenerate configuration

**Frontend cannot connect to backend**
- Verify both services are running
- Check `VITE_API_BASE_URL` in frontend/.env
- Ensure API key matches between backend and frontend

**Packet capture not working on Windows**
- Install Npcap from https://npcap.com/
- Run the application as Administrator
- Ensure Npcap is installed in "WinPcap API-compatible Mode"

**Database errors**
- Run `python -m alembic upgrade head` to ensure migrations are applied
- Check that the `data` directory exists and is writable

**ML model not loading**
- Ensure `ml/models/anomaly_detector_v1.0.joblib` exists
- Check that scikit-learn version is compatible
- See ML training documentation for model generation

### Getting Help

- Check the [Architecture Documentation](ARCHITECTURE.md) for system design details
- Review test files for usage examples
- Open an issue on GitHub for bugs or feature requests
- See [SECURITY.md](SECURITY.md) for security vulnerability reporting

---

## 🗺️ Roadmap

- [x] Phase 1: Stateful Packet Inspection Engine
- [x] Phase 2: Rule Engines & CLI
- [x] Phase 3: REST API & Production Readiness
- [x] Phase 4: React / Next.js Admin Dashboard (UI)
- [x] Phase 5: Machine Learning Anomaly Detection & Auto-Mitigation
- [ ] Phase 6: eBPF / Kernel-Level Integration
- [ ] Phase 7: Multi-user Support & RBAC
- [ ] Phase 8: Advanced Analytics & Reporting

---

## 🛡️ Contributing & Security

* Review the [CONTRIBUTING.md](CONTRIBUTING.md) to understand PR protocols.
* Review [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.
