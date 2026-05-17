# BCC vs Python-BPF Benchmark Plan

## Context
Benchmarking the "Middle-Level Flow" of Python-BPF (AST translation) vs. BCC (Runtime C-compilation) to measure startup latency, translation overhead, and memory footprint.

## Critical Constraint
The eBPF program must be cleanly interruptible. No perf_buffer, ring_buffer, or continuous bpf_printk polling loops allowed. Need deterministic, triggerable execution.

## Selected Hook
tracepoint/syscalls/sys_enter_openat

## Why This Hook
- Zero polling (uses bpf_printk → kernel trace_pipe)
- Deterministic trigger: single `touch /tmp/bench_test` command fires exactly once
- Kernel struct access: `struct trace_event_raw_sys_enter` from vmlinux.h
- Clean interruption: loader blocks until SIGINT; no infinite loops

## Two-Phase Benchmark

### Phase A: Translation Overhead
Measure startup/translation phase with pristine profiling data.

### Phase B: Runtime Performance
Modify program to use BPF map counter instead of bpf_printk.
Flood events and measure throughput.

## Expected strace Signatures

| Framework | Expected execve Call | Translation Method |
|-----------|---------------------|-------------------|
| BCC | execve("/usr/bin/clang", ...) | C → BPF via Clang |
| Python-BPF | execve("llc", ...) | LLVM IR → BPF via llc |

## Key Difference
- BCC: Python string containing C → fork("clang") → compile C → BPF bytecode
- Python-BPF: Python decorators → AST → llvmlite IR → llc -march=bpf → BPF object file → pylibbpf loader

## Metrics to Record

| Metric | BCC | Python-BPF |
|--------|-----|-----------|
| Elapsed time | ___ | ___ |
| Max RSS (KB) | ___ | ___ |
| execve count | ___ | ___ |
| bpf() syscalls | ___ | ___ |
| Output observed? | YES/NO | YES/NO |

## Known Limitations of Python-BPF

### 1. ctx.args[] Array Access Not Supported
- vmlinux.py defines `args` as `ctypes.c_uint64 * 6`
- Parser detects it as `ctypes.Array`
- BUT: expr_pass.py has NO handler for `ast.Subscript` (the `[]` operator)
- Confirmed failing: `tests/test_config.toml` marks it as level="ir" failure

### 2. Atomic Map Operations Not Exposed
- Map API only has `lookup`, `update`, `delete`
- Binary operations use `builder.add` (non-atomic), not `atomicrmw`
- Workaround: read-update-write with race window

## File Locations
- BCC benchmark: benchmark_bcc.py
- Python-BPF benchmark: benchmark_pythonbpf.py
- Shared eBPF: openat_trace.bpf.c

## Execution Protocol (Remote Server, Root)

Terminal 1 (Run):
```bash
/usr/bin/time -v strace -f -e bpf,execve,mmap,openat -o strace.log python3 benchmark_bcc.py
```

Terminal 2 (Trigger & Interrupt):
```bash
sleep 2 && touch /tmp/bench_test && sleep 1 && kill -INT $(pgrep -f benchmark_bcc.py)
```

## References
- Eunomia-BPF notes in Ideaverse vault
- Python-BPF source at ~/low_level_programming/Python-BPF/
- vmlinux.py located at vmdevnull:~/pythonbpf/Python-BPF/vmlinux.py
