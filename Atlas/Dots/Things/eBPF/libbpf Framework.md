---
created: 2026-04-12
up:
  - "[[Concepts]]"
  - "[[Systems MOC (kit)]]"
related:
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[CO-RE (Compile Once - Run Everywhere)]]"
  - "[[PythonBPF]]"
  - "[[BCC eBPF]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Overview]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Hello World]]"
in:
  - "[[Things]]"
  - "[[eBPF]]"
  - "[[Concepts]]"
tags:
  - framework
  - systems
  - ebpf
  - kernel
---

# libbpf Framework

## Summary
libbpf is the de facto standard library for loading, managing, and interacting with eBPF programs in modern Linux systems. It provides the foundation for "Compile Once - Run Everywhere" (CO-RE) portability, replacing the legacy BCC approach that required kernel headers on target machines.

## Key Points

- **ELF Loading**: Reads compiled eBPF object files (`.o`) and orchestrates kernel loading
- **Map Management**: Creates and manages BPF maps for kernel-user space data exchange
- **CO-RE Support**: Performs BTF-based type matching and field relocation at load time
- **Skeleton Generation**: Auto-generates C code for streamlined program integration
- **Zero Runtime Dependencies**: No need for kernel headers, LLVM, or Python on target systems

## Details

### Architecture Overview

> [!info] libbpf's Core Responsibilities
> libbpf acts as the bridge between compiled eBPF bytecode and the running kernel, handling all the complexity of program loading, attachment, and lifecycle management.

The framework operates in several phases:

1. **Object Parsing**: Reads ELF-formatted `.o` files containing eBPF bytecode and BTF metadata
2. **Kernel Negotiation**: Queries kernel capabilities and adjusts program features accordingly
3. **Dynamic Patching**: Rewrites bytecode offsets using BTF relocation data for target kernel compatibility
4. **Attachment**: Links eBPF programs to kernel hooks (tracepoints, kprobes, network interfaces)
5. **Map Setup**: Initializes BPF maps for data collection and configuration

### The CO-RE Connection

libbpf is the engine behind CO-RE portability:

```
Compilation Machine          Target Machine
     ↓                              ↓
vmlinux.h +                    /sys/kernel/btf/vmlinux
BPF code   →   libbpf loader  →   BTF comparison
                                Offset patching
                                Kernel loading
```

The loader compares the local BTF (compiled into the ELF) against the target kernel's BTF, then adjusts field offsets dynamically. This means a program compiled on kernel 5.15 can run correctly on kernel 6.2 even if internal kernel structures changed.

### Modern Toolchains Built on libbpf

| Toolchain | Description | Best For |
|-----------|-------------|----------|
| **libbpf-bootstrap** | Official minimal templates | Custom eBPF development |
| **libbpf-rs** | Rust bindings | Rust-based observability tools |
| **eunomia-bpf** | Simplified toolchain | Quick prototyping, education |
| **Cilium/Hubble** | Kubernetes networking | Cloud-native networking |

### Comparison with Legacy BCC

| Aspect | BCC | libbpf |
|--------|-----|--------|
| Compilation | JIT on target | Ahead-of-time |
| Dependencies | Kernel headers, LLVM, Python | None at runtime |
| Startup Time | Slow (compilation overhead) | Fast (pre-compiled) |
| Portability | Limited (tied to kernel version) | Universal (CO-RE) |
| Resource Usage | Higher | Minimal |

## Connections

- **Questions this raises**: How does libbpf handle kernel version mismatches beyond structure offsets? What happens when BTF is unavailable?
- **Related concepts**: [[eBPF (extended Berkeley Packet Filter)]], [[CO-RE (Compile Once - Run Everywhere)]], [[BTF (BPF Type Format)]]
- **Applies to**: Building portable observability tools, kernel tracing, network filtering

## Source

- Original eBPF CO-RE Tutorial
- Frameworks: libbpf, libbpf-rs, Cilium, eunomia-bpf

---

*Created from eBPF CO-RE Tutorial distillation by Sensemaker*