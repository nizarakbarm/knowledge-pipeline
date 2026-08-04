---
created: 2026-07-25
updated: 2026-07-29
up:
  - "[[PyCon-TW-2026]]"
  - "[[BCC vs Python-BPF Comparisons MOC]]"
related:
  - "[[20260516-pycon-tw-ebpf-proposal]]"
in: "[[Spaces]]"
tags:
  - pycon
  - slides
  - ebpf
  - pycon-tw-2026
---

# Slide Structure — PyCon TW 2026 eBPF Talk

Based on full reading of all comparison notes (July 2026).

---
## 1. Title (1 slide)

**Python eBPF: BCC C-String Runtime vs Python-BPF AST AOT**

Nizar Akbar Meilani — DomaiNesia

---

## 2. Motivation & Architecture (2 slides)

### 2a. Motivation

**Hook:** Two tools, same goal. Which is faster? Which can do the job? The answer isn't binary.

Key framing: We measured both frameworks across startup syscalls, process CPU/memory, profiling, bytecode, and JIT instruction cost. The results surprised us.

### 2b. Architecture Comparison

| Aspect | BCC | Python-BPF |
|--------|-----|------------|
| Compilation | fork clang (preprocessor + compiler) | AST parsed → llvmlite IR → llc |
| Init CPU | **0.52s** | **0.018s** (28-30× faster) |
| Kernel headers | 10,517 `read()` calls | **0** |
| Callback bridge | ctypes (`c_void_p`, zero-copy) | pybind11 (`py::bytes` alloc per event) |
| Poll mechanism | `poll()` (POSIX) | `epoll_wait()` (libbpf) |
| GIL release | implicit — ctypes `Py_BEGIN_ALLOW_THREADS` | explicit — `py::gil_scoped_release` |
| Attach method | legacy `PERF_EVENT_IOC_SET_BPF` ioctl | modern `BPF_LINK_CREATE` |
| Format string | **Stack** — `movabs` per 8 bytes | **`.rodata` map** — single `movabs` |

**Key stat:** BCC init = **0.52s CPU** vs PBPF **0.018s** — **28-30× slower**.

**Why:** Clang forks twice per program, reads **10,517 kernel header files** via `read()` syscalls, parses full kernel BTF/type definitions.

---

## 3. Methodology / Measurement (1 slide)

### Two Workload Triggers

| Workload | Tracepoint | Event rate | Purpose |
| -------- | ---------- | ---------- | ------- |
| **High-rate** | `syscalls/sys_enter_unlink` (uid 1002 filter) | **552K ev/s** (1.81 µs/ev via gen_fast) | Main benchmark — 2M events |
| **Low-rate** | `syscalls/sys_enter_openat` | ~few ev/s (natural) | Format string tests (print_pid, print_long_str) |
| **kprobe** | `kprobe/do_nanosleep` | — | Foundation baseline (bytecode identity) |

### Measurement Techniques (12 tools)

**Core (10) — produce the numbers on result slides:**

| # | Tool | What it measures | Used for |
|---|------|------------------|----------|
| ① | `strace -c` | Syscall count per type | Framework startup overhead |
| ② | `strace -T` | Per-syscall wall time | Individual syscall cost |
| ③ | `time.process_time()` inside Python | CPU time of poll loop only (not init/teardown) | Per-event cost isolation |
| ④ | `perf stat` | Cycles, instructions, IPC, ctx switches | JIT instruction cost, CPU efficiency |
| ⑤ | `perf record -F 199` | Sampling profile + flamegraph | Where CPU time is spent |
| ⑥ | `perf probe` | Dynamic tracing on Python/C functions | `PyBytes_FromStringAndSize` call count (383K vs 40K) |
| ⑦ | `pyinstrument` (`python3 -m pyinstrument`) | Startup call tree (imports vs compilation) | 1.96× real-work gap |
| ⑧ | `scalene` | Memory + CPU profiler, line-level attribution | Line-level memory usage (53 MB vs 126 MB) |
| ⑨ | `/usr/bin/time -v` | Wall clock, user/sys CPU, RSS, page faults | Overall resource comparison |
| ⑩ | `bpftool prog dump xlated/jited` | Verifier + JIT bytecode disassembly | Instruction count, JIT quality |

