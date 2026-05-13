# Application Report: GuardianWeb / Personal-Firewall

## Executive Summary
GuardianWeb is a prototype cloud-connected security monitoring platform with three cooperating parts: a React dashboard, a FastAPI backend, and a Python endpoint agent that captures network traffic and reports telemetry. It demonstrates the full loop of registration, telemetry ingestion, threat reporting, and dashboard visibility, but it is still a demonstration-grade implementation rather than a production-ready security product.

## Application Purpose
The application is intended to act like a lightweight SOC-style monitoring system for endpoint activity.
- The agent runs on a user machine and watches traffic locally.
- The backend acts as the cloud control plane and telemetry collector.
- The dashboard shows agents, logs, and recent threats in near real time.

## Technology Stack
- Frontend: Vite, React 19, plain CSS.
- Backend: FastAPI, Pydantic, Uvicorn.
- Agent: Python, Requests, Scapy, threading, socket, platform.
- Supporting packages: the frontend uses ESLint and Vite tooling; the Python agent uses Scapy for packet capture and Requests for HTTP calls.

## Architecture
### Frontend
The frontend is a single-page dashboard that loads data from the backend and refreshes every 3 seconds. It shows the number of active agents, total logs, critical threats, recent threat detections, and the list of connected agents.

### Backend
The backend exposes a small REST API for agent registration, log ingestion, threat ingestion, and stats retrieval. It currently keeps all state in memory, which makes the service easy to run but not durable across restarts.

### Agent
The agent runs locally on a machine, gathers basic system information, registers itself once, then begins sniffing network packets with Scapy. It samples traffic, sends a subset of packet logs to the backend, and generates threat alerts when its simple detection logic triggers.

## Runtime Flow
1. The agent collects hostname, operating system information, and IP address.
2. The agent posts that information to the backend registration endpoint.
3. The backend creates a UUID-based `agent_id`, stores the agent in memory, and returns the ID.
4. The agent saves the ID to `agent_id.txt` and reuses it on later launches.
5. Packet sniffing begins in a background thread.
6. The agent samples traffic and sends selected log events to the backend.
7. When its heuristic rules trigger, it sends a threat event as well.
8. The frontend polls the backend and displays the latest state.

## API Surface
### `GET /`
Returns a simple status message confirming the API is running.

### `POST /api/agents/register`
Registers a new agent and returns a generated `agent_id` and status.

### `GET /api/agents`
Returns the current in-memory list of agents.

### `POST /api/logs`
Accepts a log entry for a registered agent and updates that agent’s `last_seen` field.

### `GET /api/logs?limit=100`
Returns the most recent log entries, capped by the requested limit.

### `POST /api/threats`
Accepts a threat record for a registered agent and updates `last_seen`.

### `GET /api/threats`
Returns all stored threats.

### `GET /api/stats`
Returns counts for active agents, total logs, total threats, and a filtered list of recent high-severity threats.

## Data Models
### Agent registration payload
- `hostname`
- `os_info`
- `ip_address`

### Log payload
- `agent_id`
- `timestamp`
- `source_ip`
- `dest_ip`
- `protocol`
- `port`
- `action`

### Threat payload
- `agent_id`
- `timestamp`
- `threat_type`
- `description`
- `severity`
- `source_ip`

## Frontend Behavior
The dashboard has a polished security-operations look with a dark gradient background, glass panels, and status badges. It fetches stats, agents, and the latest logs, then renders:
- a stats row for agent count, logs, threats, and critical alerts,
- a recent threat table,
- a connected agents table,
- a top navigation bar with a download-agent action.

The UI is visually stronger than the backend is functionally mature. It looks like a real monitoring product, but the data layer underneath is still very lightweight.

## Agent Behavior
The agent is the most operationally interesting part of the system, but also the most fragile.
- It uses `scapy.sniff()` to capture packets.
- It identifies TCP and UDP traffic and extracts destination ports.
- It simulates threat detection using random chance and a few sensitive ports such as 23, 445, and 3389.
- It posts sampled logs and threat alerts back to the backend.
- It stores the generated agent ID in a local text file.

This makes it suitable for a demo or proof of concept, but not yet for reliable endpoint protection.

## Strengths
- Clear separation between UI, backend, and agent responsibilities.
- Simple API design that is easy to understand and extend.
- Working end-to-end registration and telemetry flow.
- Good dashboard presentation for a prototype.
- Low barrier to running locally.

## Limitations
- No persistence layer: all backend data is lost on restart.
- No authentication or authorization.
- No encryption or secure transport configuration in the code shown.
- Hardcoded localhost backend URL in the frontend and agent.
- Threat detection is mostly randomized simulation instead of deterministic security logic.
- No multi-user or tenant isolation.
- No retry logic, backpressure handling, or offline buffering in the agent.
- No test suite is visible in the repository structure provided.

## Security and Operational Risks
- Any client that knows the API can potentially submit fake telemetry because the backend trusts `agent_id` alone.
- Cross-origin requests are permitted from any origin, which is unsafe for production.
- Packet sniffing usually requires elevated privileges and can fail or behave differently by platform.
- Polling every 3 seconds is simple but inefficient compared with push-based streaming or websocket updates.
- In-memory state is unsuitable for incident response, auditing, or historical analysis.

## Deployment Notes
The README describes a cloud deployment model:
- Deploy the backend to a public host.
- Change the agent’s backend URL to the hosted API.
- Change the frontend’s API URL to the hosted API.
- Deploy the frontend separately.

That deployment story is conceptually sound, but the current code hardcodes localhost values, so the application needs configuration work before it can be moved cleanly to a remote environment.

## Recommended Next Steps
- Replace in-memory collections with a persistent database and migrations.
- Add authentication for agents and dashboard users.
- Move backend URLs into environment variables.
- Replace simulated detection with a real rule engine or detection pipeline.
- Add server-side validation, rate limiting, and audit logging.
- Add retries and offline buffering in the agent.
- Add tests for registration, ingestion, and stats aggregation.

## Overall Assessment
This is a solid proof-of-concept for a distributed security monitoring platform. The architecture is sensible and the UI is presentable, but the current implementation is not production-ready because of missing persistence, authentication, secure transport, and real detection logic. With those gaps addressed, it could become a credible monitoring prototype.
