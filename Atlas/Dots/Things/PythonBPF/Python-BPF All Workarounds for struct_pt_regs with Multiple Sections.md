---
created: 2026-05-18
up:
  - "[[PythonBPF]]"
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Tutorial - Kprobe Unlink]]"
  - "[[Python-BPF RecursionError with Multiple Sections Using Union Structs]]"
  - "[[Python-BPF Debug Info Recursion Bug with Union Types]]"
  - "[[Python-BPF Cannot Create Buffer Arrays Inside BPF Functions]]"
tags:
  - pythonbpf
  - workaround
  - union
  - pt_regs
  - multiple-sections
  - experiment
---

# Python-BPF: All Workarounds for Using `struct_pt_regs` with Multiple Sections

## Problem Statement

Python-BPF crashes with a **RecursionError** when multiple BPF functions use `ctx: struct_pt_regs` because `struct_pt_regs` contains union members that create circular metadata references when shared between functions.

**Single section**: Works (with warnings)
**Two sections**: Fails with RecursionError in `function_debug_info.py:73`

---

## Option 1: One Section Per File ⭐ (Currently Working)

### Description
Split kprobe and kretprobe into separate Python files. Each file contains exactly one BPF function using `struct_pt_regs`.

### Implementation

**File 1: `kprobe-unlink-entry.py`**
```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_int64
from pythonbpf.helper import pid, uid
from vmlinux import struct_pt_regs
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    process_id = pid()
    user_id = uid()
    dfd = ctx.di
    filename_ptr = ctx.si
    print(f"KPROBE ENTRY pid={process_id}, uid={user_id}, dfd={dfd}, filename_ptr={filename_ptr}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

**File 2: `kprobe-unlink-exit.py`**
```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_int64
from pythonbpf.helper import pid, uid
from vmlinux import struct_pt_regs
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: struct_pt_regs) -> c_int64:
    process_id = pid()
    user_id = uid()
    ret = ctx.ax
    print(f"KPROBE EXIT pid={process_id}, uid={user_id}, ret={ret}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

### Pros
- ✅ Works immediately, no library modifications
- ✅ Full access to `ctx.di`, `ctx.si`, `ctx.ax`
- ✅ No RecursionError

### Cons
- ❌ Cannot have entry+exit probes in one file
- ❌ More files to manage
- ❌ Harder to share data between entry and exit

---

## Option 2: Detect Union Structs & Skip Debug Info Upfront

### Description
Modify `function_debug_info.py` to check if the struct contains unions **before** generating metadata. Skip debug info entirely for union-containing structs.

### Implementation

**File**: `pythonbpf/functions/function_debug_info.py`
**Lines**: 43-51 (after ctype_name check)

```python
if hasattr(annotation, "id"):
    ctype_name = annotation.id
    if ctype_name == "c_void_p":
        return
    elif ctype_name.startswith("ctypes"):
        raise SyntaxError(
            "The first argument should always be a pointer to a struct or a void pointer"
        )
    
    # NEW: Check if struct contains unions before generating debug info
    handler = VmlinuxHandlerRegistry.get_handler()
    if handler and handler.is_vmlinux_struct(ctype_name):
        struct_info = handler.vmlinux_symtab.get(ctype_name)
        if struct_info and _struct_contains_unions(struct_info):
            logger.warning(
                f"Skipping debug info for {func_node.name}: {ctype_name} contains union types"
            )
            return
    
    context_debug_info = VmlinuxHandlerRegistry.get_struct_debug_info(annotation.id)
    # ... rest of function continues
```

**Helper function to add** (after existing functions or in a new module):
```python
def _struct_contains_unions(struct_info) -> bool:
    """
    Check if a vmlinux struct contains union members.
    
    Args:
        struct_info: The vmlinux symbol table entry for the struct
    
    Returns:
        True if any field is a union type
    """
    if not hasattr(struct_info, 'fields') or not struct_info.fields:
        return False
    
    for field_name, field in struct_info.fields.items():
        # Check if field type is a union or contains union
        if hasattr(field, 'type') and field.type:
            type_name = getattr(field.type, '__name__', str(field.type))
            if 'union' in type_name.lower():
                return True
    
    return False
```

### Challenge
The exact implementation of `_struct_contains_unions()` depends on the internal structure of `struct_info` in the vmlinux symtab. You may need to inspect `handler.vmlinux_symtab` at runtime to determine the correct field access pattern.

### Pros
- ✅ Cleanest targeted fix
- ✅ No broken metadata left behind
- ✅ Other functions still get debug info

### Cons
- ❌ Requires understanding vmlinux symtab internals
- ❌ Loses debug info for union structs
- ❌ May not be trivial to implement `_struct_contains_unions()`

---

## Option 3: Isolate Metadata Per-Function (Ideal Fix)

### Description
Modify Python-BPF to create fresh copies of struct debug info for each function, preventing shared circular references.

### Implementation Option A: Deep Copy

**File**: `pythonbpf/functions/function_debug_info.py`
**Lines**: 51-57

```python
context_debug_info = VmlinuxHandlerRegistry.get_struct_debug_info(annotation.id)

# NEW: Create a fresh copy for this function to prevent circular references
# when the same struct is used in multiple functions
import copy
try:
    context_debug_info = copy.deepcopy(context_debug_info)
except (TypeError, AttributeError):
    # llvmlite metadata may not support deep copying
    logger.warning(f"Could not deep copy debug info for {func_node.name}")
```

**Note**: This likely **won't work** because llvmlite metadata objects are not standard Python objects and don't support deep copying.

### Implementation Option B: Fresh Generation

**File**: `pythonbpf/vmlinux_parser/ir_gen/debug_info_gen.py`
**Lines**: 30-32

Current code:
```python
# Check if debug info for this struct has already been generated
for existing_struct, debug_info in generated_debug_info:
    if existing_struct.name == struct.name:
        return debug_info  # Reuses shared metadata
```

Modified code (force fresh generation):
```python
# Always generate fresh debug info to prevent circular references
# when the same struct is used in multiple functions
# Comment out or skip the reuse logic:
# for existing_struct, debug_info in generated_debug_info:
#     if existing_struct.name == struct.name:
#         return debug_info
```

### Challenge
Fresh generation for every function may significantly increase:
- Compilation time
- Memory usage
- Binary size

### Pros
- ✅ Proper fix, preserves debug info for all functions
- ✅ No special-casing for union structs

### Cons
- ❌ Complex implementation
- ❌ May increase compilation time and memory usage
- ❌ Option A (deep copy) likely fails with llvmlite
- ❌ Option B (fresh generation) has performance impact

---

## Option 4: Disable All Debug Info (Nuclear Option)

### Description
Skip debug info generation entirely. This bypasses the buggy code path.

### Implementation

**File**: `pythonbpf/functions/functions_pass.py`
**Line**: 468

Current code:
```python
logger.info(f"Generating Debug Info for Function {func_node.name}")
generate_function_debug_info(func_node, module, func)
```

Modified code:
```python
# DISABLED: Debug info generation causes RecursionError with union structs
# logger.info(f"Generating Debug Info for Function {func_node.name}")
# generate_function_debug_info(func_node, module, func)
```

Or with environment variable check:
```python
import os
if os.environ.get("PYTHONBPF_NO_DEBUG_INFO") != "1":
    logger.info(f"Generating Debug Info for Function {func_node.name}")
    generate_function_debug_info(func_node, module, func)
```

### Pros
- ✅ Guaranteed to work immediately
- ✅ No per-function logic needed
- ✅ Can be toggled with environment variable

### Cons
- ❌ No debug info for ANY function
- ❌ Makes debugging eBPF programs harder
- ❌ Nuclear option — overkill for most use cases

---

## Option 5: Use Tracepoints Instead of Kprobes

### Description
Tracepoints provide arguments directly without needing `struct_pt_regs`.

### Implementation

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_int64, c_void_p
from pythonbpf.helper import pid, uid
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@section("tracepoint/syscalls/sys_enter_unlinkat")
def trace_unlinkat_entry(ctx: c_void_p) -> c_int64:
    # Note: ctx structure is different for tracepoints
    # You'd need to cast ctx to the tracepoint struct
    process_id = pid()
    user_id = uid()
    print(f"TRACE ENTRY pid={process_id}, uid={user_id}")
    return 0

@bpf
@section("tracepoint/syscalls/sys_exit_unlinkat")
def trace_unlinkat_exit(ctx: c_void_p) -> c_int64:
    process_id = pid()
    user_id = uid()
    print(f"TRACE EXIT pid={process_id}, uid={user_id}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
```

### Challenge
Tracepoint context structures are different from kprobe `struct pt_regs`. You'd need to know the exact tracepoint format.

### Pros
- ✅ May avoid the union bug (depends on tracepoint struct)
- ✅ Arguments accessible without register mapping

### Cons
- ❌ Different context structure
- ❌ May have same union issues if tracepoint struct contains unions
- ❌ Less flexible than kprobes

---

## Failed Approaches (Documented for Reference)

### Failed: Using `c_void_p` Context

**What we tried**: Use `c_void_p` instead of `struct_pt_regs` to avoid the union bug.

**Why it failed**: Python-BPF doesn't support pointer arithmetic on `c_void_p`. Cannot access `ctx + offset` to read registers.

**Error**: `AttributeError: 'NoneType' object has no attribute '__name__'`

**Conclusion**: `c_void_p` only works for basic helpers without argument access.

### Failed: Patching function_debug_info.py with Try/Except

**What we tried**: Wrap `create_subprogram()` in try/except to catch RecursionError.

**Result**: Caught the error but left broken metadata, causing:
```
libbpf: failed to perform CO-RE relocations: -EINVAL
```

**Conclusion**: Catching the error isn't enough — the partial metadata still breaks BTF.

### Failed: Creating Buffer Arrays for probe_read_str

**What we tried**: Use `c_char * 256` to create buffers for string reading.

**Why it failed**: Python-BPF's AST parser cannot handle ctypes type expressions in BPF functions.

**Error**: `TypeError: Unsupported operand type: <class 'ast.Name'>`

**Conclusion**: Cannot dynamically allocate buffers inside `@bpf` functions.

---

## Recommendation Matrix

| Approach | Effort | Reliability | Debug Info | Multiple Sections | Full ctx Access |
|----------|--------|-------------|------------|-------------------|-----------------|
| **Option 1: One section/file** | Low | ✅ High | ✅ Yes | ⚠️ Split files | ✅ Yes |
| **Option 2: Detect unions** | Medium | ✅ High | ⚠️ Partial | ✅ Yes | ✅ Yes |
| **Option 3: Isolate metadata** | High | ✅ High | ✅ Yes | ✅ Yes | ✅ Yes |
| **Option 4: Disable debug info** | Low | ✅ High | ❌ No | ✅ Yes | ✅ Yes |
| **Option 5: Tracepoints** | Medium | ⚠️ Unknown | ⚠️ Depends | ✅ Yes | ⚠️ Different |

## Current Recommendation

**For immediate use**: **Option 1** (one section per file) — works right now, no code changes.

**For a proper fix**: **Option 2** (detect unions and skip debug info) — cleanest approach if you want to modify Python-BPF.

**For production**: Consider **BCC** or **libbpf/CO-RE** instead of Python-BPF for complex multi-section programs.

---

## Related Notes

- [[Python-BPF RecursionError with Multiple Sections Using Union Structs]] — Original discovery
- [[Python-BPF Debug Info Recursion Bug with Union Types]] — Deep dive into the bug
- [[Python-BPF Cannot Create Buffer Arrays Inside BPF Functions]] — Buffer limitation
- [[Python-BPF Compiler Limitations]] — Other parser gaps

---

*Created: 2026-05-18*
*Python-BPF version: alpha (as of May 2026)*
*Purpose: Personal experimentation and PyCon talk preparation*
