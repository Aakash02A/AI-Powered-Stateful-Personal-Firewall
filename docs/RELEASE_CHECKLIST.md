# Release Checklist (v1.1.0)

## Build Verification
- [x] Backend FastAPI / PyDivert Engine successfully compiled via PyInstaller (`firewall_service.exe`).
- [x] React Frontend successfully transpiled and bundled via Vite.
- [x] Dashboard UI successfully compiled into WebView2 application (`ai_firewall_dashboard.exe`).
- [x] System Tray application successfully compiled (`ai_firewall_tray.exe`).

## Installer Verification
- [x] Inno Setup script (`setup.iss`) correctly packages all dependencies.
- [ ] Clean Installation verified on Windows 11 VM. *(Manual step required)*
- [ ] Shortcut creation verified.
- [ ] Windows Service registration and auto-start configuration verified.

## Upgrade & Uninstall Testing
- [ ] Upgrade installation over previous version correctly overwrites binaries without locking errors. *(Manual step required)*
- [ ] Uninstaller gracefully stops `AIFirewallService` before deleting files. *(Manual step required)*

## Security & Integrity
- [x] Windows Defender / SmartScreen scan: Verified locally. *(Note: Beta testers may still see SmartScreen warnings unless an EV Code Signing certificate is applied).*
- [ ] Digital Code-Signing Status: **Pending**. Current executables are unsigned. A valid Authenticode certificate must be obtained for final public non-beta release.
- [x] SHA-256 Checksums generated and attached to release package.

## Final Checks
- [x] Version strings updated across `VERSION`, `package.json`, and Python modules to `1.1.0`.
- [x] Documentation (`README.md`, `CHANGELOG.md`, `Troubleshooting_Guide.md`, `BETA_TESTING_GUIDE.md`) generated.
