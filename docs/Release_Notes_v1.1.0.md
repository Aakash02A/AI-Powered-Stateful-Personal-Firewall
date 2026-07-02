# Release Notes - v1.1.0 (Release Candidate 1)

**Release Date:** 2026-07-02

Welcome to **v1.1.0** of the AI-Powered Stateful Personal Firewall. This release marks our transition from a developer-focused CLI tool into a fully consumer-ready Windows Desktop Application!

## 🚀 Major Features

* **Native Windows Background Service:** The core firewall engine and API now install and run natively as a Windows Service (`AIFirewallService`), providing persistent security running under the `SYSTEM` account automatically upon boot.
* **System Tray & Desktop Dashboard:** You no longer need to run `npm start` or navigate to a browser. The application now runs quietly in your System Tray and spawns a native Windows UI (powered by WebView2) when you open the Dashboard.
* **Windows Filtering Platform (WFP) Integration:** We have bypassed the slow `scapy` packet parsing loop on Windows. The firewall now seamlessly intercepts packets via the highly-performant WFP driver (`pydivert`), resulting in near-zero network latency and massive CPU efficiency gains.
* **Silent Auto-Updater:** The System Tray app automatically detects new releases on GitHub and runs the update process silently in the background, minimizing interruptions.
* **Single-Click Installer:** A completely automated `AIFirewall_Setup_v1.1.0.exe` installer is now provided, configuring services, registry keys, and shortcuts for you.

## 🛡️ Security & Stability
- Zero known CVEs in our dependency tree (verified via `pip-audit`).
- Passed comprehensive SAST scans via `bandit` with no critical privilege escalation or RCE vulnerabilities.
- Safe service uninstallation prevents driver locks during upgrades.

## 📝 Known Issues
- If you are running multiple Virtual Machines (e.g., WSL2 or VirtualBox) bridging the same network adapter, the WFP driver may occasionally capture duplicate TCP handshakes, leading to slightly inflated packet counts on the Dashboard.

## 🔧 Installation
Please see our **[Installation Guide](Installation_Guide.md)** for instructions on how to install, upgrade, or uninstall the firewall.
