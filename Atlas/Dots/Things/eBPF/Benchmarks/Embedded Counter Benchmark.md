---
created: 2026-07-28
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
  - "[[Spaces/PyCon-TW-2026/ebpf-slides-structure]]"
tags:
  - ebpf
  - benchmark
  - embedded-counter
  - pythonbpf
  - bcc
---

> [!summary] Embedding the HashMap counter in the per-event struct eliminates the stale-value problem. Each delivered event shows its exact sequence number at event time, not callback read time. PBPF delivers **99.9% at 2M** vs BCC 33.9% with this fix.

# Embedded Counter Benchmark — map_1_perf_timed_count.py

## Problem

The original `map_1_perf_timed.py` reads the HashMap counter via BPF syscall (`HashMap.values()`) inside the Python callback. This adds 2 BPF syscalls per event (`bpf_map_get_next_key` + `bpf_map_lookup_elem`) and returns the counter value at **callback time**, not event time. During a burst, the kernel side has already incremented the counter many times before the callback reads it → all callbacks see the same final value (e.g. all `count: 20` for 20 events).

## Fix

Embed the counter value in the per-event `data_t` struct at BPF program time. The callback reads `event.count` directly — no extra syscall, correct value at event time.

## Programs

| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_count.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_count.py` |

### BPF struct changes

```c
// BCC
struct data_t {
    u32 uid;
    u64 count;          // ← added: embedded counter
    char comm[16];
};
```

```python
# PBPF
@struct
class data_t:
    uid: c_uint64
    count: c_uint64     # ← added
    last_comm: str(16)
```

### BPF increment + embed

```c
// BCC
if (count) { (*count)++; data.count = *count; }
else { count_hash.update(&uid, &zero); data.count = 0; }
events.perf_submit(args, &data, sizeof(data));
```

```python
# PBPF
count = Count.lookup(u_id)
if count:
    Count.update(u_id, count + 1)
    data.count = count + 1
else:
    Count.update(u_id, 1)
    data.count = 1
events.output(data)
```

## Commands

```bash
# BCC  (sleep 2 before trigger)
/usr/bin/python3 /root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_count.py >/tmp/bcc_cnt<N>.log 2>&1 & sleep 2; sudo -u radare2 /tmp/gen_fast <N>; sleep <T>; pkill -INT -f map_1_perf_timed_count

