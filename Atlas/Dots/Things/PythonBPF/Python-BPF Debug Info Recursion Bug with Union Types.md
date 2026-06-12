---
created: 2026-05-18
up:
  - "[[PythonBPF]]"
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Compiler Limitations]]"
  - "[[Python-BPF Register Access in ctx and The Argument Mapping]]"
  - "[[Python-BPF Tutorial - Kprobe Unlink]]"
tags:
  - pythonbpf
  - bug
  - debug-info
  - union
  - pt_regs
  - llvmlite
  - recursion
---

# Python-BPF Debug Info Recursion Bug with Union Types

## Problem

Python-BPF crashes with a **RecursionError** when generating debug information for eBPF programs that use kernel structures containing **union types**, such as `struct pt_regs`.

## Stack Trace

```
File ".../pythonbpf/debuginfo/debug_info_generator.py", line 256, in create_subprogram
    return self.module.add_debug_info("DISubprogram", ...)
File ".../llvmlite/ir/module.py", line 84, in add_debug_info
    operands = tuple(sorted(self._fix_di_operands(operands.items())))
File ".../llvmlite/ir/values.py", line 775, in __hash__
    return hash((self.is_distinct, self.kind, self.operands))
RecursionError: maximum recursion depth exceeded
```

## Root Cause

1. `struct pt_regs` contains union members (`union_pt_regs_0`, `union_pt_regs_1`)
2. Python-BPF's debug info generator attempts to create metadata for these unions
3. The metadata creation produces **circular references** in the LLVM debug info graph
4. When llvmlite tries to hash the metadata operands for caching, it recurses infinitely

## Warning Signs

The following warnings appear before the crash:

```
WARNING: Skipping debug info generation for union: union_pt_regs_0
WARNING: Blindly handling non-struct type to avoid type errors in vmlinux IR generation. Possibly a union.
WARNING: Skipping debug info generation for union: union_pt_regs_1
```

Python-BPF recognizes it cannot handle unions but still creates broken metadata references that trigger the recursion.

## Impact

Any eBPF program using `struct pt_regs` or other kernel structures with union members will fail to compile with Python-BPF.

## Workarounds

### Option 1: Disable Debug Info
If Python-BPF supports disabling debug info generation, this bypasses the buggy code path entirely.

### Option 2: Avoid Typed `struct_pt_regs`
Use `c_void_p` instead of `struct_pt_regs`, though this defeats Python-BPF's type-safe API:

```python
from ctypes import c_void_p

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: c_void_p) -> c_int64:
    # Cannot access ctx.di, ctx.si, etc.
    return 0
```

### Option 3: Patch Python-BPF
Modify `pythonbpf/functions/function_debug_info.py` to catch the recursion error and skip debug info for problematic functions.

## Reproduction Code

```python
from pythonbpf import bpf, bpfglobal, section, BPF
from ctypes import c_int64
from pythonbpf.helper import pid, uid
from vmlinux import struct_pt_regs

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
    
    if user_id > 999:
        print(f"pid={process_id}, uid={user_id}, dfd={dfd}")
    return 0

b = BPF()  # <-- Crashes here during debug info generation
b.load()
```

## Significance

This is a **critical parser gap** in Python-BPF that prevents real-world eBPF programs from accessing kernel structures like `pt_regs` through the intended Pythonic API. It exemplifies one of the limitations discussed in the PyCon talk: Python-BPF's alpha-stage parser cannot handle complex kernel types with unions.

## Related

- [[Python-BPF Compiler Limitations]] — Other parser gaps and missing features
- [[Python-BPF Register Access in ctx and The Argument Mapping]] — How ctx access works when it doesn't crash
- [[Python-BPF Tutorial - Kprobe Unlink]] — Working example using simple types

---

*Discovered: 2026-05-18*
*Python-BPF version: alpha (as of May 2026)*
