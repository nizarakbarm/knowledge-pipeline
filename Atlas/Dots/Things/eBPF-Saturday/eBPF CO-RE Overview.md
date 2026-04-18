---
created: 2025-04-17
up:
  - "[[eBPF MOC]]"
related:
  - "[[eBPF Hello World Tutorial]]"
in:
  - "[[Library]]"
  - "[[Things]]"
tags:
  - concept
  - linux
  - systems-programming
  - ebpf
---

# eBPF CO-RE Overview

## Summary

**eBPF** = kernel virtual machine for safely executing custom programs inside Linux without source modifications or kernel modules.

**CO-RE** = Compile Once — Run Everywhere. Solves kernel version portability via BTF (BPF Type Format) adapting structure layouts at load time.

## Architecture

| Layer | Function |
|-------|----------|
| **Verifier** | Pre-load static analysis: no crashes, infinite loops, or invalid memory access |
| **JIT Compiler** | Bytecode → native machine code (x86_64, ARM64) at load time |
| **Event Hooks** | Attach to tracepoints, kprobes, uprobes, network packets, syscalls |

## CO-RE Portability

**Problem**: Kernel struct offsets change between versions (e.g., `task_struct` 5.4 vs 6.1).

**Solution**: 
- **BTF** embeds structure metadata in kernels 5.2+
- **`BPF_CORE_READ()`** generates relocation entries; loader resolves at runtime

```c
// Field access works across kernel versions
filename = BPF_CORE_READ(name, name);
```

## Tracepoints vs Kprobes

| | Tracepoints | Kprobes |
|---|-------------|---------|
| **Type** | Static (kernel hardcoded) | Dynamic (runtime injection) |
| **Stability** | API/ABI guaranteed | Breaks on kernel changes |
| **Overhead** | Low, predictable | Higher (CPU exceptions) |
| **Use** | Production monitoring | Ad-hoc debugging |

## Connections

- **Related**: [[BCC eBPF]], [[eBPF Hello World Tutorial]]
- **Questions**: BTF offset encoding? CO-RE relocation overhead?

## Source

- https://eunomia.dev/tutorials/
- https://eunomia.dev/tutorials/0-introduce/
- https://eunomia.dev/tutorials/1-helloworld/
