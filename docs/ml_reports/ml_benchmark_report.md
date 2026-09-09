# ML Benchmark Report

## Hardware / Environment Snapshot
- OS: Windows x64
- Memory Tracking via `psutil`
- Test Payload: `10,000` synthesized stateful flows

## 1. Model Initialization Profile
- **Loading Latency**: `0.9319 seconds`
- **Memory Footprint**: `77.29 MB` (Includes `IsolationForest`, `StandardScaler`, and configuration overhead). This is well within acceptable limits for a background firewall agent.

## 2. Inference Throughput
Testing conducted sequentially vs batch mode to highlight the efficiency gap. 
- **Single Inference**: `79.30 flows/sec`
  *In single inference, the firewall processes each packet/connection asynchronously via individual API calls. This is relatively slow because of the overhead of Python data structure manipulation and numpy conversion per request.*
- **Batch Inference**: `153,761.98 flows/sec`
  *Batch inference scales perfectly. The system can process hundreds of thousands of flows sub-second.*
- **Speedup Ratio**: `1939.08x`

## 3. Conclusions & Recommendations
The system runs highly efficiently in batch mode. However, for real-time live traffic, packets arrive individually. If performance becomes a bottleneck for single inference (`~80 flows/sec` might drop traffic on Gigabit lines), the firewall's `IDSEngine` should be rewritten to aggregate stateful flow scores into a buffer queue, executing `evaluate_batch()` every 500ms rather than evaluating synchronously inline.
