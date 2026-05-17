---
created: 2026-05-16
up:
  - "[[PythonBPF]]"
  - "[[Python-BPF Register Access in ctx and The Argument Mapping]]"
related:
  - "[[eBPF Tutorial - Kprobe Unlink]]"
  - "[[BCC]]"
  - "[[Python-BPF Compiler Limitations]]"
  - "[[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - python-bpf
  - kprobe
  - kretprobe
  - tutorial
  - unlink
---

# Python-BPF Tutorial - Kprobe Unlink

## Summary

Monitor file deletion via the `unlink` syscall using Python-BPF kprobe and kretprobe. Demonstrates dynamic kernel instrumentation on `do_unlinkat` with Python decorators, register-based argument access, and the BPF() loader.

---

## What is a kprobe?

> [!info] kprobe
> **kprobes** dynamically insert probes into almost any Linux kernel function. They rely on CPU exception handling and single-step debugging: when kernel execution hits the probe point, control redirects to a user-defined callback. After the callback, single-stepping executes the original instruction and resumes normal flow.

### Detection Methods

| Type | Purpose |
|------|---------|
| **kprobe** | Place at any position; provides `pre_handler`, `post_handler`, `fault_handler` |
| **jprobe** | Capture input values of a probed function |
| **kretprobe** | Capture return values of a probed function |

> [!warning] kprobe Usage Restrictions
> - **Forbidden targets:** kprobe implementation files (`kernel/kprobes.c`), `do_page_fault`, and `notifier_call_chain`
> - **Inline functions unreliable:** GCC optimizations may inline functions
> - **Callback constraints:** Preemption is disabled during callbacks
> - **Re-entrancy guard:** If a probe triggers itself, callback is skipped

> [!warning] kretprobe Limitations
> - **Stack traces break:** `__builtin_return_address()` shows trampoline address
> - **Entry/exit mismatch:** Functions with unequal call/return counts won't work
> - **Task stack switching:** `__switch_to()` is explicitly unsupported

---

## Checking unlinkat Arguments with bpftrace

Before writing the Python-BPF program, we can inspect the `unlinkat` syscall arguments using bpftrace:

```bash
localhost:~ # bpftrace -vl tracepoint:syscalls:sys_enter_unlinkat
tracepoint:syscalls:sys_enter_unlinkat
    int __syscall_nr
    int dfd
    const char * pathname
    int flag
```

```bash
localhost:~ # bpftrace -vl tracepoint:syscalls:sys_exit_unlinkat
tracepoint:syscalls:sys_exit_unlinkat
    int __syscall_nr
    long ret
```

From this output, we can see:
- **Entry**: `dfd` (directory fd), `pathname` (file path string), `flag` (flags)
- **Exit**: `ret` (return value)

> **Note**: While bpftrace shows tracepoint arguments, Python-BPF uses **kprobes** which access arguments through CPU registers via `struct_pt_regs`. The argument names from bpftrace help us understand what each register contains.

---

## Register Mapping for do_unlinkat

Based on the x86_64 calling convention and bpftrace output:

| Argument | Type | Register | Python-BPF |
|----------|------|----------|------------|
| `dfd` | `int` | `rdi` | `ctx.di` |
| `name` | `struct filename *` | `rsi` | `ctx.si` |
| Return value | `long` | `rax` | `ctx.ax` |

For full register documentation, see [[Python-BPF Register Access in ctx and The Argument Mapping]].

---

## Source Code

### Python-BPF Program (kprobe_unlink.py)

```python
from pythonbpf import bpf, section, bpfglobal, BPF
from pythonbpf.helper import pid
from pythonbpf.utils import trace_pipe
from ctypes import c_int64
from vmlinux import struct_pt_regs


@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    """Entry probe: captures dfd and name pointer"""
    current_pid = pid()
    dfd = ctx.di        # 1st arg: directory file descriptor (int)
    name_ptr = ctx.si   # 2nd arg: struct filename* (pointer only)
    
    # Note: This is the simple version without filename reading.
    # For the advanced version with probe_read_str, see "Alternative" section below.
    print(f"KPROBE ENTRY pid = {current_pid}, dfd = {dfd}")
    return 0


@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: struct_pt_regs) -> c_int64:
    """Exit probe: captures return value"""
    current_pid = pid()
    ret = ctx.ax        # Return value in rax register
    
    print(f"KPROBE EXIT: pid = {current_pid}, ret = {ret}")
    return 0


@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"


# Compile, load, and attach
b = BPF()
b.load_and_attach()

# Read trace output
print("Tracing... Hit Ctrl-C to end.")
trace_pipe()
```

### Why the Simple Version Doesn't Read the Filename

The simple version above only captures `pid` and `dfd` because reading the filename requires kernel memory access. Python-BPF **does** have `probe_read()` and `probe_read_str()` helpers for this, but with an important limitation compared to BCC:

**What Python-BPF has:**
- `probe_read(dst, size, src)` — reads kernel memory into buffer
- `probe_read_str(dst, src)` — reads null-terminated string from kernel

