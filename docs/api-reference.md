# SentinelX AI-SOC — API Reference

This document outlines the REST API endpoints provided by the SentinelX microservices. All services are exposed externally via the API Gateway on port `8080`.

---

## 1. Authentication Service (`auth-service` / Port `8000` / Route `/auth`, `/users`)

### Register Account
* **URL**: `/auth/register`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "email": "analyst@company.com",
    "password": "SecurePassword123!",
    "full_name": "Security Analyst"
  }
  ```
* **Success Response (201 Created)**:
  ```json
  {
    "id": "u-123-abc",
    "email": "analyst@company.com",
    "role": "user"
  }
  ```

### User Login (JWT Token Issuance)
* **URL**: `/auth/login`
* **Method**: `POST`
* **Content-Type**: `application/x-www-form-urlencoded`
* **Payload**:
  * `username`: `analyst@company.com`
  * `password`: `SecurePassword123!`
* **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer",
    "requires_mfa": false
  }
  ```

### Setup MFA
* **URL**: `/auth/mfa/setup`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Success Response (200 OK)**:
  ```json
  {
    "secret": "JBSWY3DPEHPK3PXP",
    "uri": "otpauth://totp/SentinelX:analyst@company.com?secret=JBSWY3DPEHPK3PXP&issuer=SentinelX"
  }
  ```

### Verify & Enable MFA
* **URL**: `/auth/mfa/verify`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "code": "123456"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "message": "MFA enabled successfully"
  }
  ```

---

## 2. Telemetry Ingestion Service (`telemetry-service` / Port `8001` / Route `/telemetry`, `/events`)

### Agent Heartbeat
* **URL**: `/telemetry/heartbeat`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "agent_token": "tok_1234abcd...",
    "hostname": "DESKTOP-WIN10",
    "agent_version": "0.1.0",
    "cpu_percent": 12.5,
    "ram_percent": 64.2,
    "disk_percent": 45.1
  }
  ```
* **Success Response (202 Accepted)**:
  ```json
  {
    "status": "accepted"
  }
  ```

### Ingest Telemetry Batch
* **URL**: `/telemetry/batch`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "agent_token": "tok_1234abcd...",
    "events": [
      {
        "event_type": "process_create",
        "occurred_at": "2026-06-08T12:00:00Z",
        "payload": {
          "process_name": "cmd.exe",
          "pid": 5824,
          "parent_pid": 1024,
          "command_line": "cmd.exe /c whoami",
          "executable": "C:\\Windows\\System32\\cmd.exe",
          "user": "SYSTEM"
        }
      }
    ]
  }
  ```
* **Success Response (202 Accepted)**:
  ```json
  {
    "accepted": 1,
    "rejected": 0
  }
  ```

---

## 3. Alert & Correlation Engine (`alert-engine` / Port `8005` / Route `/alerts`, `/incidents`)

### List Security Alerts
* **URL**: `/alerts`
* **Method**: `GET`
* **Params**: `status` (optional), `severity` (optional), `endpoint_id` (optional)
* **Success Response (200 OK)**:
  ```json
  [
    {
      "id": "al_9876",
      "endpoint_id": "ep_123",
      "title": "Suspicious PowerShell Execution",
      "severity": "high",
      "status": "new",
      "threat_score": 78.5,
      "triggered_at": "2026-06-08T12:05:00Z"
    }
  ]
  ```

### Update Alert Status
* **URL**: `/alerts/{alert_id}`
* **Method**: `PATCH`
* **Payload**:
  ```json
  {
    "status": "investigating",
    "assigned_to": "u-123-abc"
  }
  ```

---

## 4. Threat Intelligence Service (`threat-intel` / Port `8004` / Route `/threatintel`)

### Lookup IP/Domain/Hash Reputation
* **URL**: `/threatintel/lookup/{ioc_value}`
* **Method**: `GET`
* **Success Response (200 OK)**:
  ```json
  {
    "found": true,
    "source": "local_db",
    "ioc_value": "185.190.140.23",
    "ioc_type": "ip",
    "reputation_score": 85.0,
    "confidence": 90.0,
    "description": "Known C2 Beacon IP / Cobalt Strike",
    "tags": "c2,cobalt_strike"
  }
  ```

---

## 5. Automated Response Engine (`response-engine` / Port `8006` / Route `/response`)

### Execute Response Action
* **URL**: `/response/execute`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "endpoint_id": "ep_123",
    "action": "isolate_host",
    "reason": "Compromised host with Cobalt Strike C2 beacon",
    "incident_id": "inc_442"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "action": "isolate_host",
    "endpoint_id": "ep_123",
    "message": "Host isolation dispatched to ep_123"
  }
  ```
