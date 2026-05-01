---
created: 2026-04-28
up:
  - "[[MOC-Network-Performance]]"
related:
  - "[[Batching NIC Interrupts via ethtool Coalescing to Relieve ksoftirqd Saturation]]"
  - "[[Validating CPU Load Distribution via proc-softirqs, mpstat, and softnet_stat]]"
  - "[[IRQ Balancing Heuristics & The irqbalance Daemon]]"
  - "[[IRQ Affinity & smp_affinity Bitmask Mapping]]"
  - "[[Resolving IRQ Ping-Pong: Banned CPUs & Oneshot Mode]]"
in:
  - "[[Atlas]]"
tags:
  - linux-networking
  - kernel
  - performance-tuning
  - rps
  - smp
---

# Distributing softirq Processing with Receive Packet Steering (RPS) on Single-Queue NICs

## Summary
**Receive Packet Steering (RPS)** is a software-layer mechanism that distributes network packet processing across multiple CPUs when the NIC provides only a single hardware RX queue. The interrupt-handling CPU performs a flow hash over packet headers, enqueues the packet on a target CPU's backlog, and sends an **IPI (inter-processor interrupt)** to wake that CPU for stack processing.

## Key Points
- RPS is a purely software-based alternative to hardware multi-queue (RSS)
- CPU2 handles the initial hardware interrupt, hashes the flow, then steers the packet to another CPU
- Target CPUs are selected via a hexadecimal bitmask written to sysfs (`rps_cpus`)
- For 8 CPUs, the mask `ff` (binary `11111111`) enables steering to all cores
- In high-load scenarios, exclude the interrupting CPU (CPU2) from the mask so it focuses on harvesting packets from the DMA ring

## Details
RPS operates after the hardware interrupt but **before** the network stack's protocol processing. The sequence is:

1. NIC raises hardware interrupt on CPU2 (the CPU affinity of `rx-0`)
2. CPU2 executes the NAPI poll routine, harvesting packets from the DMA ring
3. For each packet, the kernel computes a **flow hash** from the IP addresses and port numbers (if available)
4. The hash is used to index into the `rps_cpus` bitmask to select a target CPU
5. The packet is placed on that CPU's `backlog` queue
6. An **IPI** is sent to the target CPU to trigger softirq processing there
7. The target CPU processes the packet up the network stack (IP, TCP/UDP, sockets)

### Hardware Mapping Context
Because the observed system has only **one hardware RX queue** (`rx-0`), all hardware interrupts are delivered to a single CPU. RPS does not eliminate this bottleneck—it **re-distributes the software work** that happens *after* the interrupt. The interrupt-handling CPU still spends cycles harvesting packets; RPS offloads the heavier protocol-stack processing to other cores.

### CLI Reference

Enable RPS for all 8 CPUs on `eth0` (mask `ff`):
```bash
echo ff > /sys/class/net/eth0/queues/rx-0/rps_cpus
```

Read the current RPS CPU mask:
```bash
cat /sys/class/net/eth0/queues/rx-0/rps_cpus
```

For high-load tuning, exclude CPU2 (interrupt handler). For 8 CPUs, mask `fb` = binary `11111011`:
```bash
echo fb > /sys/class/net/eth0/queues/rx-0/rps_cpus
```

Verify IPI activity (column 10 = `received_rps`):
```bash
cat /proc/net/softnet_stat
```

### Source
Notebook ID: `af92dc53-4c4b-4e37-b346-19f4cb5fc9d6`
