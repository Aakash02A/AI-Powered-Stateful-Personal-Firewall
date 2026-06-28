import pytest
from unittest.mock import patch, MagicMock
from firewall.threat_intel import ThreatIntelClient

@pytest.fixture
def ti_client():
    # Provide a dummy key for testing, bypassing dotenv
    with patch('os.getenv', return_value='dummy_key'):
        return ThreatIntelClient(cache_ttl_seconds=60)

def test_threat_intel_local_ip(ti_client):
    """Test that local IPs are whitelisted and don't trigger API calls."""
    response = ti_client.check_ip("192.168.1.100")
    assert response["abuseConfidenceScore"] == 0
    assert response["isPublic"] is False

def test_threat_intel_invalid_ip(ti_client):
    """Test that invalid IPs are gracefully handled as local/safe."""
    response = ti_client.check_ip("invalid_ip_string")
    assert response["abuseConfidenceScore"] == 0

@patch('requests.get')
def test_threat_intel_external_ip_success(mock_get, ti_client):
    """Test successful API lookup and caching."""
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "ipAddress": "8.8.8.8",
            "abuseConfidenceScore": 25,
            "countryCode": "US"
        }
    }
    mock_get.return_value = mock_response

    # First call - should hit the API
    response = ti_client.check_ip("8.8.8.8")
    assert response["abuseConfidenceScore"] == 25
    assert response["countryCode"] == "US"
    assert mock_get.call_count == 1

    # Second call - should hit the cache, NOT the API
    cached_response = ti_client.check_ip("8.8.8.8")
    assert cached_response["abuseConfidenceScore"] == 25
    assert mock_get.call_count == 1  # Still 1!

@patch('requests.get')
def test_threat_intel_rate_limit(mock_get, ti_client):
    """Test rate limit handling (429)."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    response = ti_client.check_ip("9.9.9.9")
    assert response["abuseConfidenceScore"] == 0 # Returns safe default
    
    # Second call should use short-lived cache, no extra API call
    response2 = ti_client.check_ip("9.9.9.9")
    assert response2["abuseConfidenceScore"] == 0
    assert mock_get.call_count == 1

def test_threat_intel_no_api_key():
    """Test behavior when API key is missing."""
    with patch('os.getenv', return_value=None):
        client = ThreatIntelClient()
        response = client.check_ip("8.8.8.8")
        assert response["abuseConfidenceScore"] == 0
