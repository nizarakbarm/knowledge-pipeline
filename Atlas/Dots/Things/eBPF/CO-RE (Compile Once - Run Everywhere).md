---
created: 2026-04-12
up:
  - "[[Concepts]]"
  - "[[Systems MOC (kit)]]"
related:
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[libbpf Framework]]"
  - "[[BTF (BPF Type Format)]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Overview]]"
  - "[[Atlas/Dots/Things/eBPF/eBPF Tutorial - Hello World]]"
in:
  - "[[Things]]"
  - "[[eBPF]]"
  - "[[Concepts]]"
tags:
  - concept
  - portability
  - ebpf
  - kernel
---

# CO-RE (Compile Once - Run Everywhere)

## Summary
CO-RE solves the fundamental portability problem of eBPF: compiled programs traditionally broke when run on different kernel versions due to changing internal data structures. CO-RE enables a single compiled eBPF program to run across diverse kernel versions through sophisticated compile-time and load-time cooperation.

## Key Points

- **The Portability Problem**: Kernel internal structs (like `task_struct`) change between versions, breaking hardcoded offsets
- **BTF as Metadata**: Uses BPF Type Format to encode type information in compiled binaries
- **Relocation Records**: Compiler emits symbolic references instead of fixed offsets
- **Runtime Resolution**: libbpf patches bytecode at load time to match target kernel layout
- **Compile Once**: Single `.o` file works across kernel versions without recompilation

## Details

### The Problem CO-RE Solves

Without CO-RE, eBPF programs had to be compiled on the target machine with matching kernel headers:

```c
// Traditional approach (fragile)
int pid = ctx->pid;  // Hardcoded offset - breaks on kernel changes!
```

Kernel structures evolve:
- Fields get added or removed
- Padding changes
- Type sizes shift

A program compiled on kernel 5.4 might crash or return garbage on kernel 5.15 because `task_struct` grew by 48 bytes.

### The Three Pillars of CO-RE

> [!info] 1. BTF (BPF Type Format)
> Compact metadata encoding C-type information (structs, unions, enums). Embedded in kernel at `/sys/kernel/btf/vmlinux` and in compiled eBPF objects.

> [!info] 2. Field Access Relocations
> Clang/LLVM emits records like "offset of field X in struct Y" instead of hardcoded numbers. These are placeholders resolved at load time.

> [!info] 3. Type Matching
> libbpf loader compares local BTF against target kernel's BTF, matching by name and structure, then patches bytecode offsets in memory.

### How Relocation Works

```
Compile Time:
  C code: bpf_probe_read(&pid, sizeof(pid), &task->pid);
  ↓
  Relocation record: "task_struct.pid at offset ?"
  
Load Time:
  libbpf reads /sys/kernel/btf/vmlinux
  ↓
  Locates task_struct in target kernel's BTF
  ↓
  Discovers pid offset (e.g., 136 instead of 120)
  ↓
  Patches bytecode: offset 136 → instruction updated
  ↓
  Program loads successfully!
```

### Kernel Requirements

| Requirement | Purpose |
|-------------|---------|
| `CONFIG_DEBUG_INFO_BTF=y` | Enables BTF generation in kernel build |
| Linux 5.2+ | Minimum for BTF support |
| Linux 5.15+ / 6.2+ | Recommended for BPF tokens, arenas |

> [!warning] Fallback Limitation
> If BTF is unavailable on target kernel, CO-RE cannot perform relocations. The program may fail to load or require workarounds.

### BTF vs DWARF

BTF replaces bulky DWARF debug info:
- **Size**: BTF is ~10x smaller than DWARF
- **Kernel**: Embedded directly in kernel binary
- **Runtime**: Kernel exposes via `/sys/kernel/btf/vmlinux`

## Connections

- **Questions this raises**: What happens when BTF types change semantically (not just layout)? How does CO-RE handle type redefinitions?
- **Related concepts**: [[eBPF (extended Berkeley Packet Filter)]], [[libbpf Framework]], [[BTF (BPF Type Format)]], [[Kernel ABI]]
- **Applies to**: Building portable observability tools, distributed tracing, kernel monitoring at scale

## Source

- Original eBPF CO-RE Tutorial
- Kernel config: `CONFIG_DEBUG_INFO_BTF=y`
- BTF location: `/sys/kernel/btf/vmlinux`

---

*Created from eBPF CO-RE Tutorial distillation by Sensemaker*