# Troubleshooting Guide

This guide helps you resolve common issues with the AI-Powered Personal Firewall.

## 1. The Firewall Service Doesn't Start
**Symptoms:** You see a red "Disconnected" indicator on the dashboard, or traffic is not populating.
**Resolution:**
1. Press `Win + R`, type `services.msc`, and press Enter.
2. Locate **AI-Powered Stateful Personal Firewall** in the list.
3. If the status is empty, right-click and select **Start**.
4. If it fails to start, check the logs located at: `C:\ProgramData\AIFirewall\service.log`.

## 2. "Permission Denied" Errors for WFP
**Symptoms:** The firewall falls back to `scapy` mode or drops packets very slowly.
**Resolution:** The Windows Filtering Platform driver requires Administrator access. Ensure you installed the application using an Administrator account. The Windows Service naturally runs as `SYSTEM`, which inherently possesses these privileges.

## 3. The Dashboard Shows a Blank White Screen
**Symptoms:** The UI window opens but nothing loads.
**Resolution:** 
The UI requires the `frontend/dist` static files to exist in the installation directory. If you are a developer running from source, ensure you ran `npm run build` in the `frontend` directory. If you installed via the `.exe`, try reinstalling to repair missing files.

## 4. High CPU Usage
**Symptoms:** `firewall_service.exe` is consuming >20% CPU.
**Resolution:**
- If you are downloading large files (e.g., Steam games, torrents), the ML Anomaly Detection engine may be working overtime calculating entropy across millions of packets.
- You can temporarily pause the firewall via the System Tray icon if you require absolute peak performance during massive downloads.

## 5. False Positives (Legitimate Apps Blocked)
**Symptoms:** A game or application you trust loses connection.
**Resolution:**
1. Open the Dashboard.
2. Navigate to the **Alerts** tab.
3. Find the alert blocking the application's Port or IP.
4. Click **Ignore / Whitelist** to allow the traffic in the future.
