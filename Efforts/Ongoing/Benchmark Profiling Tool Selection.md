---
created: 2026-05-12
up:
  - "[[Efforts]]"
  - "[[eBPF MOC]]"
  - "[[Compare BCC and Python BPF]]"
related:
  - "[[BCC vs Python-BPF bpf_printk Comparison]]"
  - "[[pythonbpf-limitations-analysis]]"
  - "[[bpf-benchmark-plan]]"
  - "[[eBPF Tutorial - Hello World]]"
  - "[[eBPF Tutorial - Opensnoop]]"
  - "[[PythonBPF Setup]]"
in:
  - "[[Efforts/Ongoing]]"
tags:
  - benchmark
  - ebpf
  - profiling
  - python-bpf
  - bcc
  - scalene
  - pyinstrument
---

# Benchmark: Python-BPF vs BCC — Profiling Tool Selection

> [!summary]
> Empirical answer: no single tool is sufficient. The full picture requires five tools at different scopes: `/usr/bin/time -v` (total cost), `strace` (syscall layer), `perf + FlameGraph` (native stack), `Scalene --profile-all` (Python internals), `pyinstrument` embedded `Profiler()` (wall-clock call tree). Scalene's predicted "90% Python" split did not materialise — every BPF operation shows 0% Python time because all work is in C extensions and child processes. Pyinstrument revealed that `inspect.stack()` (0.018s) costs as much as running `llc` (0.019s) — a hidden overhead invisible to all other tools.

---

## Context

We are comparing the "Middle-Level Flow" of **Python-BPF** (AST-to-BPF translation) vs **BCC** (Runtime C-compilation). The objective is to provide empirical proof of the resource gap caused by BCC's C++ backend versus Python-BPF's pure-Python frontend.

**Critical constraint:** The eBPF program must be cleanly interruptible — no `perf_buffer`, `ring_buffer`, or continuous polling loops. We use `tracepoint/syscalls/sys_enter_openat` with deterministic `touch` triggering.

---

## Tool Scope Map (empirically derived)

Each tool answers a different question. No single tool covers all layers.

| Tool | Scope | Sees | Blind to |
|------|-------|------|----------|
| `/usr/bin/time -v` | Process total | Wall time, RSS, user/sys CPU, page faults | Where time is spent |
| `strace -f -e trace=execve,bpf,openat` | Syscall layer | File opens, bpf() calls, execve for child procs | Native CPU work |
| `perf record + FlameGraph` | Native stacks (in-process + kernel) | libclang/libLLVM/llc frames, kernel paths | Python bytecode layer |
| `Scalene --profile-all` | Python source lines | Which Python file/line, Python% vs native% vs sys% | Child subprocesses, C extension internals |
| **Pyinstrument** | Python call tree | Call tree with cumulative time | Native time, memory |
| **cProfile + Snakeviz** | Deterministic counts | Exact call counts | High overhead distorts fast operations |
| **Memray** | C-level allocations | `libbcc.so` heap | Python-BPF's Python-side allocations |

---

## Tool 1: `/usr/bin/time -v` — Total cost baseline

**Best for:** Proving the performance gap exists before explaining why.

Actual results (`time -v` on `hello_*.py`, Ctrl+C after first output):

| Metric | Python-BPF | BCC | Ratio |
|---|---|---|---|
| Elapsed | 0:04.35 | 0:10.57 | 2.4× |
| Max RSS (KB) | 51,656 | 189,404 | 3.7× |
| User CPU (s) | 0.15 | 2.93 | 19.5× |
| Sys CPU (s) | 0.03 | 0.31 | 10.3× |
| Minor page faults | 5,314 | 26,344 | 5.0× |

---

## Tool 2: `strace` — Syscall layer

**Best for:** Identifying what BCC and Python-BPF actually do at the OS boundary.

**Critical correction from actual run:** BCC does **not** `execve("/usr/bin/clang", ...)` on modern installs. It loads Clang as a shared library. The discriminating markers are:

| Framework | Actual marker |
|---|---|
| Python-BPF | `execve("llc", ["-march=bpf", ...])` — llc forked as child |
| BCC | `openat("/lib64/libclang-cpp.so.19.1")` — Clang runs in-process |