**Supporting (2) — investigation detail, no standalone result:**

| # | Tool | Used for |
|---|------|----------|
| ⑪ | `gen_fast` (event trigger) | 2M unlink() events @ 1.81 µs/ev — workload, not measurement |
| ⑫ | `perf script \| stackcollapse-perf.pl \| flamegraph.pl` | Flamegraph SVG generation from ⑤ |

**Auxiliary (in notes, not on slides):** `diff -ay` (4-way strace diff), `/proc/<pid>/fdinfo` (fd/link state), `strings .so` (binary feature detection), `bpftool prog show` (run_time_ns stats), JIT cost harness `measure.c` (100M iterations, `perf stat cycles:u -r 3`).

### Test Programs — Taxonomy

Each comparison note varies 3 axes: **map** (HashMap vs none), **callback** (full vs empty vs none), **struct** (named fields vs raw bytes).

| Axes | Program | Map | Callback | Struct | Used in |
|------|---------|:---:|:--------:|:------:|---------|
| with_map + full | `map_1_perf_timed.py` | HashMap | full | ✓ | Per-event ratio |
| with_map + empty | `map_1_perf_timed_empty.py` | HashMap | empty | ✓ | Empty baseline |
| perf_only + full | `print_long_str_timed.py` | — | full | ✓ | **6× JIT diff** |
| perf_only + full | `tracepoint_1_timed.py` | — | full | ✓ | Format string test |
| perf_only + full | `print_pid_timed.py` | — | full | ✓ | Print perf |
| perf_only + empty | `perf_timed.py` | — | empty | ✓ | **Fair baseline** |
| perf_only + empty | `perf_timed_empty.py` | — | empty | ✓ | Pure bridge cost |
| perf_only + no-struct | `perf_timed_empty_no_struct.py` | — | empty | ✗ | Struct_parser overhead |
| perf_only + no-struct | `perf_empty_no_struct.py` | — | empty | ✗ | Struct_parser cost |
| no_perf + no_map | `bpf_only_syscall_timed.py` | — | none | — | **Bytecode identical** |
| kprobe (broken) | `kprobe-unlink.py` | — | full | — | Limitation slide |

Each program has a BCC equivalent.

---

## 4. Foundation: BPF Syscall-Only Program (2 slides)

### 4a. Source & Syscall Output (1 slide)

**Tool:** `strace -c` + `strace -T`

**Programs** — minimal kprobe on `do_nanosleep`, return 0. No map, no perf buffer, no callback.

| Framework | Source location | Logic |
|:----------|:----------------|:------|
| PBPF | `/root/learn-pythonbpf/pythonbpf_only_bpf_syscall.py` | `@bpf` decorators → `b.load()` → `b.attach_all()` |
| BCC | `/root/learn-BCC/bcc_only_bpf_syscall.py` | `BPF(text=...)` → `attach_kprobe()` |

**Syscall output (strace -c):**

| syscall | PBPF | BCC | Notes |
|:--------|:----:|:----:|:------|
| `BPF_PROG_LOAD` | 5 | 3 | PBPF: 3 socket_filter probes + tracepoint probe + real kprobe |
| `BPF_LINK_CREATE` | **2** | **0** | PBPF modern attach; BCC legacy ioctl |
| `BPF_BTF_LOAD` | 0 | 1 | BCC loads BTF metadata |
| `BPF_TOKEN_CREATE` | 1 (EOPNOTSUPP) | 0 | PBPF probes kernel token support |
| `perf_event_open` | 1 | 1 | both create kprobe perf event |
| `ioctl` | 212 | 134 | BCC: `PERF_EVENT_IOC_SET_BPF` attach |
| `mmap` | 203 | 163 | ring buffer mapping |
| `read` | **441** | **10,489** | BCC: `/proc/kallsyms` symbol resolution |
| `close` | 300 | 492 | BCC more fd cleanup |
| `execve` | 0 | 1 | BCC spawns clang subprocess |
| **Total** | **1,170** | **11,262** | **10× BCC** |

