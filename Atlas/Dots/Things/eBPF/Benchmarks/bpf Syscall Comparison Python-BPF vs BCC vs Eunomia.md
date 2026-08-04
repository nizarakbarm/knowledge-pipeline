---
created: 2026-07-14
updated: 2026-07-29
up:
  - "[[BCC vs Python-BPF Comparisons MOC]]"
tags:
  - ebpf
  - pythonbpf
  - bcc
  - eunomia
  - benchmark
  - syscall
---
# bpf() Syscall Comparison: Python-BPF vs BCC vs Eunomia-bpf

> [!summary] BCC makes **11× more syscalls** than PBPF and Eunomia for the same minimal 2-insn kprobe program. The gap is entirely from BCC's kernel header reading (`read` syscalls). This note compares the **bpf() syscall layer only** — not total startup cost.

## Programs compared

All load a minimal 2-insn KPROBE program (`r0 = 0; exit`) with `SEC("kprobe/do_nanosleep")` + attach.

## Complete strace comparison

> [!example]- Python-BPF (load + attach)
> ```
> bpf() call                              type            ret   notes
> ──────────────────────────────────────────────────────────────────────
> TOKEN_CREATE                            —               -1    EOPNOTSUPP
> PROG_LOAD                               SOCKET_FILTER    3    probe: bpf_object__probe_loading()
> PROG_LOAD                               SOCKET_FILTER    3    probe: feature detection
> PROG_LOAD ("libbpf_nametest")           SOCKET_FILTER    3    probe: FEAT_PROG_NAME
> PROG_LOAD "nop"                         KPROBE           3    user program (2 insns, no BTF)
> PROG_LOAD                               TRACEPOINT       5    probe: FEAT_PERF_LINK
> LINK_CREATE (prog_fd=5, tgt=-1)         —               -1    probe: link test → EBADF (expected)
> LINK_CREATE (prog_fd=3, tgt=4)          —                5    real attach (nop → perf_event)
> ─────
> Total: 8 bpf() calls
> BTF_LOADs: 0 · Extra internal programs: 0
> ```
>
>> [!info]- Why so many probes? libbpf probes kernel features at `BpfObject.load()` — loading socket_filter programs to detect BPF support, naming, and perf_link availability. These close after probing; zero trace in final fdinfo.

> [!example]- BCC (with attach)
> ```
> bpf() call                              type            ret   notes
> ──────────────────────────────────────────────────────────────────────
> PROG_LOAD                               SOCKET_FILTER    —    BCC init probe
> BTF_LOAD                                —                —    BTF generation
> PROG_LOAD "hello"                       KPROBE           —    user program (loaded at attach)
> [perf_event_open]                       —                —    not a bpf() call
> [ioctl PERF_EVENT_IOC_SET_BPF]          —                —    not a bpf() call
> ─────
> Total: 2–3 bpf() calls visible
> BTF_LOADs: 1 · Extra internal programs: 0
> ```
>
> [!warning] BCC bypasses libbpf entirely — uses `ioctl` directly, no `LINK_CREATE`. Loading is deferred to `attach_kprobe()`, not done at object load.

> [!example]- Eunomia-bpf (ecli run package.json)
> ```
> bpf() call                              type            ret   notes
> ──────────────────────────────────────────────────────────────────────
> TOKEN_CREATE                            —               -1    EOPNOTSUPP
> PROG_LOAD                               SOCKET_FILTER    7    probe: bpf_object__probe_loading()
> PROG_LOAD                               SOCKET_FILTER    7    probe: feature detection
> BTF_LOAD × 3                            —                7    det_arg_ctx BTF
> PROG_LOAD ("libbpf_nametest")           SOCKET_FILTER    8    probe: FEAT_PROG_NAME
> PROG_LOAD "det_arg_ctx"                 KPROBE           8    eunomia internal (4 insns + func_info)
> BTF_LOAD × 7                            —                7    CO-RE BTF for user program
> PROG_LOAD "NOP"                         KPROBE           8    user program (2 insns + BTF + line_info)
> PROG_LOAD                               TRACEPOINT      10    probe: FEAT_PERF_LINK
> LINK_CREATE (prog_fd=10, tgt=-1)        —               -1    probe: link test → EBADF (expected)
> LINK_CREATE (prog_fd=8, tgt=9)          —               10    real attach (NOP → perf_event)
> ─────
> Total: ~20 bpf() calls
> BTF_LOADs: 11 · Extra internal programs: 1 (det_arg_ctx)
> ```
>
> [!tip] Eunomia loads 11× BTF — full CO-RE for both user program and internal `det_arg_ctx` compatibility check. Rust-based, libbpf-rs.

