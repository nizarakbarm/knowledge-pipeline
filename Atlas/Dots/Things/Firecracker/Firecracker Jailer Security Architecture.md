---
created: 2026-05-19
up:
  - "[[MOC-MicroVM]]"
related:
  - "[[Firecracker Overview & Core Concepts]]"
  - "[[Firecracker Prerequisites & Installation]]"
  - "[[Firecracker VirtIO Network and Block IO Rate Limiting]]"
  - "[[Flow of Firecracker SDK]]"
in:
  - "[[Atlas]]"
tags:
  - systems/microvm
  - security
  - linux-namespaces
---

# Firecracker Jailer Security Architecture

## Summary
The **Firecracker Jailer** is a Rust-based companion process that implements defense-in-depth isolation for the Firecracker VMM by wrapping it in a "digital prison." It prepares system resources requiring elevated permissions before VM startup, then drops privileges to create a hardened, minimal-attack-surface execution environment.

## Key Points
- The Jailer is a **separate companion process** (not built into Firecracker itself) written in Rust
- Operates on a **privilege separation model**: performs privileged setup, then relinquishes root access before executing the VMM
- Implements **six distinct isolation layers** spanning filesystem, namespaces, resources, syscalls, capabilities, and file descriptors
- Uses **unshare()**, **pivot_root()**, and **chroot** for filesystem isolation
- Applies **seccomp whitelisting** to enforce a strict minimum syscall vocabulary
- Drops to unprivileged **POSIX user/group** via `--uid` and `--gid` flags

## Details

### Six Layers of Security Isolation

#### 1. Filesystem Isolation (Chroot)
- Locks the process into a restricted single-directory subtree under `/srv/jailer`
- Uses `unshare()`, `pivot_root()`, and `chroot` system calls
- Makes the **host filesystem invisible** to the jailed process
- Prevents traversal outside the designated root directory

#### 2. Namespace Separation
- Isolates Linux namespaces for:
  - **Mount table** (filesystem mounts)
  - **Network stack** (network interfaces, routing)
  - **PID list** (process IDs)
- `--new-pid-ns` uses `clone()` with `CLONE_NEWPID`; the child process becomes `init(1)` in the new namespace
- Can join an existing network namespace via `setns()`

#### 3. Resource Restrictions (cgroups)
- Enforces hardware budgets through **cgroups v1/v2**
- Dynamically parses `/proc/mounts` to determine cgroup hierarchy
- Creates a **VM-specific control directory** for per-VM resource management
- Limits: **CPU**, **memory**, and **I/O bandwidth**

#### 4. System Call Filtering (Seccomp)
- Implements a **strict whitelist** of the minimum required syscalls
- Any syscall outside the allowed vocabulary causes the process to be **blocked or killed**
- Dramatically reduces kernel attack surface

#### 5. Capabilities and Privilege Dropping
- Switches from **root to unprivileged POSIX user/group** before executing Firecracker
- Controlled via `--uid` and `--gid` command-line flags
- If an attacker escapes the VMM, they inherit the **de-privileged environment**

#### 6. File Descriptor Management
- Parses `/proc/<jailer-pid>/fd` to audit open file descriptors
- **Closes all unnecessary file descriptors**
- Leaves only **stdin**, **stdout**, and **stderr** open
- Prevents accidental information leakage through inherited descriptors

## Execution Flow
```
Host Root
    ↓
[Jailer Process] — runs as root initially
    ↓
1. chroot to /srv/jailer/firecracker/<id>/root
2. unshare(CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWNET)
3. Setup cgroups at /sys/fs/cgroup/<parent>/<id>
4. Load seccomp-bpf filter
5. setuid/setgid to unprivileged user
6. Close all fd except stdin/stdout/stderr
    ↓
[Firecracker VMM] — runs as unprivileged user
    ↓
[microVM Guest] — hardware-isolated workload
```

## Related / Links
- [[MOC-MicroVM]]
- [[Linux Namespaces]]
- [[cgroups]]
- [[Seccomp]]
- [[Firecracker Overview & Core Concepts]]
- [[Firecracker Prerequisites & Installation]]

---
*Confidence Score: 0.92*
**Reasoning**: This is a clear technical reference describing a multi-layered security system. Input is well-structured with enumerated layers, making it ideal for an atomic note. The parent MOC `[[MOC-MicroVM]]` is explicitly appropriate.