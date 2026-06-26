# Deployment Guide

This document outlines how to deploy the AI-Powered Stateful Personal Firewall in a production environment. 

> [!WARNING]
> Packet capture requires elevated privileges. Ensure you run these services with the proper capabilities.

## 1. Docker Deployment

We provide a `Dockerfile` that packages the entire backend (Firewall Daemon + FastAPI).

### Build the Image
```bash
docker build -t ai-firewall .
```

### Run the Container
Because the firewall uses raw sockets to sniff packets, you **must** pass `--cap-add=NET_ADMIN`. If you are running on a Linux host and want it to monitor the host's actual network interface, use `--network host`.

```bash
docker run -d \
  --name firewall \
  --network host \
  --cap-add=NET_ADMIN \
  -e API_KEY=your_secure_api_key_here \
  -v $(pwd)/data/firewall.db:/app/data/firewall.db \
  ai-firewall
```

## 2. Enabling HTTPS (SSL/TLS)

For production, exposing the REST API and WebSocket over HTTPS/WSS is highly recommended. 
The easiest way is to use a reverse proxy like **Nginx** or **Caddy** in front of the container. 

Alternatively, if running locally without Docker, you can pass SSL certificates directly to Uvicorn via the CLI:
```bash
python -m firewall.cli start-api --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem
```

## 3. Database Resilience

The backend uses `SQLite` which performs well under moderate loads. 
To ensure data resilience without locking the database:
1. Run the included backup script on a cron job:
   ```bash
   python scripts/backup_db.py --dest /path/to/backup/dir
   ```
2. The script uses SQLite's safe backup API, so it won't corrupt the database while the DBWriter daemon is actively flushing.
