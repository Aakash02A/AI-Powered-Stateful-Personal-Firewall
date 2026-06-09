# SentinelX AI-SOC — Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Endpoint Layer                                      │
│  Windows │ Linux │ macOS agents                                       │
│  Process Monitor │ File Monitor │ Network Monitor │ Registry Monitor  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS + Bearer token
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  API Gateway (NGINX / Kong)                           │
│  Rate limiting │ TLS termination │ Routing │ Auth header forwarding   │
└────────┬────────────────────┬──────────────────────────────────────┘
         │                    │
    ┌────▼─────┐         ┌────▼───────────────────────────────────────┐
    │   Auth   │         │            Backend Microservices            │
    │ Service  │         │                                             │
    │ :8000    │         │  Telemetry :8001                            │
    └────┬─────┘         │  Rule Engine :8002                          │
         │ JWT           │  ML Engine :8003                            │
         │               │  Threat Intel :8004                         │
         │               │  Alert Engine :8005                         │
         │               │  Response Engine :8006                      │
         │               │  AI Analyst :8007                           │
         │               └────────────────────┬────────────────────────┘
         │                                    │
         │               ┌────────────────────▼────────────────────────┐
         │               │              Apache Kafka                    │
         │               │  Topics:                                     │
         │               │  sentinelx.telemetry (raw events)           │
         │               │  sentinelx.events (normalized ECS events)   │
         │               │  sentinelx.alerts (detection results)       │
         │               │  sentinelx.response (response commands)     │
         │               │  sentinelx.dlq (dead letters)               │
         │               └────────────────────┬────────────────────────┘
         │                                    │
         │               ┌────────────────────▼────────────────────────┐
         │               │              Storage Layer                   │
         │               │  MySQL       — Users, Endpoints, Alerts      │
         │               │  OpenSearch  — Log search, Threat hunting    │
         │               │  Redis       — Caching, Rate limits          │
         │               │  AWS S3      — ML models, Reports            │
         │               └─────────────────────────────────────────────┘
```

## Event Flow

```
Agent
  │
  ├── POST /telemetry/heartbeat  →  Update endpoint last_seen
  │
  └── POST /telemetry/batch  →  Telemetry Service
          │
          ├── Validate agent token (Redis cache → DB)
          ├── Normalize event to ECS format
          └── Publish to kafka:sentinelx.events
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    Rule Engine  ML Engine  Threat Intel
    (Kafka       (Kafka      (IOC lookup
    consumer)    consumer)   enrichment)
         │          │          │
         └──────────┴──────────┘
                    │
              kafka:sentinelx.alerts
                    │
              Alert Engine
              (Correlation + Scoring)
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
     Create Alert         Create Incident
          │                    │
          ▼                    ▼
     AI Analyst ─────────── Dashboard
     (LangGraph)            (WebSocket)
          │
     Response Engine
     (Automated actions)
```

## Threat Score Formula

```
ThreatScore = (rule_score × 0.35)
            + (ml_score × 0.30)
            + (threat_intel_score × 0.25)
            + (behavior_score × 0.10)

Clamped to [0, 100]

Risk Levels:
  0-20  → Low
  21-50 → Medium
  51-80 → High
  81-100 → Critical
```

## Database Schema

### MySQL Tables

| Table | Purpose |
|-------|---------|
| `users` | Authentication, RBAC roles |
| `endpoints` | Registered agents, health status |
| `events` | Normalized security events |
| `alerts` | Generated security alerts |
| `incidents` | Incident cases grouping alerts |
| `threat_intel` | IOC database |

### OpenSearch Indices

| Index | Purpose |
|-------|---------|
| `sentinelx-events-*` | Searchable event history (SIEM) |
| `sentinelx-alerts-*` | Alert index for correlation |
| `sentinelx-audit-*` | Audit trail for compliance |

## Security Controls

| Control | Implementation |
|---------|---------------|
| Transport encryption | TLS 1.3 everywhere |
| Authentication | JWT (HS256) + TOTP MFA |
| Authorization | RBAC (User/Analyst/Admin/SuperAdmin) |
| Agent auth | Bearer token (per-device) |
| Secrets | HashiCorp Vault (prod) / .env (dev) |
| Audit logging | All security actions → OpenSearch |
| Container security | Non-root, read-only FS, no capabilities |
| API security | Rate limiting, CORS, input validation |
| SAST | Semgrep in CI |
| Secret scanning | Gitleaks in CI |
| Container scanning | Trivy in CI |
