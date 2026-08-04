---
created: 2026-07-29
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
tags:
  - ebpf
  - benchmark
  - bcc
  - pythonbpf
  - memory
  - performance
---

# Minimal Program Memory Footprint

> [!summary] For a trivial kprobe (return 0, no maps), BCC uses 2.3× more memory (122 MB vs 52 MB), 3.2× more page faults (16K vs 5K), and 5.8× more system CPU (0.23s vs 0.04s) than pythonbpf. The gap comes from in-process Clang compilation and kallsyms parsing.

## Metrics (from `/usr/bin/time -v`)

| Metric | pythonbpf | BCC | Ratio |
|---|---|---|---|
| Elapsed time | 0.45s | 0.71s | 1.6× |
| Max RSS | 52,088 KB | 122,280 KB | 2.3× |
| User CPU | 0.15s | 0.45s | 3.0× |
| Sys CPU | 0.04s | 0.23s | 5.8× |
| Minor page faults | 5,304 | 16,704 | 3.2× |
| CPU % | 42% | 95% | — |
| FS inputs | 0 | 192 | — |

## What Drives Each Metric

- **RSS (2.3×)**: BCC loads `libclang-cpp.so` into process memory (~80 MB for LLVM). pythonbpf keeps compilation in a subprocess.
- **Page faults (3.2×)**: BCC touches more memory pages during kernel header parsing and kallsyms scanning. Each `read()` syscall touches buffer pages.
- **Sys CPU (5.8×)**: Dominated by 10,489 `read()` syscalls for kallsyms resolution (see [[BCC kallsyms Symbol Resolution Overhead]]) and 192 FS inputs for kernel header parsing (see [[BCC In-Process Clang Compilation Path]]).
- **FS inputs (192 vs 0)**: BCC reads kernel headers (`/usr/src/linux/include/*.h`) for type resolution. pythonbpf uses BTF — no header files needed.

## Why These Numbers Matter

At 95% CPU usage for a program that does nothing (kprobe returns 0 immediately), BCC's overhead is almost entirely framework initialization. For production use where startup time is amortized over long-running tracing, these costs are paid once. But for short-lived probes, CLI tools, or frequent attach/detach cycles, the gap is significant.

## Related

- [[BPF Syscall-Only — kallsyms Symbol Resolution Overhead]]
- [[BPF Syscall-Only — BCC In-Process Clang Compilation Path]]
- [[Syscall and Startup Comparison]]