**Program types loaded:** PBPF = 3 SOCKET_FILTER + 1 KPROBE + 1 TRACEPOINT; BCC = 2 SOCKET_FILTER + 1 KPROBE.

### 4b. JIT / Xlated + Deciding Metrics (1 slide)

**Tool:** `bpftool prog dump xlated/jited` + `/usr/bin/time -v`

**Bytecode — byte-for-byte IDENTICAL:**

```
xlated (2 insns, both):
0: (b7) r0 = 0
1: (95) exit

JIT (9 insns, both):
endbr64; nopl 0x0(%rax,%rax,1); nopl (%rax); push %rbp;
mov %rsp,%rbp; endbr64; xor %eax,%eax; leave; jmp <trampoline>
```

| | PBPF (prog 275) | BCC (prog 297) |
|:--|:--:|:--:|
| xlated insns | 2 | 2 |
| JIT insns | 9 | 9 |
| JIT size | 218 B | 253 B (extra annotation chars) |
| **BTF tag** | `a04f5eef06a7f555` | `a04f5eef06a7f555` |

**Deciding metrics (`/usr/bin/time -v`):**

| Metric | PBPF | BCC | Ratio |
|:-------|:----:|:----:|:-----:|
| Runtime | 0.45s | 0.71s | 1.6× BCC |
| Max RSS | 52 MB | 122 MB | 2.3× BCC |
| User CPU | 0.15s | 0.45s | 3× BCC |
| Sys CPU | 0.04s | 0.23s | 5.8× BCC |
| Minor page faults | 5,304 | 16,704 | 3.2× BCC |
| CPU % | 42% | 95% | — |
| FS inputs (kernel headers) | 0 | 192 | ∞ |

**Key insight:** BCC's overhead is entirely from in-process Clang compilation reading 10K kernel headers + `/proc/kallsyms` symbol resolution + legacy ioctl attach path. At the BPF bytecode level — **byte-for-byte identical**.

**Why this matters:** All per-event performance differences between BCC and PBPF come from **framework glue** (ctypes vs pybind11 dispatch), not BPF JIT quality or kernel execution. The bytecode is the same — the wrapper around it is not.

---
## 5. Building Up: Map + Perf (7 slides)

### 5.1. Why Combine Map + Perf — and NOT a Struct in the Map (1 slide)

**The goal:** per-UID state (HashMap) **plus** streaming events to Python (perf buffer).

**First attempt — struct as the map value:**

| Attempt | Pattern | Result |
|:--------|:--------|:-------|
| `maps_with_struct_perf.py` (docs pattern) | `stats.count = stats.count + 1; update(stats)` | ❌ llc crash: `invalid getelementptr indices` (double-index GEP on `i64*` lookup result) |
| `maps_with_struct_single.py` (read-then-update) | `new = stats.count + 1; s = Stats(); update(s)` | ✅ compiles, but **8,619 ns/ev at 2M** — 19% slower than u64 |

**Decision — keep the map value simple (`u64` counter):**
- Struct-in-map: capability demo, not a perf win (+1,364 ns/ev vs u64)
- BTF is also malformed for struct maps (`bits_offset=8` bug) — no CO-RE
- So: `HashMap(u32 → u64)` for state, `data_t` struct for the **perf event payload only**

**This is why the next slide's program exists** — `map_1_perf_timed_timing.py`: combine map + perf with a **plain u64 counter**, and read it back in the callback. That decision exposes the next problem (stale counter) — the exact story the rest of this section walks through.

> [!note] Full struct-map details (llc bug, BTF bug, benchmark): [[Python-BPF Struct-in-Map Value — llc Bug & Benchmark]]

---

### 5.3. The Timing Program — `map_1_perf_timed_timing.py` (1 slide)

**Tool:** `time.process_time()` + `strace -T` (per-event CPU, syscall cost)

