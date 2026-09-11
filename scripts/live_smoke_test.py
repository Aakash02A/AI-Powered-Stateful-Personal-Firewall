"""Read-only smoke test for a running firewall API and dashboard."""

import argparse
import asyncio
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import websockets


def request_json(url, api_key=None):
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    request = Request(url, headers=headers)
    with urlopen(request, timeout=10) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def request_text(url):
    with urlopen(Request(url), timeout=10) as response:
        return response.status, response.read().decode("utf-8")


async def check_websocket(ws_url, api_key):
    websocket_url = ws_url.replace("http://", "ws://").replace("https://", "wss://")
    async with websockets.connect(f"{websocket_url.rstrip('/')}/stream?api_key={api_key}") as socket:
        await socket.send("ping")
        message = await asyncio.wait_for(socket.recv(), timeout=10)
        if message != "pong":
            raise AssertionError(f"unexpected WebSocket response: {message!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default=os.getenv("FIREWALL_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--ui", default=os.getenv("FIREWALL_UI_URL", "http://127.0.0.1:5173"))
    parser.add_argument("--api-key", default=os.getenv("API_KEY"))
    parser.add_argument("--skip-websocket", action="store_true")
    args = parser.parse_args()

    if not args.api_key:
        parser.error("provide --api-key or set API_KEY")

    api = args.api.rstrip("/")
    checks = [
        ("health", f"{api}/health/live", None),
        ("stats", f"{api}/api/v1/stats", args.api_key),
        ("alerts", f"{api}/api/v1/alerts?limit=1", args.api_key),
        ("rules", f"{api}/api/v1/rules/", args.api_key),
        ("analytics", f"{api}/api/v1/protocols", args.api_key),
        ("settings", f"{api}/api/v1/settings", args.api_key),
    ]

    failures = []
    for name, url, key in checks:
        try:
            status, payload = request_json(url, key)
            if status != 200:
                raise AssertionError(f"HTTP {status}")
            print(f"PASS {name}: HTTP {status}")
        except (AssertionError, HTTPError, URLError, ValueError) as error:
            failures.append(name)
            print(f"FAIL {name}: {error}")

    for page in ("index.html", "rules.html", "logs.html", "analytics.html", "settings.html"):
        try:
            status, body = request_text(f"{args.ui.rstrip('/')}/{page}")
            if status != 200 or "<html" not in body.lower():
                raise AssertionError(f"HTTP {status} or invalid HTML")
            print(f"PASS ui/{page}: HTTP {status}")
        except (AssertionError, HTTPError, URLError) as error:
            failures.append(f"ui/{page}")
            print(f"FAIL ui/{page}: {error}")

    if not args.skip_websocket:
        try:
            asyncio.run(check_websocket(f"{api}/api/v1/ws", args.api_key))
            print("PASS websocket: ping/pong")
        except Exception as error:  # noqa: BLE001 - report live connectivity failures
            failures.append("websocket")
            print(f"FAIL websocket: {error}")

    if failures:
        print(f"\nLive smoke test failed: {', '.join(failures)}")
        return 1
    print("\nLive smoke test passed. No data was created or modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())