"""
SentinelX Agent — main entry point.
Starts all collectors, runs detection, and ships events to the cloud backend.
"""
import asyncio
import logging
import signal
import sys

from sentinelx_agent.config import AgentConfig
from sentinelx_agent.registration import AgentRegistrar
from sentinelx_agent.collectors.process_collector import ProcessCollector
from sentinelx_agent.collectors.file_collector import FileCollector
from sentinelx_agent.collectors.network_collector import NetworkCollector
from sentinelx_agent.collectors.system_collector import SystemCollector
from sentinelx_agent.transport.http_client import TelemetryClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("sentinelx.agent")


async def run_agent(config: AgentConfig) -> None:
    """Main agent coroutine — orchestrates all subsystems."""
    logger.info("=" * 60)
    logger.info("  SentinelX Endpoint Agent v%s", config.agent_version)
    logger.info("=" * 60)

    # ── Registration ─────────────────────────────────────────
    registrar = AgentRegistrar(config)
    agent_token = await registrar.register_or_restore()
    logger.info("Agent token acquired: %s…", agent_token[:8])

    # ── Transport ────────────────────────────────────────────
    client = TelemetryClient(config, agent_token=agent_token)

    # ── Collectors ───────────────────────────────────────────
    collectors = [
        ProcessCollector(config, client),
        FileCollector(config, client),
        NetworkCollector(config, client),
        SystemCollector(config, client),
    ]

    # Add registry collector on Windows
    if sys.platform == "win32":
        from sentinelx_agent.collectors.registry_collector import RegistryCollector
        collectors.append(RegistryCollector(config, client))

    logger.info("Starting %d collectors...", len(collectors))

    # Run all collectors concurrently
    tasks = [asyncio.create_task(c.start()) for c in collectors]

    # Heartbeat loop
    heartbeat_task = asyncio.create_task(client.heartbeat_loop())
    tasks.append(heartbeat_task)

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Agent shutting down gracefully...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await client.flush()


def main() -> None:
    config = AgentConfig.load()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    main_task: asyncio.Task | None = None

    def _shutdown(sig: signal.Signals) -> None:
        logger.info("Received signal %s — initiating shutdown", sig.name)
        if main_task:
            main_task.cancel()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _shutdown, sig)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler for all signals
            pass

    try:
        main_task = loop.create_task(run_agent(config))
        loop.run_until_complete(main_task)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped by user")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
