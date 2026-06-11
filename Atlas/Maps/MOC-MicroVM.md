---
created: 2026-05-19
up:
  - "[[Things]]"
related:
  - "[[MOC-Network-Performance]]"
in:
  - "[[Atlas]]"
tags:
  - moc
  - microvm
  - firecracker
  - virtualization
  - systems
---

# MOC MicroVM

## Overview
Map of Content for Firecracker MicroVM architecture, deployment lifecycle, security model, and I/O resource management.

## Core Concepts

| Concept | Note | Description |
|---------|------|-------------|
| Architecture Overview | [[Firecracker Overview & Core Concepts]] | Design philosophy, thread model, device model, and trade-offs vs traditional VMs/containers |
| Installation | [[Firecracker Prerequisites & Installation]] | Hardware prerequisites, kernel requirements, dependencies, and step-by-step setup commands |
| Security Isolation | [[Firecracker Jailer Security Architecture]] | Six-layer defense-in-depth containment: chroot, namespaces, cgroups, seccomp, privilege dropping, fd management |
| I/O Rate Limiting | [[Firecracker VirtIO Network and Block IO Rate Limiting]] | Token bucket algorithm for bandwidth and ops/sec throttling on network and block devices |

## MOC Anchors

### MicroVM
Lightweight virtual machine optimized for transient, event-driven workloads. Firecracker microVMs boot in <125ms with <5 MiB memory overhead per instance.

### KVM
Linux Kernel-based Virtual Machine. Firecracker leverages KVM for hardware-assisted virtualization, creating isolated guest environments with their own kernel instances.

### Jailer
Companion process that wraps the Firecracker VMM in a defense-in-depth digital prison with six layers of mandatory security isolation before executing guest code.

### VirtIO
Paravirtualized I/O standard. Firecracker exposes minimal device model: virtio-net (network), virtio-block (storage), virtio-vsock (host-guest communication).

### Token Bucket
Rate limiting algorithm using token replenishment. Allows burst I/O while enforcing sustained throughput caps. Configured via Firecracker REST API per device.

### Serverless Computing
Event-driven execution model where workloads are ephemeral and scale to zero. Firecracker was purpose-built by AWS for Lambda and Fargate workloads.

## All MicroVM Notes

```dataview
TABLE WITHOUT ID
  file.link as "Note",
  tags as "Tags"
FROM "Atlas/Dots/Things/Firecracker"
SORT file.name asc
```