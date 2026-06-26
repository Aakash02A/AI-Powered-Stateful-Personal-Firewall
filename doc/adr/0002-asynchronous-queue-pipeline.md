# ADR 0002: Asynchronous Queue Pipeline

**Status:** Accepted

## Context
The Phase 1 architecture invoked synchronous SQLite `session.commit()` calls within the primary sniffer thread. The Python GIL combined with disk I/O resulted in a maximum throughput of ~180 PPS, drastically failing to meet network scale requirements.

## Decision
Decouple the packet ingestion from database I/O using a Producer-Consumer pattern.
- A thread-safe `queue.Queue` absorbs processed flows and alerts instantly.
- A background `DBWriter` daemon thread aggregates queue items into micro-batches (e.g., 100 items).
- The `DBWriter` flushes batches using SQLAlchemy's `bulk_save_objects`.

## Consequences
- **Positive:** The system achieves over 1.4 million items/sec of queue ingestion throughput, functionally eliminating software bottlenecks for packet capturing.
- **Negative:** In the event of a sudden, ungraceful crash, items remaining in the in-memory queue that haven't been flushed could be lost. A graceful shutdown hook was implemented to flush the buffer on exit.
