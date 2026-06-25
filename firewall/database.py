from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List, Optional
from firewall.models import Packet, Connection, FirewallEvent, Alert

Base = declarative_base()

class PacketRecord(Base):
    __tablename__ = 'packets'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    src_ip = Column(String)
    src_port = Column(Integer)
    dst_ip = Column(String)
    dst_port = Column(Integer)
    protocol = Column(String)
    packet_size = Column(Integer)
    flags = Column(String)

class ConnectionRecord(Base):
    __tablename__ = 'connections'
    id = Column(Integer, primary_key=True)
    src_ip = Column(String)
    src_port = Column(Integer)
    dst_ip = Column(String)
    dst_port = Column(Integer)
    protocol = Column(String)
    state = Column(String)
    creation_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    packets_in = Column(Integer)
    packets_out = Column(Integer)
    bytes_in = Column(Integer)
    bytes_out = Column(Integer)

class FirewallEventRecord(Base):
    __tablename__ = 'firewall_events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    rule_id = Column(String)
    action = Column(String)
    src_ip = Column(String)
    src_port = Column(Integer)
    dst_ip = Column(String)
    dst_port = Column(Integer)
    protocol = Column(String)
    reason = Column(String)

class AlertRecord(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    alert_type = Column(String)
    severity = Column(String)
    src_ip = Column(String)
    dst_ip = Column(String)
    description = Column(String)
    action_taken = Column(String)

class FirewallDatabase:
    def __init__(self, db_path: str = "sqlite:///firewall.db"):
        self.engine = create_engine(db_path, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def log_packet(self, packet: Packet):
        session = self.Session()
        record = PacketRecord(
            timestamp=packet.timestamp,
            src_ip=packet.src_ip,
            src_port=packet.src_port,
            dst_ip=packet.dst_ip,
            dst_port=packet.dst_port,
            protocol=packet.protocol,
            packet_size=packet.size,
            flags=packet.flags
        )
        session.add(record)
        session.commit()
        session.close()

    def log_event(self, event: FirewallEvent):
        session = self.Session()
        record = FirewallEventRecord(
            timestamp=event.timestamp,
            rule_id=event.rule_id,
            action=event.action,
            src_ip=event.src_ip,
            src_port=event.src_port,
            dst_ip=event.dst_ip,
            dst_port=event.dst_port,
            protocol=event.protocol,
            reason=event.reason
        )
        session.add(record)
        session.commit()
        session.close()
        
    def log_alert(self, alert: Alert):
        session = self.Session()
        record = AlertRecord(
            timestamp=alert.timestamp,
            alert_type=alert.alert_type,
            severity=alert.severity,
            src_ip=alert.src_ip,
            dst_ip=alert.dst_ip,
            description=alert.description,
            action_taken=alert.action_taken
        )
        session.add(record)
        session.commit()
        session.close()
    
    def query_connections(self, limit: int = 100) -> List[dict]:
        session = self.Session()
        records = session.query(ConnectionRecord).order_by(ConnectionRecord.creation_time.desc()).limit(limit).all()
        result = [r.__dict__ for r in records]
        for r in result:
            r.pop('_sa_instance_state', None)
        session.close()
        return result
        
    def query_alerts(self, severity: str = None, limit: int = 100) -> List[dict]:
        session = self.Session()
        query = session.query(AlertRecord)
        if severity:
            query = query.filter(AlertRecord.severity == severity)
        records = query.order_by(AlertRecord.timestamp.desc()).limit(limit).all()
        result = [r.__dict__ for r in records]
        for r in result:
            r.pop('_sa_instance_state', None)
        session.close()
        return result
