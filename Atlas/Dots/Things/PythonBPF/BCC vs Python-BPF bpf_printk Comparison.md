---
created: 2026-05-11
up:
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF bpf_printk]]"
  - "[[BCC vs Python-BPF Benchmark Plan]]"
  - "[[Architecture]]"
in:
  - "[[Atlas]]"
tags: [ebpf, bcc, python-bpf, bpf-printk, benchmark, strace, tracepoint, comparison, perf-flamegraph]
---

# BCC vs Python-BPF bpf_printk Comparison

Side-by-side comparison of a `sys_enter_write` tracepoint with `bpf_printk` in both frameworks, including `time -v` and `strace` methodology to observe compilation pipeline differences.

## Key Points

- Python-BPF uses `print(f"...")` + Python decorators; BCC uses an embedded C string with `bpf_printk("...", args)`
- Python-BPF forks `llc` (LLVM IR → BPF); BCC forks `clang` (C → BPF) — visible in `strace execve`
- BCC requires no explicit `LICENSE` declaration; Python-BPF requires `@bpfglobal def LICENSE()`
- Both read from `/sys/kernel/tracing/trace_pipe` — `trace_pipe()` vs `b.trace_print()`

## Details

### Side-by-Side Code

**Python-BPF:**
```python
from pythonbpf import bpf, section, bpfglobal, BPF
from pythonbpf.helper import pid, uid
from pythonbpf.utils import trace_pipe
from ctypes import c_void_p, c_int32

@bpf
@section("tracepoint/syscalls/sys_enter_write")
def hanndle_tp(ctx: c_void_p) -> c_int32:
    process_id = pid()
    user_id = uid()
    if user_id >= 999:
        print(f"Hello World from PID: {process_id}")
    return c_int32(0)

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

> Note: `uid` must be explicitly imported alongside `pid` — omitting it causes `NameError` at runtime.

**BCC equivalent:**
```python
from bcc import BPF

prog = r"""
#include <linux/bpf.h>

int handle_tp(void *ctx) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 process_id = (u32)pid_tgid;
    u32 uid = (u32)bpf_get_current_uid_gid();
    if (uid >= 999) {
        bpf_trace_printk("Hello World from PID: %d\n", process_id);
    }
    return 0;
}
"""

b = BPF(text=prog)
b.attach_tracepoint(tp="syscalls:sys_enter_write", fn_name="handle_tp")
b.trace_print()
```

**Trigger (run as a user with uid ≥ 999):**
```bash
echo "test" > /dev/null   # fires only when current uid >= 999
```

### Differences Table

| Aspect | Python-BPF | BCC |
|---|---|---|
| Program body | Python `@bpf` decorator | C string in Python |
| `bpf_printk` syntax | `print(f"... {var}")` | `bpf_trace_printk(fmt, sizeof(fmt), var)` |
| `pid` call | `pid()` helper | `bpf_get_current_pid_tgid()` + cast |
| `uid` call | `uid()` helper (import explicitly) | `bpf_get_current_uid_gid()` + cast |
| License | `@bpfglobal def LICENSE()` | Implicit |
| Trace output | `trace_pipe()` | `b.trace_print()` |
| Loader | `b.load()` + `b.attach_all()` | `b.attach_tracepoint(tp=..., fn_name=...)` |
| Compiler forked | `llc -march=bpf` | `clang -target bpf` |

### `time -v` Comparison

```bash
/usr/bin/time -v python3 hello_pythonbpf.py
/usr/bin/time -v python3 hello_bcc.py
```

Record from output:
```
Elapsed (wall clock) time:   X.XX       ← startup latency
Maximum resident set size:   XXXXX KB   ← peak memory
```

Ctrl+C after the first output line appears. `time -v` still prints the full summary on signal exit.

### `strace` Comparison

```bash
# Python-BPF — look for llc
strace -f -e trace=execve,bpf -o /tmp/strace_pythonbpf.log python3 hello_pythonbpf.py
grep execve /tmp/strace_pythonbpf.log | grep -v "python\|/bin\|/lib"

# BCC — look for clang
strace -f -e trace=execve,bpf -o /tmp/strace_bcc.log python3 hello_bcc.py
grep execve /tmp/strace_bcc.log | grep -v "python\|/bin\|/lib"

