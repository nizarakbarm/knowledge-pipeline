---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-modules]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - dynamic-libraries
  - symbols
---

# llvmlite Dynamic Libraries

Dynamic library loading and symbol resolution for LLVM execution engines.

## Summary

Provides functionality to load shared libraries and resolve symbols at runtime, enabling JIT-compiled code to call external functions.

## Key Concepts

### Library Loading

`load_library_permanently(filename)` — Load a shared library
- `filename` — Path to the shared library (.so, .dll, .dylib)
- Returns None on success, raises exception on failure
- Library remains loaded for the lifetime of the process

### Symbol Resolution

`get_function_address(name)` — Get address of a function symbol
- `name` — Symbol name as string
- Returns integer address (0 if not found)

`get_global_value_address(name)` — Get address of a global value symbol
- `name` — Symbol name as string
- Returns integer address (0 if not found)

### Symbol Search Order

1. Symbols in the main executable
2. Symbols in libraries loaded with `load_library_permanently()`
3. Symbols in LLVM-generated code

## Code Example

```python
from llvmlite import binding as llvm

# Load a shared library
llvm.load_library_permanently("/usr/lib/libm.so")

# Get function address
sin_addr = llvm.get_function_address("sin")
print(f"sin function at: {hex(sin_addr)}")

# Use with execution engine
engine = llvm.create_mcjit_compiler(module, target_machine)
engine.add_global_mapping(func, sin_addr)
```

## Connections

- Used by [[llvmlite-binding-engine]] for external function calls
- Complements [[llvmlite-binding-modules]] for linking
- Essential for JIT compilation with external dependencies

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/dynamic-libraries.html

Back to [[llvmlite-Binding-Layer-MoC]]
