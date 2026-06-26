FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# Needed for scapy if capturing raw packets in certain environments
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY firewall/ firewall/
COPY api/ api/
COPY analytics/ analytics/

# Expose API port
EXPOSE 8000

# To capture raw packets, the container MUST be run with NET_ADMIN capabilities:
# docker run --cap-add=NET_ADMIN -p 8000:8000 firewall-image
CMD ["python", "-m", "firewall.cli", "start-api"]
