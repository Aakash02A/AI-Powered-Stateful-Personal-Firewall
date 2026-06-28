import os
import time
import requests
import ipaddress
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ThreatIntelClient:
    def __init__(self, cache_ttl_seconds: int = 86400):
        """
        Initializes the Threat Intelligence Client using AbuseIPDB.
        cache_ttl_seconds: How long to cache IP reputation (default: 24 hours)
        """
        load_dotenv()
        self.api_key = os.getenv("ABUSEIPDB_API_KEY")
        if not self.api_key:
            logger.warning("ABUSEIPDB_API_KEY not found in environment. Threat intelligence will run in degraded mode (always returning 0 score).")
            
        self.base_url = "https://api.abuseipdb.com/api/v2/check"
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds

    def _is_local_ip(self, ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved
        except ValueError:
            return True # If it's an invalid IP, treat it as local to skip external lookup

    def _clean_cache(self):
        """Removes expired entries from the cache."""
        now = time.time()
        expired = [ip for ip, data in self.cache.items() if now - data['timestamp'] > self.cache_ttl]
        for ip in expired:
            del self.cache[ip]

    def check_ip(self, ip: str) -> Dict[str, Any]:
        """
        Checks an IP address against AbuseIPDB.
        Returns a dictionary with 'abuseConfidenceScore', 'countryCode', etc.
        Returns a default safe response if the IP is local, API key is missing, or request fails.
        """
        # Default safe response
        default_response = {
            "ipAddress": ip,
            "abuseConfidenceScore": 0,
            "isPublic": False,
            "countryCode": None,
            "domain": None,
            "totalReports": 0
        }

        if self._is_local_ip(ip):
            return default_response

        # Check cache
        self._clean_cache()
        if ip in self.cache:
            return self.cache[ip]['data']

        if not self.api_key:
            return default_response

        # Query AbuseIPDB
        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }
        params = {
            'ipAddress': ip,
            'maxAgeInDays': 90
        }

        try:
            # We use a short timeout (2 seconds) so we don't stall packet processing
            response = requests.get(self.base_url, headers=headers, params=params, timeout=2.0)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                # Cache the successful response
                self.cache[ip] = {
                    'timestamp': time.time(),
                    'data': data
                }
                return data
            elif response.status_code == 429:
                logger.warning("AbuseIPDB rate limit exceeded.")
                # Cache a safe response for a short time to avoid hitting the API immediately again
                short_lived_data = dict(default_response)
                self.cache[ip] = {
                    'timestamp': time.time() - self.cache_ttl + 300, # expires in 5 minutes
                    'data': short_lived_data
                }
            else:
                logger.error(f"AbuseIPDB API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to AbuseIPDB: {e}")

        # If we failed, return the default (safe) response
        return default_response
