# ADR 0004: Analytics Cache Strategy

**Status:** Accepted

## Context
Phase 2B implements a REST API and WebSocket layer. If these web endpoints continuously query SQLite for aggregated telemetry (Top Talkers, Threat Scores), the dashboard will experience high latency and risk locking the database.

## Decision
Introduce an in-memory `AnalyticsCache` warmed by a background `JobScheduler`.
- Aggregation queries are moved out of the API request path.
- The Scheduler periodically (e.g., every 5 seconds) queries SQLite, formats the analytics, and writes them into a thread-safe singleton dictionary.
- The API endpoints instantly retrieve the dictionary payload.

## Consequences
- **Positive:** Cache read latency drops to < 0.1ms, enabling real-time WebSocket broadcasting without database strain.
- **Negative:** Data displayed on dashboards is eventually consistent (lagging by the refresh interval).
