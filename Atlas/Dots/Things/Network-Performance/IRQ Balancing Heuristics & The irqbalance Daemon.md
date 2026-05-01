---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[IRQ Affinity & smp_affinity Bitmask Mapping]]"
  - "[[Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode]]"
in:
  - "[[Atlas]]"
tags:
  - irq-balancing
  - linux-kernel
  - power-management
  - interrupt-handling
  - daemon
---

# IRQ Balancing Heuristics & The irqbalance Daemon

## Summary
**IRQ balancing** is the process of distributing hardware interrupts across processors on a multiprocessor system to increase overall performance. The **irqbalance** daemon automates this by dynamically monitoring CPU load and rebalancing interrupt assignments to prevent any single core from becoming a bottleneck, toggling between performance distribution and power-saving heuristics.

## Key Points
- irqbalance constantly evaluates system load and spreads hardware interrupts across available CPUs to maximize throughput in performance mode
- The `--powerthresh=<threshold>` parameter controls the heuristic toggle between performance and power-saving modes
- Power-save mode activates when CPUs are more than 1 standard deviation below average softirq workload, preventing unnecessary wakeups
- In power-save mode, no interrupts are balanced to that CPU, saving energy but potentially creating bottlenecks on high-throughput edge servers
- For reverse proxy edge servers under sustained load, performance mode is typically preferred over power-saving

## Details
The irqbalance daemon runs as a background service and periodically samples interrupt rates across all CPUs. When it detects imbalance—where one CPU is handling disproportionately more interrupts than others—it migrates IRQs to less-loaded cores.

### Performance vs. Power-Saving Heuristics

**Performance Distribution (Default under load):**
- Interrupts are actively spread across all available CPUs
- No CPU is allowed to monopolize interrupt handling
- Maximizes throughput for high-PPS network workloads

**Power-Saving Mode:**
- Triggered when the number of CPUs below threshold are >1 standard deviation below average softirq workload
- AND no CPUs are >1 standard deviation above average
- AND the CPU has more than one IRQ assigned
- The CPU is placed into powersave mode—no interrupts balanced to it

### Hardware Mapping Context
On an 8-core system with a single RX queue, irqbalance sees CPU2 handling all hardware interrupts for the NIC. Without intervention, irqbalance may attempt to migrate these interrupts to other CPUs, conflicting with static RPS tuning.

### CLI Reference

Check irqbalance status:
```bash
systemctl status irqbalance
```

View current IRQ distribution:
```bash
watch -n1 cat /proc/interrupts
```

Set power threshold (example: 2 CPUs):
```bash
irqbalance --powerthresh=2
```

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
