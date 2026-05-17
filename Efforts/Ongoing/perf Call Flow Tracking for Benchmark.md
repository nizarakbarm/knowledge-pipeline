---
created: 2026-05-12
up:
  - "[[Compare BCC and Python BPF]]"
  - "[[Benchmark Profiling Tool Selection]]"
related:
  - "[[pythonbpf-limitations-analysis]]"
  - "[[bpf-benchmark-plan]]"
  - "[[run_perf_benchmark.sh]]"
in:
  - "[[Efforts/Ongoing]]"
tags:
  - benchmark
  - ebpf
  - perf
  - profiling
  - call-stack
  - python-3.13
  - linux-perf
---

# perf Call Flow Tracking for Benchmark

> [!summary]
> Using `perf` with `PYTHONPERFSUPPORT=1` (Python 3.13+) to trace calling flow in both BCC and Python-BPF. Validates Scalene's Python vs Native split with actual function call chains.

---

## Objective

Use Linux `perf` to capture **complete call chains** (Python + Native) for both frameworks:

- **BCC**: Trace `BPF()` → `libbcc.so` → `fork("clang")` → C++ compilation
- **Python-BPF**: Trace `BPF()` → `compile_to_ir()` → AST traversal → `_run_llc()` → `llc` subprocess

This provides qualitative validation of Scalene's quantitative Python vs Native split.

---

## Python 3.13.13 Advantage

Python 3.12+ introduced **PEP 669** (`sys.monitoring`) and **`PYTHONPERFSUPPORT=1`**:

- Emits DWARF unwind info for Python frames
- `perf` symbolizes Python functions natively (no `py-spy` needed)
- Enables seeing Python-BPF's AST traversal chain:
  ```
  compile_to_ir → processor → vmlinux_proc → maps_proc → eval_expr → _handle_attribute_expr
  ```

**Without this:** `perf` collapses all Python execution into `PyEval_EvalFrameDefault`

---

## Tool Comparison

| Tool | Captures | Best For | Limitation |
|------|----------|----------|------------|
| **Scalene** | Python vs Native time split + memory | Quantitative comparison | No deep call chains |
| **perf + PYTHONPERFSUPPORT** | Full call chains (Python + Native) | Qualitative validation | Sampled (~4kHz), may miss brief calls |
| **pyinstrument** | Statistical Python call tree | Detailed Python timing | Limited native visibility |

**Recommended pairing:**
- **Scalene** = primary (quantifies the bloat)
- **perf** = secondary (validates *which* functions cause it)

---

## BCC Execution

### Command

```bash
sudo perf record -g --call-graph=fp \
  -e cycles,instructions \
  python3 benchmark_bcc.py
```

### Terminal 2: Trigger and Stop

```bash
sleep 2 && touch /tmp/bench_test && sleep 1 && \
sudo kill -INT $(pgrep -f benchmark_bcc)
```

### Expected Call Chain

```
python3
  → BPF.__init__
    → BPF._trace_autoload
      → libbcc.so!bpf_prog_load
        → (kernel bpf() syscall)
      → fork()
        → execve("/usr/bin/clang", ...)
          → clang::driver::Driver::ExecuteCompilation
            → clang::FrontendAction::Execute
              → LLVMCodeGen
                → BPF bytecode generation
```

**Key insight:** The `fork() → execve("clang")` chain is the smoking gun for BCC's C++ backend bloat.

---

## Python-BPF Execution

### Command

```bash
sudo PYTHONPERFSUPPORT=1 perf record -g --call-graph=lbr \
  -e cycles,instructions \
  python3 benchmark_pythonbpf.py
```

### Terminal 2: Trigger and Stop

```bash
sleep 2 && touch /tmp/bench_test && sleep 1 && \
sudo kill -INT $(pgrep -f benchmark_pythonbpf)
```

### Expected Call Chain