BCC strace stats (from `strace_bcc_hello.log`):
- 2,342 `openat()` calls total; **2,160 open kernel header files** from `/usr/src/linux-6.12.0/`
- 10,135 `read()` calls
- Only 4 `bpf()` syscalls: 2 probes + 1 BTF + 1 actual tracepoint load

---

## Tool 3: `perf record + FlameGraph` — Native stack

**Best for:** Seeing what libclang/libLLVM/llc actually do internally.

**Critical limitation:** Both `libclang-cpp.so` and `libLLVM.so` are distro release builds compiled with `-fomit-frame-pointer`. `perf record -g` (frame pointer mode) reports them as `[unknown]`. Fix:
```bash
perf record -F 99 -g --call-graph dwarf -- python3 hello_bcc.py
```

Actual findings from `flame_bcc.svg` and `flame_pythonbpf.svg`:

| Metric | Python-BPF | BCC |
|---|---|---|
| Total CPU samples | 433M | 9,270M (21×) |
| Stack depth | ~29 levels | ~139 levels |
| Compiler in graph | `llc` tower at 13.27% | `[libclang-cpp.so]` at 12.15% |
| Named Clang frames | none (child proc) | `clang::Sema::*`, `clang::Lexer::*`, `clang::Parser::*` |

---

## Tool 4: Scalene `--profile-all` — Python internals

**Selection confidence:** 0.92 → revised to **0.65** (scope more limited than expected)

### What was predicted vs what actually happened

**Predicted (pre-empirical):**
- BCC: ~80% native, ~20% Python
- Python-BPF: ~90% Python, ~10% native

**Actual (from `scalene-pipeline.json`, 30 × `compile_to_ir()`):**

| Source | CPU% | What it is |
|---|---|---|
| `ast.py` | **48.1%** | Python AST traversal + `ast.dump()` |
| `logging/__init__.py` | **33.3%** | Logging I/O overhead |
| `llvmlite/ir/values.py` | 7.4% | LLVM metadata hashing |
| `llvmlite/ir/instructions.py` | 7.4% | IR instruction serialization |
| `structs_pass.py` | 3.7% | Struct decorator detection |
| `expr_pass.py`, `vmlinux_proc`, `bpf_helper_handler` | **0%** | Too fast for hello-world to sample |

**Why `%python = 0%` for everything:** Scalene uses statistical sampling. When individual lines run in microseconds, Python bytecode evaluation is too brief to be sampled. All BPF operations are C extensions — Scalene sees duration but not Python frames.

**Why Scalene missed most of the work:**
- `b = BPF()` triggers ALL compilation (AST → LLVM IR → llc), but it is attributed to library code outside the script file
- `--profile-all` is required to see into `pythonbpf/` library files
- `llc` subprocess CPU is permanently invisible — perf is required for that layer

### What Scalene uniquely revealed

1. **`ast.dump()` called unconditionally** — `codegen.py:73` evaluates `ast.dump(tree, indent=4)` before passing to logger, even when DEBUG is disabled. Accounts for ~23% of Python-visible CPU. Fix: guard with `if logger.isEnabledFor(logging.DEBUG):`

2. **Logging is the #1 Python-side cost** (33%) — 30× `logger.info()` calls per compilation (timestamps, file paths) dominate over actual compilation logic. Suppressed with `loglevel=logging.WARNING`.

3. **Compilation passes are near-zero for simple programs** — `expr_pass.py`, `vmlinux_exports_handler.py` only become hot for complex BPF programs with maps, vmlinux types, and many helpers.

### Correct Scalene invocation

```bash
# Profile Python compilation pipeline only (no llc, no sleep)
scalene --profile-all --cpu-only --json --outfile scalene-pipeline.json \
    scalene_compile_bench.py
```

Do not profile BCC with Scalene — BCC's work is entirely in `libclang-cpp.so` (C extension), which Scalene cannot see inside.

---

## Tool 5: Pyinstrument — Python call tree

**Selection confidence:** 0.88 → **empirically validated 0.91**

**Method:** Embedded `pyinstrument.Profiler()` inside the script, wrapping `BPF()` + `b.load()` + `b.attach_all()`. `trace_pipe` runs via `subprocess.Popen` in a daemon thread for 10s. `show_all=True` reveals pythonbpf library frames (hidden by default).

**Actual findings (from `hello_pythonbpf_pyinstrument.py`, 1 invocation):**

