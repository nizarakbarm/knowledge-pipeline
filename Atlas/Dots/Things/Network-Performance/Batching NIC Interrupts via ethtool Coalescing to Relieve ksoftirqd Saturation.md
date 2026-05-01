---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[Distributing softirq Processing with Receive Packet Steering (RPS) on Single-Queue NICs]]"
  - "[[Validating CPU Load Distribution via proc-softirqs, mpstat, and softnet_stat]]"
  - "[[IRQ Balancing Heuristics & The irqbalance Daemon]]"
in:
  - "[[Atlas]]"
tags:
  - linux-networking
  - kernel
  - performance-tuning
  - interrupts
  - softirq
---

# Batching NIC Interrupts via ethtool Coalescing to Relieve ksoftirqd Saturation

## Summary
**Interrupt coalescing** controls how long a NIC delays hardware interrupts after receiving packets, directly influencing CPU pressure from `ksoftirqd` kernel threads. Configuring `rx-usecs 100` batches packet arrivals into 100-microsecond windows, trading minimal latency for drastically reduced interrupt frequency and context-switch overhead.

## Key Points
- Without coalescing, high-speed packet streams generate one hardware interrupt per packet, forcing constant context switches
- `rx-usecs 100` accumulates packets in the DMA ring buffer and processes them in large batches
- Reduced interrupt frequency prevents ksoftirqd saturation on the handling CPU
- The trade-off is a small, bounded latency increase (≤100μs) in exchange for throughput stability
- In single-queue NIC environments, this is the first-line defense against softirq monopolization

## Details
When a packet arrives, the NIC normally raises a hardware interrupt immediately. The CPU must then context-switch into interrupt context, schedule a **softirq** (NET_RX), and potentially wake `ksoftirqd` if the per-CPU softirq budget is exhausted. Under high PPS (packets per second), this sequence saturates a single core—typically the one bound to the hardware RX queue.

Interrupt coalescing rewrites this equation by asking the NIC to **wait** until either:
- The `rx-usecs` timer expires (e.g., 100μs), **or**
- The RX ring buffer fills to a configured threshold

Only then is the interrupt fired, and the kernel drains the entire batch in one pass.

### Hardware Mapping Context
This research applies to a system with **a single hardware RX queue** (`rx-0`), meaning all ingress traffic funnels through one physical queue. Without coalescing, that queue's interrupt is pinned to one CPU (CPU2 in the observed case), making that core a bottleneck regardless of total system capacity.

### CLI Reference

Configure 100μs RX interrupt coalescing:
```bash
ethtool -C eth0 rx-usecs 100
```

Verify current coalescing settings:
```bash
ethtool -c eth0
```

Monitor softirq distribution per CPU in real time:
```bash
watch -n1 grep RX /proc/softirqs
```

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
