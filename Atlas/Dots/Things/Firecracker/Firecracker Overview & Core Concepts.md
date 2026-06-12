---
created: 2026-05-19
up:
  - "[[MOC-MicroVM]]"
related:
  - "[[Firecracker Prerequisites & Installation]]"
  - "[[Firecracker Jailer Security Architecture]]"
  - "[[Firecracker VirtIO Network and Block IO Rate Limiting]]"
  - "[[Flow of Firecracker SDK]]"
in:
  - "[[Atlas]]"
tags:
  - systems/microvm
  - devops/infrastructure
  - aws
---

# Firecracker Overview & Core Concepts

## Summary
Firecracker is an open-source VMM developed by AWS that creates lightweight, secure microVMs using Linux KVM. Written in Rust, it strips away legacy virtualization baggage to achieve sub-125ms boot times with under 5 MiB memory overhead per VM—enabling dense multi-tenant serverless workloads.

## Key Points
- **Purpose-built for serverless**: Designed specifically for AWS Lambda and Fargate, not general-purpose virtualization (at beginning)
- **Rust-based safety**: Guarantees memory and thread safety at the language level
- **Extreme minimalism**: Intentionally omits legacy devices (BIOS, USB, PCI, VGA) to reduce attack surface and resource consumption
- **Process-per-VM isolation**: Each microVM runs in its own Firecracker process with dedicated threads (API, VMM, vCPU)
- **Defense in depth**: The Jailer companion process provides six containment layers around each VMM

## Details

### Architecture
Each Firecracker process hosts exactly one microVM through three thread types:

| Thread | Responsibility |
|--------|---------------|
| API Thread | RESTful control plane via Unix Domain Socket |
| VMM Thread | Machine model, VirtIO emulation, MMDS |
| vCPU Threads | One per guest core; executes guest code via KVM |

### Minimal Device Model
Guests see only five emulated devices:
- `virtio-net` — network interface
- `virtio-block` — storage
- `virtio-vsock` — host-guest socket communication
- Serial console
- Single-button keyboard controller

### Resource Controls
- **Token bucket rate limiters** govern network and storage I/O
- **Compute oversubscription** safely maximizes host utilization
- **MMDS (MicroVM Metadata Service)** enables secure host-guest configuration exchange without network exposure

### Trade-offs vs. Alternatives
| Dimension | Traditional VMs (QEMU) | Containers (Docker) | Firecracker |
|-----------|----------------------|---------------------|-------------|
| Boot time | Seconds to minutes | Milliseconds | <125ms |
| Memory overhead | Hundreds of MB | ~MBs shared kernel | <5 MiB |
| Isolation boundary | Hardware virtualized | Shared host kernel | Hardware virtualized |
| Compatibility | Full PC emulation | OS-level | Minimal devices |

Firecracker sacrifices broad hardware compatibility for speed and security—unlike containers, it provides true kernel isolation without the resource tax of traditional virtualization.

## Related / Links
- [[MOC-MicroVM]]
- [[KVM]]
- [[VirtIO]]
- [[AWS Lambda Architecture]]
- [[Container Security Model]]

---
*Confidence: 0.95*
**Reasoning**: Based on authoritative AWS documentation and Firecracker's open-source technical specifications. All numerical claims (125ms boot, <5 MiB overhead) come directly from the project's stated design goals.