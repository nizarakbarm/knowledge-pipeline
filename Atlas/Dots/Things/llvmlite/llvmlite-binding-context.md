---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-binding-engine]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - context
  - thread-safety
---

# llvmlite Context

LLVM context management for thread-safe module operations.

## Summary

The `Context` class provides a container for LLVM global state. Contexts enable thread-safe compilation by isolating state between threads.

## Key Concepts

### Context Creation

`Context()` — Create a new LLVM context
- Each context is independent and thread-safe
- Different contexts can be used in different threads concurrently

### Global Context

`get_global_context()` — Get the global singleton context
- Shared across all operations unless explicitly specified
- Not thread-safe for concurrent modifications

### Context Methods

- `parse_assembly(llvm_ir)` — Parse LLVM IR text into a module
- `parse_bitcode(bitcode)` — Parse LLVM bitcode into a module
- `create_module(name='')` — Create a new empty module

## Code Example

```python
from llvmlite import binding as llvm

# Create context
ctx = llvm.Context()

# Parse IR in context
llvm_ir = """
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
"""
module = ctx.parse_assembly(llvm_ir)

# Create module in context
new_module = ctx.create_module("example")
```

## Connections

- Used by [[llvmlite-binding-modules]] for module parsing
- Used by [[llvmlite-binding-engine]] for JIT compilation context
- Thread safety is critical for parallel compilation

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/context.html

Back to [[llvmlite-Binding-Layer-MoC]]