**What Python-BPF lacks:**
- **BTF relocations** (BPF_CORE_READ's key feature)
- **Compile-once-run-everywhere** capability
- **Portable struct field offsets** that adapt to kernel version

**The issue:** `probe_read()` requires hardcoded byte offsets. If the kernel changes `struct filename` layout, the offset breaks. BCC's `BPF_CORE_READ(name, name)` solves this via BTF relocations that patch offsets at load time.

See [[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]] for full comparison.

---

### Verifying struct filename Layout

Before using `probe_read`, we need to know the field offset. We verified this on the target kernel:

```bash
ssh vmdevnull
grep -A10 'struct filename {' /usr/src/linux-6.12.0-160000.27/include/linux/fs.h
```

**Output:**
```c
struct filename {
	const char		*name;	/* pointer to actual string */	      // offset: 0
	const __user char	*uptr;	/* original userland pointer */      // offset: 8
	atomic_t		refcnt;                                     // offset: 16
	struct audit_names	*aname;                                     // offset: 24
	const char		iname[];                                    // offset: 32
};
```

**Key finding:** The `name` field is at **offset 0** (first field). This means `name_ptr` (which points to the struct start) already points to where `name` is stored.

For other struct fields, you would need to add the byte offset: `probe_read(dst, size, struct_ptr + field_offset)`.

---

### Alternative: Using probe_read to Read the Filename

Here are both versions — simple (no filename) and advanced (with probe_read_str):

#### Version 1: Simple (No Filename Reading)

```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    current_pid = pid()
    dfd = ctx.di        # 1st arg: directory file descriptor
    print(f"KPROBE ENTRY pid = {current_pid}, dfd = {dfd}")
    return 0
```

#### Version 2: Advanced (With probe_read_str)

```python
from pythonbpf.helper import probe_read_str

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    current_pid = pid()
    dfd = ctx.di        # 1st arg: directory file descriptor
    name_ptr = ctx.si   # 2nd arg: struct filename*
    
    # Read filename string using probe_read_str
    # name field is at offset 0 in struct filename (verified above)
    filename_buf = c_char_p()
    probe_read_str(filename_buf, name_ptr)
    
    print(f"KPROBE ENTRY pid = {current_pid}, dfd = {dfd}, file = {filename_buf}")
    return 0
```

**Limitations of probe_read approach:**
- **Offset is hardcoded**: Works for `name` (offset 0), but other fields need manual offset calculation
- **Not portable**: Breaks if kernel changes struct layout
- **No CO-RE**: Unlike BCC's BPF_CORE_READ, won't adapt at load time

**For portable struct access, use libbpf/CO-RE or BCC instead.**

---

## Build & Execute

### Step 1: Generate vmlinux.py (if not already done)

```bash
sudo tools/vmlinux-gen.py
```

### Step 2: Run Python Script

```bash
sudo python3 kprobe_unlink.py
```

### Step 3: Trigger Events

Open another terminal and create/delete files:

```bash
touch test1
rm test1
touch test2
rm test2
```

### Step 4: View Output

The `trace_pipe()` function in the script automatically reads from `/sys/kernel/tracing/trace_pipe`. Alternatively, you can read it manually:

```bash
sudo cat /sys/kernel/tracing/trace_pipe
```

**Expected output:**
```
           rm-12345    [000] .... 12345.678901: bpf_trace_printk: KPROBE ENTRY pid = 12345, dfd = 0
           rm-12345    [000] .... 12345.678902: bpf_trace_printk: KPROBE EXIT: pid = 12345, ret = 0
```

> **Note on trace_pipe**: `print()` inside `@bpf` functions writes to the kernel trace buffer via `bpf_printk`. The `trace_pipe()` helper simply reads `/sys/kernel/tracing/trace_pipe` to display this output in userspace. You can also use `trace_fields()` for structured parsing.

---

## Code Breakdown

| Component | Purpose |
|-----------|---------|
| `@section("kprobe/do_unlinkat")` | Attaches entry probe to `do_unlinkat` |
| `@section("kretprobe/do_unlinkat")` | Attaches return probe to `do_unlinkat` |
| `ctx: struct_pt_regs` | BPF context providing register access |
| `pid()` | Helper: extracts current process ID |
| `ctx.di` | 1st argument: directory file descriptor |
| `ctx.si` | 2nd argument: struct filename pointer |
| `ctx.ax` | Return value (kretprobe only) |
| `BPF()` | Python-BPF loader: compiles and attaches programs |
| `trace_pipe()` | Reads kernel trace output |

---

## Key Differences from C/CO-RE

| Aspect | C/CO-RE | Python-BPF |
|--------|---------|------------|
| **Function signature** | `BPF_KPROBE(do_unlinkat, int dfd, struct filename *name)` | `@section("kprobe/do_unlinkat")` + `ctx: struct_pt_regs` |
| **Argument access** | Typed parameters | `ctx.di`, `ctx.si` registers |
| **Memory read** | `BPF_CORE_READ(name, name)` | Not available (see limitation note) |
| **Print** | `bpf_printk(...)` | `print()` (max 3 args) |
| **Compile** | `ecc file.c` | `python3 file.py` (AOT) |
| **License** | `char LICENSE[] SEC("license")` | `@bpfglobal def LICENSE()` |

---

## Key Concepts Demonstrated

1. **kprobe in Python-BPF** - Using @section with "kprobe/do_unlinkat"
2. **kretprobe in Python-BPF** - Using @section with "kretprobe/do_unlinkat"
3. **Register access** - ctx.di, ctx.si, ctx.ax
4. **bpftrace reference** - Using tracepoint output to understand kprobe arguments
5. **Python-BPF limitations** - No BPF_CORE_READ equivalent for struct dereferencing

---

## Related Notes

**Python-BPF Tutorials:**
- [[Python-BPF Register Access in ctx and The Argument Mapping]] - Complete register reference

**eBPF Frameworks:**
- [[eBPF Tutorial - Kprobe Unlink]] - C/CO-RE equivalent tutorial
- [[BCC]] - BCC architecture and runtime compilation
- [[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]] - Memory access comparison

**Python-BPF Core:**
- [[PythonBPF]] - Main overview and architecture
- [[Python-BPF Compiler Limitations]] - Known parser gaps

---

*Tutorial created: 2026-05-16*
*Based on Python-BPF repository examples and ebpf-tutorial from eunomia.dev*
