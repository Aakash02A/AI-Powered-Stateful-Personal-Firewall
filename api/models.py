from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

#
# Generic Responses
#
class GenericResponse(BaseModel):
    status: str = Field("success", json_schema_extra={"example": "success"})
    message: Optional[str] = Field(None, json_schema_extra={"example": "Operation completed successfully"})

#
# Models mirroring internal dataclasses but adapted for API responses
#

class AlertModel(BaseModel):
    id: Optional[int] = Field(None, description="Database ID if persisted")
    timestamp: datetime = Field(..., description="Time the alert was generated")
    alert_type: str = Field(..., json_schema_extra={"example": "port_scan"})
    severity: str = Field(..., json_schema_extra={"example": "high"})
    src_ip: str = Field(..., json_schema_extra={"example": "192.168.1.100"})
    dst_ip: str = Field(..., json_schema_extra={"example": "10.0.0.1"})
    description: str = Field(..., json_schema_extra={"example": "Detected port scan from 192.168.1.100"})
    action_taken: str = Field(..., json_schema_extra={"example": "log"})

    model_config = {"from_attributes": True}

class ConnectionModel(BaseModel):
    id: Optional[int] = Field(None)
    src_ip: str = Field(..., json_schema_extra={"example": "192.168.1.10"})
    src_port: int = Field(..., json_schema_extra={"example": 54321})
    dst_ip: str = Field(..., json_schema_extra={"example": "8.8.8.8"})
    dst_port: int = Field(..., json_schema_extra={"example": 53})
    protocol: str = Field(..., json_schema_extra={"example": "UDP"})
    state: str = Field(..., json_schema_extra={"example": "ESTABLISHED"})
    creation_time: datetime
    end_time: Optional[datetime] = None
    packets_in: int = Field(0)
    packets_out: int = Field(0)
    bytes_in: int = Field(0)
    bytes_out: int = Field(0)
    duration: float = Field(0.0)

    model_config = {"from_attributes": True}

#
# Endpoint Response Models
#

class StatsResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]

class TopTalkersResponse(BaseModel):
    status: str = "success"
    data: List[Dict[str, Any]]

class AlertsResponse(BaseModel):
    status: str = "success"
    data: List[AlertModel]

class ConnectionsResponse(BaseModel):
    status: str = "success"
    data: List[ConnectionModel]

class ProtocolStatsResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]

class WebSocketMessage(BaseModel):
    topic: str = Field(..., json_schema_extra={"example": "alert"})
    data: Dict[str, Any]
