# SentinelX AI-SOC

> **Cloud-native Security Operations Center (SOC) Monitoring and Endpoint Protection Platform**

[![CI](https://github.com/Aakash02A/Personal-Firewall/actions/workflows/ci.yml/badge.svg)](https://github.com/Aakash02A/Personal-Firewall/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)

---

## Overview

SentinelX AI-SOC is an enterprise-grade, cloud-native security platform that combines:

| Capability | Technology |
|-----------|-----------|
| **SIEM** | OpenSearch + OpenSearch Dashboards |
| **EDR** | Python/Rust endpoint agent |
| **Rule-Based Detection** | Sigma + YARA + IOC matching |
| **ML Detection** | Isolation Forest + XGBoost |
| **Threat Intelligence** | VirusTotal, AbuseIPDB, AlienVault OTX, MISP, NVD |
| **AI SOC Analyst** | LangGraph + GPT-4o |
| **Automated Response** | Kill process, quarantine, block IP, isolate host |
| **Observability** | Prometheus + Grafana + OpenTelemetry |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Endpoint Agents (Python / Rust)                  │
│  Process Monitor │ File Monitor │ Network Monitor │ Registry Monitor   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTPS + JWT
                                ▼
                    ┌─────────────────────┐
                    │    API Gateway       │   (NGINX / Kong)
                    │    Port 8080         │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────────────────┐
              ▼            ▼                        ▼
        ┌──────────┐ ┌──────────┐           ┌──────────────┐
        │  Auth    │ │Telemetry │           │  Other APIs  │
        │ :8000    │ │  :8001   │           │  :8002-8007  │
        └──────────┘ └────┬─────┘           └──────────────┘
                          │ Kafka
              ┌───────────┼──────────────────────┐
              ▼           ▼                      ▼
        ┌──────────┐ ┌──────────┐        ┌──────────────┐
        │  Rule    │ │    ML    │        │  Threat Intel│
        │  Engine  │ │  Engine  │        │   Service    │
        └─────┬────┘ └────┬─────┘        └──────┬───────┘
              └───────────┴──────────────────────┘
                          │ Kafka (alerts topic)
                          ▼
                  ┌───────────────┐
                  │ Alert Engine  │ ← Correlation + Scoring
                  └───────┬───────┘
                          │
              ┌───────────┼─────────────────┐
              ▼           ▼                 ▼
        ┌──────────┐ ┌──────────┐   ┌─────────────┐
        │Response  │ │  AI SOC  │   │  Dashboard  │
        │  Engine  │ │ Analyst  │   │  (Next.js)  │
        └──────────┘ └──────────┘   └─────────────┘
```

---

## Project Structure

```
sentinelx/
├── .github/workflows/          # GitHub Actions CI/CD
├── backend/
│   ├── shared/                 # Shared Python library (DB, Kafka, JWT, models)
│   └── services/
│       ├── auth/               # JWT + OAuth2 + MFA + RBAC
│       ├── telemetry/          # Agent event ingestion → Kafka
│       ├── rule-engine/        # Sigma + YARA + IOC detection
│       ├── ml-engine/          # Isolation Forest + XGBoost
│       ├── threat-intel/       # VirusTotal, AbuseIPDB, OTX, MISP, NVD
│       ├── alert-engine/       # Correlation + scoring + incidents
│       ├── response-engine/    # Automated response actions
│       └── ai-analyst/         # LangGraph SOC analyst
├── frontend/                   # Next.js 15 + TypeScript + Tailwind + ShadCN
├── agent/
│   ├── python/                 # Python MVP agent (psutil + watchdog)
│   └── rust/                   # Rust agent (Phase 2)
├── infra/
│   ├── terraform/              # AWS infrastructure (VPC, EKS, RDS, etc.)
│   └── k8s/                    # Kubernetes manifests
├── ml/                         # Notebooks, datasets, model artifacts
├── docs/                       # Architecture + API docs
├── docker-compose.yml          # Full local dev stack
├── Makefile                    # Developer commands
└── .env.example                # All environment variables documented
```

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### 1. Clone & Configure
```bash
git clone https://github.com/Aakash02A/Personal-Firewall.git
cd Personal-Firewall
make setup          # copies .env.example → .env
# Edit .env with your API keys
```

### 2. Start the Full Stack
```bash
make dev
# Dashboard: http://localhost:3000
# API Gateway: http://localhost:8080
# Kafka UI: http://localhost:8090
# Grafana: http://localhost:3001 (admin/admin)
```

### 3. Install & Run the Agent
```bash
cd agent/python
pip install -e .
sentinelx-agent
```

---

## Microservices

| Service | Port | Description |
|---------|------|-------------|
| Auth | 8000 | JWT, OAuth2, MFA, RBAC |
| Telemetry | 8001 | Agent event ingestion |
| Rule Engine | 8002 | Sigma/YARA/IOC detection |
| ML Engine | 8003 | Anomaly + malware detection |
| Threat Intel | 8004 | IOC enrichment feeds |
| Alert Engine | 8005 | Correlation + scoring |
| Response Engine | 8006 | Automated response |
| AI Analyst | 8007 | LangGraph SOC agent |
| Frontend | 3000 | Next.js dashboard |
| Gateway | 8080 | NGINX API gateway |

---

## Detection Capabilities

### Rule-Based (Sigma + YARA + IOC)
- PowerShell abuse (T1059.001)
- LOLBin execution
- Ransomware extension patterns (T1486)
- Registry persistence (T1547)
- Credential dumping (T1003)
- C2 beaconing detection

### Machine Learning
- Anomaly detection (Isolation Forest)
- Malware classification (XGBoost)
- Combined threat score (0–100)

### Threat Intelligence
- IP, domain, hash, URL IOC matching
- CVE vulnerability correlation
- Real-time feed updates

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0 |
| Database | MySQL 8.3 (primary), OpenSearch (SIEM) |
| Cache | Redis 7.2 |
| Streaming | Apache Kafka |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, ShadCN UI |
| AI | LangGraph, LangChain, GPT-4o |
| ML | scikit-learn, XGBoost, LightGBM |
| Agent | Python (psutil, watchdog) / Rust (planned) |
| Infra | Kubernetes, Terraform, AWS EKS |
| Observability | Prometheus, Grafana, OpenTelemetry, Jaeger |
| Security | JWT, MFA (TOTP), RBAC, TLS 1.3, Vault |
| DevSecOps | GitHub Actions, Trivy, Semgrep, Gitleaks |

---

## Development

```bash
make test              # Run all service tests
make lint              # Lint all Python services
make format            # Auto-format all Python
make test-service s=auth  # Test a single service
make logs              # Tail all container logs
make migrate           # Run DB migrations
```

---

## Roadmap

- **Phase 1 (MVP)** — Auth, Agent, Telemetry, Rule Engine, Dashboard, Alerting
- **Phase 2** — Threat Intelligence, ML Detection, Automated Response
- **Phase 3** — AI SOC Analyst, Threat Hunting, Incident Response
- **Phase 4** — Multi-tenant SaaS, SOAR, Enterprise Compliance

---

## License

MIT License — see [LICENSE](LICENSE)
