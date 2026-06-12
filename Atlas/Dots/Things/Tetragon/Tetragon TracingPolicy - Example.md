---
created: 2026-06-12
up:
  - "[[Tetragon TracingPolicy]]"
  - "[[eBPF MOC]]"
related:
  - "[[Tetragon Overview]]"
  - "[[Tetragon Events]]"
  - "[[Tetragon TracingPolicy - Hook Points]]"
  - "[[Tetragon TracingPolicy - Argument Types]]"
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[Kubernetes]]"
in:
  - "[[Things]]"
tags:
  - concept
  - example
  - tetragon
  - tracing-policy
  - ebpf
  - security
  - kubernetes
---

# Tetragon TracingPolicy - Example

## Summary

A complete walkthrough of a minimal [[Tetragon TracingPolicy]] that monitors `fd_install` for access to `/tmp/tetragon`, demonstrating the four-layer architecture and the kill-before-exposure enforcement model that makes Tetragon immune to user-space bypass.

## Key Points

- A single `kprobe` on `fd_install` with one selector and one `Sigkill` action constitutes a complete enforcement policy
- The policy operates across four distinct layers: Kubernetes identity, hook definition, selector logic, and event observation
- Process is killed **before** the file descriptor is installed — the file is never technically opened from the process's perspective
- All match-and-kill logic executes in [[eBPF (extended Berkeley Packet Filter)|eBPF]] with zero userspace round-trip
- Path-based policies are bypassable via hard links — this example is for illustration only

## Full Example

Minimal policy that kills any process attempting to open `/tmp/tetragon`:

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: "fd-install"
spec:
  kprobes:
  - call: "fd_install"
    syscall: false
    args:
    - index: 0
      type: "int"
    - index: 1
      type: "file"
    selectors:
    - matchArgs:
      - index: 1
        operator: "Equal"
        values:
        - "/tmp/tetragon"
      matchActions:
      - action: Sigkill
```

Load via `sudo ./tetragon --bpf-lib bpf/objs --tracing-policy example.yaml`. Monitor via `./tetra getevents -o compact`.

## Four-Layer Architecture

This single policy operates across four distinct layers:

1. **Kubernetes Object Identity** (control plane) — `apiVersion`, `kind`, `metadata.name` make the policy a cluster resource manageable via `kubectl apply/get/delete`. Standard [[Kubernetes]] lifecycle.
2. **Hook Point Definition** (data plane) — `spec.kprobes` with `call: "fd_install"` and `syscall: false` attaches to the *kernel function* (not the syscall entry), intercepting file descriptor installation. Arguments declared by index and type enable BPF-level data extraction.
3. **Selectors** (decision logic) — `matchArgs` is the *if* (context filter: argument index 1, a `file` struct, equals `/tmp/tetragon`); `matchActions` is the *then* (enforcement response: `Sigkill`). Both execute entirely in BPF — no userspace round-trip.
4. **Event Observation** — `tetra getevents -o compact` displays the enforcement result.

## Kill-Before-Exposure

The critical insight: hooking `fd_install` means the process is killed **before** the file descriptor is installed in the process's FD table. The file is never technically opened from the process's perspective. Event output:

```
🚀 process  /usr/bin/cat /tmp/tetragon
📬 open     /usr/bin/cat /tmp/tetragon
💥 exit     /usr/bin/cat /tmp/tetragon SIGKILL
```

### Practical Implications

- **Immunity to bypass** — hooking the kernel function `fd_install` means no user-space trick (`LD_PRELOAD`, static linking, custom syscall wrappers) can evade detection. Every file open path converges at this kernel function.
- **Zero-trust enforcement** — SIGKILL cannot be caught, blocked, or ignored by the application. Effective for protecting honeypot files, private keys, and crypto wallets.
- **Kernel-space performance** — the entire match-and-kill decision happens in BPF with no context switch to a userspace agent.
- **Policy-as-code** — security logic deployed as version-controlled YAML, no application code changes, no sidecar injection, no agent SDK.

## Caveat

Path-based policies are bypassable via **hard links** — an attacker can create a hard link to the protected file under a different name and access it without triggering the policy. This example is for illustration purposes only; production policies should use inode-based or other path-independent matching where possible.

## Source

- Example documentation: https://tetragon.io/docs/concepts/tracing-policy/example/
