---
created: 2026-04-28
up:
  - "[[Things]]"
related: []
in:
  - "[[Atlas]]"
tags:
  - moc
  - network-performance
  - linux
  - systems
  - sre
  - nic
  - irq
---

# MOC Network Performance

## Overview
Map of Content for Linux network performance tuning, specifically focused on NIC IRQ saturation mitigation for single-queue hardware environments.

## Core Concepts

| Concept | Note | Description |
|---------|------|-------------|
| Interrupt Coalescing | [[Batching NIC Interrupts via ethtool Coalescing to Relieve ksoftirqd Saturation]] | Batch hardware interrupts via `ethtool rx-usecs` to reduce ksoftirqd pressure |
| Receive Packet Steering | [[Distributing softirq Processing with Receive Packet Steering (RPS) on Single-Queue NICs]] | Software-based packet distribution using `rps_cpus` bitmask and flow hashing |
| Observability | [[Validating CPU Load Distribution via proc-softirqs, mpstat, and softnet_stat]] | Validate load spreading via `/proc/softirqs`, `mpstat`, and `softnet_stat` |
| IRQ Balancing Heuristics | [[IRQ Balancing Heuristics & The irqbalance Daemon]] | Dynamic interrupt distribution via irqbalance daemon with performance/power-save toggling |
| IRQ Affinity | [[IRQ Affinity & smp_affinity Bitmask Mapping]] | CPU core binding for ISRs via `/proc/irq/*/smp_affinity` hexadecimal bitmask |
| IRQ Ping-Pong Resolution | [[Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode]] | Fix dynamic irqbalance conflicts with static RPS using banned CPUs or oneshot mode |

## MOC Anchors

### RPS
Receive Packet Steering. Software-layer alternative to hardware RSS for distributing network processing across CPUs when limited to a single hardware RX queue.

### ksoftirqd Saturation
Condition where the kernel's softirq deferral thread (`ksoftirqd/CPU`) consumes 100% of a CPU core, indicating the interrupt handler cannot keep up with packet arrival rates.

### softirq Processing
Deferred interrupt handling context in the Linux kernel. NET_RX softirqs process incoming packets up the network stack (IP, TCP/UDP, sockets).

### rps_cpus
Sysfs bitmask (`/sys/class/net/eth0/queues/rx-0/rps_cpus`) controlling which CPUs are eligible to receive steered packets. `ff` enables all 8 cores; `fb` excludes CPU2.

### ethtool Coalescing
NIC driver configuration modifying interrupt generation behavior. `rx-usecs` sets a microsecond delay before raising RX interrupts, enabling packet batching.

### rx-usecs
Parameter for receive-side interrupt coalescing. `rx-usecs 100` delays interrupts up to 100μs to accumulate packets in the DMA ring buffer.

### IRQ Affinity
CPU binding of hardware interrupts. In single-queue NICs, all interrupts route to one CPU, creating a bottleneck that RPS mitigates at the software layer.

### irqbalance
Userspace daemon that dynamically monitors CPU load and rebalances hardware interrupts across cores. Toggles between performance mode (spread interrupts) and power-save mode (park on fewer CPUs) via `--powerthresh`. Can conflict with static RPS assignments.

### smp_affinity
Sysfs bitmask (`/proc/irq/[IRQ]/smp_affinity`) defining which CPU cores may execute a specific ISR. Written in hexadecimal where each bit represents one CPU (e.g., `04` = CPU 2, `ff` = all 8 CPUs). Forms the foundation for hardirq pinning before RPS steers softirq work.

### IRQBALANCE_BANNED_CPUS
Environment variable (hex mask without `0x` prefix) telling irqbalance which CPUs to ignore entirely. Used to prevent irqbalance from migrating a hardware interrupt away from a statically pinned CPU, preserving RPS alignment.

### irq-ping-pong
Problem where irqbalance dynamically migrates interrupts, overriding static `smp_affinity` or `rps_cpus` settings. Destroys CPU cache locality and triggers excessive context switches. Resolved via `IRQBALANCE_BANNED_CPUS` or `--oneshot` mode.

### NIC Hardware Interrupts
Physical signals from the Network Interface Card to the CPU indicating packet arrival. Coalescing reduces their frequency; RPS redistributes the subsequent software work.

## Relationship Diagram

```
Hardware Interrupt (CPU2)
    ↓
[irqbalance] -- decides which CPU receives hardware IRQ
    ↓
[smp_affinity] -- pins ISR to specific CPU (e.g., CPU2 = 04)
    ↓
NAPI Poll (harvest packets from DMA ring)
    ↓
[Interrupt Coalescing] -- batches packets, reduces IRQ frequency
    ↓
Flow Hash (IP, ports)
    ↓
[RPS] -- steers to target CPU via IPI
    ↓
NET_RX softirq on target CPU
    ↓
Protocol processing (IP → TCP/UDP → socket)

### IRQ Configuration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    IRQ Configuration Chain                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  irqbalance daemon ──► smp_affinity ──► NAPI/hardirq ──► RPS│
│       (dynamic)          (static)         (ISR)      (soft) │
│                                                             │
│  • irqbalance: migrates interrupts based on CPU load        │
│  • smp_affinity: pins specific IRQ to specific CPU          │
│  • Conflict: irqbalance overrides static smp_affinity       │
│  • Resolution: IRQBALANCE_BANNED_CPUS or --oneshot          │
│                                                             │
│  ┌─────────────────┐     ┌─────────────────┐               │
│  │  Banned CPUs    │     │   Oneshot Mode  │               │
│  │  (protect CPU2) │     │ (balance once,  │               │
│  │                 │     │  then exit)     │               │
│  └─────────────────┘     └─────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
```

## All Network Performance Notes

```dataview
TABLE WITHOUT ID
  file.link as "Note",
  tags as "Tags"
FROM "Atlas/Dots/Things/Network-Performance"
SORT file.name asc
```
