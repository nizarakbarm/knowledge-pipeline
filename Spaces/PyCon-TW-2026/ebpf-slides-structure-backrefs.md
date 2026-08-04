---
created: 2026-07-27
up:
  - "[[Spaces/PyCon-TW-2026/ebpf-slides-structure]]"
  - "[[Spaces/PyCon-TW-2026/fresh-benchmark-results]]"
  - "[[BCC vs Python-BPF Comparisons MOC]]"
tags:
  - ebpf
  - benchmark
  - reference
  - pycon-tw-2026
---

> [!warning] **Log archive location (final, verified 2026-07-29):** TWO copies exist — a **local** archive at `~/low_level_programming/out_temp_log/` (249 files incl. source, logs, perf data, flamegraphs) AND a **remote** mirror at `/root/out_temp_log/` on `vmdevnull`. **Prefer the local copy** — it is the full archive (73 subdirs, ~4.5 GB). The `.data` and `.folded` files are write-protected locally (`-rw-------`). The `/tmp/` working copies on the VM are cleaned after archiving.

# Benchmark Artifact Locations — BCC vs Python-BPF

Reference for slide creation. **Primary path: `~/low_level_programming/out_temp_log/`** (local). Remote mirror at `/root/out_temp_log/` on `vmdevnull`. Program source files live on `vmdevnull` under `/root/learn-{BCC,pythonbpf}/`.

## 1. Program Source Files

### with_map + full (HashMap + print per event)
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed.py` |

### with_map + empty (HashMap, no print)
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_empty.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_empty.py` |

### with_map + e100 (HashMap, print every 100th)
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_e100.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_e100.py` |

### perf_timed (without_map, struct + print, no HashMap)
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/without_map/perf_timed.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/without_map/perf_timed.py` |

### perf_only + no-struct (empty callback, no struct)
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/without_map/perf_empty_no_struct.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/without_map/perf_empty_no_struct.py` |

### map_1_perf_timed_timing (naive counter read, 2 BPF syscalls/event) — slide 5.1
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_timing.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_timing.py` |

