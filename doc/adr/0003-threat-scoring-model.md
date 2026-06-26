# ADR 0003: Threat Scoring Model

**Status:** Accepted

## Context
Rule matching and IDS heuristics generate discrete alerts. However, isolated alerts do not holistically reflect an IP's threat level. A dynamic threat scoring model is required to categorize external nodes continuously for Phase 2 API consumption.

## Decision
Implement an additive decay scoring model based on Severity, Frequency, and Recency.
- Base events (Blocks, Scans, Floods) contribute discrete scalar points.
- Repeated offenses from the same IP within a temporal window apply multiplier weights.
- A cron-scheduler decays the threat score periodically (e.g., deducting points every 24 inactive hours).
- Scores classify nodes into Safe, Suspicious, Dangerous, and Critical buckets.

## Consequences
- **Positive:** Enables automated dynamic blocking and allows ML pipelines to train on historical behavior reputation.
- **Negative:** Requires continuous state tracking and scheduled decay, introducing minor background processing overhead.
