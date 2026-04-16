---
created: 2025-01-12
up:
  - "[[eBPF]]"
  - "[[eBPF Tutorials]]"
related:
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Hello World]]"
  - "[[eBPF Tutorial - Kprobe Unlink]]"
  - "[[CO-RE (Compile Once - Run Everywhere)]]"
  - "[[libbpf Framework]]"
in:
  - "[[Things]]"
  - "[[eBPF]]"
  - "[[Concepts]]"
tags:
  - ebpf
  - core
  - libbpf
  - tutorial
  - eunomia
source:
  - https://eunomia.dev/tutorials/
  - https://eunomia.dev/tutorials/0-introduce/
  - https://eunomia.dev/tutorials/1-helloworld/
---

# eBPF Tutorial - Overview

> [!summary]
> Foundation concepts for eBPF development using the eunomia-bpf framework. Covers eBPF fundamentals, libbpf toolchain, and CO-RE methodology for portable kernel programming.

---

## What is eBPF?

**eBPF (extended Berkeley Packet Filter)** allows developers to safely run small programs directly in the Linux kernel without modifying kernel source code or loading modules.

### Core Capabilities

- **Direct Kernel Interaction** - Hook into system calls, tracepoints, network packets, and kernel functions
- **Safe Execution** - In-kernel verifier checks program logic before execution to prevent crashes and security breaches
- **Minimal Overhead** - JIT compiler translates eBPF bytecode to optimized machine code for near-native performance

### Modern Toolchain

| Component | Purpose |
|-----------|---------|
| **LLVM** | Compiles high-level languages (C, Rust) to eBPF bytecode |
| **libbpf** | Manages, loads, and interacts with eBPF programs |
| **eunomia-bpf** | Modern framework simplifying eBPF development |

> [!info] Framework Evolution
> Modern development uses **libbpf**, **libbpf-rs**, **Cilium**, or **eunomia-bpf** rather than legacy BCC tools.

---

## CO-RE: Compile Once, Run Everywhere

**CO-RE** enables compiling eBPF programs once and running them on different kernel versions without recompilation.

### Why CO-RE Matters

Traditional eBPF development required recompiling programs for each target kernel version due to changing kernel data structures. CO-RE eliminates this constraint through:

- **BTF (BPF Type Format)** - Kernel metadata describing data structures
- **Relocation Records** - Compile-time placeholders for structure offsets
- **libbpf Loader** - Runtime resolution and patching of offsets

> [!tip] Key Benefit
> Write once, run on any kernel with BTF support. No need to ship kernel headers or recompile for different distributions.

### Workflow

```
Source Code (C) 
    ↓
Compile with BTF (ecc toolchain)
    ↓
Portable bytecode + BTF metadata
    ↓
Load on target kernel (libbpf resolves offsets)
    ↓
Execute
```

---

## eunomia-bpf Framework

The eunomia-bpf framework simplifies eBPF development by:

- **Single compilation** - One command builds portable eBPF programs
- **Dynamic loading** - Built-in loader handles kernel-space code without writing user-space programs
- **CO-RE by default** - Automatic BTF generation and relocation handling

### Toolchain Commands

| Command | Purpose |
|---------|---------|
| `ecc <file.bpf.c>` | Compile eBPF C code to portable bytecode |
| `ecli run <package.json>` | Load and execute eBPF program |

---

## Prerequisites

- Linux kernel 4.8+ (5.15+ recommended)
- `CONFIG_DEBUG_INFO_BTF=y` enabled
- Root privileges for loading eBPF programs

---

## Next Steps

→ Continue to [[Atlas/Dots/Things/eBPF/eBPF Tutorial - Hello World]] for a complete implementation example.

---

## References

- eunomia.dev tutorials: https://eunomia.dev/tutorials/
- libbpf documentation: https://libbpf.readthedocs.io/
- Kernel BTF: `/sys/kernel/btf/vmlinux`