**Programs** — HashMap counter (`count[uid]++`) + perf buffer delivery. Callback reads counter via `HashMap.values()` = **2 BPF syscalls per event** (`get_next_key` + `lookup_elem`).

| Framework | Source location |
|:----------|:----------------|
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_timing.py` |
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_timing.py` |

**Usage:**
```bash
# BCC — init ~0.5s (sleep 2 before trigger)
/usr/bin/python3 /root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_timing.py &

# PBPF — init ~0.02s (sleep 1 before trigger)
/root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_timing.py &

sudo -u radare2 /tmp/gen_fast 2000000   # 2M unlink() events
```

**From our notes:**
* Counter value read at **callback time**, not **event time** → stale values during bursts (all callbacks print `count: 20` for 20 events)
* **+2 BPF syscalls per event** in the hot path (`get_next_key` + `lookup_elem`)
* More syscall time going into the map than into the perf buffer delivery

**❓ Audience question:**

gen_fast generates events at **1.81 µs/event** (2M events = 3.625s). The callback does a map lookup syscall, then submits to the perf map. **Is this program's timing correct?**

[Present evidence only, no verdict: identical count values across callbacks, the extra map syscalls, the timing split]

### 5.4. The Count Program — `map_1_perf_timed_count.py` (1 slide)

**Tool:** `time.process_time()` (CPU), `perf stat` (cycles), `strace -c` (syscalls), `bpftool dump` (JIT/xlated)

**Programs** — embedded counter: `data.count = *count` at BPF program time. Zero extra syscalls, value correct at event time.

| Framework | Source location |
|:----------|:----------------|
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_count.py` |
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_count.py` |

**BPF struct change:**
```c
struct data_t { u32 uid; u64 count; };   // count embedded at BPF time
```

**Syscall output (startup, strace -c):**

| syscall | BCC | PBPF | Notes |
|:--------|:----:|:----:|:------|
| `read` | **10,511** | 443 | BCC: kernel headers |
| `poll` | 1,039 | 646 | poll loop setup |
| `openat` | 576 | 276 | BCC: header search |
| `close` | 498 | 294 | fd cleanup |
| `mmap` | 168 | 129 | LLVM memory |
| `ioctl` | 114 | **219** | PBPF: more perf handling |
| `bpf` | 9 | **23** | PBPF: probes + LINK_CREATE |
| `write` | 8 | 10 | — |
| **Total** | **16,274** | **5,198** | 3.1× BCC |
| **Total syscall time** | 0.127s | 0.028s | 4.5× BCC |

**Bytecode / JIT (bpftool dump):**

| Property | BCC | PBPF |
|:---------|:----:|:----:|
| xlated | 49 insns (400B) | 64 insns (616B) |
| JIT size | 242B | 347B |
| Stack frame | `sub $0x30` | `sub $0x60` |
| Saved regs | rbx, r13 | rbx, r13, r14 |
| BTF tag | `17b2653ec143600b` | `e291fdb1cc5171f5` |

**Key JIT diff:** BCC `(*count)++; data.count = *count;` = 3 direct pointer-deref insns. PBPF `Count.lookup() + update() + assign` = helper call (~22 insns arg setup) + 2× increment calculation.

**Full comparison (2M events):**

| Metric | BCC | PBPF |
|--------|:---:|:----:|
| Delivered | **1,523,098 (76%)**\* | **1,997,971 (99.9%)** |
| Poll loop CPU | 12.512s | 14.496s |
| Per-callback cycles | 28,506 | 24,241 (1.18× leaner) |
| JIT size | 242B | 347B |

\* BCC run-to-run variance **60-76%** (1,214,049–1,523,098, two valid runs). Under perf record: BCC **58%** (1,164,031) vs PBPF **99.97%** (1,999,457). Earlier 29-34% BCC runs had a broken `lost_cb` lambda (SyntaxError) — invalid.

**Startup of the same program** (from `strace -c` + `perf stat` + `time -v`, no trigger):