### map_1_perf_timed_count (embedded counter) — slide 5.2
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/syscall_trigger/with_map/map_1_perf_timed_count.py` |
| PBPF | `/root/learn-pythonbpf/syscall_trigger/with_map/map_1_perf_timed_count.py` |

### bpf_only_syscall (minimal kprobe, return 0) — Layer 0, slide 4a
| Framework | Path |
|-----------|------|
| BCC | `/root/learn-BCC/bcc_only_bpf_syscall.py` |
| PBPF | `/root/learn-pythonbpf/pythonbpf_only_bpf_syscall.py` |

### bpf_only_syscall strace files — Layer 0, slide 4a
| Framework | Path |
|-----------|------|
| BCC | `/root/straces/bpf_only_syscall_bcc_strace.txt` (733.9K, full) |
| PBPF | `/root/straces/bpf_only_syscall_pythonbpf_strace.txt` (85.5K) |

---

## 2. Benchmark Output Logs

Base path: **`~/low_level_programming/out_temp_log/`** (local, primary) — remote mirror `/root/out_temp_log/` on `vmdevnull`. Paths below are relative to it unless noted. The `/tmp/` working copies on the VM were cleaned after archiving.

### Embedded counter benchmark (slide 5.2) — VERIFIED (both copies)

| File | Contents |
|------|----------|
| `bcc_cnt{5,10,20,2k,2m,2m_perf,2m_v3}.log` | BCC count program runs (2m = 72MB, 2m_v3 = 58MB) |
| `pbpf_cnt2m_perf.log` | PBPF count 2M under perf record (97MB) |
| `bcc_map_1_perf_timed_count_strace.txt` / `pbpf_map_1_perf_timed_count_strace.txt` | Startup strace -c (5.2 syscall table) |
| `bcc_map_1_perf_timed_count_perfstat.txt` / `pbpf_map_1_perf_timed_count_perfstat.txt` | perf stat (5.2 cycles) |
| `bcc_cnt_timev.txt` / `pbpf_cnt_timev.txt` | /usr/bin/time -v (RSS, CPU) |
| `bcc_cnt_xlated.txt` / `bcc_cnt_jited.txt` | BCC bytecode (49 insns / 242B JIT) |
| `pbpf_cnt_xlated.txt` / `pbpf_cnt_jited.txt` | PBPF bytecode (64 insns / 347B JIT) |
| `bcc_map_1_perf_timed_count_2m.data` (21MB) / `pbpf_map_1_perf_timed_count_2m.data` (14MB) | perf record data |
| `bcc_cnt_2m.folded` / `pbpf_cnt_2m.folded` | Folded stacks |

### 2M events (clean, no perf record)

| Test | BCC log | PBPF log |
|------|--------:|---------:|
| perf_timed (without_map) | `/tmp/bpt2m.log` (VM only) | `/tmp/ppt2m.log` (VM only) |
| perf_only + no-struct | `bcc_pf_nostruct_2m.log` | `pbpf_pf_nostruct_2m.log` |
| perf_only + empty | `bcc_pf_empty_2m.log` | `pbpf_pf_empty_2m.log` |
| perf_only + full | `bcc_pf_full_2m.log` | `pbpf_pf_full_2m.log` |
| with_map + empty | `bcc_wm_empty_2m.log` | `pbpf_wm_empty_2m.log` |
| with_map + e100 | `bcc_wm_e100_2m.log` | `pbpf_wm_e100_2m.log` |
| with_map + full | `bcc_wm_full_2m.log` | `pbpf_wm_full_2m.log` |
| with_map + full (fg) | `bcc_wm_2m_fg.log` | `pbpf_wm_2m_fg.log` |

### 2M events (under perf record)

| Test | BCC log | PBPF log |
|------|--------:|---------:|
| with_map + full | `/tmp/bcc_wm2m_perf.log` (VM only) | `/tmp/pbpf_wm2m_perf.log` (VM only) |
| perf_timed (without_map) | `/tmp/bcc_pt2m_perf.log` (VM only) | `/tmp/pbpf_pt2m_perf.log` (VM only) |

### Small count tests (under perf record)

All **VM only** at `/tmp/`:

| Count | BCC log | PBPF log |
|-------|--------:|---------:|
| 5 | `/tmp/bcc_wm5_perf.log` | `/tmp/pbpf_wm5_perf.log` |
| 10 | `/tmp/bcc_wm10_perf.log` | `/tmp/pbpf_wm10_perf.log` |
| 50 | `/tmp/bcc_wm50_perf.log` | `/tmp/pbpf_wm50_perf.log` |
| 2000 | `/tmp/bcc_wm2k_perf.log` | `/tmp/pbpf_wm2k_perf3.log` |

### 50-event tests

All at `~/low_level_programming/out_temp_log/`:

| Test | BCC log | PBPF log |
|------|--------:|---------:|
| perf_only + no-struct | `bcc_pf_nostruct_50.log` | `pbpf_pf_nostruct_50.log` |
| perf_only + empty | `bcc_pf_empty_50.log` | `pbpf_pf_empty_50.log` |
| perf_only + full | `bcc_pf_full_50.log` | `pbpf_pf_full_50.log` |
| with_map + empty | `bcc_wm_empty_50.log` | `pbpf_wm_empty_50.log` |
| with_map + e100 | `bcc_wm_e100_50.log` | `pbpf_wm_e100_50.log` |
| with_map + full | `bcc_wm_full_50.log` | `pbpf_wm_full_50.log` |

## 3. Flamegraph SVGs

All at `/root/flamegraphs/` on vmdevnull.

| File | Size | Test | Events |
|------|:----:|------|:------:|
| `bcc_wm_2m.svg` | 140KB | with_map + full (old capture) | 2M |
| `pbpf_wm_2m.svg` | 172KB | with_map + full (old capture) | 2M |
| `bcc_wm_full_perf.svg` | **428KB** | with_map + full (perf direct) | **2M** |
| `pbpf_wm_full_perf.svg` | **457KB** | with_map + full (perf direct) | **2M** |
| `bcc_pt2m_perf.svg` | **347KB** | perf_timed, no HashMap (perf direct) | **2M** |
| `pbpf_pt2m_perf.svg` | **338KB** | perf_timed, no HashMap (perf direct) | **2M** |
| `bcc_map_1_perf_timed_count_2m.svg` | — | **count program (slide 5.2)** | **2M** |
| `pbpf_map_1_perf_timed_count_2m.svg` | — | **count program (slide 5.2)** | **2M** |
| `bcc_wm2k_perf.svg` | 243KB | with_map + full | 2000 |
| `pbpf_wm2k_perf.svg` | 190KB | with_map + full | 2000 |
| `bcc_wm5_perf.svg` | 267KB | with_map + full | 5 |
| `bcc_wm10_perf.svg` | 217KB | with_map + full | 10 |
| `bcc_wm50_perf.svg` | 217KB | with_map + full | 50 |
| `pbpf_wm5_perf.svg` | 227KB | with_map + full | 5 |
| `pbpf_wm10_perf.svg` | 204KB | with_map + full | 10 |
| `pbpf_wm50_perf.svg` | 185KB | with_map + full | 50 |

---

## 4. Perf Data Files

All in `/tmp/` on vmdevnull.

| File | Size | Contents |
|------|:----:|----------|
| `/tmp/bcc_wm_full_perf.data` | 11MB | BCC with_map 2M (perf direct) |
| `/tmp/pbpf_wm_full_perf3.data` | 14MB | PBPF with_map 2M (perf direct) |
| `/tmp/bcc_pt2m_perf.data` | 11MB | BCC perf_timed 2M |
| `/tmp/pbpf_pt2m_perf.data` | 11MB | PBPF perf_timed 2M |
| `/tmp/bcc_wm2k_perf.data` | 1.8MB | BCC with_map 2000 |
| `/tmp/pbpf_wm2k_perf3.data` | 835KB | PBPF with_map 2000 |
| `/tmp/bcc_wm5_perf.data` | 1.7MB | BCC with_map 5 |
| `/tmp/bcc_wm10_perf.data` | 1.5MB | BCC with_map 10 |
| `/tmp/bcc_wm50_perf.data` | 1.7MB | BCC with_map 50 |
| `/tmp/pbpf_wm5_perf.data` | 735KB | PBPF with_map 5 |
| `/tmp/pbpf_wm50_perf.data` | 576KB | PBPF with_map 50 |

Count program (slide 5.2) — at `/root/out_temp_log/`:

| File | Size | Contents |
|------|:----:|----------|
| `/root/out_temp_log/bcc_map_1_perf_timed_count_2m.data` | 21MB | BCC count 2M (perf direct) |
| `/root/out_temp_log/pbpf_map_1_perf_timed_count_2m.data` | 14MB | PBPF count 2M (perf direct) |
---

## 5. Folded Stack Data (for flamegraph/analysis)

All in `/tmp/` on vmdevnull.

| File | Source |
|------|--------|
| `/tmp/bcc_wm2m.folded` | BCC with_map 2M |
| `/tmp/pbpf_wm2m.folded` | PBPF with_map 2M |
| `/tmp/bcc_pt2m.folded` | BCC perf_timed 2M |
| `/tmp/pbpf_pt2m.folded` | PBPF perf_timed 2M |
| `/tmp/bcc_2k.folded` | BCC with_map 2000 |
| `/tmp/pbpf_2k.folded` | PBPF with_map 2000 |

---

## 6. Bytecode & JIT Dumps

All at `/root/straces/` on vmdevnull.

### bpf_only_syscall (minimal kprobe, return 0)

| File | Contents |
|------|----------|
| `/root/straces/pythonbpf_xlated_275.txt` | PBPF xlated — 2 insns: `r0=0; exit` |
| `/root/straces/pythonbpf_jited_275.txt` | PBPF JIT — 9 native insns, BTF `a04f5eef06a7f555` |
| `/root/straces/bcc_xlated_297.txt` | BCC xlated — 2 insns: `r0=0; exit` |
| `/root/straces/bcc_jited_297.txt` | BCC JIT — 9 native insns, BTF `a04f5eef06a7f555` |

Both produce **identical** bytecode. Different prog IDs (275 vs 297) from different sessions. Different trampoline target address.

### count program (slide 5.2) — at `/root/out_temp_log/`

| File | Contents |
|------|----------|
| `/root/out_temp_log/bcc_cnt_xlated.txt` | BCC count — 49 insns (400B) |
| `/root/out_temp_log/bcc_cnt_jited.txt` | BCC count — 242B JIT |
| `/root/out_temp_log/pbpf_cnt_xlated.txt` | PBPF count — 64 insns (616B) |
| `/root/out_temp_log/pbpf_cnt_jited.txt` | PBPF count — 347B JIT |

### tracepoint programs

| File | Contents |
|------|----------|
| `/root/straces/pythonbpf_tp_xlated_1456.txt` | PBPF tracepoint xlated |
| `/root/straces/pythonbpf_tp_jited_1456.txt` | PBPF tracepoint JIT |
| `/root/straces/bcc_tp_xlated_1479.txt` | BCC tracepoint xlated |
| `/root/straces/bcc_tp_jited_1479.txt` | BCC tracepoint JIT |
| `/root/straces/bcc_tp_xlated_1485.txt` | BCC (variant) xlated |
| `/root/straces/bcc_tp_jited_1485.txt` | BCC (variant) JIT |
| `/root/straces/bcc_tp_xlated_1488.txt` | BCC (variant) xlated |
| `/root/straces/bcc_tp_jited_1488.txt` | BCC (variant) JIT |
| `/root/straces/pybpf_measure_jited.txt` | PBPF JIT measurement |

---

## 7. JIT Instruction Cost Measurements

| Location | Contents |
|----------|----------|
| `/root/jit_measurement/` | JIT instruction cost framework — cycle measurement via RDTSC |
| `+/JIT Instruction Cost Measurement Framework.md` | Vault note documenting JIT cost methodology |

---

## 8. gen_fast Trigger

| Path | Purpose |
|------|---------|
| `/tmp/gen_fast` | Benchmark trigger — fires N `unlink()` calls at uid=1002 |
| Run via: `sudo -u radare2 /tmp/gen_fast <N>` | 2M events in ~3.6s, per-event rate ~1.81µs |