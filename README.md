# GuardianWeb

A cloud-based SOC monitoring and endpoint protection platform.

## Architecture

This project has been restructured into a professional Agent-Server architecture so that it can be hosted online and used by many users to test and monitor their systems.

1. **Frontend (`/frontend`)**: A React (Vite) web dashboard where users can view their connected endpoints and monitor threat detections in real-time.
2. **Backend (`/backend`)**: A FastAPI cloud server that acts as the control plane. It receives telemetry from agents, stores logs, and serves data to the frontend.
3. **Agent (`/agent`)**: A standalone Python application that users download and run on their local systems. It monitors network traffic, detects threats, and sends data back to the cloud backend.

## Quick Start

### 1. Start the Backend API
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

### 3. Run the Local Agent
(In a new terminal window)
```bash
cd agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```
*Note: Because the agent uses `scapy` to capture raw network packets, you may need to run it with Administrator privileges.*

## Deployment
To host this online:
1. Deploy the `backend` to a service like AWS, Heroku, or Render.
2. Update the `API_BASE_URL` in `agent/agent.py` to point to your hosted backend.
3. Update the `API_URL` in `frontend/src/App.jsx` to point to your hosted backend.
4. Deploy the `frontend` to a service like Vercel or Netlify.
5. Provide a download link on your frontend for users to download the `agent.py` script.
