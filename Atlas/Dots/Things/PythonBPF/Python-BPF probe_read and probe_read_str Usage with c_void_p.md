---
created: 2026-05-18
up:
  - "[[PythonBPF]]"
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Debug Info Recursion Bug with Union Types]]"
  - "[[Python-BPF RecursionError with Multiple Sections Using Union Structs]]"
tags:
  - pythonbpf
  - probe_read
  - probe_read_str
  - kernel-memory
  - c_void_p
  - pt_regs
  - x86_64
---

# Python-BPF: Using probe_read and probe_read_str with c_void_p Context

## Overview

When using `ctx: c_void_p` instead of `struct_pt_regs`, you lose the convenient typed register access (`ctx.di`, `ctx.si`) but avoid the union-related RecursionError with multiple sections. To access kernel data, you must use `probe_read` and `probe_read_str` helpers.

> **WARNING**: The examples below using `ctx + offset` are **theoretical** and **will not compile** with Python-BPF. Python-BPF does not support pointer arithmetic on `c_void_p`. See [Critical Limitation](#critical-limitation-c_void_p-cannot-access-ctx-arguments) below for details.

## Helper Signatures

### probe_read
```python
def probe_read(dst, size, src):
    """Safely read data from kernel memory"""
    return ctypes.c_int64(0)
```

**Parameters:**
- `dst`: Destination buffer (pointer to local memory)
- `size`: Number of bytes to read
- `src`: Source address in kernel memory (pointer)

**Returns:**
- `0` on success, negative error code on failure

### probe_read_str
```python
def probe_read_str(dst, src):
    """Safely read a null-terminated string from kernel memory"""
    return ctypes.c_int64(0)
```

**Parameters:**
- `dst`: Destination buffer for the string
- `src`: Source address of the null-terminated string in kernel memory

**Returns:**
- Number of bytes read (including null terminator) on success
- Negative error code on failure

## x86_64 struct pt_regs Offsets

When `ctx` is `c_void_p` in a kprobe, it points to `struct pt_regs`. Here are the x86_64 offsets:

| Offset | Register | Field | Common Use |
|--------|----------|-------|------------|
| 0 | r15 | | |
| 8 | r14 | | |
| 16 | r13 | | |
| 24 | r12 | | |
| 32 | rbp | | |
| 40 | rbx | | |
| 48 | r11 | | |
| 56 | r10 | | |
| 64 | r9 | | 6th arg |
| 72 | r8 | | 5th arg |
| 80 | rax | ax | Return value (kretprobe) |
| 88 | rcx | cx | 4th arg |
| 96 | rdx | dx | 3rd arg |
| **104** | **rsi** | **si** | **2nd arg** |
| **112** | **rdi** | **di** | **1st arg** |
| 120 | orig_rax | | Original syscall number |
| 128 | rip | | Instruction pointer |
| 136 | cs | | Code segment |
| 144 | eflags | | Flags register |
| 152 | rsp | | Stack pointer |
| 160 | ss | | Stack segment |

**Total size**: 168 bytes

## Usage Examples

### Example 1: Reading Integer Arguments

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_void_p, c_int64, c_uint64, c_int32, create_string_buffer
from pythonbpf.helper import pid, uid, probe_read
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    
    # Read dfd (1st argument) from ctx + 112 (rdi offset)
    dfd_buf = c_int64(0)
    probe_read(ctypes.addressof(dfd_buf), 8, ctx + 112)
    dfd = dfd_buf.value
    
    # Read filename pointer (2nd argument) from ctx + 104 (rsi offset)
    name_ptr_buf = c_uint64(0)
    probe_read(ctypes.addressof(name_ptr_buf), 8, ctx + 104)
    filename_ptr = name_ptr_buf.value
    
    print(f"ENTRY pid={process_id}, uid={user_id}, dfd={dfd}, name_ptr=0x{filename_ptr:x}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

### Example 2: Reading a String (Filename)

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_void_p, c_int64, c_uint64, create_string_buffer
from pythonbpf.helper import pid, uid, probe_read, probe_read_str
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    
    # Read filename pointer from ctx + 104 (rsi)
    name_ptr_buf = c_uint64(0)
    probe_read(ctypes.addressof(name_ptr_buf), 8, ctx + 104)
    filename_ptr = name_ptr_buf.value
    
    # Read the actual filename string (max 256 bytes)
    filename_buf = create_string_buffer(256)
    result = probe_read_str(ctypes.addressof(filename_buf), filename_ptr)
    
    if result >= 0:
        filename = filename_buf.value.decode('utf-8', errors='replace')
        print(f"ENTRY pid={process_id}, uid={user_id}, filename={filename}")
    else:
        print(f"ENTRY pid={process_id}, uid={user_id}, filename=<read failed>")
    
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

### Example 3: Reading Return Value (kretprobe)

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_void_p, c_int64
from pythonbpf.helper import pid, uid, probe_read
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    
    # Read return value from ctx + 80 (rax offset)
    ret_buf = c_int64(0)
    probe_read(ctypes.addressof(ret_buf), 8, ctx + 80)
    ret = ret_buf.value
    
    print(f"EXIT pid={process_id}, uid={user_id}, ret={ret}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

### Example 4: Combining Entry and Exit (Multiple Sections Work!)

This is the key advantage of `c_void_p`: **no RecursionError with multiple sections**.

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_void_p, c_int64, c_uint64
from pythonbpf.helper import pid, uid, probe_read, probe_read_str
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    
    # Read dfd
    dfd_buf = c_int64(0)
    probe_read(ctypes.addressof(dfd_buf), 8, ctx + 112)
    dfd = dfd_buf.value
    
    # Read filename
    name_ptr_buf = c_uint64(0)
    probe_read(ctypes.addressof(name_ptr_buf), 8, ctx + 104)
    
    print(f"ENTRY pid={process_id}, uid={user_id}, dfd={dfd}")
    return 0

@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    
    # Read return value
    ret_buf = c_int64(0)
    probe_read(ctypes.addressof(ret_buf), 8, ctx + 80)
    ret = ret_buf.value
    
    print(f"EXIT pid={process_id}, uid={user_id}, ret={ret}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

## Important Notes

### Buffer Allocation
Always allocate local buffers before passing to `probe_read`:
```python
# Correct
buf = c_int64(0)
probe_read(ctypes.addressof(buf), 8, src)

# WRONG - passing Python int directly
probe_read(0, 8, src)  # This won't work
```

### Size Must Match
The `size` parameter must match the actual data size:
```python
# Reading 64-bit value
buf64 = c_int64(0)
probe_read(ctypes.addressof(buf64), 8, src)

# Reading 32-bit value
buf32 = c_int32(0)
probe_read(ctypes.addressof(buf32), 4, src)
```

### probe_read_str Buffer Size
`probe_read_str` will read up to the buffer size or until null terminator, whichever comes first:
```python
# Reads up to 256 bytes or until '\0'
buf = create_string_buffer(256)
probe_read_str(ctypes.addressof(buf), src_ptr)
```

### Return Value Check
Always check the return value, especially for `probe_read_str`:
```python
result = probe_read_str(ctypes.addressof(buf), src)
if result < 0:
    # Read failed - invalid address, etc.
    pass
```

### Architecture Dependency
The offsets above are for **x86_64 only**. ARM64 and other architectures have different `struct pt_regs` layouts. For portable code, you should either:
- Detect architecture at compile time
- Use BTF/CO-RE for field access (when Python-BPF supports it)

## Comparison: c_void_p vs struct_pt_regs

| Feature | `ctx: struct_pt_regs` | `ctx: c_void_p` |
|---------|----------------------|-----------------|
| Multiple sections | **Fails** (RecursionError) | **Works** |
| Register access | Easy (`ctx.di`, `ctx.si`) | Manual offsets |
| Readability | Clean Pythonic API | Low-level pointer math |
| vmlinux import | Required | **Not required** |
| Portability | Architecture-independent via BTF | Architecture-dependent offsets |
| Error-prone | Low | Higher (wrong offset = wrong data) |

## Critical Limitation: c_void_p Cannot Access ctx Arguments

**Important finding**: Python-BPF does **not** support pointer arithmetic on `c_void_p` context. This means you **cannot access kprobe arguments** with `c_void_p`.

### What Fails

```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    dfd_buf = c_int64(0)
    probe_read(ctypes.addressof(dfd_buf), 8, ctx + 112)  # ERROR!
    return 0
```

**Error**:
```
AttributeError: 'NoneType' object has no attribute '__name__'
```

### Why It Fails

Python-BPF's parser cannot handle `ctx + 112`:
1. `ctx` is typed as `c_void_p`
2. The addition `ctx + 112` loses type information
3. `allocation_pass.py:340` tries to determine `struct_type.__name__` but gets `None`
4. This causes the AttributeError during compilation

### What Actually Works with c_void_p

Only basic helpers that don't access `ctx`:

```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    process_id = pid()   # Works - no ctx access
    user_id = uid()      # Works - no ctx access
    print(f"ENTRY pid={process_id}")
    return 0
```

### Revised Comparison

| Feature | `ctx: struct_pt_regs` | `ctx: c_void_p` |
|---------|----------------------|-----------------|
| Multiple sections | **Fails** (RecursionError) | **Works** |
| Register access | Easy (`ctx.di`, `ctx.si`) | **Impossible** |
| Access arguments | Yes | **No** |
| Read kernel memory | Yes | **No** |
| Use basic helpers | Yes | Yes |
| vmlinux import | Required | Not required |

## When to Use Which

**Use `struct_pt_regs` when:**
- Single section per file (workaround for RecursionError)
- Readability is priority
- You don't want to manage offsets manually

**Use `c_void_p` when:**
- Multiple sections in one file needed
- You only need basic helpers (pid, uid, ktime) without argument access
- You don't need to read ctx or kernel memory
- You want to avoid vmlinux import

**Do NOT use `c_void_p` when:**
- You need to access kprobe arguments (use `struct_pt_regs` instead)
- You need to read kernel memory via offsets
- You need ctx register access

## Related

- [[Python-BPF Debug Info Recursion Bug with Union Types]] — Why struct_pt_regs fails with multiple sections
- [[Python-BPF RecursionError with Multiple Sections Using Union Structs]] — Workarounds for the union bug
- [[Python-BPF Compiler Limitations]] — Other Python-BPF parser gaps

---

*Created: 2026-05-18*
*Python-BPF version: alpha (as of May 2026)*
*Architecture: x86_64 Linux*
