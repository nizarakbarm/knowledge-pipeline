---
created: 2026-07-29
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
tags:
  - ebpf
  - benchmark
  - bcc
  - pythonbpf
  - kallsyms
  - performance
---

# BCC kallsyms Symbol Resolution Overhead

> [!summary] BCC reads `/proc/kallsyms` ~10,000 times to resolve kernel symbol addresses at attach time. This dominates syscall overhead — pythonbpf avoids it entirely by using BTF IDs.

## The Problem

When BCC attaches a kprobe to `do_nanosleep`, it needs the kernel address of that function. BCC resolves this by reading `/proc/kallsyms` line by line, scanning for the target symbol. For a minimal kprobe program, this produces **10,489 `read()` syscalls** (strace filter: `strace -e read`).

pythonbpf uses BTF IDs to locate kernel symbols — zero reads of kallsyms.

## Strace Evidence

| Metric | pythonbpf | BCC |
|---|---|---|
| `read()` calls | 441 | 10,489 |
| Total syscalls | 1,170 | 11,262 |
| read() fraction of total | 38% | 93% |

The `read()` gap alone (10,048 calls) accounts for 89% of BCC's total syscall advantage over pythonbpf.

## Why BCC Does This

BCC compiles C source at runtime via Clang/LLVM. The compiler resolves `kprobe/do_nanosleep` to an address by parsing kernel headers and symbols. BCC's attach path then passes this address to `perf_event_open()`.

pythonbpf uses libbpf's `bpf_program__attach_kprobe_opts()`, which lets the kernel handle symbol resolution internally via BTF — no userspace scanning needed.

## Related

- [[bpf Syscall Comparison Python-BPF vs BCC vs Eunomia]]
- [[BPF Syscall-Only — BCC In-Process Clang Compilation Path]]
