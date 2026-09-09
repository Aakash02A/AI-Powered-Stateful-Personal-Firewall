# ADR 0001: Flow-Based Architecture

**Status:** Accepted

## Context
Phase 1 captured network telemetry at the packet level, meaning every single packet was uniquely logged to the database. At production traffic speeds, logging per-packet immediately bottlenecks the system. To support ML Anomaly Detection (Phase 2C), traffic needs to be analyzed in broader contexts rather than fragmented packets.

## Decision
We transitioned from a Packet-centric architecture to a Canonical Flow-centric architecture.
- Connections are identified by a deterministic 5-tuple: `(min_ip, min_port, max_ip, max_port, protocol)`.
- This ensures bidirectional tracking (A->B and B->A resolve to the exact same flow).
- The flow stores duration, byte/packet volumes, and states in memory before persisting as a unified record.

## Consequences
- **Positive:** Substantial reduction in database volume (>90% reduction). Flow statistics natively prepare the data for Pandas feature generation.
- **Negative:** Flows must be tracked in an in-memory dictionary, slightly increasing immediate memory footprints during high concurrent connections.
