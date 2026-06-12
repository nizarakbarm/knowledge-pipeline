---
created: 2026-06-12
up:
  - "[[Tetragon TracingPolicy]]"
  - "[[eBPF MOC]]"
related:
  - "[[Tetragon Overview]]"
  - "[[Tetragon Events]]"
  - "[[Tetragon TracingPolicy - Argument Types]]"
  - "[[Tetragon TracingPolicy - Example]]"
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[eBPF Concept - BPF_CORE_READ]]"
  - "[[Kubernetes]]"
in:
  - "[[Things]]"
tags:
  - concept
  - hook-points
  - tetragon
  - tracing-policy
  - ebpf
  - security
  - kubernetes
---

# Tetragon TracingPolicy - Hook Points

## Summary

The five instrumentation families available in [[Tetragon TracingPolicy]] — kprobes, tracepoints, uprobes, USDTs, and LSM BPF — plus the argument resolution system, return value tracking, function lists, and selector macros that complete the hook point specification.

## Key Points

- Five hook types span kernel-space (kprobes, tracepoints, LSM BPF) and user-space (uprobes, USDTs)
- LSM BPF is the **only** hook type that enforces *before* operation completion — eliminates TOCTOU race conditions
- BTF attribute resolution enables dynamic nested kernel structure extraction without manual offset calculation
- Function lists and selector macros provide reusability across multiple hooks within a policy

## Hook Types

### Kprobes

Dynamic hooking of any kernel function. Key details:

- **Architecture-prefixed symbols** (`__arm64_`, `__x64_`) — use bare names (`sys_write`) for cross-architecture portability
- The `syscall` field selects between syscall entry ABI and regular kernel function calling convention
- Kernel symbols discoverable via `/proc/kallsyms`
- Most flexible but may break across kernel versions (dynamic attachment)

### Tracepoints

Statically defined kernel instrumentation with **stable ABI** across versions.

- Discovered under `/sys/kernel/tracing/events/` organized by subsystem (e.g., `net`, `syscalls`, `sched`)
- **Raw tracepoints** (`raw: true`) bypass the perf subsystem for lower latency and direct kernel argument access
- Support `resolve` for field extraction from `TRACE_EVENT` arguments
- Preferred over kprobes when a stable tracepoint exists for the target function

### Uprobes

Dynamic user-space function hooking via binary symbol resolution.

- Specify the **path** to the executable/library and **symbol names** (found with `nm`, `objdump`, `readelf`)
- Support the full selector suite including `matchArgs`, `matchReturnArgs`, and `matchBinaries`
- Binary-dependent stability — symbol changes across versions break the hook

### USDTs (User Statically-Defined Tracing)

Tracing probes embedded in ELF binaries by the application developer.

- Addressed by **Path + Provider + Name** triple
- Use `tetra tracingpolicy generate usdts` to auto-generate policy YAML from a binary
- **Max 5 arguments** per probe
- Most stable user-space instrumentation (application-defined ABI)

### LSM BPF (Linux Security Module)

Hook instrumentation for Mandatory Access Control and Audit.

- Requires `CONFIG_BPF_LSM=y` and `bpf` listed in `/sys/kernel/security/lsm`
- The **only** hook type that enforces *before* operation completion
- Eliminates **TOCTOU race conditions** inherent in kprobe-based enforcement (operates on kernel-resident state)
- Preferred for security-critical enforcement where timing matters

## Arguments & Attribute Resolution

### Basic Argument Specification

The `args` list specifies function arguments by `index` and `type` (from the TracingPolicy CRD). Optional `label` parameter annotates output.

### Buffer Capture Options

- `char_buf`/`char_iovec` types support `returnCopy` — captures buffer content on function *return* (after the syscall modifies it)
- `sizeArgIndex` (1-based) points to the length argument — **not** 0-based
- `maxData` flag extends `char_buf` capture from 4,096 to 327,360 bytes

### BTF Attribute Resolution

The `resolve` flag dynamically traverses nested kernel structures via **dot notation** (e.g., `mm.owner.real_parent.comm`).

- Works on **kprobes** (kernel ≥5.4) and **LSM hooks** (≥5.7)
- Array access via square brackets
- `btfType` casts generic pointers to specific structs
- `btfTypeModule` specifies kernel module BTF provider
- Eliminates manual offset calculation — see [[eBPF Concept - BPF_CORE_READ]]

## Return Values

- Set `return: true` with `returnArg` specifying index and type
- `returnArgAction: TrackSock`/`UntrackSock` maintains BPF maps linking sockets to processes for async network event attribution
- **Limitations**: kernel ≥5.3, LRU map overflow under high socket churn, socket sharing via `fork`/IPC not tracked

## Function Lists

Define reusable hook targets under `spec.lists`. Reference via `call: "list:NAME"`.

- `type: syscalls` enables syscall list with architecture-aware name resolution
- `generated_syscalls` auto-generates all syscalls
- `generated_ftrace` builds from `available_filter_functions` with regex pattern
- Reduces policy verbosity when monitoring many related functions

## Selector Macros

Reusable filter snippets defined in `selectorsMacros` at the spec level.

- Referenced via `macros: [name]` within any selector
- **No-overlap rule**: the same field name must not appear in both a macro and an inline selector definition
- Enables DRY policy authoring across multiple hooks sharing common filter conditions

## Source

- Hook points documentation: https://tetragon.io/docs/concepts/tracing-policy/hooks/
