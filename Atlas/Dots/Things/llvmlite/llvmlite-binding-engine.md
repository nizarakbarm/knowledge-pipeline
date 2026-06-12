---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-binding-target]]"
  - "[[llvmlite-binding-passmanager]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - execution-engine
  - jit
---

# llvmlite Execution Engine

JIT compilation and execution engine for LLVM modules.

## Summary

Provides classes to compile LLVM modules to machine code and execute them at runtime. Supports both MCJIT and ORC JIT compilation models.

## Key Concepts

### MCJIT Engine

`create_mcjit_compiler(module, target_machine)` — Create MCJIT compiler
- `module` — Module to compile
- `target_machine` — Target machine configuration

Methods:
- `get_function_address(name)` — Get compiled function address
- `add_global_mapping(global_val, addr)` — Map global to address
- `add_module(module)` — Add module to engine
- `finalize_object()` — Finalize compilation
- `set_object_cache(notify_func, get_func)` — Set object cache callbacks

### Execution

Once compiled, functions can be called via ctypes or similar FFI mechanisms:

```python
import ctypes

# Get function address
addr = engine.get_function_address("add")

# Create ctypes function
cfunc = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)(addr)

# Call
result = cfunc(5, 3)
```

### Memory Management

- Engine owns compiled code memory
- Code remains valid while engine exists
- Engine can compile multiple modules

## Code Example

```python
from llvmlite import binding as llvm
import ctypes

# Initialize
target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine()

# Parse and compile IR
llvm_ir = """
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
"""
module = llvm.parse_assembly(llvm_ir)
module.verify()

# Create execution engine
engine = llvm.create_mcjit_compiler(module, target_machine)
engine.finalize_object()

# Get and call function
addr = engine.get_function_address("add")
cfunc = ctypes.CFUNCTYPE(
    ctypes.c_int32, ctypes.c_int32, ctypes.c_int32
)(addr)

print(f"5 + 3 = {cfunc(5, 3)}")
```

## Connections

- Uses [[llvmlite-binding-modules]] for module input
- Uses [[llvmlite-binding-target]] for target machine
- Optimized by [[llvmlite-binding-passmanager]] before execution
- Links with [[llvmlite-binding-dynamic-libraries]] for external symbols

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/execution-engine.html

Back to [[llvmlite-Binding-Layer-MoC]]
