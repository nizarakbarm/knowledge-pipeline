---
created: 2025-04-24
up:
  - "[[eBPF Helpers]]"
  - "[[libbpf Framework]]"
related:
  - "[[eBPF Concept - BPF_CORE_READ]]"
  - "[[eBPF Tutorial - Execsnoop]]"
  - "[[bpf_get_current_pid_tgid]]"
  - "[[bpf_get_current_uid_gid]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - helpers
  - task_struct
  - verifier
  - memory-safety
  - process-info
source:
  - "https://docs.ebpf.io/linux/helper-function/bpf_get_current_task/"
---

# eBPF Helper - bpf_get_current_task

> [!summary]
> Returns a pointer (encoded as `u64`) to the current process's `task_struct` — the kernel's comprehensive process descriptor. Enables reading parent PID, command name, namespaces, cgroups, and other process metadata that simple helpers cannot provide.

---

## Definition

```c
u64 bpf_get_current_task(void);
```

**Returns:** A `u64` value encoding a pointer to `struct task_struct` of the current process.

**Usage:**
```c
struct task_struct *task = (struct task_struct *)bpf_get_current_task();
```

> [!info] Why u64 Return?
> The helper returns `u64` because eBPF registers and underlying kernel memory addresses on 64-bit platforms are 64 bits wide. This encoding ensures consistency across different architectures. The caller must explicitly cast to `struct task_struct*` before use.

---

## Why task_struct?

### What bpf_get_current_pid_tgid() Cannot Do

| Information       | `bpf_get_current_pid_tgid()` | `bpf_get_current_task()`                   |
| ----------------- | ---------------------------- | ------------------------------------------ |
| **PID/TGID**      | ✅ Returns directly           | ✅ Accessible via `task->pid`               |
| **Parent PID**    | ❌ Not available              | ✅ `BPF_CORE_READ(task, real_parent, tgid)` |
| **Command name**  | ❌ Not available              | ✅ `BPF_CORE_READ(task, comm)`              |
| **UID/GID**       | ❌ Not available              | ✅ `BPF_CORE_READ(task, cred, uid.val)`     |
| **On-CPU time**   | ❌ Not available              | ✅ Compute exact CPU runtime                |
| **Kernel thread** | ❌ Not available              | ✅ Determine if task is kthread             |
| **Run queue**     | ❌ Not available              | ✅ Inspect current CPU run queue            |
| **Namespaces**    | ❌ Not available              | ✅ `BPF_CORE_READ(task, nsproxy, ...)`      |
| **Cgroups**       | ❌ Not available              | ✅ `BPF_CORE_READ(task, cgroups, ...)`      |

### Common Use Cases

- **Process lineage:** Trace process trees by reading `real_parent` → `parent` chains
- **Command filtering:** Check `task->comm` to filter by process name
- **Namespace awareness:** Determine which PID namespace a process belongs to
- **Security context:** Read credentials, SELinux contexts, capabilities
- **Resource tracking:** Access cgroup information for resource attribution

---

## Verifier Safety: Why Direct Dereferencing Is Forbidden

> [!danger] CRITICAL: Never Use Direct Dereferencing
> The eBPF verifier will **reject** programs that attempt direct field access like `task->pid`. In traditional tracing environments, direct access to an invalid memory page or null pointer would **crash the entire operating system**.
>
> Because eBPF executes within a restricted, safe environment, the verifier requires special helper functions that gracefully handle invalid memory accesses without faulting.
>
> **Exceptions:** Certain newer BTF-enabled program types like `fentry` do allow direct dereferencing because the verifier can prove pointer validity at the function boundary.

### Mandatory: CO-RE Macros

All `task_struct` field reads **must** use `BPF_CORE_READ()`. Instead of direct pointer chasing, `BPF_CORE_READ(task, field1, field2)` decomposes the access into sequential, safe `bpf_probe_read_kernel` helper calls.

