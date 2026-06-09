"""
Kafka producer and consumer helpers.
All services use these wrappers to publish/consume events.
"""
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from sentinelx_shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    """Return a singleton Kafka producer (start it if not running)."""
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            compression_type="gzip",
            acks="all",             # Wait for all ISR replicas — durability
            enable_idempotence=True,
            max_batch_size=65536,
            linger_ms=5,
        )
        await _producer.start()
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def publish(topic: str, payload: dict[str, Any], key: str | None = None) -> None:
    """Publish a JSON payload to the given Kafka topic."""
    producer = await get_producer()
    try:
        await producer.send_and_wait(
            topic,
            value=payload,
            key=key.encode("utf-8") if key else None,
        )
    except KafkaError as exc:
        logger.error("Failed to publish to Kafka topic=%s: %s", topic, exc)
        raise


def make_consumer(
    topics: list[str],
    group_id: str,
    auto_offset_reset: str = "earliest",
) -> AIOKafkaConsumer:
    """Create a Kafka consumer for the given topics and consumer group."""
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=False,   # Manual commit for at-least-once semantics
        max_poll_records=500,
    )


async def consume_forever(
    consumer: AIOKafkaConsumer,
    *,
    dlq_topic: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Async generator that yields messages from the consumer.
    On error, sends to DLQ if configured, then commits.
    """
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                yield msg.value
                await consumer.commit()
            except Exception as exc:
                logger.error("Error processing message: %s", exc, exc_info=True)
                if dlq_topic:
                    await publish(
                        dlq_topic,
                        {"original": msg.value, "error": str(exc)},
                    )
                await consumer.commit()  # Don't block on bad messages

    finally:
        await consumer.stop()


def get_kafka_consumer(
    topic: str,
    group_id: str,
    auto_offset_reset: str = "earliest",
) -> AIOKafkaConsumer:
    """Create a Kafka consumer for a single topic."""
    return make_consumer([topic], group_id, auto_offset_reset)

