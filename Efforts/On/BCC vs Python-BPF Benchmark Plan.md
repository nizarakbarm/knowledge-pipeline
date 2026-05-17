---
created: 2026-05-11
up:
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Compiler Limitations]]"
  - "[[BCC vs Python-BPF bpf_printk Comparison]]"
  - "[[Architecture]]"
  - "[[PythonBPF Setup]]"
in:
  - "[[Efforts]]"
tags: [ebpf, benchmark, bcc, python-bpf, performance, methodology, tracepoint]
---

# BCC vs Python-BPF Benchmark Plan

Two-phase benchmark comparing BCC (runtime Clang compilation) vs Python-BPF (AST → llvmlite IR → llc) on the `tracepoint/syscalls/sys_enter_openat` hook, measuring translation overhead and runtime throughput.

## Key Points

- **Hook:** `tracepoint/syscalls/sys_enter_openat` — deterministic trigger (`touch /tmp/bench_test`), zero polling
- **Phase A:** Translation overhead — startup latency, max RSS, execve count, bpf() syscall count
- **Phase B:** Runtime throughput — BPF map counter, flood events, measure per-event cost
- **Critical constraint:** No `perf_buffer`, `ring_buffer`, or continuous `bpf_printk` polling — must be cleanly interruptible via SIGINT
- **Known blocker:** `ctx.args[0]` access not supported in Python-BPF (see [[Python-BPF Compiler Limitations]]) — Python-BPF program must avoid subscripting `args`

## Details

### Pipeline Comparison

| Stage | BCC | Python-BPF |
|---|---|---|
| Input | Python string containing C | Python with `@bpf` decorators |
| Translation | fork → `execve("/usr/bin/clang", ...)` | AST → llvmlite IR → `execve("llc", ...)` |
| Output | BPF bytecode | ELF object via `llc -march=bpf` |
| Loader | BCC built-in | pylibbpf |

The `execve` call in `strace` output is the primary discriminator between the two pipelines.

### Metrics Table (to fill)

| Metric | BCC | Python-BPF |
|---|---|---|
| Elapsed time | ___ | ___ |
| Max RSS (KB) | ___ | ___ |
| execve count | ___ | ___ |
| bpf() syscalls | ___ | ___ |
| Output observed? | YES/NO | YES/NO |

### Execution Protocol (on vmdevnull, root)

**Terminal 1 — Run:**
```bash
/usr/bin/time -v strace -f -e bpf,execve,mmap,openat -o strace.log python3 benchmark_bcc.py
```

**Terminal 2 — Trigger & interrupt:**
```bash
sleep 2 && touch /tmp/bench_test && sleep 1 && kill -INT $(pgrep -f benchmark_bcc.py)
```

Repeat with `benchmark_pythonbpf.py`.

### Files (vmdevnull)

- `benchmark_bcc.py` — BCC loader
- `benchmark_pythonbpf.py` — Python-BPF loader
- `openat_trace.bpf.c` — shared eBPF program

## Connections

- [[Python-BPF Compiler Limitations]] — defines the scope constraint for the Python-BPF benchmark program
- [[Architecture]] — Python-BPF pipeline stages being benchmarked
- [[PythonBPF Setup]] — environment setup required before running