```
python3
  → pythonbpf.codegen.BPF.__init__
    → pythonbpf.codegen.compile_to_ir
      → pythonbpf.codegen.processor
        → pythonbpf.vmlinux_parser.vmlinux_proc
        → pythonbpf.maps.maps_proc
        → pythonbpf.expr.expr_pass.eval_expr
          → _handle_attribute_expr      (works for ctx.id)
          → _handle_name_expr
          → _handle_constant_expr
        → pythonbpf.codegen._run_llc
          → execve("llc", ...)
            → (LLVM IR → BPF object file)
    → pylibbpf.BpfObject.__init__
      → bpf_obj_open
      → bpf_object__load
```

**Key insight:** Pure Python AST traversal → single `llc` subprocess. No Clang fork.

---

## Analysis Commands

### Interactive Report

```bash
# BCC
sudo perf report -g --stdio -i ./perf_results_*/bcc/perf.data

# Python-BPF
sudo perf report -g --stdio -i ./perf_results_*/pythonbpf/perf.data
```

### Export Call Flow

```bash
# Export to text for parsing
sudo perf script -g -i ./perf_results_*/bcc/perf.data > bcc_callflow.txt
sudo perf script -g -i ./perf_results_*/pythonbpf/perf.data > pythonbpf_callflow.txt
```

### Filter for Key Functions

```bash
# BCC: Find Clang compilation
grep -E "clang::|libbcc|fork|execve|bpf_prog_load" bcc_callflow.txt

# Python-BPF: Find AST traversal
grep -E "pythonbpf\.|compile_to_ir|_run_llc|eval_expr|llc|execve" pythonbpf_callflow.txt
```

---

## Runnable Script

See: [[run_perf_benchmark.sh]] — Automated execution of both benchmarks with results aggregation.

**Usage:**
```bash
cd ~/benchmark
cp /path/to/run_perf_benchmark.sh ./
sudo bash run_perf_benchmark.sh
```

**Outputs:**
```
perf_results_YYYYMMDD_HHMMSS/
├── bcc/
│   ├── perf.data
│   ├── callflow.txt
│   ├── report.txt
│   └── key_functions.txt
├── pythonbpf/
│   ├── perf.data
│   ├── callflow.txt
│   ├── report.txt
│   └── key_functions.txt
└── comparison_report.txt
```

---

## Troubleshooting: Perf Map Timing

### Problem

`PYTHONPERFSUPPORT=1` creates `/tmp/perf-PID.map` **lazily** — only after Python starts executing bytecode, not at process startup. Immediate `cp` after `&` fails:

```bash
python3 hello_pythonbpf.py &   # Returns immediately
PY_PID=$!
cp /tmp/perf-${PY_PID}.map     # FAILS — Python hasn't started yet
```

### Solution: Wait for Map Creation

```bash
# Run in background
PYTHONPERFSUPPORT=1 python3 hello_pythonbpf.py &
PY_PID=$!

# Wait for Python to ACTUALLY START (not just fork)
sleep 3

# Check if map exists
ls -la /tmp/perf-${PY_PID}.map

# Copy once confirmed
cp /tmp/perf-${PY_PID}.map /tmp/pythonbpf_perf.map
```

### Verified: Python 3.13.13 on vmdevnull

```bash
# Python has perf support compiled in
python3 -c "import sysconfig; print(sysconfig.get_config_var('PY_HAVE_PERF_TRAMPOLINE'))"
# Output: 1

# Map files are created (check while process runs)
ls -la /tmp/perf-*.map
# Output: -rw-------. 1 root root 119486 May 13 08:37 /tmp/perf-614299.map
```

---

## Alternative: py-spy (Recommended)

Since perf map timing is tricky and `call-graph=lbr` may not be supported on all hardware, **py-spy** is the more reliable alternative.

### Installation

```bash
# Method 1: pip
pip install py-spy

# Method 2: Pre-built binary
curl -LO https://github.com/benfred/py-spy/releases/download/v0.3.14/py-spy-v0.3.14-x86_64-unknown-linux-gnu.tar.gz
tar xzf py-spy-*.tar.gz
sudo mv py-spy /usr/local/bin/
```

