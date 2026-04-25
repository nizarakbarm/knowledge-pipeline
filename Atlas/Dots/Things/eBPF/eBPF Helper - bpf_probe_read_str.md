---
created: 2025-04-25
up:
  - "[[eBPF Helpers]]"
  - "[[eBPF Tutorial - Execsnoop]]"
related:
  - "[[eBPF Tutorial - Uprobe Bashreadline]]"
  - "[[eBPF Helper - bpf_get_current_task]]"
  - "[[eBPF Concept - BPF_CORE_READ]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - helpers
  - memory-safety
  - probe-read
  - kernel
  - user-space
source:
  - "https://docs.ebpf.io/linux/helper-function/bpf_probe_read_str/"
  - "https://docs.ebpf.io/linux/helper-function/bpf_probe_read_user_str/"
  - "https://docs.ebpf.io/linux/helper-function/bpf_probe_read_kernel_str/"
---

# eBPF Helper - bpf_probe_read_str

> [!summary]
> The `bpf_probe_read_str` family of helpers safely copies null-terminated strings from either kernel or user-space memory into the eBPF program's stack. They prevent page faults and security vulnerabilities that would result from direct pointer dereferencing.

---

## Why These Helpers Exist

> [!warning] Memory Safety
> eBPF programs cannot safely dereference arbitrary pointers. When accessing memory outside the eBPF program's own stack, the verifier cannot guarantee the pointer is valid. Direct dereferencing could cause:
> - Page faults
> - Security vulnerabilities
> - Kernel crashes

These helpers perform **validated memory copies** with boundary checking, ensuring safe access to both kernel and user-space memory.

---

## Three Variants

| Helper | Target Memory | Use Case |
|--------|--------------|----------|
| `bpf_probe_read_str()` | Any (legacy, kernel preferred) | Generic string reads |
| `bpf_probe_read_user_str()` | User-space only | Uprobes, user-space tracing |
| `bpf_probe_read_kernel_str()` | Kernel-space only | Kprobes, tracepoints, fentry |

> [!info] Kernel 5.5+ Distinction
> Before kernel 5.5, `bpf_probe_read_str()` was the only option and worked for both spaces. Starting with kernel 5.5, the kernel introduced `bpf_probe_read_user_str()` and `bpf_probe_read_kernel_str()` for explicit memory space separation, improving security and verifier clarity.

---

## bpf_probe_read_str

### Signature

```c
static long bpf_probe_read_str(
    void *dst,          // Destination buffer (eBPF stack)
    u32 size,           // Maximum bytes to copy
    const void *unsafe_ptr   // Source pointer (kernel memory)
);
```

### Return Value

| Value | Meaning |
|-------|---------|
| `> 0` | Number of bytes copied (includes null terminator) |
| `< 0` | Error code (-EFAULT for invalid address) |

### Example: Execsnoop

```c
char *cmd_ptr = (char *) BPF_CORE_READ(ctx, args[0]);
bpf_probe_read_str(&event.comm, sizeof(event.comm), cmd_ptr);
```

> [!tip] Null Termination Guarantee
> Unlike `bpf_probe_read()`, `bpf_probe_read_str()` guarantees null-termination. It reads until either the buffer is full or a null byte is encountered, always ensuring the last byte is `\0`.

---

## bpf_probe_read_user_str

### Signature

```c
static long bpf_probe_read_user_str(
    void *dst,          // Destination buffer (eBPF stack)
    u32 size,           // Maximum bytes to copy
    const void *unsafe_ptr   // Source pointer (user-space memory)
);
```

### Use Case: Uprobe Bashreadline

```c
SEC("uretprobe/bash_readline")
int BPF_KPROBE(printret, const void *ret)
{
    char str[80];
    bpf_probe_read_user_str(&str, sizeof(str), ret);
    bpf_printk("<-%s\\n", str);
    return 0;
}
```

> [!warning] User-Space Context
> When a uprobe fires, the eBPF program runs in kernel mode but the target data lives in user-space. `bpf_probe_read_user_str()` is **required** because the source pointer references user-space memory that the kernel cannot directly access.

---

## bpf_probe_read_kernel_str

### Signature

```c
static long bpf_probe_read_kernel_str(
    void *dst,          // Destination buffer (eBPF stack)
    u32 size,           // Maximum bytes to copy
    const void *unsafe_ptr   // Source pointer (kernel memory)
);
```

