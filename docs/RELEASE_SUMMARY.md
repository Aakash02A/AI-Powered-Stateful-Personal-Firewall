# Release Summary - v1.1.0

- **Version:** `1.1.0` (Release Candidate 1)
- **Build Date:** `2026-07-02`
- **Supported Operating Systems:** Windows 10, Windows 11 (64-bit)

## Release Artifacts
1. `AIFirewall_Setup_v1.1.0.exe` (The primary Inno Setup Installer)
2. `checksums.txt` (SHA-256 Hashes)

### SHA-256 Checksums (Internal Binaries)
* `firewall_service.exe`: `b37805ac73930326434d0ded2fb1e200d07569a7a33527ecc89b13a0467fb318`
* `ai_firewall_tray.exe`: `f1fc783bdbec65670012c63b69a4d81b3795ef743378f1a389293940e568ba70`
* `ai_firewall_dashboard.exe`: `2bddd37e9296357fa182879325db005acd3a3e890aa63524105f05ffb9e65971`

## Known Limitations
* The `packets.log` file can encounter a `WinError 32` lock condition during extreme synthetic packet generation (>100k flows/sec) across day-rotation boundaries.
* Duplicate TCP handshakes may appear in the UI if you bridge multiple virtual network adapters on the host machine.
* **SmartScreen Warnings:** The binaries are currently unsigned, meaning beta testers will encounter Microsoft SmartScreen warnings during installation.

## Final Recommendation
**🟠 Ready for Closed Beta**

The codebase and builds have passed all automated validation, security audits (`pip-audit`, `bandit`), and local runtime checks. Because this release fundamentally changes how the firewall intercepts traffic natively in Windows via the WFP and introduces a native Service architecture, it must undergo manual OS-level testing on diverse hardware configurations. 

Distributing this as a **Closed Beta** will allow testers to validate the installer, uninstaller, and driver stability in real-world Windows environments before an EV certificate is purchased for the final public release.
