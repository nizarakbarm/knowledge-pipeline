---
created: 2026-06-12
up:
  - "[[Tetragon TracingPolicy]]"
  - "[[eBPF MOC]]"
related:
  - "[[Tetragon Overview]]"
  - "[[Tetragon Events]]"
  - "[[Tetragon TracingPolicy - Hook Points]]"
  - "[[Tetragon TracingPolicy - Example]]"
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[eBPF Concept - BPF_CORE_READ]]"
  - "[[Kubernetes]]"
in:
  - "[[Things]]"
tags:
  - concept
  - argument-types
  - tetragon
  - tracing-policy
  - ebpf
  - security
  - kubernetes
---

# Tetragon TracingPolicy - Argument Types

## Summary

The complete argument type catalog for [[Tetragon TracingPolicy]] selectors — eight categories of types with their supported operators, security use cases for each category, and critical gotchas around `sizeArgIndex`, `maxData`, kernel version gates, and `dentry` vs `path` resolution.

## Key Points

- Eight argument categories: Integers, String, Network, Buffer, Filesystem, Credential, BPF, and Special
- Integer types uniquely support bitmask matching via the `Mask` operator
- Filesystem types (`file`, `path`) support `FileType`/`NotFileType` operators for filtering by file type (regular, socket, pipe, directory)
- `sizeArgIndex` is **1-based** — off-by-one errors silently truncate or over-read captured data
- `dentry` resolves within a single mountpoint only; `path` traverses mount boundaries but fails if filesystem unmounts during event

## Argument Type Catalog

| Category | Types | Operators |
|----------|-------|-----------|
| **Integers** | `sint8`/`int8`, `uint8`, `sint16`/`int16`, `uint16`, `int`/`sint32`/`int32`, `uint32`, `long`/`sint64`/`int64`, `ulong`/`uint64`/`size_t` | Equal, NotEqual, GT, LT, **Mask** |
| **String** | `string` | Equal, NotEqual, Prefix, Postfix, SubString (≥6.17), SubStringIgnoreCase (≥6.19) |
| **Network** | `skb`, `sock`, `sockaddr`, `sockaddr_un`, `socket` | SAddr, DAddr, SPort, DPort, Protocol, Family, State |
| **Buffer** | `char_buf`, `char_iovec`, `const_buf` | Equal, NotEqual, Prefix, Postfix, SubString |
| **Filesystem** | `file`, `dentry`, `path`, `filename`, `fd`, `kiocb`, `linux_binprm` | Equal, NotEqual, Prefix, Postfix, SubString, **FileType**, **NotFileType** |
| **Credential** | `cred`, `kernel_cap_t`, `capability`, `cap_inheritable`/`permitted`/`effective`, `user_namespace` | In, NotIn |
| **BPF** | `bpf_attr`, `bpf_map`, `bpf_prog`, `perf_event` | Type-specific |
| **Special** | `nop`, `syscall64`, `data_loc`, `net_device`, `iov_iter`, `load_info`, `module` | Type-specific |

**Notable type behaviors:**
- `syscall64` resolves syscall IDs with ABI awareness (x64, i386)
- `nop` skips an argument slot while preserving index alignment
- `file` and `path` types support `FileType`/`NotFileType` for filtering by file type (regular, socket, pipe, directory, etc.)

## Security Use Cases by Category

1. **Integer Types** — Detect failed privilege escalation: `setuid(0)` returning non-zero indicates a failed root attempt worth alerting on. Comparison operators on return values catch anomalous syscall failures.

2. **String Types** — Command injection detection: `SubString: "nc -e"` on `execve` arguments catches reverse shell attempts regardless of surrounding flags. `Prefix`/`Postfix` match on binary names or file extensions.

3. **Buffer Types** — Data exfiltration prevention: `SubString: "Authorization: Bearer"` on `write()` to a socket FD detects credential leakage. `char_buf` with `returnCopy` captures buffer content *after* the syscall modifies it.

4. **Network Types** — C2 beacon blocking: `SAddr`/`DAddr` with CIDR matching against threat intel IP blocklists. `sock` state tracking identifies unexpected outbound connections from server processes. `sockaddr_un` extends visibility to Unix domain socket IPC paths including abstract namespaces.

5. **Filesystem/Path Types** — Sensitive file integrity monitoring: `path` matching on `/etc/shadow`, `/etc/passwd`, or SSH key directories. `linux_binprm` captures the binary being executed at `execve` time. `kiocb` enables tracing of async I/O operations for storage-layer monitoring.

6. **Credential/Capability Types** — Container escape detection: unexpected `CAP_SYS_ADMIN` in `cap_effective` for a containerized process signals a potential breakout. `user_namespace` isolates context identifiers across container boundaries. `cred` captures full credential snapshots at privilege transition points.

7. **BPF/Kernel Internal Types** — Rootkit detection: `bpf_prog` loading events from unrecognized binaries or unexpected `bpf_map` creation by non-system processes. `module` type tracks kernel module loading for supply chain integrity. `load_info` exposes BPF program verification metadata.

## Critical Gotchas

### `sizeArgIndex` is 1-based, not 0-based

If the buffer length is the second function parameter, set `sizeArgIndex: 2` — not 1. Off-by-one errors here silently truncate or over-read captured data.

### `maxData` caps bytes copied from kernel buffer

Default capture is 4096 bytes; `maxData` flag extends to 32,768 bytes. A policy matching content at offset 300 with `maxData: 256` **silently fails** — the match region falls outside the captured window. Always set `maxData` to exceed the furthest expected match offset.

### Kernel version feature gates

| Feature | Minimum Kernel |
|---------|---------------|
| `SubString` operator | 6.17+ |
| `SubStringIgnoreCase` operator | 6.19+ |
| Full path resolution (`path` type) | 5.3+ |
| BTF attribute resolution (kprobes) | 5.4+ |
| BTF attribute resolution (LSM) | 5.7+ |

### `dentry` vs `path` resolution

- **`dentry`** resolves only within a *single mountpoint* — it cannot traverse mount boundaries
- **`path`** traverses mountpoints but returns an empty string if the filesystem is unmounted during the event
- Neither resolves correctly if the mount context changes between hook attachment and event firing
- **Prefer `path`** for cross-mount scenarios; **use `dentry`** for single-filesystem precision

## Source

- Argument types documentation: https://tetragon.io/docs/concepts/tracing-policy/argument_types/
