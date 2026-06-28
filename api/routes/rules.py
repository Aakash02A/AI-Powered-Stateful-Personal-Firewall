from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid

import firewall.cli as fw_cli
from firewall.models import FirewallRule

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])

class RuleCreateUpdate(BaseModel):
    priority: int = 100
    enabled: bool = True
    protocol: str = "any"
    src_ip: str = "any"
    src_port: str = "any"
    dst_ip: str = "any"
    dst_port: str = "any"
    direction: str = "both"
    action: str = "allow"
    description: str = ""

def get_rule_engine():
    if hasattr(fw_cli, "fw_instance") and fw_cli.fw_instance is not None:
        return fw_cli.fw_instance.rule_engine
    else:
        # Fallback for standalone API testing - requires path to be valid
        from firewall.rule_engine import RuleEngine
        engine = RuleEngine()
        engine.load_rules_from_json("firewall/config/rules.json")
        return engine

@router.get("/")
def get_rules(engine = Depends(get_rule_engine)):
    return {"rules": [rule.__dict__ for rule in engine.rules]}

@router.post("/")
def create_rule(rule_data: RuleCreateUpdate, engine = Depends(get_rule_engine)):
    rule_id = f"rule_{str(uuid.uuid4())[:8]}"
    rule = FirewallRule(
        rule_id=rule_id,
        priority=rule_data.priority,
        enabled=rule_data.enabled,
        protocol=rule_data.protocol,
        src_ip=rule_data.src_ip,
        src_port=rule_data.src_port,
        dst_ip=rule_data.dst_ip,
        dst_port=rule_data.dst_port,
        direction=rule_data.direction,
        action=rule_data.action,
        description=rule_data.description
    )
    engine.add_rule(rule)
    return {"status": "success", "rule": rule.__dict__}

@router.delete("/{rule_id}")
def delete_rule(rule_id: str, engine = Depends(get_rule_engine)):
    # Check if rule exists first
    exists = any(r.rule_id == rule_id for r in engine.rules)
    if not exists:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    engine.delete_rule(rule_id)
    return {"status": "success", "message": f"Rule {rule_id} deleted"}

@router.put("/{rule_id}")
def update_rule(rule_id: str, rule_data: RuleCreateUpdate, engine = Depends(get_rule_engine)):
    exists = any(r.rule_id == rule_id for r in engine.rules)
    if not exists:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    engine.update_rule(
        rule_id, 
        priority=rule_data.priority,
        enabled=rule_data.enabled,
        protocol=rule_data.protocol,
        src_ip=rule_data.src_ip,
        src_port=rule_data.src_port,
        dst_ip=rule_data.dst_ip,
        dst_port=rule_data.dst_port,
        direction=rule_data.direction,
        action=rule_data.action,
        description=rule_data.description
    )
    
    # Return updated rule
    updated_rule = next(r for r in engine.rules if r.rule_id == rule_id)
    return {"status": "success", "rule": updated_rule.__dict__}
