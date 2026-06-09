FROM python:3.12-slim

# Security: run as non-root
RUN groupadd -r sentinelx && useradd -r -g sentinelx sentinelx

WORKDIR /app

# Install shared library first (layer caching)
COPY backend/shared /tmp/shared
RUN pip install --no-cache-dir /tmp/shared

# Install service dependencies
COPY backend/services/telemetry/pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source
COPY backend/services/telemetry/app ./app

RUN chown -R sentinelx:sentinelx /app
USER sentinelx

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