# Count bpf() syscalls
grep -c 'bpf(' /tmp/strace_pythonbpf.log
grep -c 'bpf(' /tmp/strace_bcc.log
```

**Actual discriminating signatures (from `strace_bcc_hello.log`):**

| Framework | Actual marker | Note |
|---|---|---|
| Python-BPF | `execve("llc", ["-march=bpf", "-filetype=obj", "-O2", ...]` | `llc` is forked as a child process |
| BCC | `openat(..., "/lib64/libclang-cpp.so.19.1", ...)` | Clang runs **in-process** as a shared library — no `execve(clang)` on modern BCC |

> Note: The `execve("/usr/bin/clang", ...)` signature only appears in older BCC (pre ~2021). On SUSE with BCC/LLVM 19, Clang is a library call, not a subprocess. The reliable discriminator is `openat` for `libclang-cpp.so`.

### Perf Flame Graph Comparison

Flame graphs answer **where CPU time is spent inside the process** — complementing `time -v` (total) and `strace` (syscalls).

Expected stories:
- **Python-BPF:** Python interpreter base → llvmlite IR emission → narrow `llc` spike
- **BCC:** Python bootstrap → massive `clang` block (C frontend + optimizer + BPF backend)

**Setup (one-time on vmdevnull):**
```bash
zypper install perf
git clone https://github.com/brendangregg/FlameGraph ~/FlameGraph
```

**Record + Generate:**
```bash
# Python-BPF
perf record -F 99 -g -- python3 hello_pythonbpf.py &
ppid=$!; sleep 3; kill -INT $ppid; wait $ppid


# BCC
perf record -F 99 -g -- python3 hello_bcc.py &
ppid=$!; sleep 3; kill -INT $ppid; wait $ppid
perf script | ~/FlameGraph/stackcollapse-perf.pl | \
    ~/FlameGraph/flamegraph.pl > /tmp/flame_bcc_dwarf.svg
```

Copy SVGs to view locally:
```bash
scp vmdevnull:/tmp/flame_pythonbpf.svg .
scp vmdevnull:/tmp/flame_bcc.svg .
```

**Actual findings (from `flame_pythonbpf.svg` and `flame_bcc.svg`):**

| Metric | Python-BPF | BCC |
|---|---|---|
| Total CPU samples | 433M | 9,270M (21× more) |
| Unique named frames | 59 | 525 |
| Max call stack depth | ~29 levels | ~139 levels |
| Compiler in flame graph | `llc` separate tower at 13.27% | `[libclang-cpp.so.19.1]` in-process at 12.15% |
| Widest `[unknown]` block | 73.21% (CPython, no frame ptrs) | 45.72% + many 5.58% layers (libclang, no frame ptrs) |
| Notable named frames | `_dl_map_object` 10.48%, page faults 10.48% | `clang::Sema::*`, `clang::Lexer::*`, `clang::Parser::*`, `llvm::StringMapImpl` 2.51% |

**Why BCC flame graph has so many `[unknown]` frames:**
`libclang-cpp.so.19.1` and `libLLVM.so.19.1` are distro release builds compiled with `-fomit-frame-pointer`. `perf record -g` uses frame-pointer unwinding by default — without `rbp` chains, the whole Clang call stack appears as `[unknown]`. The tower of 30+ layers all at ~5.58% is one single deep call chain sampled repeatedly that perf cannot name.

Fix: use DWARF-based unwinding instead:
```bash
perf record -F 99 -g --call-graph dwarf -- python3 hello_bcc.py
```
This reads `.eh_frame` from the ELF files and resolves the `clang::*` frames properly.

### Pyinstrument Call Tree (Python-BPF)

**Method:** Embedded `pyinstrument.Profiler()` wrapping `BPF()` + `b.load()` + `b.attach_all()`. `trace_pipe` runs via `subprocess.Popen` in a daemon thread for 10s then exits. `show_all=True` reveals pythonbpf library frames.

**BPF() total: 0.046s — breakdown:**

| Phase | Time | % of BPF() | Notes |
|---|---|---|---|
| `_run_llc` (llc subprocess) | 0.019s | 41% | Scalene invisible — child process |
| `inspect.stack()` in `BPF()` | 0.018s | 39% | `codegen.py:218` → `realpath/lstat/readlink` filesystem I/O |
| `compile_to_ir` (Python pipeline) | 0.008s | 17% | AST → llvmlite LLVM IR |
| `NamedTemporaryFile` + other | 0.001s | 3% | |

**Key finding: `inspect.stack()` costs as much as running `llc`.**

`BPF()` at `codegen.py:218` calls `inspect.getsource(inspect.stack()[1].frame)` to read the caller's source file. Pyinstrument traces this through `getouterframes → getframeinfo → findsource → getmodule → realpath → lstat → readlink` — filesystem I/O on every `BPF()` invocation, costing 0.018s.

**`compile_to_ir` sub-breakdown (0.008s total):**
- `processor` 0.006s → `func_proc` 0.002s → `process_bpf_chunk` → `eval_expr` → `ast.dump` (the unconditional dump bug)
- `parse` (ast.parse) 0.001s
- `vmlinux_proc` 0.001s
- `find_bpf_chunks` + `ast.dump` 0.001s each
- `finalize_module` → `re.sub` 0.001s
- `Module.__repr__` (llvmlite IR serialization) 0.001s

**Scalene blind spots confirmed by pyinstrument:**
- `_run_llc` (0.019s) — invisible to Scalene, child subprocess
- `inspect.stack()` (0.018s) — C extension syscalls (`lstat`, `readlink`), Scalene reports 0% Python

**`b.load()` and `b.attach_all()`: both 0.001s** — negligible; all bpf() syscall cost is in C extension.

```
BPF  pythonbpf/codegen.py:218                   0.046s
├─ _run_llc  pythonbpf/codegen.py:171           0.019s  (llc subprocess wall time)
├─ stack  inspect.py:1761                        0.018s  (caller source inspection overhead)
├─ compile_to_ir  pythonbpf/codegen.py:96       0.008s  (Python AST → LLVM IR)
└─ NamedTemporaryFile                            0.001s
```

### Metrics Table

| Metric | Python-BPF | BCC |
|---|---|---|
| Elapsed time | 0:04.35 | 0:10.57 (2.4×) |
| Max RSS (KB) | 51,656 | 189,404 (3.7×) |
| User CPU (s) | 0.15 | 2.93 (19.5×) |
| Sys CPU (s) | 0.03 | 0.31 (10.3×) |
| Minor page faults | 5,314 | 26,344 (5.0×) |
| Compiler invocation | `llc` (forked subprocess) | `libclang-cpp.so.19.1` (in-process) |
| `bpf()` syscall count | — | 4 (2 probes + 1 BTF + 1 tracepoint load) |

## Analysis: Why Python-BPF is Faster

Cross-referencing `time -v` results, `strace_bcc_hello.log`, and both flame graphs reveals three independent root causes.

### 1. RSS: subprocess vs in-process library (51 MB vs 189 MB)

**strace evidence:** BCC maps two enormous shared libraries into the python3 process:
- `libclang-cpp.so.19.1` → 74 MB mmap'd (line 1377)
- `libLLVM.so.19.1` → 124 MB mmap'd (line 1386)

That's ~198 MB of LLVM/Clang code pages inside the python3 address space, directly counted in its RSS.

Python-BPF forks `llc` as a **separate child process** — visible as its own tower in `flame_pythonbpf.svg` (13.27%). The `llc` process's memory never enters python3's RSS. Python3 only carries: Python interpreter + llvmlite + pythonbpf = 51 MB.

The 5× more minor page faults in BCC (26,344 vs 5,314) confirms this: those are OS faults triggered by demand-paging the Clang/LLVM library pages into RAM for the first time.

### 2. User CPU: header I/O + full C pipeline vs IR-only (2.93s vs 0.15s)

**strace evidence:** BCC runs the full Clang C compilation pipeline in-process:
- 2,342 `openat()` calls total; **2,160 of those open kernel header files** from `/usr/src/linux-6.12.0-160000.27/` — `compiler_types.h`, `compiler_attributes.h`, `compiler-clang.h`, `posix_types.h`, hundreds more
- 10,135 `read()` calls for processing those headers
- `KSyms::resolve_name` in flame graph (1.26%) — BCC reads `/proc/kallsyms` to resolve kernel symbol addresses

**Flame graph evidence:** `clang::Lexer::SkipBlockComment`, `clang::TokenLexer::ExpandFunctionArguments` (0.93%), `clang::Parser::ParseDeclarationSpecifiers`, `clang::Sema::BuildStmtExpr`, `clang::SourceManager::getFileIDLocal` (1.47%) — the entire C compilation front-end is visible and consuming CPU.

Python-BPF has **none of this**: Python AST → llvmlite LLVM IR is a direct translation. No C preprocessing, no header traversal, no Sema. `llc` starts from already-lowered IR so its backend work is minimal and runs in a separate process.

### 3. Elapsed time: compilation depth (4.35s vs 10.57s)

**Flame graph evidence:**
- BCC reaches **139 call stack levels** deep — the full Clang IR optimizer pass pipeline
- Python-BPF reaches only **29 levels** — shallow Python interpreter + brief llc fork

BCC's 21× more CPU samples (9.27B vs 433M) directly maps to more wall-clock time. The elapsed time gap (2.4×) is smaller than the user CPU gap (19.5×) because BCC's Clang runs at only 30% CPU utilization (`time -v`: "Percent of CPU this job got: 30%") — the rest is spent blocked on header file I/O. Python-BPF ran at only 4% CPU, mostly waiting for `trace_pipe`.

### Summary Table

| Root cause | Evidence source | Python-BPF | BCC |
|---|---|---|---|
| Compiler RSS | strace `mmap` sizes | `llc` in separate process, not counted | 71 MB libclang + 119 MB libLLVM in python3 RSS |
| Header I/O | strace `openat` count | 0 kernel headers | 2,160 header `openat()` calls |
| Compilation depth | flame graph stack depth | 29 levels | 139 levels |
| CPU pipeline | flame graph named frames | `llc` only | `clang::Lexer`, `::Parser`, `::Sema`, `::TokenLexer` |
| CPU samples | flame graph total | 433M | 9,270M (21×) |

## Connections

- [[Python-BPF bpf_printk]] — Python-BPF syntax and IR emission details
- [[BCC vs Python-BPF Benchmark Plan]] — full two-phase benchmark extending this comparison
- [[Architecture]] — Python-BPF pipeline stages (AST → llvmlite IR → llc) being compared here

## Result:
- pythonbpf
```
[](<(pythonbpf) localhost:~/pythonbpf/pythonbpf_coba # /usr/bin/time -v python3 hello_pythonbpf.py
            bash-530267  [000] ...21 1762820.940293: bpf_trace_printk: Hello World from PID: 530267

            bash-530267  [000] ...21 1762821.476610: bpf_trace_printk: Hello World from PID: 530267

            bash-530267  [000] ...21 1762821.925669: bpf_trace_printk: Hello World from PID: 530267

            bash-530267  [000] ...21 1762821.926283: bpf_trace_printk: Hello World from PID: 530267

            bash-530267  [000] ...21 1762821.926746: bpf_trace_printk: Hello World from PID: 530267

^CTracing stopped.
        Command being timed: "python3 hello_pythonbpf.py"
        User time (seconds): 0.15
        System time (seconds): 0.03
        Percent of CPU this job got: 4%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:04.35
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 51656
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 5314
        Voluntary context switches: 19
        Involuntary context switches: 145
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0>)
```

- BCC
```
[](<localhost:~/bcc_coba # /usr/bin/time -v python3 hello_bcc.py
b'            bash-530267  [000] ...21 1761772.292831: bpf_trace_printk: Hello World from PID: 530267'
b''
b'            bash-530267  [000] ...21 1761772.380273: bpf_trace_printk: Hello World from PID: 530267'
b''
b'            bash-530267  [000] ...21 1761772.518361: bpf_trace_printk: Hello World from PID: 530267'
b''
b'              ls-530411  [000] ...21 1761772.520846: bpf_trace_printk: Hello World from PID: 530411'
b''
b'            bash-530267  [000] ...21 1761772.521302: bpf_trace_printk: Hello World from PID: 530267'
b''
^CTraceback (most recent call last):
  File "/root/bcc_coba/hello_bcc.py", line 19, in %3Cmodule%3E
    b.trace_print()
    ~~~~~~~~~~~~~^^
  File "/usr/lib/python3.13/site-packages/bcc/__init__.py", line 1647, in trace_print
    line = self.trace_readline(nonblocking=False)
  File "/usr/lib/python3.13/site-packages/bcc/__init__.py", line 1627, in trace_readline
    line = trace.readline(1024).rstrip()
           ~~~~~~~~~~~~~~^^^^^^
KeyboardInterrupt
Command terminated by signal 2
        Command being timed: "python3 hello_bcc.py"
        User time (seconds): 2.93
        System time (seconds): 0.31
        Percent of CPU this job got: 30%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:10.57
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 189404
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 26344
        Voluntary context switches: 10
        Involuntary context switches: 2071
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0>)
```
