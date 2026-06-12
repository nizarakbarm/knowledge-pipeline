---
created: 2025-04-17
up:
  - "[[Things]]"
in:
  - "[[Atlas/Maps/Maps]]"
tags:
  - moc
  - ebpf
  - systems
  - linux
---

# eBPF MOC

A Map of Content for eBPF (extended Berkeley Packet Filter) knowledge — kernel-level programmable tracing, networking, and observability.

## Core Concepts
- [[eBPF CO-RE Overview]] — Compile Once – Run Everywhere, verifier, JIT, tracepoints
- [[eBPF Hello World Tutorial]] — Minimal tracepoint program with ecc/ecli toolchain

## Frameworks & Tools
- [[BCC]] — BPF Compiler Collection: architecture, tools, runtime compilation
- [[PythonBPF]] — Main overview: architecture, installation, design rationale
- [[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]] — BPF_CORE_READ, ProbeVisitor AST rewriting, LLVM IR generation
- [[PythonBPF Setup]] — Platform-specific installation (OpenSUSE, etc.)
- [[Python-BPF Compiler Limitations]] — Confirmed AST→IR gaps: missing ast.Subscript handler, non-atomic builder.add
- [[Python-BPF bpf_printk]] — Using print() as bpf_printk, trace_pipe reading, 3-arg limit
- [[BCC vs Python-BPF bpf_printk Comparison]] — Side-by-side code, time -v and strace methodology
- [[BCC vs Python-BPF Benchmark Plan]] — Two-phase performance benchmark on sys_enter_openat tracepoint
- [[Benchmark Profiling Tool Selection]] — Scalene + Pyinstrument rationale for measuring translation overhead
- [[Compare BCC and Python BPF]] — Active effort tracking and metrics collection
- [[perf Call Flow Tracking for Benchmark]] — Using `perf` + `PYTHONPERFSUPPORT=1` for call chain validation
- [[py-spy Flame Graph Analysis]] — Line-by-line mapping of Python-BPF execution (22 samples)
- [[py-spy BCC Flame Graph Analysis]] — BCC flame graph plan and execution
- [[py-spy BCC vs Python-BPF Deep Analysis]] — Deep analysis: BCC 93.98% C++ backend vs Python-BPF 27% AST translation
- [[run_perf_benchmark.sh]] — Automated benchmark execution script

### Security & Enforcement
- [[Tetragon Overview]] — Cilium Tetragon: real-time eBPF-based security observability & runtime enforcement
- [[Tetragon TracingPolicy]] — User-defined eBPF policies for kernel-level security observability, filtering & runtime enforcement
## Related Topics
- [[LLVM MOC]] — LLVM compiler infrastructure used for eBPF bytecode generation
- [[Systems MOC (kit)]] — Complex systems and emergent behavior
- [[Things]] — All things in the Ideaverse

## Questions
- How does BTF encoding work at the binary level?
- What are the performance implications of CO-RE relocations?
- How does `ecc` differ from `clang` + `llvm-strip`?
