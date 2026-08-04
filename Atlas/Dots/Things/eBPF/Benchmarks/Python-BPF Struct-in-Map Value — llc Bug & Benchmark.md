---
created: 2026-08-04
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
related:
  - "[[Embedded Counter Benchmark]]"
  - "[[PythonBPF Structs]]"
  - "[[Python-BPF Compiler Limitations]]"
in: "[[Atlas]]"
tags:
  - ebpf
  - pythonbpf
  - benchmark
  - struct-map
  - compiler-bug
  - btf
---

# Python-BPF Struct-in-HashMap-Value: perf vs single (and the llc bug)

> [!summary] PBPF **can** use a struct as a HashMap value, but only if the BPF code uses **read-then-update** (construct a fresh struct, `update()`). The docs' **write-through-map** pattern (`stats.count = ...` then `update(stats)`) crashes llc with `invalid getelementptr indices`. At 2M events the struct-map program costs **8,619 ns/ev** — 19% slower than the u64-counter program (7,255 ns/ev).

## Programs

| File | Map value | Status |
|------|-----------|--------|
| `maps_with_struct_perf.py` | `Stats { count: u64 }` — docs pattern (write-through) | ❌ llc error |
| `maps_with_struct_single.py` | `Stats { count: u64 }` — read-then-update | ✅ works |

Both: `/root/learn-pythonbpf/syscall_trigger/with_map/`. Same skeleton as `map_1_perf_timed_count.py` (SIGINT handler, `data_t` perf event, `Count`/`events` maps, `t0..t3` timing, poll loop, `[TIMING]`/`[SUMMARY]` prints).

## The llc error (maps_with_struct_perf.py)

Docs pattern ([maps.md](https://github.com/pythonbpf/Python-BPF/blob/master/docs/user-guide/maps.md)):
```python
stats = process_stats.lookup(process_id)
if stats:
    stats.count = stats.count + 1      # write through map pointer
    process_stats.update(process_id, stats)
```

Fails at `b = BPF()`:
```
subprocess.CalledProcessError: llc -march=bpf -filetype=obj -O2 ... returned non-zero exit status 1
```

**Root cause (LLVM IR):** the write-through generates a double-index GEP on the `i64*` lookup result:
```llvm
%".13" = getelementptr inbounds i64*, i64** %"stats", i32 0, i32 0   ; ❌
```
`i64*` is a pointer, not an aggregate — you cannot index into it twice. llc: `error: invalid getelementptr indices`.

**Why single-field worked before / why this is the same bug:** the GEP appears regardless of field count; the docs 3-field example trips it identically. The working `maps_with_struct_single.py` avoids it entirely by never writing through the map pointer.

## The fix (maps_with_struct_single.py)

Read the field, build a fresh struct, update:
```python
stats = Count.lookup(u_id)
if stats:
    new_count = stats.count + 1
else:
    new_count = 1
s = Stats()
s.count = new_count
Count.update(u_id, s)
data.count = new_count
```

## BTF bug (both programs)

Even when it compiles, the BTF blob is malformed:
```
[4] STRUCT (anon) size=8 vlen=1
        count type_id=5 bits_offset=8   ← should be 0
Member exceeds struct_size
```
PBPF's BTF encoder writes the first struct member at `bits_offset=8` (1 byte) instead of 0 → kernel rejects `BPF_BTF_LOAD` (`-EINVAL`). libbpf logs the dump, then **"BTF is optional, ignoring"** — the program still loads/runs (map layout comes from the program's own type info). Consequence: no CO-RE, no BTF introspection for that map.

## Benchmark — 2M events (`sys_enter_unlink`, uid 1002, gen_fast)

| Metric | **PBPF struct-map** | PBPF count (u64) | BCC count (u64) |
|--------|:---:|:---:|:---:|
| Delivered / 2M | **1,989,747 (99.4%)** | 1,997,971 (99.9%) | 1,523,098 (76%) |
| Poll loop CPU | 17.151s | 14.496s | 12.512s |
| **ns/event** | **8,619** | **7,255** | **8,213** |
| Map value | struct `Stats` | `u64` | `u64` |

**Verdict: struct-map is a capability demo, not a perf win.**
- **vs PBPF count:** +1,364 ns/ev (+19%) — the struct construction + update round-trip in the BPF program.
- **vs BCC count:** +406 ns/ev (+5%) — but delivers **99.4% vs 76%**, so it still wins on delivery the same way the u64 count program does (PBPF drains the perf buffer faster).
- Use **u64 counters** for hot paths; struct values only when you genuinely need multi-field per-key state.

## Origin story — why `map_1_perf_timed_timing.py` exists

The struct-map attempt was the **early motivation for `map_1_perf_timed_timing.py`**: the goal was to read a value back from the map *inside the userspace callback* to time/observe it. `timing.py` does `Count.lookup(u_id)` + `HashMap.values()` in the callback — **2 extra BPF syscalls per event** (`get_next_key` + `lookup_elem`) — which produced the **stale counter** artifact (all callbacks print `count: 20` for 20 events) that led to the embedded-counter fix in `map_1_perf_timed_count.py`. The struct-map experiment hit the llc GEP bug and was set aside — the u64 + embedded-counter path became the benchmark.

**Timeline:**
1. Struct-in-map attempt → llc GEP bug → abandoned (this note)
2. `map_1_perf_timed_timing.py` — callback reads map via BPF syscalls → stale counter
3. `map_1_perf_timed_count.py` — embedded counter in `data_t` at BPF time → correct sequence ([[Embedded Counter Benchmark]])

## Related

- [[Embedded Counter Benchmark]] — the fix that replaced the timing program
- [[PythonBPF Structs]] — `@bpf @struct` as map values/payloads (docs claim)
- [[Python-BPF Compiler Limitations]] — other expr_pass/codegen gaps
