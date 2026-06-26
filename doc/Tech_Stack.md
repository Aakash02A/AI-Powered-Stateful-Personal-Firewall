# AI-Powered Stateful Personal Firewall: Complete Tech Stack

---

## 🔴 TIER 1: Core Firewall & Stateful Inspection

### Packet Capture & Network Analysis
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Scapy** | ≥2.5.0 | Packet capture, parsing, manipulation | Python-native, full control, widely used in security |
| **PyShark** | Latest | Alternative packet capture (optional) | Better performance than Scapy for high-throughput |
| **Dpkt** | Optional | Low-level packet parsing | Lightweight alternative |

### Core Framework & Language
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Python** | 3.9+ | Primary language | Security tools standard, libraries ecosystem |
| **asyncio** | Built-in | Async packet processing (optional) | Non-blocking I/O for high throughput |

### Data Models & Validation
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Pydantic** | ≥2.0 | Data validation, serialization | Type safety, JSON schema generation |
| **dataclasses** | Built-in | Define Packet, Connection, Rule models | Clean, built-in Python feature |

### Database & Persistence
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **SQLite** | Built-in (Python) | Local database for logging | Lightweight, no server, built-in Python support |
| **SQLAlchemy** | ≥2.0 | ORM for database operations | Abstraction, query builder, migrations |
| **sqlite3** | Built-in | Direct SQLite access | Simple, fast for local storage |

### CLI & Configuration
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Click** | ≥8.0 | Command-line interface | User-friendly, decorator-based, built-in help |
| **JSON** | Built-in | Rule configuration format | Human-readable, standard, no dependencies |
| **YAML** | Optional | Alternative config format | More readable than JSON |

### Testing & Validation
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **pytest** | ≥7.0 | Unit & integration testing | Standard Python testing framework |
| **unittest** | Built-in | Alternative testing | Python standard library |
| **Nmap** | System | Port scan simulation | Industry-standard network scanner |
| **hping3** | System | SYN flood simulation | Packet crafting tool |
| **Wireshark/tshark** | System | Packet verification | Packet analysis, verification |

### Logging & Monitoring
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **logging** | Built-in | Application logging | Python standard library |
| **structlog** | Optional | Structured logging | JSON-formatted logs for parsing |

---

## 🟢 TIER 2: ML Anomaly Detection & Analytics Dashboard

### Machine Learning
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Scikit-learn** | ≥1.0 | Isolation Forest, preprocessing | Industry standard, simple to use |
| **NumPy** | ≥1.20 | Numerical computations | Fast array operations, ML standard |
| **Pandas** | ≥1.3 | Data manipulation, feature engineering | Data analysis, sliding window operations |
| **pickle** | Built-in | Model persistence | Save/load trained models |
| **joblib** | Optional | Alternative model serialization | Better for large objects |

### Backend API
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **FastAPI** | ≥0.95 | RESTful API + WebSockets | Async, auto-docs, modern Python |
| **Uvicorn** | ≥0.20 | ASGI server | Lightning-fast async server |
| **Pydantic** | ≥2.0 | Request/response validation | Type-safe API contracts |
| **python-socketio** | Optional | WebSocket alternative | Real-time bidirectional communication |

### Frontend Options

#### **Option A: React (Full-Featured)**
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **React** | ≥18.0 | UI framework | Component-based, industry standard |
| **React Router** | ≥6.0 | Client-side routing | Multi-page navigation |
| **Axios** | ≥1.0 | HTTP client | Promise-based API calls |
| **Recharts** | ≥2.0 | Data visualization | React-friendly charting |
| **Tailwind CSS** | ≥3.0 | Styling | Utility-first CSS |
| **WebSocket** | Native | Real-time updates | Browser API for live data |
| **Node.js** | ≥16 | Build environment | npm, package management |
| **npm/yarn** | Latest | Package management | Dependency management |

#### **Option B: Streamlit (Rapid MVP)**
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Streamlit** | ≥1.20 | Dashboard framework | Python-only, rapid prototyping, no frontend skills needed |
| **Plotly** | ≥5.0 | Interactive charts | High-quality visualizations |
| **Pandas** | ≥1.3 | Data tables | DataFrame display |

