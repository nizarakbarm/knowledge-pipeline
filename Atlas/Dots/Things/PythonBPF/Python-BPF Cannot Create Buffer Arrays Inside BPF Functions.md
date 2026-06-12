---
created: 2026-05-18
up:
  - "[[PythonBPF]]"
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Tutorial - Kprobe Unlink]]"
  - "[[Python-BPF Compiler Limitations]]"
  - "[[Python-BPF Debug Info Recursion Bug with Union Types]]"
tags:
  - pythonbpf
  - buffer
  - array
  - ctypes
  - probe_read
  - probe_read_str
  - limitation
---

# Python-BPF Cannot Create Buffer Arrays Inside BPF Functions

## Problem

Python-BPF **cannot create buffer arrays** inside `@bpf` decorated functions using ctypes syntax (e.g., `c_char * 256`). This prevents using `probe_read` and `probe_read_str` helpers to read strings or complex data from kernel memory.

## Error

When attempting to create a buffer inside a BPF function:

```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    name_ptr = ctx.si
    filename_buf = c_char * 256  # This line causes the error!
    probe_read_str(filename_buf, name_ptr)
    return 0
```

**Result**:
```
TypeError: Unsupported operand type: <class 'ast.Name'>
```

**Full stack trace**:
```
File ".../pythonbpf/expr/expr_pass.py", line 205, in get_operand_value
    raise TypeError(f"Unsupported operand type: {type(operand)}")
TypeError: Unsupported operand type: <class 'ast.Name'>
```

## Root Cause

Python-BPF's AST parser analyzes the BPF function code and tries to compile `c_char * 256` into LLVM IR. However:

1. `c_char` is parsed as an `ast.Name` node (imported from ctypes)
2. Python-BPF's expression evaluator (`expr_pass.py`) has **no handler** for ctypes type names in binary expressions
3. The parser doesn't understand that `c_char * 256` means "create a 256-byte buffer"
4. BPF programs **cannot dynamically allocate memory** — all buffers must be pre-declared or stored in maps

### Where the Error Occurs

The error originates in `pythonbpf/expr/expr_pass.py`:

```python
def get_operand_value(func, module, operand, builder, local_sym_tab, map_sym_tab, structs_sym_tab):
    # ... handles constants, variables, etc. ...
    raise TypeError(f"Unsupported operand type: {type(operand)}")
```

When Python-BPF encounters `c_char * 256`:
- `c_char` is an `ast.Name` (not a constant or variable)
- The parser doesn't know how to resolve ctypes type names
- Falls through to the `TypeError`

## What Cannot Be Done

Inside `@bpf` functions, you **cannot**:

```python
# Create buffer arrays
buf = c_char * 256

# Use ctypes constructors
buf = create_string_buffer(256)

# Dynamic memory allocation
buf = ctypes.allocate(ctypes.c_char, 256)

# Any ctypes type expression
arr = ctypes.c_int * 10
```

## Workarounds

### Option 1: Print Pointer Address Only (Simplest)

Instead of reading the string, just print the pointer address:

```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    current_pid = pid()
    dfd = ctx.di
    name_ptr = ctx.si  # Just a pointer address
    print(f"ENTRY pid={current_pid}, dfd={dfd}, name_ptr=0x{name_ptr:x}")
    return 0
```

**Pros**: Works immediately, no buffer needed
**Cons**: Cannot see the actual filename string

---

### Option 2: Use bpftrace for String Reading

Use bpftrace to read strings while developing:

```bash
bpftrace -e 'kprobe:do_unlinkat {
    printf("unlink: %s\n", str(arg1));
}'
```

**Pros**: Native string reading, simple syntax
**Cons**: Not Python-BPF, not suitable for production Python tooling

---

### Option 3: Use BCC for String Reading

BCC supports string reading via C-string embedding:

```python
from bcc import BPF

prog = """
#include <uapi/linux/ptrace.h>
BPF_PERF_OUTPUT(events);

struct data_t {
    u32 pid;
    char comm[16];
    char fname[256];
};

int trace_entry(struct pt_regs *ctx) {
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    // Read filename from pointer
    bpf_probe_read_kernel_str(&data.fname, sizeof(data.fname), 
                            (void *)PT_REGS_PARM2(ctx));
    
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

b = BPF(text=prog)
b.attach_kprobe(event="do_unlinkat", fn_name="trace_entry")
```

**Pros**: Full kernel memory access, string reading, BTF/CO-RE support
**Cons**: Requires C knowledge, compiles at runtime (slower)

---

### Option 4: Use Pre-declared BPF Map with String Field

Define a struct with char array in a BPF map (if Python-BPF supports it):

```python
from pythonbpf import bpf, map, struct, BPF
from pythonbpf.maps import HashMap
from ctypes import c_uint32, c_char

@bpf
@struct
class event_t:
    pid: c_uint32
    fname: c_char * 256  # May or may not work in struct definition

@bpf
@map
def events() -> HashMap:
    return HashMap(key=c_uint32, value=event_t, max_entries=1024)
```

**Note**: This may not work either, as Python-BPF's struct definition support is also alpha-stage.

---

### Option 5: Wait for Python-BPF to Mature

This is a known limitation in Python-BPF's alpha-stage parser. Future versions may support:
- Buffer allocation in BPF functions
- `probe_read_str` with automatic buffer handling
- String helper functions similar to BCC

## Comparison: Python-BPF vs BCC for String Reading

| Capability | Python-BPF | BCC |
|-----------|-----------|-----|
| Read kernel strings | **Not supported** | ✅ `bpf_probe_read_kernel_str()` |
| Buffer allocation | **Not supported** | ✅ C array declarations |
| Pointer argument access | ✅ `ctx.di`, `ctx.si` | ✅ `PT_REGS_PARM1()`, etc. |
| Runtime compilation | No (AOT) | Yes (Clang/LLVM at runtime) |
| Ease of use | Python decorators | C string embedding |

## Practical Recommendation

**For production tools requiring string reading:**
- Use **BCC** or **libbpf/CO-RE** instead of Python-BPF
- Python-BPF is suitable for simple probes without string arguments

**For Python-BPF development:**
- Accept pointer addresses only (`name_ptr = ctx.si`)
- Use **bpftrace** for quick string debugging
- Combine Python-BPF for the Python wrapper with BCC/libbpf for the actual BPF program

## Related

- [[Python-BPF Tutorial - Kprobe Unlink]] — Where this limitation was discovered
- [[Python-BPF Compiler Limitations]] — Other parser gaps and missing features
- [[Python-BPF probe_read and probe_read_str Usage with c_void_p]] — Attempted workaround (also limited)

---

*Discovered: 2026-05-18*
*Python-BPF version: alpha (as of May 2026)*
*Error: TypeError: Unsupported operand type: <class 'ast.Name'>*
