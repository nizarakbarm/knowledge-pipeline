---
created: 2026-05-19
up:
  - "[[MOC-MicroVM]]"
related:
  - "[[Firecracker Overview & Core Concepts]]"
  - "[[Firecracker Jailer Security Architecture]]"
  - "[[Firecracker Prerequisites & Installation]]"
  - "[[MOC-Network-Performance]]"
  - "[[Flow of Firecracker SDK]]"
in:
  - "[[Atlas]]"
tags:
  - systems/microvm
  - virtio
  - networking
  - storage
---

# Firecracker VirtIO Network & Block I/O Rate Limiting

## Summary
Firecracker enforces resource isolation in multi-tenant environments by applying rate limits to VirtIO network and block devices. These limits prevent a single microVM from consuming disproportionate host I/O bandwidth or operation capacity, ensuring predictable performance for co-located tenants.

## Key Points
- Uses **token bucket algorithm** for sustained caps with burst accommodation
- Configured independently for **bandwidth** (bytes) and **operations/sec** (IOPS)
- Network devices have **separate rx/tx limiters** for bidirectional traffic shaping
- Block devices apply both bandwidth and ops limits
- All configuration via **Firecracker REST API** at runtime

## Token Bucket Algorithm

The rate limiting mechanism employs a token bucket that permits temporary bursts while enforcing sustained throughput ceilings. Tokens represent discrete units of work: bytes for bandwidth throttling or individual operations for IOPS limiting. When the bucket contains tokens, I/O proceeds at hardware speed; once depleted, the workload throttles to the bucket's steady refill rate.

### Execution Behavior
- **Tokens available**: I/O proceeds at unbounded hardware speed (burst capacity)
- **Bucket empty**: I/O strictly throttled to `size / refill_time` rate
- **one_time_burst**: Optional initial allocation consumed before standard refill begins

## Configuration Parameters

Rate limiters are configured per-device through the Firecracker REST API via `TokenBucket` objects:

| Parameter | Type | Description |
|-----------|------|-------------|
| **size** | integer | Total token capacity (burst ceiling and refill quantum) |
| **refill_time** | integer | Duration in ms for bucket to refill from empty to full |
| **one_time_burst** | integer (optional) | Initial burst allocation granted at device startup |

### Sustained Rate Calculation
```
rate_limit = size / refill_time
```
Example: `size=104857600` (100MB), `refill_time=1000` (1s) → **100 MB/s sustained**

### REST API Example
```json
{
  "rate_limiter": {
    "bandwidth": {
      "size": 104857600,
      "refill_time": 1000,
      "one_time_burst": 1073741824
    },
    "ops": {
      "size": 10000,
      "refill_time": 1000,
      "one_time_burst": 50000
    }
  }
}
```

## Network vs Block Device Specifics

### Network Devices (virtio-net)
Maintain independent limiters for each traffic direction:
- **rx_rate_limiter**: Governs incoming (receive) traffic
- **tx_rate_limiter**: Governs outgoing (transmit) traffic

### Block Devices (virtio-block)
Apply both bandwidth and operations limits:
- **bandwidth**: Constrains throughput (bytes/sec)
- **ops**: Constrains IOPS (operations/sec)

## Related / Links
- [[MOC-MicroVM]]
- [[MOC-Network-Performance]]
- [[VirtIO]]
- [[Token Bucket Algorithm]]
- [[Firecracker Overview & Core Concepts]]
- [[Firecracker Jailer Security Architecture]]

---
*Confidence Score: 0.92*
**Reasoning**: This note accurately distills the source material regarding Firecracker's rate limiting architecture. The token bucket explanation correctly balances burst behavior against sustained throttling. Configuration parameters match the documented REST API fields.