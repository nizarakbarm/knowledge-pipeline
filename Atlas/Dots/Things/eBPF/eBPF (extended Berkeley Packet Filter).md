---
created: 2026-04-12
up:
  - "[[Concepts]]"
  - "[[Systems MOC (kit)]]"
related:
  - "[[libbpf Framework]]"
  - "[[CO-RE (Compile Once - Run Everywhere)]]"
  - "[[BTF (BPF Type Format)]]"
  - "[[PythonBPF]]"
  - "[[BCC eBPF]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Overview]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Hello World]]"
in:
  - "[[Things]]"
  - "[[eBPF]]"
  - "[[Concepts]]"
tags:
  - concept
  - systems
  - kernel
  - ebpf
---

# eBPF (extended Berkeley Packet Filter)

## Summary
eBPF is a revolutionary Linux kernel technology that enables safe execution of user-defined programs directly in kernel space without modifying kernel source code or loading modules. It transforms the kernel from a closed system into a programmable platform.

## Key Points

- **Kernel Programmability**: Run custom code inside the Linux kernel safely without kernel patches or module compilation
- **Event-Driven Architecture**: Hook into system-level events—network packets, tracepoints, syscalls, kernel functions
- **Safety-First Design**: In-kernel verifier analyzes programs before execution to prevent crashes or infinite loops
- **Zero-Cost Performance**: JIT compiler transforms eBPF bytecode to native machine code with minimal overhead
- **Modern Ecosystem**: Replaced legacy BCC with frameworks like libbpf, libbpf-rs, Cilium, and eunomia-bpf

## Details

### How eBPF Works

> [!info] The Execution Pipeline
> User-written C/Rust code → LLVM compiles to eBPF bytecode → Verifier checks safety → JIT compiler → Native machine code executes in kernel

The eBPF virtual machine operates inside the kernel with a restricted instruction set. Unlike traditional kernel modules that can crash the system, eBPF programs must pass a rigorous verifier that checks for:

- No infinite loops or unreachable code
- Bounded memory access (no out-of-bounds reads/writes)
- Limited stack size and complexity
- No unauthorized kernel memory access

### Common Hook Points

| Hook Type | Use Case |
|-----------|----------|
| Tracepoints | Kernel function tracing |
| Kprobes/Kretprobes | Dynamic kernel instrumentation |
| Network (XDP, TC) | Packet filtering, load balancing |
| LSM | Security policy enforcement |
| Uprobes | User-space application tracing |

### The Toolchain Evolution

The eBPF ecosystem has matured significantly:

- **Legacy**: BCC (BPF Compiler Collection) required Python and kernel headers on target machines
- **Modern**: libbpf-based solutions compile once, package as ELF, and run anywhere with CO-RE support
- **Specialized**: Cilium for networking, eunomia-bpf for simplified tooling, libbpf-rs for Rust

## Connections

- **Questions this raises**: How does the verifier balance safety with expressiveness? What are the hard limits of eBPF complexity?
- **Related concepts**: [[Kernel Space]], [[System Calls]], [[Tracing]]
- **Applies to**: Network monitoring, security enforcement, performance profiling, observability

## Source

- Original eBPF CO-RE Tutorial
- Frameworks mentioned: libbpf, libbpf-rs, Cilium, eunomia-bpf

---

*Created from eBPF CO-RE Tutorial distillation by Sensemaker*