### Load-only (no attach, timing)

> [!example]- Python-BPF load only
> ```
> bpf() call                    type           time
> ─────────────────────────────────────────────────
> TOKEN_CREATE                  —              14 µs
> PROG_LOAD                     SOCKET_FILTER  166 µs
> PROG_LOAD                     SOCKET_FILTER   39 µs
> PROG_LOAD ("libbpf_nametest") SOCKET_FILTER   72 µs
> PROG_LOAD "nop"               KPROBE         103 µs
> ─────
> Total: 5 calls, ~394 µs
> ```

> [!example]- BCC load only
> ```
> bpf() call                    type           time
> ─────────────────────────────────────────────────
> PROG_LOAD                     SOCKET_FILTER  232 µs
> BTF_LOAD                      —              57 µs
> ─────
> Total: 2 calls, ~289 µs
> ```

## Final fd state (Python-BPF, after full cycle)

From `/proc/<pid>/fdinfo/`:

| fd | Identity | Created by |
|---|---|---|
| 3 | `anon_inode:bpf-prog` (KPROBE "nop", prog_id=727) | `bpf_program_load()` |
| 4 | `anon_inode:[perf_event]` | `perf_event_open_probe("do_nanosleep")` — invisible to `-e bpf` strace |
| 5 | `anon_inode:bpf_link` (prog 3 → perf 4, link_id=62) | 2nd LINK_CREATE (reuses fd 5 after probe closed it) |

The 3 SOCKET_FILTER probe programs + TRACEPOINT probe program are all **closed after probing** — zero trace in final fdinfo.

> [!abstract]- Key Differences
>
| Aspect | Python-BPF | BCC | Eunomia-bpf |
> |---|---|---|---|
> | **Framework** | pylibbpf (libbpf C) | BCC (vendored libbpf fork) | libbpf-rs (Rust) |
> | **bpf_object layer?** | ✅ Yes | ❌ No — raw `bpf_prog_load()` | ✅ Yes |
> | **Feature probes at load?** | ✅ Yes | ❌ No | ✅ Yes |
> | **BTF for user prog** | ❌ no | ❌ no (uses own BTF gen) | ✅ yes (full CO-RE) |
> | **Extra internal progs** | 0 | 0 | 1 (det_arg_ctx) |
> | **Attach method** | LINK_CREATE | `ioctl` | LINK_CREATE |
> | **FEAT_PERF_LINK probe** | ✅ yes | ❌ no | ✅ yes |
> | **bpf_link created?** | ✅ yes | ❌ no | ✅ yes |
> | **Total bpf() calls (load+attach)** | ~8 | ~2-3 | ~20 |

> [!info]- Why BCC Uses a Completely Different Path
>
> BCC is not just "Python-BPF without the probes." It is architecturally different at every layer.
>
> **Loading:**
> ```
> BCC:  BPF(text) → bcc_func_load() → bcc_prog_load_xattr() → libbpf_bpf_prog_load() → syscall(SYS_bpf, BPF_PROG_LOAD)
> ```
> BCC calls `bpf_prog_load()` directly — **no bpf_object**, no probe infrastructure.
>
> ```
> Python-BPF:  BpfObject.load() → bpf_object_load() → bpf_object__probe_loading() → bpf_prog_load() with cached results
> ```
>
> **Attaching:**
> ```
> Python-BPF:  bpf_program__attach_kprobe_opts() → bpf_program__attach_perf_event_opts()
>               → kernel_supports(FEAT_PERF_LINK)?
>                 → LINK_CREATE(prog_fd, perf_fd, BPF_PERF_EVENT)    [returns bpf_link fd]
>                 OR → ioctl(perf_fd, PERF_EVENT_IOC_SET_BPF, prog_fd)
> ```
> ```
> BCC:  bpf_attach_kprobe() → perf_event_open() → ioctl(PERF_EVENT_IOC_SET_BPF, progfd) → ioctl(ENABLE)
> ```
>
> BCC uses **perf_event_open() syscall + ioctl** — completely different from `BPF_LINK_CREATE`. No `bpf_link` fd, no `bpf_cookie`. BCC predates `BPF_LINK_CREATE` (Linux 5.7) and was never updated.