### Usage: Record Flame Graph

```bash
# Terminal 1: Record Python-BPF call flow
sudo py-spy record -o pythonbpf_flame.svg -- python3 hello_pythonbpf.py

# Terminal 2: Trigger and stop
sleep 2 && touch /tmp/bench_test && sleep 1 && \
sudo kill -INT $(pgrep -f hello_pythonbpf)
```

### Usage: Live Top View

```bash
# See Python functions in real-time
sudo py-spy top --pid $(pgrep -f hello_pythonbpf)
```

### What py-spy Shows

| Function | Where It Lives | Expected % |
|----------|---------------|------------|
| `trace_pipe` | `pythonbpf/utils.py` | ~50-70% |
| `BPF.load` | `pythonbpf/codegen.py` | ~10-15% |
| `BPF.attach_all` | `pylibbpf` bindings | ~5-10% |
| `compile_to_ir` | `pythonbpf/codegen.py` | ~5-10% |
| `processor` | `pythonbpf/codegen.py` | ~3-5% |
| `eval_expr` | `pythonbpf/expr/expr_pass.py` | ~2-3% |

**Advantages:**
- No perf map files needed
- No timing issues
- Shows Python function names directly
- Works regardless of `PYTHONPERFSUPPORT`

---

## Tracepoint Selection Warning

**`sys_enter_write` is too noisy** — it fires on every terminal character, prompt redraw, and command:

```
tty-615337, uname-615339, tput-615356, bash-615335, ip-615361...
```

Every shell command triggers `sys_enter_write`, polluting the trace with constant activity.

**Recommended for benchmarking:** Use **`sys_enter_openat`** from the benchmark plan:
- Only fires on file opens
- Deterministic trigger: `touch /tmp/bench_test`
- Clean, isolated events

---

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Sampled profiling** (~4kHz) | May miss brief function calls | Increase sample rate: `perf record -F 9999` |
| **Requires root** | Security consideration | Run on isolated benchmark VM |
| **Python frame overhead** | `PYTHONPERFSUPPORT` adds minor overhead | Negligible compared to translation time |
| **LBR depth limit** | `call-graph=lbr` limited to ~16 frames | Use `call-graph=fp` or `call-graph=dwarf` |
| **Perf map timing** | Map created lazily after process start | Wait 3s before copying, or use py-spy |
| **Tracepoint noise** | `sys_enter_write` fires constantly | Use `sys_enter_openat` instead |

---

## Integration with Scalene

**Workflow:**

1. **Scalene** (primary): Quantifies Python vs Native time split
   ```bash
   scalene --cli --cpu --memory benchmark_bcc.py
   scalene --cli --cpu --memory benchmark_pythonbpf.py
   ```

2. **perf** (validation): Confirms *which specific functions* consume that time
   ```bash
   sudo PYTHONPERFSUPPORT=1 perf record -g -- python3 benchmark_pythonbpf.py
   ```

3. **Comparison**: Map Scalene's "Python time" to specific `pythonbpf.*` functions in perf output

---

## Expected Results

| Framework | Top Native Function | Top Python Function | Native % |
|-----------|-------------------|-------------------|----------|
| **BCC** | `clang::ExecuteCompilerInvocation` | `BPF.__init__` | ~80% |
| **Python-BPF** | `llc` (brief) | `compile_to_ir` | ~10% |

---

## Related Notes

- [[Compare BCC and Python BPF]] — Main effort tracking and metrics collection
- [[Benchmark Profiling Tool Selection]] — Scalene + Pyinstrument rationale
- [[pythonbpf-limitations-analysis]] — Code-level analysis of Python-BPF gaps
- [[bpf-benchmark-plan]] — Execution protocol and terminal commands
- [[BCC vs Python-BPF bpf_printk Comparison]] — Side-by-side code comparison

---

*Created: 2026-05-12*
*Status: Ready for execution*
*Python Version Required: 3.12+ (3.13.13 recommended)*