### Threat Intelligence
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **requests** | ≥2.28 | HTTP client for API calls | Simple, reliable HTTP library |
| **AbuseIPDB** | API | IP reputation service | Free tier, comprehensive database |
| **cachetools** | Optional | API response caching | Reduce API calls, improve performance |

### Data Processing
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **Pandas** | ≥1.3 | Feature extraction, sliding windows | Time-series operations, groupby |
| **NumPy** | ≥1.20 | Array operations | Fast computations |

---

## 🟡 TIER 3: Advanced Features (Optional)

### Notifications & Alerting
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **smtplib** | Built-in | Email alerts | Python standard library |
| **email** | Built-in | Email formatting | Python standard library |
| **requests** | ≥2.28 | Telegram Bot API | HTTP requests |
| **python-telegram-bot** | Optional | Higher-level Telegram | Wrapper around Telegram API |

### OS-Level Enforcement
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **subprocess** | Built-in | Execute system commands | Run iptables from Python |
| **iptables** | System | Firewall rules | Linux kernel packet filtering |
| **netfilter** | System | Kernel framework | Underlying Linux firewall |

### Advanced ML (Nice-to-have)
| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| **TensorFlow/Keras** | ≥2.10 | Deep learning (LSTM anomaly detection) | Sequence modeling, temporal patterns |
| **PyTorch** | ≥1.10 | Alternative deep learning | More flexible, research-friendly |
| **statsmodels** | Optional | Time-series analysis | Statistical anomaly detection |

---

## 📦 Complete Dependencies Summary

### **Tier 1 Only** (Minimal Setup)
```
scapy>=2.5.0
pydantic>=2.0
sqlalchemy>=2.0
click>=8.0
```

### **Tier 1 + Tier 2** (Full Production)
```
# Tier 1
scapy>=2.5.0
pydantic>=2.0
sqlalchemy>=2.0
click>=8.0

# Tier 2 - ML & Backend
scikit-learn>=1.0
numpy>=1.20
pandas>=1.3
fastapi>=0.95
uvicorn>=0.20

# Tier 2 - Frontend (choose one)
# For React:
# (managed via Node.js/npm)

# For Streamlit:
streamlit>=1.20
plotly>=5.0

# Threat Intel
requests>=2.28
```

### **All Tiers** (Complete Stack)
```
# Core
scapy>=2.5.0
pydantic>=2.0
sqlalchemy>=2.0
click>=8.0

# ML & Analytics
scikit-learn>=1.0
numpy>=1.20
pandas>=1.3

# Backend API
fastapi>=0.95
uvicorn>=0.20

# Frontend (Streamlit)
streamlit>=1.20
plotly>=5.0

# Threat Intel
requests>=2.28
cachetools

# Alerting
python-telegram-bot  # Optional

# Testing
pytest>=7.0

# Development
black  # Code formatting
flake8  # Linting
mypy  # Type checking
```

---

## 🏗️ System Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Operating System (Linux)                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │             Kernel Networking (netfilter)              ││
│  │                   (iptables optional)                  ││
│  └────────────────────────────────────────────────────────┘│
│                           ▲                                  │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────────┐│
│  │      Python 3.9+ (Firewall Application)                 ││
│  │                                                         ││
│  │  ┌──────────────────────────────────────────────────┐ ││
│  │  │   Scapy / PyShark (Packet Capture)              │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   Connection Tracker (asyncio, collections)    │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   Rule Engine (Pydantic models, JSON config)   │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   IDS Engine (Signature-based detection)       │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   SQLite Database (SQLAlchemy ORM)             │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   FastAPI Backend + WebSockets                 │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   Scikit-learn (Isolation Forest)              │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                         │                              ││
│  │  ┌──────────────────────▼──────────────────────────┐ ││
│  │  │   Threat Intel API Client (requests)           │ ││
│  │  └──────────────────────────────────────────────────┘ ││
│  │                                                         ││
│  └─────────────────────┬──────────────────────────────────┘│
│                        │                                   │
│  ┌─────────────────────▼──────────────────────────────┐   │
│  │    Frontend (React/Streamlit)                      │   │
│  │    - Recharts / Plotly (Charts)                    │   │
│  │    - Tailwind CSS / Streamlit Styling             │   │
│  │    - WebSocket / HTTP Client                      │   │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Development Environment Stack

