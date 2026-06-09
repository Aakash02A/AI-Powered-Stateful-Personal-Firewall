FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY sentinelx_agent ./sentinelx_agent

# Run the agent entry point
CMD ["sentinelx-agent"]