| Metric | BCC | PBPF | Ratio |
|--------|:---:|:----:|:-----:|
| Total syscalls | **16,274** | 5,198 | 3.1× BCC |
| Kernel header `read()` calls | **10,511** | 443 | 24× BCC |
| Syscall time | 0.127s | 0.028s | 4.5× BCC |
| Cycles | 2.09×10⁹ | 0.56×10⁹ | 3.7× BCC |
| Instructions | 1.78×10⁹ | 0.49×10⁹ | 3.6× BCC |
| Max RSS | **126 MB** | 54 MB | 2.3× BCC |
| Sys CPU | 0.20s | 0.05s | 4× BCC |

Same mechanism as Foundation: BCC's in-process Clang + kernel header parsing dominates startup. PBPF's `llc` compiles in a subprocess — memory invisible to Python RSS.

**Reveal:** the timing program measured a **stale counter + 2 syscalls/event overhead**. With the fix, PBPF delivers **99.9%** vs BCC **60-76%** — ctypes dispatch overhead slows BCC's drain rate → more perf buffer overflow.

> [!note] **Measurement trap:** the perf buffer is `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, 32KB/CPU (~1,365 events). When BCC's ctypes drain is slow (>2.5 µs/ev), it drops **5,543 of 2M samples** — so early "BCC is 1.68× faster" was an **artifact of fewer callbacks, not faster dispatch**.

### 5.5. Per-Event: without_map Baseline (1 slide)

**Tool:** `time.process_time()` (poll loop CPU), `perf record` (delivery under sampling)

**Programs:** `perf_timed.py` — PBPF `/root/learn-pythonbpf/syscall_trigger/without_map/`, BCC `/root/learn-BCC/syscall_trigger/without_map/`
**2M events, perf buffer only, no HashMap.** Fresh benchmark data (2026-07-25).
| Test | BCC CPU | PBPF CPU | Ratio | BCC ns/ev | PBPF ns/ev | Delivered |
|---|---|---|---|---|---|---|
| **No-struct** (raw bytes, empty cb) | 9.409s | **7.936s** | **0.844× PBPF** | 4,705 | 3,968 | both ~100% |
| **Empty** (struct parsing, empty cb) | 9.885s | **9.546s** | **0.966× PBPF** | 4,943 | 4,773 | both ~100% |
| **Full** (print per event) | **13.963s** | 14.424s | 1.033× BCC | 6,982 | 7,212 | **99.94% vs 99.93%** |

**Key findings:**

- **Without HashMap in the callback, both frameworks deliver >99.9% at 2M** — the earlier 95-99% loss was purely slow callbacks (map iter + print), not buffer size (same 32KB).
- **PBPF no-struct is 16% faster than BCC** — cleanest baseline. pybind11 dispatch with raw bytes is leaner than ctypes.
- **PBPF empty is 3.4% faster** — struct parser adds overhead but PBPF still wins.
- **Full callback: BCC 3.3% faster** (6,982 vs 7,212 ns/ev) — both spend most CPU in `print()`; the ctypes-vs-pybind11 diff (~230 ns/ev) is dwarfed by print (~7 µs/ev).
- **Struct_parser cost in PBPF:** 9.546s - 7.936s = **1.61s (805 ns/event)** for `struct_name="data_t"` parsing.
- **BCC struct vs no-struct delta:** 9.885s - 9.409s = 0.476s — BCC's `.event(data)` struct parsing is cheaper.
- **No perf buffer losses** in any of these tests (verified).

#### Struct Parser Code Path (`sample_callback_wrapper` + `StructParser::parse()`)

```cpp
// perf_event_array.cpp
py::bytes py_data(data, size);           // COPY #1: perf buffer → Python bytes (~130 ns)
parser_->parse(struct_name_, py_data);   // → struct_parser.cpp:
  struct_type.attr("from_buffer_copy")(data)  // COPY #2: bytes → ctypes struct (~675 ns)
