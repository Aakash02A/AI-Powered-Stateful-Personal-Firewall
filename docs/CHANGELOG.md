# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-02

### Added
- **Windows Desktop App**: Fully wrapped the React frontend in a `pywebview` window.
- **Windows Service**: `desktop/service.py` runs the FastAPI server and the core engine as a background `win32service`.
- **System Tray**: `desktop/tray.py` allows quick access to the dashboard and updates.
- **Auto Updater**: `desktop/updater.py` downloads and applies installer `.exe` silently.
- **WFP Integration**: Native `pydivert` parsing bypassing `scapy` for high-performance packet interception on Windows.
- **Installer**: `installer/setup.iss` Inno Setup configuration.
- **Build Scripts**: `scripts/build_desktop.py` for automated PyInstaller/Vite bundling.

### Changed
- Dashboard UI is now permanently styled as a dark-mode, high-tech FUI (Futuristic UI).
- Packet filtering falls back to `scapy` gracefully if `pydivert` or administrator privileges are missing.

## [1.0.0] - 2026-06-25
### Added
- Initial Release.
- Stateful packet inspection engine.
- Isolation Forest ML anomaly detection.
- Threat Intelligence integration.
- FastAPI backend and React frontend.
