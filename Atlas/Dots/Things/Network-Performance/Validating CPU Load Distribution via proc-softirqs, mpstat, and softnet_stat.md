---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[Batching NIC Interrupts via ethtool Coalescing to Relieve ksoftirqd Saturation]]"
  - "[[Distributing softirq Processing with Receive Packet Steering (RPS) on Single-Queue NICs]]"
  - "[[Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode]]"
in:
  - "[[Atlas]]"
tags:
  - linux-networking
  - observability
  - performance-tuning
  - monitoring
  - softirq
---

# Validating CPU Load Distribution via /proc/softirqs, mpstat, and softnet_stat

## Summary
Validating network receive-side optimizations requires observing three signals: per-CPU **NET_RX softirq counts**, **per-CPU %soft utilization**, and **RPS IPI counters**. Together, these metrics confirm whether interrupt coalescing and Receive Packet Steering (RPS) are successfully distributing kernel network processing across CPU cores.

## Key Points
- `/proc/softirqs` exposes cumulative NET_RX counts per CPU; RPS success shows increases across multiple CPUs, not just the interrupt handler
- `mpstat -P ALL 1` reveals per-CPU `%soft` utilization; ideal RPS distribution shows balanced softirq load instead of 100% on one core
- `/proc/net/softnet_stat` column 10 (`received_rps`) counts IPI wakeups for steered packets; non-zero values confirm RPS is actively triggering remote CPUs
- All three metrics should be observed together—softirq counts alone don't prove balanced *utilization*
- Baseline measurements before and after tuning are essential to quantify improvement

## Details
Linux exposes network processing metrics through `/proc` pseudo-filesystems. Each metric answers a different question about the receive path:

| Metric | Source | What It Reveals |
|--------|--------|-----------------|
| NET_RX softirqs | `/proc/softirqs` | Total RX softirq invocations per CPU |
| %soft CPU time | `mpstat -P ALL 1` | Percentage of CPU time spent in softirq context |
| RPS IPI count | `/proc/net/softnet_stat` (col 10) | Number of packets steered via IPI to remote CPUs |

### Hardware Mapping Context
On a system with a **single hardware RX queue**, pre-tuning observations show extreme asymmetry: CPU2 handles 100% of hardware interrupts and softirq processing, while CPUs 0-1 and 3-7 show near-zero network activity. Post-RPS, the same total throughput should appear as distributed NET_RX increments and `%soft` load, while CPU2 retains the hardware interrupt duty.

### CLI Reference

Watch NET_RX softirq counts per CPU (updates every second):
```bash
watch -n1 grep RX /proc/softirqs
```

Monitor per-CPU softirq utilization in real time:
```bash
mpstat -P ALL 1
```

Inspect softnet statistics, including RPS counters:
```bash
cat /proc/net/softnet_stat
```

Column mapping for `/proc/net/softnet_stat` (space-separated):
```text
Column 1:  processed
Column 2:  dropped
Column 3:  time_squeeze
...
Column 10: received_rps   <-- IPI steered packets
```

Snapshot baseline before tuning (save for comparison):
```bash
echo "=== softirqs ===" && grep RX /proc/softirqs && echo "=== softnet ===" && cat /proc/net/softnet_stat > /tmp/net-baseline.txt
```

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