callback_(cpu, event);
```

**Not zero-copy.** It's a **double memcpy** — BCC uses zero-copy `c_void_p` instead.

| Component | Per-event | 2M total | Notes |
|-----------|-----------|----------|-------|
| COPY #1: `py::bytes` | ~130 ns | 0.26s | Always — BCC skips (c_void_p) |
| COPY #2: `from_buffer_copy` | ~675 ns | 1.35s | Only with `struct_name="data_t"` |
| **Total struct_parser** | **805 ns/ev** | **1.61s** | PBPF-specific double-copy |
| BCC `.event(data)` | ~238 ns | 0.48s | Cheaper — pointer overlay |

**Why bottleneck at high rate?** 805 ns × 2M = 1.61s = 17% of total CPU at 2M events. Scales linearly.

**Why NOT "fixed" by per-100 print?** Struct parser runs on **every event**, not every 100th. Same 1.61s in both empty-callback and e100. Print overhead (1.21s) just makes struct % drop 18% → 16% — absolute cost unchanged.

### 5.6. Format String: Storage Strategy (1 slide)

**Tool:** `bpftool prog dump xlated/jited`

PBPF stores format strings in **`.rodata` BPF map** — single pointer load regardless of length.

BCC stores on **stack** — `movabs` pairs per 8 bytes, scales with string length.

| Program | BCC xlated | PBPF xlated | BCC JIT | PBPF JIT |
|---|---|---|---|---|
| `print_pid` | ~12 | ~11 | ~14 | ~10 |
| `print_long_str` (~100B) | **~30** | **~6** | **~30+** | **~5** |

**6× fewer instructions for long strings in PBPF.** No stack frame allocation needed.

### 5.7. Profile: Where CPU Goes (1 slide)

**Tool:** `perf record -F 199` + flamegraph (count program, 2M events)

**Leaf-level breakdown (count program, debug symbols):**

| Leaf function | BCC | PBPF | What it is |
|---|:---:|:----:|------------|
| `libpython3.13.so.1.0` | 26.7% | **32.6%** | Python runtime |
| `_PyEval_EvalFrameDefault` | **8.6%** | 5.5% | Python bytecode exec |
| `[_ctypes]` | **4.8%** | 1.8% | ctypes dispatch |
| `[libffi.so]` | **2.7%** | 0.0% | libffi (called by ctypes) |
| `asm_sysvec_apic_timer_interrupt` | **4.9%** | 1.0% | Perf sampling interrupt |
| `_PyType_LookupRef` | 2.4% | 2.5% | Python type lookup |
| `htab_map_get_next_key` | 0.0% | 0.0% | HashMap iteration (**ELIMINATED**) |

**Key findings:**
- **ctypes + libffi = 7.5% of BCC cycles vs 1.8% PBPF** — the ctypes dispatch cost shows up directly in the profile.
- `htab_map_get_next_key` **absent from both** — the embedded counter eliminated the HashMap syscall in the callback.
- BCC's `asm_sysvec_apic_timer_interrupt` is **4.9× higher** (4.9% vs 1.0%) — perf interrupts hit BCC more because it spends proportionally more time in dispatch overhead.
- PBPF's higher Python runtime (32.6% vs 26.7%) — it processes **1.7× more callbacks**, so more Python execution per unit time.

**Startup contrast:** at init, BCC is dominated by `clang::CompilerInstance::ExecuteAction` (**65%**) — LLVM C compilation; PBPF by Python interpreter + imports. At 2M events, init is amortized and the runtime dispatch profile above emerges.

---
### 5.8. Bridge Cost & GIL (1 slide)

**Tool:** `time.process_time()` (per-event ns) + `perf probe` (PyBytes counts)

| GIL release | implicit via ctypes `Py_BEGIN_ALLOW_THREADS` | explicit `py::gil_scoped_release` in poll() |
| GIL re-acquire | implicit on ctypes C return | explicit `py::gil_scoped_acquire` per event in callback |
| Per-event (no-struct empty) | 4,705 ns | **3,968 ns (0.844×)** |
| Per-event (empty) | 4,943 ns | **4,773 ns (0.966×)** |
| Per-event (full print) | **6,965 ns** | 7,056 ns (1.013×) |

**Surprising result:** PBPF's pybind11 bridge + py::bytes alloc is NOT slower for simple callbacks. With no struct parsing, PBPF is 16% faster than ctypes. The `py::bytes` alloc cost (~130 ns) is offset by more efficient wakeup/dispatch in epoll_wait vs poll.

---

## 6. Python-BPF Limitations (2 slides)

### 6.1. Two Compiler Gaps

Both in `expr_pass.py`:

**Gap 1 — No `ast.Subscript` handler (line 730)**

* `ctx.args[0]` → `eval_expr` hits `return None`
* Blocks all array-indexed field access
* Fix: `builder.gep` + `builder.load`

**Gap 2 — No atomic map operations (line 227)**

* `count += 1` → `builder.add` (not `atomic_rmw`)
* Load → add → store has **race window** → lost updates on multi-CPU
* Fix: `builder.atomic_rmw` + `seq_cst`

### 6.2. Struct-in-Map-Value: Write-Through Pattern Crashes llc

```python
stats = Count.lookup(u_id)
if stats:
    stats.count = stats.count + 1     # write through map pointer → ❌ llc crash
    Count.update(u_id, stats)
