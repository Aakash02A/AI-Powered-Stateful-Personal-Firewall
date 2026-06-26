# Security Policy

## Supported Versions
Only the latest major version of the AI-Powered Stateful Personal Firewall receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Security is a core focus of this project. If you discover a security vulnerability, please **DO NOT** open a public issue.

Instead, please send an email to `security@example.com` (replace with actual contact) with the following details:
- A description of the vulnerability.
- Steps to reproduce the issue.
- Potential impact.

You should receive a response within 48 hours. If the vulnerability is confirmed, we will release a patch as quickly as possible and credit you in the release notes.

## Security Practices
- **Dependency Scanning:** We use `pip-audit` and Dependabot to continuously monitor for vulnerable dependencies.
- **Static Analysis:** We use `bandit` and GitHub CodeQL to detect insecure coding patterns.
- **Container Hardening:** Our Docker images run with the minimum required capabilities (`NET_ADMIN`) and avoid `--privileged` mode where possible.
- **SBOM:** We generate CycloneDX Software Bill of Materials on every CI build.