```c
// ❌ VERIFIER WILL REJECT (direct access crashes on invalid memory)
int pid = task->pid;

// ✅ VERIFIER ACCEPTS (gracefully handles invalid memory)
int pid = BPF_CORE_READ(task, pid);
```

**Under the hood:** The macro wraps the access in `__builtin_preserve_access_index()`, which emits BTF relocation records. This guarantees libbpf can dynamically recalculate correct memory offsets at load time, ensuring CO-RE portability across kernel versions.

> [!info] Cross-Link: BPF_CORE_READ
> For a deeper understanding of how `BPF_CORE_READ` safely handles field access via BTF relocations, see [[eBPF Concept - BPF_CORE_READ|BPF_CORE_READ]].

---

## Safe Reading Patterns

### Pattern 1: Simple Field Access

```c
struct task_struct *task = (struct task_struct *)bpf_get_current_task();
int pid = BPF_CORE_READ(task, pid);
int tgid = BPF_CORE_READ(task, tgid);
```

### Pattern 2: Chained Pointer Access

```c
// Read parent process ID
int ppid = BPF_CORE_READ(task, real_parent, tgid);

// Read grandparent (chained)
int gppid = BPF_CORE_READ(task, real_parent, real_parent, tgid);
```

### Pattern 3: String Fields

```c
char comm[TASK_COMM_LEN];
bpf_probe_read_kernel_str(comm, sizeof(comm), BPF_CORE_READ(task, comm));
```

### Pattern 4: Credential Information

```c
// Access UID (requires nested read through cred pointer)
unsigned int uid = BPF_CORE_READ(task, cred, uid.val);
unsigned int gid = BPF_CORE_READ(task, cred, gid.val);
```

---

## Alternative: bpf_get_current_task_btf()

> [!info] Kernel 5.11+ Enhancement
> `bpf_get_current_task_btf()` returns a BTF-annotated pointer (`PTR_TO_BTF_ID`) rather than an opaque integer. Because the verifier natively understands the exact BTF type of this returned pointer, it proves the memory is safe to read.

**Key difference:**

| Aspect | `bpf_get_current_task()` | `bpf_get_current_task_btf()` |
|--------|--------------------------|------------------------------|
| **Return type** | `u64` (opaque) | `PTR_TO_BTF_ID` (typed) |
| **Field access** | Requires `BPF_CORE_READ()` everywhere | Direct dereferencing allowed |
| **Verifier** | Cannot prove pointer safety | Understands exact memory layout |
| **Code clarity** | Verbose macro calls | Natural C syntax |
| **Overhead** | Higher (macro expansion) | Lower (direct access) |

**Direct dereferencing with btf:**
```c
// With bpf_get_current_task_btf (kernel 5.11+, fentry/fexit only)
struct task_struct *task = bpf_get_current_task_btf();
int pid = task->pid;  // ✅ Verifier allows direct access
```

**Availability:**
| Kernel Version | Helper |
|---------------|--------|
| 4.8+ | `bpf_get_current_task()` |
| 5.11+ | `bpf_get_current_task_btf()` |

---

## Internal Links

- [[eBPF Concept - BPF_CORE_READ]] — Relocation mechanics for safe field access
- [[eBPF Tutorial - Execsnoop]] — Practical usage: `BPF_CORE_READ(task, real_parent, tgid)`
- [[eBPF Helper - bpf_get_current_pid_tgid]] — Lightweight PID/TGID retrieval
- [[eBPF Helper - bpf_get_current_uid_gid]] — Packed UID/GID retrieval

---

## Key Concepts

1. **u64 encoding** — Return value is a pointer cast to integer for architectural consistency
2. **Explicit casting** — Caller must cast `u64` to `struct task_struct*` before use
3. **Verifier restrictions** — Direct dereferencing (`task->field`) is strictly prohibited
4. **CO-RE mandatory** — All field access must use `BPF_CORE_READ()` for relocation
5. **Rich metadata** — Provides access to process lineage, namespaces, cgroups, credentials
6. **Modern alternative** — `bpf_get_current_task_btf()` (kernel 5.11+) offers enhanced BTF integration