| Phase | Time | % of BPF() |
|---|---|---|
| `_run_llc` subprocess | 0.019s | 41% |
| `inspect.stack()` overhead | 0.018s | 39% |
| `compile_to_ir` Python pipeline | 0.008s | 17% |
| Other | 0.001s | 3% |
| **BPF() total** | **0.046s** | 100% |
| `b.load()` + `b.attach_all()` | 0.001s each | negligible |

**What Pyinstrument uniquely revealed:**

1. **`inspect.stack()` costs as much as `llc`** — `BPF()` at `codegen.py:218` calls `inspect.getsource(inspect.stack()[1].frame)` every invocation. Pyinstrument traces it through `realpath → lstat → readlink` (filesystem I/O), costing 0.018s. Scalene reported 0% for this (C extension syscalls).

2. **`_run_llc` wall time now visible: 0.019s** — Scalene could not see this (child subprocess). Pyinstrument confirms the llc backend takes 41% of total BPF() time.

3. **Python AST pipeline is only 17% of BPF() time** — `compile_to_ir` (0.008s) is fast. The bottleneck is external: llc subprocess and inspect overhead, not the Python compilation passes.

**Call tree summary:**
```
BPF  codegen.py:218                  0.046s
├─ _run_llc  codegen.py:171          0.019s  (llc subprocess wall time)
├─ stack  inspect.py:1761            0.018s  (caller source inspection)
├─ compile_to_ir  codegen.py:96      0.008s  (Python AST → LLVM IR)
└─ NamedTemporaryFile                0.001s
```

**Note on CLI vs programmatic:** Running `pyinstrument script.py` wraps the whole script — `time.sleep(10)` dominates (10.000s) and the 0.046s BPF() becomes invisible. The embedded `Profiler()` API is required to isolate the compilation phase.

---

## Tool Selection by Question

| Question | Right tool |
|---|---|
| How much slower/heavier is BCC overall? | `/usr/bin/time -v` |
| Does BCC fork clang or use a library? | `strace -e trace=execve,openat` |
| What does Clang do inside BCC? | `perf record --call-graph dwarf + FlameGraph` |
| Which Python-BPF compilation pass is slow? | `scalene --profile-all` |
| How long does `_run_llc()` take wall-clock? | `pyinstrument` (embedded `Profiler()`) |
| What overhead does `inspect.stack()` add? | `pyinstrument` (embedded `Profiler()`) |
| How much memory does BCC allocate at C level? | `memray` |

---

## Actual Results Signature (empirical)

| Metric | Python-BPF | BCC | Source |
|---|---|---|---|
| Elapsed | 0:04.35 | 0:10.57 | `time -v` |
| Max RSS | 51,656 KB | 189,404 KB | `time -v` |
| User CPU | 0.15s | 2.93s | `time -v` |
| Compiler invocation | `execve("llc")` (child) | `openat(libclang-cpp.so)` (in-process) | `strace` |
| Kernel headers read | 0 | 2,160 files | `strace openat` count |
| bpf() syscalls | — | 4 total | `strace` |
| CPU samples (perf) | 433M | 9,270M | `perf + FlameGraph` |
| Stack depth | 29 levels | 139 levels | `perf + FlameGraph` |
| Python-visible bottleneck | logging I/O 33%, `ast.dump()` 23% | not applicable (C extension) | `scalene --profile-all` |
| BPF() total wall time | 0.046s | — | `pyinstrument` (embedded Profiler) |
| `_run_llc` wall time | 0.019s (41% of BPF()) | — | `pyinstrument` |
| `inspect.stack()` overhead | 0.018s (39% of BPF()) | — | `pyinstrument` |
| `compile_to_ir` Python pipeline | 0.008s (17% of BPF()) | — | `pyinstrument` |

---

## Connections

- [[BCC vs Python-BPF bpf_printk Comparison]] — Full analysis with strace, flame graph, and time -v results
- [[pythonbpf-limitations-analysis]] — Code-level analysis of `ctx.args[]` and atomic operation gaps
- [[bpf-benchmark-plan]] — Full benchmark protocol with terminal commands
- [[Compare BCC and Python BPF]] — Main effort tracking file

---

*Created: 2026-05-12 | Updated: 2026-05-12 (pyinstrument findings added)*
*Status: Empirically validated*
