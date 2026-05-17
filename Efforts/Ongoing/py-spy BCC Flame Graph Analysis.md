---
created: 2026-05-13
up:
  - "[[Compare BCC and Python BPF]]"
  - "[[Benchmark Profiling Tool Selection]]"
related:
  - "[[py-spy Flame Graph Analysis]]"
  - "[[pythonbpf-limitations-analysis]]"
  - "[[bpf-benchmark-plan]]"
  - "[[perf Call Flow Tracking for Benchmark]]"
in:
  - "[[Efforts/Ongoing]]"
tags:
  - benchmark
  - ebpf
  - py-spy
  - bcc
  - flame-graph
  - profiling
  - call-stack
  - todo
---

# py-spy BCC Flame Graph Analysis

> [!summary]
> Planned py-spy flame graph capture for BCC (Runtime C-compilation) benchmark. Will compare with Python-BPF flame graph to demonstrate Clang fork overhead vs pure-Python AST translation.

---

## Status

| Item | Status | Notes |
|------|--------|-------|
| **Benchmark code** | Draft | Placeholder tracepoint — to be decided |
| **py-spy execution** | Pending | Requires `--subprocesses` to see Clang |
| **Flame graph analysis** | Pending | Awaiting results |
| **Comparison with Python-BPF** | Pending | Will update after both complete |

---

## Benchmark Code

**File:** `benchmark_bcc.py` (draft — tracepoint TBD)

```python
from bcc import BPF

# eBPF program (tracepoint to be decided)
prog = """
#include <uapi/linux/ptrace.h>

struct trace_event_raw_sys_enter {
    unsigned long long unused;
    long id;
    unsigned long args[6];
};

int trace_{tracepoint}(struct trace_event_raw_sys_enter *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    bpf_printk("BCC pid=%d\\n", pid);
    return 0;
}
"""

# Phase 1: Parse C string, fork Clang, compile to BPF bytecode
# Phase 2: Load into kernel via bpf() syscall
b = BPF(text=prog)

# Phase 3: Attach to tracepoint
b.attach_tracepoint(tp="syscalls:sys_enter_{tracepoint}", fn_name="trace_{tracepoint}")

# Phase 4: Block reading trace_pipe
try:
    b.trace_print()
except KeyboardInterrupt:
    pass
```

---

## py-spy Execution

### Command

```bash
# Terminal 1: Record with subprocess visibility
sudo py-spy record --subprocesses -o bcc_flame.svg -- python3 benchmark_bcc.py

# Terminal 2: Trigger and stop
sleep 2 && touch /tmp/bench_test && sleep 1 && \
sudo kill -INT $(pgrep -f benchmark_bcc)
```

**Why `--subprocesses`:** BCC forks `/usr/bin/clang` to compile C to BPF bytecode. Without this flag, py-spy only sees the Python parent process waiting for Clang.

---

## Expected Flame Graph Structure

### Anticipated Call Flow

```
&lt;module&gt; (benchmark_bcc.py)
  ├── import bcc (5%)
  │     └── _find_and_load → exec_module
  │
  ├── b = BPF() (15% Python wrapper)
  │     ├── BPF.__init__ (bcc/__init__.py)
  │     ├── libbcc.so!bpf_prog_load (native)
  │     └── subprocess.Popen("/usr/bin/clang") ← FORK
  │
  ├── Clang compilation (70% — in subprocess)
  │     ├── clang::driver::Driver::ExecuteCompilation
  │     ├── clang::FrontendAction::Execute
  │     ├── clang::ParseAST
  │     └── LLVMCodeGen → BPF bytecode
  │
  ├── b.attach_tracepoint() (2%)
  │     └── bpf() syscall
  │
  └── b.trace_print() (8%)
        └── subprocess → read /sys/kernel/debug/tracing/trace_pipe
```

### Expected py-spy Frames

| Phase | Expected Functions | Est. % |
|-------|-------------------|--------|
| **Import** | `_find_and_load`, `_load_unlocked`, `exec_module` | ~5% |
| **BPF() wrapper** | `BPF.__init__`, `libbcc` Python bindings | ~15% |
| **Clang compile** | `clang::` C++ symbols (subprocess) | ~70% |
| **Attach** | `attach_tracepoint` | ~2% |
| **trace_print** | `trace_print`, `subprocess` read | ~8% |

---

## Key Comparison Points (vs Python-BPF)

| Aspect | BCC (Expected) | Python-BPF (Actual) |
|--------|---------------|-------------------|
| **Translation** | C → Clang → BPF bytecode | Python AST → llvmlite IR → llc |
| **Subprocess** | `execve("/usr/bin/clang")` | `execve("llc")` |
| **Python time** | ~20% (wrapper only) | ~90% (pure Python) |
| **Native time** | ~80% (Clang compilation) | ~10% (llc brief) |
| **Import overhead** | ~5% | ~40% |
| **Blocking** | `trace_print()` ~8% | `trace_pipe()` ~36% |

---

## Mermaid Diagram (Planned)

```mermaid
graph TD
    subgraph "BCC (Expected)"
        A1[import bcc] -->|5%| B1[_find_and_load]
        B1 --> C1[BPF.__init__]
        C1 -->|15%| D1[libbcc.so wrapper]
        D1 --> E1[fork "clang"]
        E1 -->|70%| F1[clang::FrontendAction]
        F1 --> G1[LLVMCodeGen]
        C1 -->|2%| H1[attach_tracepoint]
        C1 -->|8%| I1[trace_print block]
    end

    subgraph "Python-BPF (Actual)"
        A2[import pythonbpf] -->|40%| B2[_find_and_load]
        B2 --> C2[BPF.__init__]
        C2 -->|13%| D2[inspect.stack]
        C2 -->|13%| E2[compile_to_ir]
        E2 --> F2[processor/func_proc]
        C2 -->|9%| G2[BPF.load]
        C2 -->|36%| H2[trace_pipe block]
    end
```

*Note: This diagram will be updated with actual data after py-spy capture.*

---

## Tracepoint Selection (TBD)

**Options:**
- `sys_enter_openat` — Matches Python-BPF benchmark, deterministic `touch` trigger
- `sys_enter_write` — Used in earlier test, very noisy (every terminal character)
- `sys_enter_clone` — From Python-BPF GitHub example

**Decision pending.** Will update this note once tracepoint is selected.

---

## Next Steps

1. [ ] **Select tracepoint** — User decision required
2. [ ] **Run py-spy** — Execute: `sudo py-spy record --subprocesses -o bcc_flame.svg -- python3 benchmark_bcc.py`
3. [ ] **Extract frames** — Parse `bcc_flame.svg` for function names
4. [ ] **Create mapping** — Line-by-line code → flame graph correspondence
5. [ ] **Update comparison** — Add to [[Compare BCC and Python BPF]] side-by-side table

---

## Related Notes

- [[py-spy Flame Graph Analysis]] — Completed Python-BPF flame graph (22 samples)
- [[Compare BCC and Python BPF]] — Main effort tracking (will receive comparison update)
- [[Benchmark Profiling Tool Selection]] — Tool rationale and pairing strategy
- [[pythonbpf-limitations-analysis]] — Python-BPF AST gap analysis
- [[bpf-benchmark-plan]] — Execution protocol and terminal commands
- [[perf Call Flow Tracking for Benchmark]] — perf workflow documentation

---

*Created: 2026-05-13*
*Status: Draft — Awaiting tracepoint selection and py-spy execution*
*Tool: py-spy v0.3.14 with `--subprocesses`*
