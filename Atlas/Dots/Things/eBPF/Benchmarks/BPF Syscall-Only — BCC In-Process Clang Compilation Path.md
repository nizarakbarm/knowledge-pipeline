---
created: 2026-07-29
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
tags:
  - ebpf
  - benchmark
  - bcc
  - pythonbpf
  - compilation
  - clang
---

# BCC In-Process Clang Compilation Path

> [!summary] BCC loads `libclang-cpp.so` into its own process, compiles C to BPF bytecode in-process, then spawns one Clang subprocess. pythonbpf spawns `llc` as a child process for codegen. The in-process path costs more memory and CPU.

## Compilation Architecture

| Aspect | pythonbpf | BCC |
|---|---|---|
| Compiler invocation | Spawns `llc` subprocess | Loads `libclang-cpp.so` in-process |
| `execve` count (strace) | 0 (llc is forked, not exec'd via python) | 1 (actual Clang binary) |
| Memory footprint | 52 MB | 122 MB (2.3×) |
| User CPU | 0.15s | 0.45s (3×) |
| Sys CPU | 0.04s | 0.23s (5.8×) |
| FS inputs (kernel headers) | 0 | 192 |

## Why BCC Compiles In-Process

BCC's design pre-dates modern BTF-driven loading. It compiles C source at runtime to support its `BPF(text=...)` API — users write inline C strings, BCC compiles them on the fly. The in-process Clang path avoids the overhead of serializing/deserializing intermediate representations to a subprocess.

## Why pythonbpf Spawns a Subprocess

pythonbpf uses LLVM's `llc` directly for BPF target codegen. The subprocess boundary isolates the compilation from the main process, keeping RSS lower (52 MB vs 122 MB). The tradeoff is one extra `fork`/`exec` (invisible to strace because it's a child process, not the traced process itself).

## Cost Breakdown

The 122 MB RSS of BCC comes primarily from:
1. **Clang/LLVM libraries** loaded into address space (~80 MB)
2. **Kernel header parsing** (192 FS inputs, reads `/usr/src/linux/include/*.h`)
3. **Symbol resolution** via kallsyms (10,489 reads — see [[BPF Syscall-Only — kallsyms Symbol Resolution Overhead]])

## Related

- [[BPF Syscall-Only — kallsyms Symbol Resolution Overhead]]
- [[bpf Syscall Comparison Python-BPF vs BCC vs Eunomia]]