# PBPF (sleep 1 before trigger)
/root/learn-pythonbpf/.venv/bin/python3 /root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_count.py >/tmp/pbpf_cnt<N>.log 2>&1 & sleep 1; sudo -u radare2 /tmp/gen_fast <N>; sleep <T>; pkill -INT -f map_1_perf_timed_count
```

Log naming: `/tmp/bcc_cnt{5,10,20,2k,2m}.log` and `/tmp/pbpf_cnt{5,10,20,2k,2m}.log`.

## Results

| N | BCC cb | BCC CPU | BCC seq | PBPF cb | PBPF CPU | PBPF seq |
|---|:------:|:-------:|:-------:|:-------:|:--------:|:--------:|
| 5 | 5 (0-4) | 0.111s | 0-4 | 5 | 0.071s | 0-4 |
| 10 | 10 (0-9) | — | 0-9 | 10 | — | 0-9 |
| 20 | 20 (0-19) | — | 0-19 | 20 | — | 0-19 |
| 2000 | 2,000 | 0.189s | 0-1999 | 2,000 | 0.116s | 0-1999 |
| 2,000,000 | **1,523,098 / 1,214,049** (60-76%) | 12.512s / 12.045s | 0-2M | **1,997,971** (99.9%) | 14.496s | 0-2M |
| 2,000,000 (under perf) | **1,164,031** (58%) | 12.215s | 0-2M | **1,999,457** (99.97%) | 19.162s | 0-2M |

> [!warning] BCC shows **high run-to-run variance at 2M**: 60-76% delivery (two valid runs after fixing `lost_cb` syntax). PBPF is consistently 99.9%. Earlier BCC runs (29-34%) had a broken `lost_cb` lambda that caused a SyntaxError on module load — invalidating those results.

### Counting method

All counts use `grep -v "TIMING|THREAD|Starting|SUMMARY|LOST|CB_TIME" <log> -c` to exclude meta lines from the per-event callback count.

## Key Findings

### 1. Embedded counter eliminates stale values
Every delivered event carries its exact sequence number. No more "all count=20" artifact. The counter reflects the HashMap value at **event time**, not callback read time.

### 2. No extra BPF syscall in callback
The original pattern called `HashMap.values()` + `HashMap.keys()` per event — 2 BPF syscalls. The embedded version reads `event.count` directly (zero-copy from the ring buffer). This reduces per-callback kernel interaction.

### 3. PBPF 99.9% vs BCC 60-76%
Same callback work (just print), same ring buffer size (32KB), same gen_fast trigger. PBPF delivers **99.9%** consistently. BCC varies **60-76%** — the gap is **ctypes dispatch overhead** slowing BCC's drain rate → more overflow.

### 4. BCC high variance
BCC's delivery rate varies 60-76% between runs. PBPF is consistently 99.9%. BCC's slower dispatch makes it more sensitive to scheduler interleaving on the shared CPU.

### 5. Smaller counts: both 100%
At 5-2000 events, both deliver 100%. The perf buffer (1365 slots) easily absorbs bursts of this size.

### 6. Dispatch overhead vs callback work


---

## Startup: Syscall Layer

> [!summary] BCC makes **3.1× more syscalls** (16,274 vs 5,198). The gap is entirely from kernel header reads (10,511 vs 443). PBPF's 1 `wait4` call is from the `llc` subprocess compilation.

Captured via `strace -c -o /tmp/{bcc,pbpf}_map_1_perf_timed_count_strace.txt`. Startup only, no gen_fast events.

| Metric | BCC | PBPF | Ratio |
|--------|:---:|:----:|:-----:|
| **Total syscalls** | **16,274** | **5,198** | 0.32× |
| read | 10,511 | 443 | 0.04× |
| poll | 1,039 | 646 | 0.62× |
| openat | 576 | 276 | 0.48× |
| close | 498 | 294 | 0.59× |
| mmap | 168 | 129 | 0.77× |
| ioctl | 114 | 219 | 1.92× |
| bpf | 9 | 23 | 2.56× |
| write | 8 | 10 | 1.25× |
| Total syscall time | 0.127s | 0.028s | 0.22× |

> [!warning] BCC's 10,511 `read` calls are from clang parsing kernel headers. PBPF reads **0** kernel headers — it uses BTF ID directly. See [[Syscall and Startup Comparison]] for detailed breakdown.

## Startup: Perf Stat & Memory

> [!summary] BCC uses **3.7× more cycles** (2.09B vs 0.56B), **3.6× more instructions** (1.78B vs 0.49B), and **2.4× more RSS** (126MB vs 54MB) at startup.

Captured with `perf stat -e cycles,instructions,task-clock,context-switches` and `/usr/bin/time -v`. Startup only, no gen_fast events.

| Metric | BCC | PBPF | Ratio |
|--------|:---:|:----:|:-----:|
| Cycles | 2,094,229,496 | 563,276,411 | 0.27× |
| Instructions | 1,775,606,164 | 489,556,797 | 0.28× |
| IPC | 0.85 | 0.87 | ~1× |
| Task-clock | 873.81 ms | 285.66 ms | 0.33× |
| Context switches | 1,552 | 858 | 0.55× |
| User time | 0.44s | 0.19s | 0.43× |
| Sys time | 0.20s | 0.05s | 0.25× |
| Max RSS | **126,156 KB** | **53,564 KB** | **0.42×** |
| Minor page faults | 19,381 | 5,464 | 0.28× |

> [!info] The 0.28× ratio (PBPF using 28% of BCC's resources) is consistent across cycles, instructions, and memory. BCC's in-process LLVM/clang compilation is the dominant cost.

## Bytecode & JIT Comparison

> [!summary] BCC produces **49 xlated insns** (400B), PBPF produces **64 xlated insns** (616B). The BCC program is 35% smaller because its C compiler optimizes the embedded counter assignment better than PBPF's AST codegen.

Captured via `bpftool prog dump {xlated,jited} id <N>` during poll loop.

| Property | BCC | PBPF |
|----------|:---:|:----:|
| xlated size | 400B (49 insns) | 616B (64 insns) |
| JIT size | 242B | 347B |
| Stack frame | sub $0x30 | sub $0x60 |
| Saved regs | push rbx, push r13 | push rbx, push r13, push r14 |
| BTF tag | `17b2653ec143600b` | `e291fdb1cc5171f5` |

**Key difference:** BCC's `(*count)++; data.count = *count;` compiles to 3 JIT insns (load, add, store) plus one store to data. PBPF's `Count.lookup()` + `Count.update()` + `data.count = count + 1` compiles to more instructions due to the helper call pattern.

> [!tip] The embedded counter adds ~2 extra xlated insns to BCC (the `data.count = *count` store) and ~5 to PBPF (assignment + struct field access). This is negligible compared to the HashMap iteration savings.

---

## 2M Events — Timing & Delivery

> [!warning] **Under perf record**, BCC delivers **1,164,031 (58%)** vs PBPF **1,999,457 (99.97%)**. The perf sampling interrupts add overhead that further slows BCC's ctypes dispatch.

| Metric | BCC | PBPF |
|--------|:---:|:----:|
| Callbacks delivered | 1,164,031 (58%) | 1,999,457 (99.97%) |
| Poll loop CPU | 12.215s | 19.162s |
| µs per callback | 10.5 µs | 9.6 µs |
| Perf data size | 21 MB | 14 MB |

## 2M Events — Flamegraph Leaf Analysis

> [!quote] Without HashMap in the callback, BCC's ctypes+libffi overhead drops to **7.5%** (down from 11.9% in the old perf_timed test). PBPF's pybind11 overhead is also smaller because there's no `HashMap.values()` generator.

## JIT Side-by-Side Comparison

> [!quote] BCC generates **242 bytes** of JIT code vs PBPF's **347 bytes**. The main difference: BCC's `(*count)++` compiles to 3 direct pointer-deref insns, while PBPF's `Count.update()` requires a helper call with argument setup (~22 insns). PBPF also has a 2× larger stack frame and saves one extra register.

| # | BCC JIT | PBPF JIT | What |
|---|:-------|:---------|:-----|
| 1 | `sub $0x30,%rsp` | `sub $0x60,%rsp` | Stack frame: BCC 48B, PBPF 96B |
| 2 | `push %rbx; push %r13` | `push %rbx; push %r13; push %r14` | Saved regs: BCC 2, PBPF 3 |
| 3 | `call uid_gid` | `call uid_gid` | Same helper |
| 4 | `shl $0x20,%rax; shr $0x20,%rax` | `shl $0x20,%rax; shr $0x20,%rax` | Same UID extract |
| 5 | `cmp $0x3ea,%rax; jne ...` | `cmp $0x3ea,%rax; jne ...` | Same UID check |
| 6 | `movabs $map_fd,%rdi` | `movabs $map_fd,%rdi` | Same map pointer load |
| 7 | `call __htab_map_lookup_elem` | `call __htab_map_lookup_elem` | Same lookup helper |
| 8 | `test %rax,%rax; je ...` | `test %rax,%rax; je ...` | Same null check |
| 9 | `add $0x38,%rax` | `add $0x38,%rax` | Same offset adjust |
| 10 | — | `mov %rax,-0x30(%rbp)` | PBPF saves ptr to stack |
| 11 | `test %rax,%rax; je ...` | `test %rax,%rax; jne ...; jmp ...` | Same check (PBPF extra branch) |
| 12 | **`mov 0x0(%rax),%r13`** | `mov -0x30(%rbp),%r13` | Load counter: BCC direct, PBPF via stack |
| 13 | **`add $0x1,%r13`** | `add $0x1,%rdi` | Increment: both 1 insn |
| 14 | **`mov %r13,0x0(%rax)`** | `call htab_map_update_elem` | Store: BCC direct store, PBPF helper call |
| 15 | — | `mov -0x30(%rbp),%r14` | PBPF reloads pointer |
| 16 | — | `mov 0x0(%r14),%rdi; add $0x1,%rdi` | PBPF redoes increment for struct embed |
| 17 | — | `mov %rdi,-0x20(%rbp)` | PBPF stores to data.count |
| 18 | `mov %r13,-0x20(%rbp)` | `mov -0x30(%rbp),%r13` | BCC stores count to data; PBPF reloads |
| 19 | — | `mov %r13,-0x20(%rbp)` | PBPF stores to data.count (second path) |
| 20 | `movabs $perf_map,%rsi` | `movabs $perf_map,%rsi` | Same perf output map |
| 21 | `call bpf_perf_event_output` | `call bpf_perf_event_output` | Same helper |
| 22 | `xor %eax,%eax` | `xor %eax,%eax` | Same return 0 |
| **Total** | **~242 bytes, 2 regs saved** | **~347 bytes, 3 regs saved** | |

**Key differences:**
- **The increment (rows 12-14)**: BCC does it in 3 insns via pointer deref. PBPF needs a `update_elem` helper call (function call + return + argument setup).
- **The embedded counter (rows 15-19)**: PBPF does the increment calculation twice — once for `Count.update()` and once for `data.count = count + 1`. BCC does it once and reuses the result.
- **Stack frame**: PBPF allocates 96 bytes (vs BCC's 48) because it needs more spill slots for intermediate values during the codegen.

## JIT Instruction Cycle Cost Estimation

> [!tip] BCC's JIT has **25 instructions** vs PBPF's **44** for the same embedded-counter program. At ~1.5 CPI (measured from `bcc_unlink` benchmark: 1.67), the kernel-side JIT cost is ~38 cycles/event (BCC) vs ~66 cycles/event (PBPF) — **negligible** compared to userspace dispatch (28,506 vs 24,241 cycles/callback).

Measured via the standalone framework at `/root/jit_measurement/` (100M iterations, AMD EPYC 7713):

| Instruction | Net cyc | Count in BCC | Count in PBPF | Notes |
|:-----------|:-------:|:------------:|:-------------:|-------|
| `call`+`ret` | 4.017 | 6 | 8 | PBPF has 2 more helpers (extra update_elem) |
| `movabs` | 1.255 | 2 | 2 | Both load 2 map pointers |
| `sub $0xN,%rsp` | 0.727 | 1 ($0x30) | 1 ($0x60) | PBPF stack 2× larger |
| `push`/`pop` (reg) | ~0 | 2 pair | 3 pair | PBPF saves 1 extra reg |
| `leave` | 1.981 | 1 | 1 | Same |
| `jmp` | 0.811 | 2 | 3 | PBPF more branches |
| `test; je/jne` | 0.182 | 3 | 5 | PBPF more null checks |
| `mov` direct | ~0 | 4 | 5 | Similar |
| `shl; shr` | 0.555 | 1 | 1 | Same (u32 extract) |
| `cmp; jne` | ~0 | 1 | 1 | Same |
| `xor`/`add` | ~0 | 3 | 4 | LSD absorbs |
| `store through ptr` | 0.185 | 2 | 1 | BCC does direct map store |
| Stack store/load | 0.215 | 2 | 6 | PBPF spills more |
| **Estimated total cycles** | | **~38 cyc/event** | **~66 cyc/event** | |

**Key takeaway:** The JIT cost difference (28 cycles/event) is **0.1%** of the total per-callback cost (~25,000-28,000 cycles). At 2M events, the JIT gap accounts for ~56M cycles out of ~40B — completely negligible. All performance differences come from **userspace dispatch**, not BPF JIT quality.

| Leaf function | BCC | PBPF | What it is |
|--------------|:---:|:----:|------------|
| `[libpython3.13.so.1.0]` | 26.7% | **32.6%** | Python runtime |
| `_PyEval_EvalFrameDefault` | **8.6%** | 5.5% | Python bytecode exec |
| `[_ctypes.cpython-313]` | **4.8%** | 1.8% | ctypes dispatch |
| `[libffi.so.8.1.4]` | **2.7%** | 0.0% | libffi (called by ctypes) |
| `__tls_get_addr` | 4.3% | 4.4% | TLS access |
| `asm_sysvec_apic_timer_interrupt` | **4.9%** | 1.0% | Perf sampling interrupt |
| `__irqentry_text_start` | 2.9% | 3.0% | Interrupt entry |
| `_PyType_LookupRef` | 2.4% | 2.5% | Python type lookup |
| `entry_SYSCALL_64` | 0.6% | 0.9% | Syscall entry |
| `do_syscall_64` | 0.6% | **1.0%** | Syscall handler |
| `copy_page_from_iter_atomic` | 0.4% | **0.9%** | Buffer copy in kernel |
| `srso_alias_safe_ret` | 0.3% | 0.6% | Retpoline |
| `htab_map_get_next_key` | 0.0% | 0.0% | HashMap iteration (ELIMINATED) |

**Key findings:**
- `htab_map_get_next_key` is **absent** from both — the embedded counter eliminated the HashMap syscall in the callback
- BCC's `asm_sysvec_apic_timer_interrupt` is **4.9× higher** than PBPF's (4.9% vs 1.0%) — perf sampling interrupts hit BCC more because it spends proportionally more time in dispatch overhead
- ctypes + libffi = **7.5%** of BCC cycles vs **1.8%** for PBPF (remnant from perf buffer read path)
- PBPF has higher Python runtime (32.6% vs 26.7%) because it processes 1.7× more callbacks — more Python execution per unit time

## Per-Callback Cycle Cost

| | BCC | PBPF | Ratio |
|----|:---:|:----:|:-----:|
| Total cycles (under perf) | 33.2B | 48.4B | PBPF 1.46× |
| Callbacks delivered | 1,164,031 | 1,999,457 | PBPF 1.72× |
|
---
## Scalene Python Line-Level Profiling

> [!info] Scalene profiles show where time goes at the Python line level. BCC's init is dominated by `BPF(text=program)` (clang compilation). PBPF's init is dominated by imports (90% native). At 2M, both spend most time in `print()` and the poll loop.

### BCC [no event trigger] — 1.696s total, 43MB peak memory

| Line | Code | Python | Native | Sys | Mem |
|:----:|:-----|:-----:|:-----:|:---:|:---:|
| 4 | `from bcc import BPF` | 5% | 32% | 5% | 1MB |
| 51 | `b = BPF(text=program)` | — | 32% | 25% | **42MB** |

> [!warning] Line 51 (BPF compilation) consumes 57% of total time and 42MB peak memory — the clang compilation overhead.

### PBPF [no event trigger] — 845ms total, 3MB peak memory

| Line | Code | Python | Native | Sys | Mem |
|:----:|:-----|:-----:|:-----:|:---:|:---:|
| 2 | imports | 6% | **90%** | 4% | — |

> [!tip] PBPF's startup is **845ms vs BCC's 1.696s** (2× faster). Most time is in native library loading (pybind11, libbpf). Memory is **3MB vs 43MB** (14× less).

### BCC [2M event trigger] — 35.891s total, 43MB peak

| Line | Code | Python | Native | Sys | Mem |
|:----:|:-----|:-----:|:-----:|:---:|:---:|
| 59 | `event = b["events"].event(data)` | — | 7% | 9% | — |
| 60 | `print(f"CPU...", flush=True)` | 2% | 11% | **17%** | — |
| 80 | `print(f"[LOST]..." )` | — | 9% | **40%** | 1MB |

> [!warning] At 2M, `print()` (line 60) dominates with 17% sys time (kernel write syscall). Line 59 (struct decode) adds 16% native time. Together they account for ~46% of all CPU.

### PBPF [2M event trigger] — 31.518s total, 5MB peak

| Line | Code | Python | Native | Sys | Mem |
|:----:|:-----|:-----:|:-----:|:---:|:---:|
| 66 | `def printdata(cpu, event)` | 6% | 1% | 9% | — |
| 69 | `print(f"CPU...", flush=True)` | 2% | 10% | 15% | — |
| 86 | `perf.poll(1)` | — | 7% | **42%** | — |

> [!tip] PBPF's `print()` (line 69) costs 2% Python + 10% native + 15% sys — similar to BCC's. The poll loop (line 86) accounts for 42% sys time (epoll_wait). Overall, PBPF uses **31.5s vs BCC's 35.9s** — 12% less CPU despite processing 1.7× more callbacks.


## Pyinstrument Startup Profile

> [!tip] Pyinstrument (using `python3 -m pyinstrument`) shows the startup call tree. Both frameworks spend ~80% of time in the poll loop (idle waiting for events). The difference is in compilation: BCC 0.543s (18.8%) vs PBPF 0.170s (9.5%).

Captured via `python3 -m pyinstrument -o <file> <program>` with SIGINT after 2s startup window. No gen_fast trigger (startup + idle poll only).

### BCC startup — 2.895s total

```
2.895 <module> map_1_perf_timed_count.py:1
├─ 2.285 (78.9%) BPF.perf_buffer_poll          ← poll loop (idle)
├─ 0.543 (18.8%) BPF.__init__                    ← clang compilation
└─ 0.047          <module> bcc/__init__.py        ← imports
```

### PBPF startup — 1.798s total

```
1.798 <module> map_1_perf_timed_count.py:1
├─ 1.429 (79.5%) PerfEventArrayHelper.poll       ← poll loop (idle)
│  ├─ 1.408      pybind11.poll <built-in>         ← C++ epoll_wait
│  └─ 0.021      [self]
├─ 0.194 (10.8%) <module> pythonbpf/__init__.py    ← module imports
└─ 0.170 ( 9.5%) BPF pythonbpf/codegen.py         ← AST+llvmlite compilation
```


| Phase | BCC | PBPF | Ratio | Dominant factor |
|-------|:---:|:----:|:-----:|----------------|
| Poll (idle) | 2.285s (78.9%) | 1.429s (79.5%) | 1.6× | BCC starts polling later (more compilation upfront) |
| Compilation | **0.543s (18.8%)** | **0.170s (9.5%)** | **3.2× BCC** | Clang with 10K header reads vs llc subprocess |
| Imports | **0.047s (2%)** | **0.194s (11%)** | **4.1× PBPF** | PBPF loads pybind11 + llvmlite at import |

### BCC [2M trigger] — 40.57s wall, 10.32s CPU

```
40.569 <module> map_1_perf_timed_count.py:1
├─ 39.705 (97.9%) BPF.perf_buffer_poll
│  ├─ 22.067 (54.4%) [self]                              ← poll idle
│  └─ 17.577 (43.3%) raw_cb_ (callback dispatch)
│     └─ 16.827 print_event
│        ├─ 9.540 (23.5%) print                            ← print()
│        ├─ 3.607 (8.9%) PerfEventArray.event              ← ctypes struct decode
│        ├─ 2.775 (6.8%) [self]                            ← callback overhead
│        └─ 0.459 (1.1%) bytes.decode                       ← string decode
└─ 0.620 (1.5%) BPF.__init__                              ← compilation (one-time)
```

### PBPF [2M trigger] — 49.00s wall, 13.49s CPU

```
48.992 <module> map_1_perf_timed_count.py:1
└─ 48.761 (99.5%) PerfEventArrayHelper.poll
   ├─ 23.383 (47.7%) printdata
   │  ├─ 17.301 (35.3%) print                              ← print()
   │  ├─ 4.819 (9.8%) [self]                               ← callback overhead
   │  └─ 0.816 (1.7%) bytes.decode                          ← string decode
   ├─ 20.537 (41.9%) pybind11.poll                          ← C++ epoll_wait
   └─ 4.835 (9.9%) [self]                                   ← wrapper overhead