| Tool | Purpose |
|---|---|
| **Python 3.9+** | Primary language |
| **Git** | Version control |
| **VS Code / PyCharm** | IDE |
| **virtualenv / venv** | Python environment isolation |
| **pip** | Package manager |
| **Docker** | Optional containerization |
| **pytest** | Testing framework |
| **black** | Code formatting |
| **flake8** | Linting |
| **mypy** | Type checking |

---

## 📊 Technology Decision Matrix

| Layer | Technology | Alternative | Rationale |
|---|---|---|---|
| **Packet Capture** | Scapy | PyShark, Dpkt | Scapy is Python-native, most educational |
| **Rule Engine** | JSON + Pydantic | YAML, HCL | JSON is simpler, widely supported |
| **Database** | SQLite | PostgreSQL, MongoDB | SQLite is lightweight, perfect for single-machine |
| **ML Algorithm** | Isolation Forest | One-Class SVM, LOF | Fast, unsupervised, outlier-focused |
| **Dashboard Frontend** | Streamlit (MVP) / React (Production) | Vue, Angular, Dash | Streamlit = rapid; React = scalable |
| **API Framework** | FastAPI | Flask, Django | Async, modern, auto-docs |
| **Threat Intel** | AbuseIPDB | VirusTotal, Shodan | Free tier, IP reputation focus |

---

## 🚀 Tech Stack by Project Phase

### **Phase 1: Tier 1 (Weeks 1–5)**
```
Python 3.9+, Scapy, Pydantic, SQLite, Click, pytest
```

### **Phase 2: Tier 2 (Weeks 6–8)**
```
+ scikit-learn, pandas, numpy
+ FastAPI, Uvicorn
+ Streamlit (or React + Node.js)
+ Plotly/Recharts
+ requests (for APIs)
```

### **Phase 3: Tier 3 (Weeks 9–10)**
```
+ python-telegram-bot (optional)
+ subprocess (iptables)
+ TensorFlow/PyTorch (optional)
```

---

## 💾 Installation Commands

### **Quick Start (Tier 1)**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install scapy pydantic sqlalchemy click pytest
```

### **Full Stack (Tier 1 + 2)**
```bash
pip install \
  scapy pydantic sqlalchemy click pytest \
  scikit-learn pandas numpy \
  fastapi uvicorn \
  streamlit plotly \
  requests
```

### **With React Frontend (Alternative)**
```bash
# Python backend dependencies (same as above)
pip install scapy pydantic sqlalchemy fastapi uvicorn scikit-learn numpy pandas

# Node.js/React
cd frontend
npm install react react-router-dom axios recharts tailwindcss
```

---

## 🔐 Security Considerations

| Technology | Security Note |
|---|---|
| **Scapy** | Requires `sudo` for raw packet capture |
| **iptables** | Requires `sudo` for rule enforcement |
| **FastAPI** | Add CORS, authentication for production |
| **SQLite** | Encrypt database file for sensitive data |
| **Requests** | Validate HTTPS certificates for threat intel APIs |
| **Credentials** | Store API keys in `.env` file (use `python-dotenv`) |

---

## 📈 Performance Considerations

| Technology | Performance Note |
|---|---|
| **Scapy** | ~1K–10K packets/sec; PyShark for higher |
| **Isolation Forest** | <1ms inference per sample |
| **SQLite** | Good for <1M records; consider migration for larger datasets |
| **FastAPI** | Can handle 1000s of concurrent connections (async) |
| **Streamlit** | Adequate for single-user dashboard; React for multi-user |

---

## 📚 Learning Resources by Technology

| Technology | Resource |
|---|---|
| **Scapy** | https://scapy.readthedocs.io/ |
| **FastAPI** | https://fastapi.tiangolo.com/ |
| **Scikit-learn** | https://scikit-learn.org/ |
| **React** | https://react.dev/ |
| **Streamlit** | https://docs.streamlit.io/ |
| **SQLAlchemy** | https://docs.sqlalchemy.org/ |
| **Click** | https://click.palletsprojects.com/ |

---

**Version:** 1.0  
**Last Updated:** 2026-06-25