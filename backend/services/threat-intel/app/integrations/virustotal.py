"""
VirusTotal integration — file hash and URL reputation lookups.
"""
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

VT_BASE_URL = "https://www.virustotal.com/api/v3"


class VirusTotalClient:
    def __init__(self, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=VT_BASE_URL,
            headers={"x-apikey": api_key},
            timeout=15,
        )

    async def lookup_hash(self, sha256: str) -> dict[str, Any]:
        """Look up a file hash. Returns VT analysis results."""
        try:
            response = await self._client.get(f"/files/{sha256}")
            if response.status_code == 404:
                return {"found": False, "sha256": sha256}
            response.raise_for_status()
            data = response.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            return {
                "found": True,
                "sha256": sha256,
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "undetected": stats.get("undetected", 0),
                "reputation_score": min(
                    round(stats.get("malicious", 0) / max(sum(stats.values()), 1) * 100, 1),
                    100,
                ),
            }
        except httpx.HTTPError as exc:
            logger.error("VirusTotal hash lookup failed: %s", exc)
            return {"found": False, "error": str(exc)}

    async def lookup_ip(self, ip: str) -> dict[str, Any]:
        """Look up an IP address reputation."""
        try:
            response = await self._client.get(f"/ip_addresses/{ip}")
            if response.status_code == 404:
                return {"found": False, "ip": ip}
            response.raise_for_status()
            data = response.json()
            attrs = data["data"]["attributes"]
            stats = attrs.get("last_analysis_stats", {})
            return {
                "found": True,
                "ip": ip,
                "country": attrs.get("country"),
                "asn": attrs.get("asn"),
                "malicious": stats.get("malicious", 0),
                "reputation": attrs.get("reputation", 0),
            }
        except httpx.HTTPError as exc:
            logger.error("VirusTotal IP lookup failed: %s", exc)
            return {"found": False, "error": str(exc)}

    async def close(self) -> None:
        await self._client.aclose()
