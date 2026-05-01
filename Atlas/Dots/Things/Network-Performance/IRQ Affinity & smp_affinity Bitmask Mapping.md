---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[IRQ Balancing Heuristics & The irqbalance Daemon]]"
  - "[[Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode]]"
in:
  - "[[Atlas]]"
tags:
  - irq-affinity
  - smp-affinity
  - cpu-pinning
  - bitmask
  - sysfs
---

# IRQ Affinity & smp_affinity Bitmask Mapping

## Summary
**smp_affinity** is a per-IRQ sysfs property that defines exactly which CPU cores are allowed to execute the Interrupt Service Routine (ISR) for a specific hardware interrupt. It is controlled via a hexadecimal bitmask written to `/proc/irq/[IRQ_NUMBER]/smp_affinity`, providing deterministic CPU assignment for interrupt handling.

## Key Points
- smp_affinity exposes CPU pinning for hardware interrupts through the sysfs pseudo-filesystem
- The value is a hexadecimal bitmask where each bit represents a CPU core
- Bit 0 = CPU0, bit 1 = CPU1, bit 2 = CPU2, etc.
- In an 8-CPU system, `ff` (11111111 binary) allows all cores; `04` (00000100) pins exclusively to CPU2
- Static smp_affinity provides cache locality but can conflict with dynamic irqbalance rebalancing

## Details
Linux represents CPU affinity for each IRQ as a bitmask. The kernel uses this mask to restrict which CPUs may execute the ISR for that interrupt. This is foundational for both manual tuning and understanding how irqbalance operates.

### Bitmask Mapping for 8-CPU System

| Binary | Hex | CPUs Enabled |
|--------|-----|--------------|
| 00000001 | 01 | CPU 0 only |
| 00000010 | 02 | CPU 1 only |
| 00000100 | 04 | CPU 2 only |
| 00001000 | 08 | CPU 3 only |
| 00010000 | 10 | CPU 4 only |
| 00100000 | 20 | CPU 5 only |
| 01000000 | 40 | CPU 6 only |
| 10000000 | 80 | CPU 7 only |
| 11111111 | ff | All CPUs 0-7 |
| 11111011 | fb | All except CPU 2 |

### Hardware Mapping Context
For a single-queue NIC on an 8-core system, the hardware interrupt is typically pinned to CPU2 via smp_affinity. This establishes the "harvesting CPU" that pulls packets from the DMA ring. RPS then steers the softirq processing to other CPUs, but the hardware interrupt itself remains bound to CPU2 unless manually changed.

### CLI Reference

Pin IRQ 123 to CPU 2 exclusively:
```bash
echo 04 > /proc/irq/123/smp_affinity
```

Allow IRQ 123 on all 8 CPUs:
```bash
echo ff > /proc/irq/123/smp_affinity
```

Pin IRQ 123 to CPU 0 exclusively:
```bash
echo 01 > /proc/irq/123/smp_affinity
```

Read current affinity for IRQ 123:
```bash
cat /proc/irq/123/smp_affinity
```

Find the IRQ number for eth0:
```bash
grep eth0 /proc/interrupts
```

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