```

**Error:** `llc: invalid getelementptr indices` — codegen emits a double-index GEP on the `i64*` lookup result (`getelementptr i64*, i64** %stats, 0, 0`).

**Workaround:** read-then-update (build a fresh struct, `update()`) — works but **+19% per-event** (8,619 vs 7,255 ns/ev). Struct-map BTF also malformed (`bits_offset=8` bug) — no CO-RE.

Full detail: [[Python-BPF Struct-in-Map Value — llc Bug & Benchmark]]

### 6.3. Cannot Read Kernel Strings from Kprobes

```python
name_str = 0
probe_read(name_str, 8, fname_ptr)   # gets char* pointer ✓
probe_read_str(buf, name_str)           # FAILS: name_str is i64, not i8*
```

Root cause: `get_ptr_from_arg` for `probe_read_str` expects `ir.PointerType`, but `name_str` evaluates to `i64` (loaded value). Missing `inttoptr(i64 → i8*)` in emitter.

### What Works

* HashMap counters, tracepoints, `bpf_printk`, basic arithmetic
* Perf event array (streaming to Python callbacks)
* Format strings in `.rodata` map (PBPF wins here)
* Ahead-of-time compilation (no LLVM at runtime)


## 7. Key Takeaways (1 slide)

| When | Choose BCC | Choose Python-BPF |
|---|---|---|
| Startup | Lost (0.54s vs 0.024s) | **Wins** (23× faster) |
| Raw bytes, empty cb | Lost (9.41s vs 7.94s) | **Wins** (16% faster) |
| Full callback per event | **Wins** (1.3% faster) | Lost |
| Format strings (long) | Loses (30 JIT insns) | **Wins** (5 JIT insns) |
| Kernel string access | **Works** | Broken |
| Atomic map counters | **Works** | Broken |
| Production deploy | **Ready** | Alpha |

**Four patches close the gap:** `ast.Subscript` handler + `atomic_rmw` + `inttoptr` + struct-map GEP fix.

**Key surprise:** PBPF bridge overhead is *lower* than BCC for simple callbacks. The earlier 1.12× gap was from measurement artifacts (perf buffer overflow). With fair comparison, PBPF equals or beats BCC on per-event CPU. The real cost is startup — and PBPF wins that by 23×.
## Slide Totals

| Section | Slides |
|:--------|:------:|
| Title | 1 |
| Motivation & Architecture | 2 |
| Methodology | 1 |
| Foundation: BPF Syscall-Only | **2** |
| **Building Up: Map + Perf** | **7** |
| - Why Combine (5.1) | 1 |
| - Timing Program (5.3) | 1 |
| - Count Program (5.4) | 1 |
| - without_map Baseline (5.5) | 1 |
| - Format String (5.6) | 1 |
| - Profile (5.7) | 1 |
| - Bridge Cost & GIL (5.8) | 1 |
| Limitations | 2 |
| Key Takeaways | 1 |
| Q&A | 1 |
| **Total** | **17** |

Target: 30 min → ~1.8 min/slide for 17 slides.
