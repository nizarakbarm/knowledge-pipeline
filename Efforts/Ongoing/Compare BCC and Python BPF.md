---
created: 2026-05-12
up:
  - "[[Efforts]]"
  - "[[eBPF MOC]]"
related:
  - "[[Benchmark Profiling Tool Selection]]"
  - "[[pythonbpf-limitations-analysis]]"
  - "[[bpf-benchmark-plan]]"
  - "[[PythonBPF Setup]]"
  - "[[BCC eBPF]]"
in:
  - "[[Efforts/Ongoing]]"
tags:
  - benchmark
  - ebpf
  - bcc
  - python-bpf
  - comparison
  - performance
---

# Compare BCC and Python BPF

> [!summary]
> Active effort to benchmark the "Middle-Level Flow" of Python-BPF (AST translation) vs BCC (Runtime C-compilation). Measuring startup latency, translation overhead, and memory footprint.

---

## Objective

Provide empirical proof of the resource gap caused by BCC's C compilation via Clang versus Python-BPF's pure-Python frontend.

## Status

| Phase | Status | Notes |
|-------|--------|-------|
| **Program Design** | Complete | `tracepoint/syscalls/sys_enter_openat` selected |
| **Tool Selection** | Complete | See [[Benchmark Profiling Tool Selection]] |
| **BCC Implementation** | Pending | `benchmark_bcc.py` |
| **Python-BPF Implementation** | Pending | `benchmark_pythonbpf.py` |
| **Execution** | Pending | Run on vmdevnull |
| **perf Call Flow** | Complete | See [[perf Call Flow Tracking for Benchmark]] |
| **py-spy Python-BPF** | Complete | See [[py-spy Flame Graph Analysis]] |
| **py-spy BCC** | Complete | See [[py-spy BCC Flame Graph Analysis]] |
| **Deep Analysis** | Complete | See [[py-spy BCC vs Python-BPF Deep Analysis]] — line-by-line comparison |
| **Analysis** | Complete | 415 BCC samples vs 22 Python-BPF samples compared |

---

## Key Findings So Far

### Python-BPF Limitations Discovered

1. **`ctx.args[]` not supported** — `expr_pass.py` lacks `ast.Subscript` handler
2. **Atomic operations not exposed** — Map API uses non-atomic `builder.add`

Full analysis: [[pythonbpf-limitations-analysis]]

### Expected Signatures

| Framework | Translation | Memory | Native Overhead |
|-----------|-------------|--------|-----------------|
| **BCC** | `fork("clang")` → C compilation | 50-100 MB | High (C++ backend) |
| **Python-BPF** | AST → llvmlite IR → `llc` | <20 MB | Low (pure Python) |

---

## Metrics Collection Table

| Metric | BCC | Python-BPF | Delta |
|--------|-----|-----------|-------|
| **Elapsed (wall clock)** | ___ sec | ___ sec | BCC - PyBPF |
| **User CPU time** | ___ sec | ___ sec | |
| **System CPU time** | ___ sec | ___ sec | |
| **Max RSS (KB)** | ___ KB | ___ KB | |
| **Minor page faults** | ___ | ___ | |
| **Major page faults** | ___ | ___ | |
| **Voluntary ctx switches** | ___ | ___ | |
| **bpf() syscall count** | ___ | ___ | |
| **execve("clang")** | YES / NO | YES / NO | |
| **execve("llc")** | YES / NO | YES / NO | |
| **Output observed?** | YES / NO | YES / NO | |

---

## Sub-Efforts

- [[Benchmark Profiling Tool Selection]] — Scalene + Pyinstrument rationale
- [[pythonbpf-limitations-analysis]] — Code-level analysis of Python-BPF gaps
- [[bpf-benchmark-plan]] — Execution protocol and terminal commands

---

## References

- [[eBPF Tutorial - Hello World]] — Tracepoint basics with `bpf_printk`
- [[eBPF Tutorial - Opensnoop]] — `sys_enter_openat` with struct access
- [[PythonBPF Setup]] — Python-BPF installation and API
- [[BCC eBPF]] — BCC framework notes

---

*Created: 2026-05-12*
*Status: In Progress*
*Next Action: Implement benchmark scripts*
