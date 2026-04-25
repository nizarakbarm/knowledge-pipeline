---
created: 2025-04-24
up:
  - "[[CO-RE (Compile Once - Run Everywhere)]]"
  - "[[libbpf Framework]]"
related:
  - "[[BTF (BPF Type Format)]]"
  - "[[eBPF Tutorial - Kprobe Unlink]]"
  - "[[eBPF Tutorial - Fentry Unlink]]"
  - "[[eBPF Tutorial - Execsnoop]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - core
  - libbpf
  - bpf_core_read
  - relocation
  - btf
source:
  - "https://docs.ebpf.io/ebpf-library/libbpf/ebpf/BPF_CORE_READ/"
---

# eBPF Concept - BPF_CORE_READ

> [!summary]
> CO-RE macro that safely reads kernel structure fields by recording relocation entries instead of hardcoding offsets. Enables eBPF programs to run on different kernel versions without recompilation.

---

## Fundamental Purpose

> [!info] Why BPF_CORE_READ Exists
> In the CO-RE ecosystem, kernel data structures change between versions (fields added, removed, reordered). `BPF_CORE_READ` allows eBPF programs to read these structures safely without knowing the exact memory layout at compile time.

**Key capability:** Adapts to structural memory layout changes automatically at load time.

---

## BTF Relocation Mechanics

### Compile-Time (Clang)

When you write:
```c
int pid = BPF_CORE_READ(task, pid);
```

The Clang compiler:
1. Generates a CO-RE relocation record (`struct bpf_core_relo`)
2. Records the BTF type ID and relative field offset
3. Embeds this metadata in the ELF object file

### Load-Time (libbpf)

When loading the program:
1. libbpf reads target kernel's BTF from `/sys/kernel/btf/vmlinux`
2. Matches compiled BTF type with live kernel's BTF type
3. Calculates the new correct byte offset
4. Dynamically patches eBPF bytecode instructions in memory
5. Injects patched program into the kernel

```
Compile: BPF_CORE_READ(task, pid) → relocation record (type_id, field_offset)
   ↓
Load: libbpf matches BTF → calculates new offset → patches bytecode
   ↓
Runtime: reads correct memory location regardless of kernel version
```

---

## CO-RE Reads vs Direct Dereferencing

| Aspect          | `ptr->field` (Direct)                       | `BPF_CORE_READ(ptr, field)` (CO-RE)            |
| --------------- | ------------------------------------------- | ---------------------------------------------- |
| **Portability** | Hardcoded offsets break on kernel updates   | Dynamic relocation works across versions       |
| **Safety**      | Prohibited in kprobes (kernel crash risk)   | Safe memory-read helpers with graceful failure |
| **Environment** | Only works in fentry (at function boundary) | Works in kprobes, tracepoints, all probes      |
| **CO-RE**       | No                                          | Yes (BTF relocation)                           |

> [!warning] Direct Dereferencing Danger
> Direct pointer dereferencing (e.g., `task->pid`) in kprobes can access invalid memory pages and **crash the kernel**. `BPF_CORE_READ` translates this into safe helper calls.

> [!tip] Fentry Exception
> `fentry` programs can use direct dereferencing (e.g., `name->name`) because they run at the exact function boundary where the pointer is guaranteed valid. This is why fentry doesn't need `BPF_CORE_READ` for simple field access.

---

## Chained Reads (Multiple Arguments)

> [!info] Pointer Chaining
> `BPF_CORE_READ` supports nested structure access via multiple arguments, decomposing them into sequential reads.

### Example

```c
// Read: task->real_parent->tgid
int ppid = BPF_CORE_READ(task, real_parent, tgid);
```

**Expansion:**
```c
// Step 1: Read task->real_parent (returns pointer)
struct task_struct *parent = bpf_core_read(task, real_parent);

// Step 2: Read parent->tgid
int ppid = bpf_core_read(parent, tgid);
```

**Another example:**
```c
// Chained access: s->a.b.c->d.e->f->g
BPF_CORE_READ(s, a.b.c, d.e, f, g)
```

**Limit:** Supports up to **9 field accessors** in a single macro call.

---

## Underlying Implementation

### Macro Expansion

`BPF_CORE_READ` expands into multiple `bpf_core_read` function calls.

### Core Function

```c
// Wrapper around bpf_probe_read_kernel
static inline void *bpf_core_read(const void *src, __u32 size)
{
    void *dst;
    bpf_probe_read_kernel(dst, size, src);
    return dst;
}
```

### Compiler Extension

The source pointer is wrapped with Clang's `__builtin_preserve_access_index()`:

```c
// What the compiler sees
bpf_core_read(
    __builtin_preserve_access_index(&task->pid
    ),
    sizeof(int)
);
```

This builtin:
1. Applies heavy type casting
2. Instructs Clang to emit CO-RE relocation metadata
3. Generates the `bpf_core_relo` record in the ELF file

---

## Internal Links

- [[eBPF Tutorial - Kprobe Unlink]] — `BPF_CORE_READ(name, name)` for safe kernel memory access
- [[eBPF Tutorial - Fentry Unlink]] — Contrast with direct `name->name` dereferencing
- [[eBPF Tutorial - Execsnoop]] — Chained: `BPF_CORE_READ(task, real_parent, tgid)`
- [[CO-RE (Compile Once - Run Everywhere)]] — Parent concept
- [[BTF (BPF Type Format)]] — Underlying metadata system
- [[eBPF Map - PERF_EVENT_ARRAY]] — Related map type

---

## Key Concepts

1. **Relocation** — Dynamic offset patching via BTF at load time
2. **Safety** — Translates direct access into `bpf_probe_read_kernel` helper calls
3. **Chaining** — Multiple arguments enable nested pointer dereferencing
4. **Compiler Magic** — `__builtin_preserve_access_index()` triggers relocation generation
5. **Portability** — Single compiled binary runs on multiple kernel versions