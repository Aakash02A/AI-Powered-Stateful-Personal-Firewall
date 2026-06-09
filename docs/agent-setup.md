# SentinelX Agent — Installation and Setup

The SentinelX Endpoint Agent runs silently as a background service on your Windows, Linux, or macOS systems, capturing telemetry events and sending them to the central AI-SOC gateway.

---

## 1. Prerequisites

Before installing the agent, ensure you have:
* Python 3.12 or higher installed.
* An active account in the SentinelX Dashboard.
* The API Gateway address (default: `http://localhost:8080`).

---

## 2. Installation (Python Agent)

### Step 1: Clone or Copy Agent Folder
Copy the `agent/python` folder to the target device.

### Step 2: Create Virtual Environment and Install Dependencies
Navigate into the agent folder and run:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install package and dependencies
pip install -e .
```

### Step 3: Configure Agent Settings
Create a `.env` file in the agent root folder or define the environment variables:
```env
# Backend API Gateway endpoint
SENTINELX_BACKEND_URL=http://localhost:8080

# Agent Info
SENTINELX_HOSTNAME=MY-SECURE-ENDPOINT
SENTINELX_LOG_LEVEL=INFO

# Collection Intervals (Seconds)
SENTINELX_PROCESS_INTERVAL=5
SENTINELX_FILE_INTERVAL=10
SENTINELX_NETWORK_INTERVAL=5
SENTINELX_SYSTEM_INTERVAL=30
```

### Step 4: Run the Agent
Execute the agent service:
```bash
sentinelx-agent
```
On startup, the agent will:
1. Register itself with the Backend.
2. Persist its unique token locally at `.sentinelx_token`.
3. Start process, file, network, and system health collectors.
4. Establish a heartbeat loop to report system health metrics.

---

## 3. Windows-Specific Registry Collection
On Windows endpoints, the agent automatically starts the Windows Registry collector which monitors key persistence hives:
* `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
* `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce`
* `HKLM\System\CurrentControlSet\Services`

---

## 4. Troubleshooting

* **Verify Connection**: Ensure you can access the gateway via curl:
  ```bash
  curl http://localhost:8080/health
  ```
* **Logs**: Check the console or logs for registration or connection issues. If you get a token error, remove `.sentinelx_token` to force registration of a new device.
