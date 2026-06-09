"""Audit log middleware — persists all security-relevant actions."""
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def audit(
    db: AsyncSession,
    *,
    actor_id: str,
    action: str,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Write a structured audit log entry.
    In production this would write to a dedicated audit_logs table
    and/or stream to OpenSearch for SIEM correlation.
    """
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor_id": actor_id,
        "action": action,
        "resource_id": resource_id,
        "metadata": metadata or {},
    }
    logger.info("AUDIT | %s", entry)
    # TODO: Insert into audit_logs table and publish to Kafka for SIEM ingestion
