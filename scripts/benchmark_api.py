import asyncio
import logging
import time

import aiohttp

from api.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Benchmark")

URLS = [
    "http://127.0.0.1:8000/api/v1/stats",
    "http://127.0.0.1:8000/api/v1/top-talkers",
    "http://127.0.0.1:8000/api/v1/alerts",
    "http://127.0.0.1:8000/api/v1/connections",
]
HEADERS = {"X-API-Key": settings.API_KEY}
CONCURRENCY = 50
TOTAL_REQUESTS = 1000


async def fetch(session, url, latencies):
    start = time.time()
    try:
        async with session.get(url, headers=HEADERS) as response:
            await response.read()
            latencies.append(time.time() - start)
    except Exception:
        pass


async def benchmark_http():
    latencies = []
    logger.info(
        f"Starting HTTP Benchmark: {TOTAL_REQUESTS} requests with {CONCURRENCY} concurrency"
    )

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            url = URLS[i % len(URLS)]
            tasks.append(fetch(session, url, latencies))

            if len(tasks) >= CONCURRENCY:
                await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    rps = TOTAL_REQUESTS / total_time

    if latencies:
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.5)] * 1000
        p95 = latencies[int(len(latencies) * 0.95)] * 1000
        p99 = latencies[int(len(latencies) * 0.99)] * 1000
        logger.info(
            f"HTTP Results: RPS: {rps:.2f} | P50: {p50:.2f}ms | P95: {p95:.2f}ms | P99: {p99:.2f}ms"
        )


if __name__ == "__main__":
    # We assume the API server is running externally via `python -m firewall.cli start-api`
    # Ensure it's running before executing this script!
    asyncio.run(benchmark_http())
