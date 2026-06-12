---
created: 2026-05-18
up:
  - "[[PythonBPF]]"
  - "[[eBPF MOC]]"
related:
  - "[[Python-BPF Compiler Limitations]]"
  - "[[Python-BPF Register Access in ctx and The Argument Mapping]]"
  - "[[Python-BPF Debug Info Recursion Bug with Union Types]]"
tags:
  - pythonbpf
  - bug
  - union
  - pt_regs
  - multiple-sections
  - debug-info
  - workaround
---

# Python-BPF: RecursionError Only Occurs with Multiple Sections Using `struct_pt_regs`

## Key Finding

The Python-BPF **RecursionError with union types** (e.g., `struct_pt_regs`) **only occurs when multiple BPF functions use the same union-containing struct**. A single function with `struct_pt_regs` works fine.

## Evidence

### Single Section Works
```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    dfd = ctx.di
    filename_ptr = ctx.si
    print(f"KPROBE ENTRY pid={pid()}, uid={uid()}, filename={filename_ptr}")
    return 0
```

**Result**: Compiles and runs successfully. Prints output:
```
KPROBE ENTRY pid = 717211, user id = 1000, filename = -131148953243648
```

### Two Sections Fails
```python
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    dfd = ctx.di
    filename_ptr = ctx.si
    print(f"KPROBE ENTRY pid={pid()}, uid={uid()}, filename={filename_ptr}")
    return 0

@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: struct_pt_regs) -> c_int64:
    ret = ctx.ax
    print(f"KPROBE EXIT ret={ret}")
    return 0
```

**Result**: RecursionError during compilation at `function_debug_info.py:73` (inside `generator.create_subprogram()`).

## Root Cause Analysis

1. **Shared Debug Info Metadata**: Python-BPF shares `struct_pt_regs` debug info between all functions
2. **Circular References in Unions**: When `struct_pt_regs` contains union members (`union_pt_regs_0`, `union_pt_regs_1`), Python-BPF creates circular metadata references
3. **llvmlite Metadata Cache**: When the second function tries to create its `DISubprogram`, llvmlite's metadata cache (`add_metadata()`) attempts to hash the shared metadata, hitting infinite recursion because of the circular references
4. **First Function Succeeds**: With only one function, there's no shared metadata conflict — the union warnings appear but don't crash because there's nothing to conflict with

## Current Patch Applied

**File**: `pythonbpf/functions/function_debug_info.py`

Applied try/except around `create_subprogram()` to catch the RecursionError:

```python
try:
    subprogram_debug_info = generator.create_subprogram(
        func_node.name, subroutine_type, retained_nodes
    )
    generator.add_scope_to_local_variable(
        context_local_variable, subprogram_debug_info
    )
    func.set_metadata("dbg", subprogram_debug_info)
except RecursionError:
    logger.warning(
        f"Skipping debug info for {func_node.name} due to union type in context"
    )
```

**Result**: The RecursionError is caught, but leaves partial/broken debug info attached. When libbpf later tries CO-RE relocations with this broken BTF, it fails with `-EINVAL`.

## Workaround Options

### Option 1: Use One Section at a Time
**Status**: Currently working workaround

**Implementation**: Split programs into separate files, each with one BPF function using `struct_pt_regs`.

```python
# file1: kprobe-unlink-entry.py
@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    dfd = ctx.di
    filename_ptr = ctx.si
    print(f"ENTRY pid={pid()}, uid={uid()}")
    return 0
```

```python
# file2: kprobe-unlink-exit.py
@bpf
@section("kretprobe/do_unlinkat")
def do_unlinkat_exit(ctx: struct_pt_regs) -> c_int64:
    ret = ctx.ax
    print(f"EXIT ret={ret}")
    return 0
```

**Pros**: Simple, no library modifications needed
**Cons**: Cannot have both entry and exit probes in the same program; increases complexity for related probes

---

### Option 2: Skip ALL Debug Info for Union-Containing Structs
**Status**: Requires library modification

**Implementation**: Detect union structs in `function_debug_info.py` and skip debug info entirely before attempting to create metadata.

**Where to modify**: `pythonbpf/functions/function_debug_info.py:43-51`

```python
if hasattr(annotation, "id"):
    ctype_name = annotation.id
    if ctype_name == "c_void_p":
        return
    elif ctype_name.startswith("ctypes"):
        raise SyntaxError(...)
    
    # NEW: Check if struct contains unions before generating debug info
    handler = VmlinuxHandlerRegistry.get_handler()
    if handler and handler.is_vmlinux_struct(ctype_name):
        struct_info = handler.vmlinux_symtab.get(ctype_name)
        # Check if struct has union fields
        if struct_info and _struct_contains_unions(struct_info):
            logger.warning(
                f"Skipping debug info for {func_node.name}: {ctype_name} contains union types"
            )
            return
    
    context_debug_info = VmlinuxHandlerRegistry.get_struct_debug_info(annotation.id)
    # ... rest of function
```

**Challenge**: Need to implement `_struct_contains_unions()` to inspect vmlinux struct definitions.

**Pros**: Clean fix, no broken metadata left behind
**Cons**: Requires understanding vmlinux symtab internals; loses debug info for all union structs

---

### Option 3: Isolate Metadata Per-Function
**Status**: Requires library modification

**Implementation**: Modify Python-BPF to create fresh copies of struct debug info for each function, preventing shared circular references.

**Where to modify**: `pythonbpf/vmlinux_parser/ir_gen/debug_info_gen.py`

Current code at lines 30-32:
```python
# Check if debug info for this struct has already been generated
for existing_struct, debug_info in generated_debug_info:
    if existing_struct.name == struct.name:
        return debug_info  # Reuses shared metadata
```

**Fix**: Force fresh generation for each function:
```python
# Always generate fresh debug info to prevent circular references
# when the same struct is used in multiple functions
```

**Alternative**: In `function_debug_info.py`, create a deep copy of `context_debug_info` before use:
```python
import copy
context_debug_info = VmlinuxHandlerRegistry.get_struct_debug_info(annotation.id)
# Create a fresh copy for this function
context_debug_info = copy.deepcopy(context_debug_info)  # May not work with LLVM metadata
```

**Challenge**: llvmlite metadata objects may not support deep copying. Would need to regenerate metadata from scratch.

**Pros**: Proper fix, preserves debug info for all functions
**Cons**: Complex implementation, may increase compilation time and memory usage

## Recommendation

**Short-term**: Use Option 1 (one section per file) for immediate productivity.

**Long-term**: Implement Option 2 (skip debug info for union structs) as it's the cleanest targeted fix. Option 3 is ideal but requires significant changes to Python-BPF's vmlinux parser.

## Related

- [[Python-BPF Debug Info Recursion Bug with Union Types]] — Original bug documentation
- [[Python-BPF Compiler Limitations]] — Other parser gaps
- [[Python-BPF Register Access in ctx and The Argument Mapping]] — Working with ctx when it doesn't crash

---

*Discovered: 2026-05-18*
*Python-BPF version: alpha (as of May 2026)*
*Patch applied: function_debug_info.py try/except (partial fix)*
