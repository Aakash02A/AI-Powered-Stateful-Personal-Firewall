from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime

app = FastAPI(title="GuardianWeb Cloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database for demonstration (In production, use PostgreSQL)
agents = {}
logs = []
threats = []

class AgentRegister(BaseModel):
    hostname: str
    os_info: str
    ip_address: str

class AgentResponse(BaseModel):
    agent_id: str
    status: str

class LogEntry(BaseModel):
    agent_id: str
    timestamp: str
    source_ip: str
    dest_ip: str
    protocol: str
    port: int
    action: str

class ThreatEntry(BaseModel):
    agent_id: str
    timestamp: str
    threat_type: str
    description: str
    severity: str
    source_ip: str

@app.get("/")
def read_root():
    return {"status": "GuardianWeb API is running"}

@app.post("/api/agents/register", response_model=AgentResponse)
def register_agent(agent: AgentRegister):
    import uuid
    agent_id = str(uuid.uuid4())
    agents[agent_id] = {
        "id": agent_id,
        "hostname": agent.hostname,
        "os_info": agent.os_info,
        "ip_address": agent.ip_address,
        "last_seen": datetime.datetime.now().isoformat(),
        "status": "active"
    }
    return {"agent_id": agent_id, "status": "registered"}

@app.get("/api/agents")
def get_agents():
    return list(agents.values())

@app.post("/api/logs")
def ingest_log(log: LogEntry):
    if log.agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    logs.append(log.dict())
    agents[log.agent_id]["last_seen"] = datetime.datetime.now().isoformat()
    return {"status": "success"}

@app.get("/api/logs")
def get_logs(limit: int = 100):
    return logs[-limit:]

@app.post("/api/threats")
def ingest_threat(threat: ThreatEntry):
    if threat.agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    threats.append(threat.dict())
    agents[threat.agent_id]["last_seen"] = datetime.datetime.now().isoformat()
    return {"status": "success"}

@app.get("/api/threats")
def get_threats():
    return threats

@app.get("/api/stats")
def get_stats():
    return {
        "active_agents": len(agents),
        "total_logs": len(logs),
        "total_threats": len(threats),
        "recent_threats": [t for t in threats if t["severity"] in ["high", "critical"]]
    }