> [!details]- How FEAT_PERF_LINK Detection Works (click to expand)
>
> `FEAT_PERF_LINK` is an enum in libbpf's `kern_feature_id` (`libbpf_internal.h:377`):
> ```c
> /* BPF perf link support */
> FEAT_PERF_LINK,
> ```
>
> Detects whether kernel supports `BPF_LINK_CREATE` with `attach_type=BPF_PERF_EVENT` (added in **Linux 5.7**, commit `0e4c0e0f37d9`).
>
> **Probe algorithm:**
> 1. Load a dummy 2-insn TRACEPOINT program
> 2. Call `BPF_LINK_CREATE(prog_fd=probe, target_fd=-1, BPF_PERF_EVENT)` with deliberately invalid `target_fd=-1`
> 3. Check return:
>    - **`EBADF`** → kernel accepted syscall structure (just rejected fd) → `FEAT_PERF_LINK` = supported ✅
>    - **`ENOTSUP`/`EINVAL`/`EPERM`** → kernel rejected command → feature missing ❌
> 4. Close probe program fd
>
> **Before** 5.7: `perf_event_open()` + `ioctl(SET_BPF)` — no refcounting, crash leaves kprobe active.
>
> **Since** 5.7: `perf_event_open()` + `bpf_link_create()` — closing link fd auto-detaches. Also enables `bpf_get_attach_cookie()`.
>
> **Who probes:**
> - **Python-BPF & eunomia**: both use libbpf → both trigger the probe
> - **BCC**: bypasses libbpf, uses `ioctl` directly → no probe
> - Kernel 6.12 supports perf links → probe succeeds → strace shows successful `LINK_CREATE`

> [!info]- The `det_arg_ctx` Extra Program (Eunomia Only)
>
> Eunomia loads `det_arg_ctx` (4 insns, with func_info) to detect the kernel's kprobe argument context type at runtime — a CO-RE compatibility check that verifies `struct pt_regs` layout before loading the real program. Python-BPF and BCC don't do this; they trust the compile-time type.

> [!important] Key Implications
>
> 1. **The bpf() syscall time is negligible** (<0.5 ms total) in all cases. The real startup cost is framework initialization — not kernel probes.
> 2. **BCC's simpler bpf() call count is deceptive** — its 2-3 calls are offset by 10,489 `read()` calls for `/proc/kallsyms`, 212 `ioctl` calls, and in-process Clang compilation.
> 3. **Python-BPF probes add ~6 extra bpf() calls** (~345 µs) — a trivial cost for the benefit of using modern libbpf infrastructure (bpf_link, auto-detach, bpf_cookie).
> 4. **Eunomia's extra BTF cost** (11 BTF_LOADs) is for full CO-RE support — useful for portability across kernel versions, but expensive at startup.

## Source references

- Python-BPF codegen: `pythonbpf/codegen.py:58,225` — `BPF()` calls `BpfObject` from `pylibbpf`
- pylibbpf loader: `pylibbpf/src/core/bpf_object.cpp:58-80` — `load()` calls `bpf_object__load(obj_)`
- BCC loader: `bcc/src/cc/bpf_module.cc:139-210,985` — `BPFModule::BPFModule()` does Clang compile only; `bcc_func_load()` does actual `BPF_PROG_LOAD`
- BCC BTF: `bpf_module.cc:325-360` (`BPFModule::load_btf`)
- Eunomia-bpf: `ecli` binary (Rust, libbpf-rs based)
- Kernel libbpf feature probes: `tools/lib/bpf/libbpf.c:5172-5197` (`bpf_object__probe_loading`), `:7961-7962` (`FEAT_PROG_NAME`), `:11555` (`FEAT_PERF_LINK`)
- `FEAT_PERF_LINK` definition: `tools/lib/bpf/libbpf_internal.h:377`
- Linux 5.7 commit: `0e4c0e0f37d9` ("bpf: Implement BPF_LINK_CREATE tracing")

## Related

- [[BPF Syscall-Only — kallsyms Symbol Resolution Overhead]]
- [[BPF Syscall-Only — Memory Footprint]]
- [[BPF Syscall-Only — BCC In-Process Clang Compilation Path]]
- [[Measuring bpf Syscall Time]]
- [[Capturing JIT Dump of Short-Lived BPF Program]]
