---
created: 2026-05-16
up:
  - "[[PythonBPF]]"
  - "[[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]]"
related:
  - "[[BCC]]"
  - "[[Python-BPF Compiler Limitations]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - python-bpf
  - kprobe
  - registers
  - x86_64
  - calling-convention
---
	
# Python-BPF: Register Access in ctx and The Argument Mapping

## Summary

Python-BPF exposes x86_64 CPU registers through `struct_pt_regs` context in kprobe functions. This note maps hardware registers to Python-BPF attributes and documents the System V AMD64 ABI calling convention for reading function arguments.

---

## Available Registers

Python-BPF provides access to all general-purpose and special-purpose x86_64 registers via `ctx` attributes:

| x86_64 Register | Python-BPF Attribute | Purpose |
|-----------------|----------------------|---------|
| `r15` | `ctx.r15` | Callee-saved register |
| `r14` | `ctx.r14` | Callee-saved register |
| `r13` | `ctx.r13` | Callee-saved register |
| `r12` | `ctx.r12` | Callee-saved register |
| `rbp` | `ctx.bp` | Frame pointer |
| `rbx` | `ctx.bx` | Callee-saved register |
| `r11` | `ctx.r11` | Temporary register |
| `r10` | `ctx.r10` | Temporary register |
| `r9` | `ctx.r9` | 6th function argument |
| `r8` | `ctx.r8` | 5th function argument |
| `rax` | `ctx.ax` | Return value / temporary |
| `rcx` | `ctx.cx` | 4th function argument |
| `rdx` | `ctx.dx` | 3rd function argument |
| `rsi` | `ctx.si` | 2nd function argument |
| `rdi` | `ctx.di` | 1st function argument |
| `orig_rax` | `ctx.orig_ax` | Original rax value |
| `rip` | `ctx.ip` | Instruction pointer |
| `cs` | `ctx.cs` | Code segment |
| `rflags` | `ctx.flags` | Flags register |
| `rsp` | `ctx.sp` | Stack pointer |
| `ss` | `ctx.ss` | Stack segment |

---

## Argument Mapping (System V AMD64 ABI)

When kprobing a kernel function, arguments are passed in specific registers according to the x86_64 calling convention:

| Argument Position | Register | Python-BPF Access | Example |
|-------------------|----------|-------------------|---------|
| 1st | `rdi` | `ctx.di` | `req = ctx.di` |
| 2nd | `rsi` | `ctx.si` | `name = ctx.si` |
| 3rd | `rdx` | `ctx.dx` | `count = ctx.dx` |
| 4th | `rcx` | `ctx.cx` | `flags = ctx.cx` |
| 5th | `r8` | `ctx.r8` | `mode = ctx.r8` |
| 6th | `r9` | `ctx.r9` | `attr = ctx.r9` |

**Return value** (kretprobe): Access via `ctx.ax` (contains `rax` register).

---

## Examples from Repository

### Example 1: Reading First Argument (disksnoop.py)

```python
from vmlinux import struct_pt_regs, struct_request
from pythonbpf import bpf, section, bpfglobal, compile

@bpf
@section("kprobe/blk_mq_start_request")
def trace_start(ctx1: struct_pt_regs) -> c_int32:
    req = ctx1.di  # 1st arg: struct request pointer
    return 0
```

### Example 2: Reading First Argument as Struct Pointer (disksnoop.py)

```python
@bpf
@section("kprobe/blk_mq_end_request")
def trace_completion(ctx: struct_pt_regs) -> c_int64:
    req_ptr = ctx.di           # 1st arg: raw pointer
    req = struct_request(ctx.di)  # Cast to struct_request
    data_len = req.__data_len   # Access struct field
    cmd_flags = req.cmd_flags   # Access struct field
    return 0
```

### Example 3: Reading Third Argument (container_monitor.py)

```python
@bpf
@section("kprobe/vfs_read")
def trace_read(ctx: struct_pt_regs) -> c_int32:
    count = c_uint64(ctx.dx)  # 3rd arg: read count
    return 0
```

### Example 4: Complete Register Dump (register_state_dump.py)

```python
@bpf
@section("kprobe/do_unlinkat")
def kprobe_execve(ctx: struct_pt_regs) -> c_int64:
    # Access all registers
    r15 = ctx.r15
    r14 = ctx.r14
    r13 = ctx.r13
    r12 = ctx.r12
    bp = ctx.bp
    bx = ctx.bx
    r11 = ctx.r11
    r10 = ctx.r10
    r9 = ctx.r9
    r8 = ctx.r8
    ax = ctx.ax
    cx = ctx.cx
    dx = ctx.dx
    si = ctx.si
    di = ctx.di
    
    print(f"rdi={di} rsi={si} rdx={dx}")
    print(f"rcx={cx} r8={r8} r9={r9}")
    
    return c_int64(0)
```

### Example 5: Simple First Argument Access (requests2.py)

```python
@bpf
@section("kprobe/blk_mq_start_request")
def example(ctx: struct_pt_regs) -> c_int64:
    req = ctx.di  # 1st arg: request pointer as u64
    print(f"data length {req}")
    return c_int64(0)
```

---

## Important Notes

### Type Handling
- Register values are returned as Python integers (mapped from u64/i64)
- Cast to specific types when needed: `c_uint64(ctx.dx)`, `c_int32(ctx.di)`
- Struct pointers: Use `struct_request(ctx.di)` to cast raw pointer to typed struct

### Known Limitations
- `ctx.args[0]` syntax is **not supported** (missing `ast.Subscript` handler)
- Use direct register access (`ctx.di`, `ctx.si`, etc.) instead
- See [[Python-BPF Compiler Limitations]] for details

### Kretprobe Return Values
- In kretprobe functions, `ctx.ax` contains the return value from the probed function
- This is the `rax` register value at function exit

---

## Related Notes

**Python-BPF Core:**
- [[PythonBPF]] — Main overview and architecture
- [[Python-BPF Compiler Limitations]] — Known parser gaps including `ctx.args[0]`

**eBPF Frameworks:**
- [[BCC]] — BCC architecture and runtime compilation
- [[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]] — Memory access comparison

**Kernel Concepts:**
- [[eBPF MOC]] — Parent MOC for all eBPF knowledge