### Use Case: Reading task_struct Fields

```c
struct task_struct *task = bpf_get_current_task();
char comm[TASK_COMM_LEN];
bpf_probe_read_kernel_str(comm, sizeof(comm), BPF_CORE_READ(task, comm));
```

> [!info] Explicit Kernel Access
> `bpf_probe_read_kernel_str()` explicitly indicates the source is kernel memory. This helps the verifier track memory provenance and prevents accidental user-space access.

---

## Comparison: bpf_probe_read vs bpf_probe_read_str

| Aspect | `bpf_probe_read()` | `bpf_probe_read_str()` |
|--------|-------------------|----------------------|
| **Null termination** | No | Yes |
| **Copy behavior** | Fixed size | Until null or buffer full |
| **Use case** | Binary data, structs | Strings, paths, commands |
| **Return value** | 0 on success, negative on error | Bytes copied (includes null) |
| **Safety** | Same validated copy | Same validated copy |

---

## Memory Space Safety Matrix

| Program Type | Source Memory | Correct Helper |
|-------------|--------------|----------------|
| Kprobe | Kernel | `bpf_probe_read_kernel_str()` |
| Tracepoint | Kernel | `bpf_probe_read_kernel_str()` |
| Fentry/Fexit | Kernel | `bpf_probe_read_kernel_str()` |
| Uprobe/Uretprobe | User-space | `bpf_probe_read_user_str()` |
| USDT | User-space | `bpf_probe_read_user_str()` |
| XDP/TC (packet) | Packet data | `bpf_skb_load_bytes()` etc. |

---

## Common Patterns

### Pattern 1: Safe String Copy with Truncation

```c
char buf[128];
long len = bpf_probe_read_kernel_str(buf, sizeof(buf), src);
if (len < 0) {
    // Handle error
    return 0;
}
// buf is guaranteed null-terminated
```

### Pattern 2: Copy with Size Limit

```c
// Ensure we don't exceed buffer
u32 copy_len = len < sizeof(buf) ? len : sizeof(buf);
bpf_probe_read_kernel_str(buf, copy_len, src);
```

### Pattern 3: Chained Reads

```c
// Read pointer first, then read string through it
const char *ptr;
bpf_probe_read_kernel(&ptr, sizeof(ptr), &src->field);
bpf_probe_read_kernel_str(buf, sizeof(buf), ptr);
```

---

## Return Value Handling

```c
long ret = bpf_probe_read_kernel_str(dst, size, src);

if (ret < 0) {
    // Error: -EFAULT (bad address), -EINVAL, etc.
    bpf_printk("Read failed: %ld\\n", ret);
    return 0;
}

// ret includes null terminator
// If ret == size, string was truncated
if (ret == size) {
    bpf_printk("Warning: string truncated\\n");
}
```

---

## Related Helpers

| Helper | Purpose |
|--------|---------|
| `bpf_probe_read()` | Read fixed-size binary data |
| `bpf_probe_read_user()` | Read user-space binary data |
| `bpf_probe_read_kernel()` | Read kernel-space binary data |
| `BPF_CORE_READ()` | CO-RE aware multi-level pointer dereference |

> [!tip] BPF_CORE_READ and Strings
> `BPF_CORE_READ()` can read a `char *` pointer, but to copy the string it points to, you still need `bpf_probe_read_str()`. Combine them:
> ```c
> char *ptr = BPF_CORE_READ(ctx, args[0]);
> bpf_probe_read_str(buf, sizeof(buf), ptr);
> ```

---

## Notes Used In

- [[eBPF Tutorial - Execsnoop]] — `bpf_probe_read_str` for command capture
- [[eBPF Tutorial - Uprobe Bashreadline]] — `bpf_probe_read_user_str` for bash input
- [[eBPF Helper - bpf_get_current_task]] — `bpf_probe_read_kernel_str` for task comm

---

## References

- [eBPF Docs - bpf_probe_read_str](https://docs.ebpf.io/linux/helper-function/bpf_probe_read_str/)
- [eBPF Docs - bpf_probe_read_user_str](https://docs.ebpf.io/linux/helper-function/bpf_probe_read_user_str/)
- [eBPF Docs - bpf_probe_read_kernel_str](https://docs.ebpf.io/linux/helper-function/bpf_probe_read_kernel_str/)
- [[eBPF Tutorial - Execsnoop]]
- [[eBPF Tutorial - Uprobe Bashreadline]]