```

### 2M Pyinstrument Comparison

| Component | BCC | PBPF | Note |
|-----------|:---:|:----:|------|
| **Total CPU** | **10.32s** | **13.49s** | PBPF 1.3× more CPU (processes 1.7× callbacks) |
| `print()` | 9.540s (23.5%) | 17.301s (35.3%) | PBPF prints 1.7× more events |
| Struct decode | 3.607s (8.9%) | — | BCC ctypes `PerfEventArray.event` |
| `bytes.decode` | 0.459s (1.1%) | 0.816s (1.7%) | Both similar |
| Callback [self] | 2.775s (6.8%) | 4.819s (9.8%) | PBPF higher (pybind11 dispatch) |
| Poll idle | 22.067s (54.4%) | 20.537s (41.9%) | Similar — both wait for events |
| Wrapper [self] | — | 4.835s (9.9%) | PBPF pylibbpf wrapper |
| Compilation | 0.620s (1.5%) | ~0s | One-time, negligible at 2M |

> [!quote] **At 2M, both spend most CPU on `print()`**: BCC 23.5% vs PBPF 35.3%. BCC has visible ctypes struct decode (8.9%) that PBPF doesn't — PBPF's struct decode is hidden inside the pybind11 wrapper overhead. Total CPU differs by 1.3×, but PBPF processes 1.7× more callbacks (1,999,457 vs 1,164,031), meaning PBPF is more efficient per callback despite higher total CPU.

> [!warning] The poll loop dominates both profiles (~79%) but is pure idle time — the program is waiting for events, not doing work. Removing idle time, real work is **0.713s (BCC) vs 0.364s (PBPF) = 1.96×**. This is smaller than the 23× init ratio from `time.process_time()` because pyinstrument includes wall time (poll sleeps), while `process_time()` only counts CPU.

**Net takeaway:** BCC's 3.2× slower compilation is the single biggest startup gap. PBPF's 4.1× slower imports are a one-time cost that doesn't affect event processing. The 1.6× total gap is amplified to 23× in `process_time()` because pyinstrument includes idle poll time (CPU-free) while `process_time()` doesn't.

## Log Files Reference

| File | Test | Notes |
|------|:----:|-------|
| `/tmp/bcc_map_1_perf_timed_count_perfstat.txt` | BCC perf stat | Startup |
| `/tmp/pbpf_map_1_perf_timed_count_perfstat.txt` | PBPF perf stat | Startup |
| `/tmp/bcc_map_1_perf_timed_count_strace.txt` | BCC strace | Startup |
| `/tmp/pbpf_map_1_perf_timed_count_strace.txt` | PBPF strace | Startup |
| `/tmp/bcc_cnt_xlated.txt` | BCC xlated | Bytecode |
| `/tmp/bcc_cnt_jited.txt` | BCC JIT | Bytecode |
| `/tmp/pbpf_cnt_xlated.txt` | PBPF xlated | Bytecode |
| `/tmp/pbpf_cnt_jited.txt` | PBPF JIT | Bytecode |
| `/tmp/bcc_map_1_perf_timed_count_scalene.json` | BCC scalene | Startup (263KB) |
| `/tmp/bcc_map_1_perf_timed_count_scalene_2m.json` | BCC scalene | 2M (7.9MB) |
| `/tmp/pbpf_map_1_perf_timed_count_scalene.json` | PBPF scalene | Startup (4.6MB) |
| `/tmp/pbpf_map_1_perf_timed_count_scalene_2m.json` | PBPF scalene | 2M (7.9MB) |
| `/tmp/pbpf_map_1_perf_timed_count_scalene2.json` | PBPF scalene (alt) | Startup (14MB) |
| `/tmp/bcc_map_1_perf_timed_count_pyinstrument.txt` | BCC pyinstrument | Startup (490B) |
| `/tmp/pbpf_map_1_perf_timed_count_pyinstrument.txt` | PBPF pyinstrument | Startup (742B) |
| `/tmp/bcc_map_1_perf_timed_count_2m.data` | BCC perf data | 2M (21MB) |
| `/tmp/pbpf_map_1_perf_timed_count_2m.data` | PBPF perf data | 2M (14MB) |
| `/tmp/bcc_cnt_2m.folded` | BCC folded stacks | 2M |
| `/tmp/pbpf_cnt_2m.folded` | PBPF folded stacks | 2M |
| `/root/flamegraphs/bcc_map_1_perf_timed_count_2m.svg` | BCC flamegraph | 2M (467KB) |
| `/root/flamegraphs/pbpf_map_1_perf_timed_count_2m.svg` | PBPF flamegraph | 2M (399KB) |