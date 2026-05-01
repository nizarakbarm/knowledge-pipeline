---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[IRQ Balancing Heuristics & The irqbalance Daemon]]"
  - "[[IRQ Affinity & smp_affinity Bitmask Mapping]]"
in:
  - "[[Atlas]]"
tags:
  - irq-ping-pong
  - rps
  - irqbalance
  - troubleshooting
  - cpu-locality
---

# Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode

## Summary
**IRQ ping-pong** occurs when the dynamic irqbalance daemon conflicts with static interrupt tuning (such as RPS or manually set smp_affinity), causing interrupts to bounce between CPUs. This destroys cache locality, triggers excessive context switches, and destabilizes throughput. Two resolution methods exist: banning CPUs from irqbalance via `IRQBALANCE_BANNED_CPUS`, or running irqbalance in `--oneshot` mode.

## Key Points
- IRQ ping-pong happens when irqbalance periodically migrates interrupts away from statically assigned CPUs
- The conflict is most severe on single-queue NICs where RPS relies on a stable hardware interrupt CPU to harvest packets
- `IRQBALANCE_BANNED_CPUS` uses a hex mask (without `0x` prefix) to exclude CPUs from irqbalance decisions
- `--oneshot` performs an optimal initial distribution then exits, preventing any future dynamic migration
- For OpenResty edge servers, `--oneshot` + manual smp_affinity tuning is often the most stable configuration

## Details
When you configure a single-queue NIC with static RPS (`rps_cpus`), you establish a fixed software rule: CPU2 harvests packets from the hardware queue and distributes softirq work to other cores. However, irqbalance—unaware of this static tuning—periodically re-evaluates system load and migrates the hardware interrupt to a different CPU.

This creates a cycle:
1. irqbalance migrates NIC interrupt from CPU2 to CPU5
2. RPS still expects CPU2 to do flow hashing and IPI steering
3. Cache lines for NIC ring buffers are now cold on CPU5
4. irqbalance later migrates back to CPU2
5. Repeat → **IRQ ping-pong**

### Resolution Methods

**Method 1: Ban CPUs from irqbalance**
Prevent irqbalance from touching specific CPUs entirely:
```bash
export IRQBALANCE_BANNED_CPUS=ff
systemctl restart irqbalance
```

This bans all 8 CPUs (binary 11111111 = hex ff) from irqbalance decisions. The daemon will not migrate interrupts to or from any of these CPUs.

**Method 2: Oneshot mode**
Run irqbalance exactly once at boot, then let manual tuning take over:
```bash
irqbalance --oneshot
```

Or set the environment variable:
```bash
export IRQBALANCE_ONESHOT=1
systemctl restart irqbalance
```

### Choosing a Strategy

| Scenario | Recommended Approach |
|----------|---------------------|
| High-throughput edge server (OpenResty) | `--oneshot` + manual smp_affinity + RPS |
| Variable load, energy-conscious | `IRQBALANCE_BANNED_CPUS` to protect RPS CPU |
| Single-queue NIC with RPS | Ban the RPS harvesting CPU from irqbalance |
| Multi-queue NIC with RSS | Allow irqbalance to manage; disable RPS |

### Hardware Mapping Context
On the 8-core single-queue system, the recommended configuration is:
1. Pin NIC IRQ to CPU2 via `smp_affinity`
2. Enable RPS with `rps_cpus=fb` (all except CPU2)
3. Run irqbalance with `--oneshot` or ban CPU2 via `IRQBALANCE_BANNED_CPUS`

This gives CPU2 dedicated hardware interrupt duty while distributing softirq processing across the remaining 7 cores.

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
