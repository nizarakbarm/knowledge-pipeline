---
created: 2026-05-25
up:
  - "[[llvmlite-IR-Layer-MoC]]"
related:
  - "[[llvmlite-ir-values]]"
  - "[[llvmlite-ir-builder]]"
  - "[[llvmlite-binding-modules]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - ir
  - modules
  - compiler
---

# llvmlite IR Modules

Modules are the top-level containers for LLVM IR. A module holds functions, global variables, and metadata.

## Summary

The `llvmlite.ir.Module` class represents a complete LLVM module. It provides methods to add and manage global values, metadata, and debug information.

## Key Concepts

### Module Creation
`Module(name="")` — Create a new compilation unit

> [!Note]
> **Module = compilation unit.** A module is a self-contained IR file that can be compiled, optimized, and linked independently.

- `name` — Optional module identifier (for debugging)
- `data_layout` — Target memory layout string (endianness, pointer size, alignment)
- `triple` — Target architecture string (e.g., "x86_64-unknown-linux-gnu")

### Global Values
- `add_global(typ, name)` — Add global variable to module's symbol table
- `get_global(name)` — Look up global by name (raises KeyError if missing)
- `global_values` — Iterable of all global values (variables and functions)
- `get_unique_name(name)` — Auto-generates unique name if collision detected

### Functions
- `add_function(fnty, name)` — Register function signature (declaration) or full implementation
- `get_global(name)` — Retrieve function by name (functions are global values)
- `functions` — List of all Function instances in module

> [!Note]
> **Declaration vs Definition:** A function with no basic blocks is a declaration (external/forward reference). With basic blocks, it's a definition (implementation).

### Metadata

> [!Note]
> **Metadata** stores debug information (source line numbers, variable names) and optimization hints. It does not affect program execution but enables source-level debugging.

- `add_metadata(values)` — Create unnamed metadata node (reused if identical)
- `add_named_metadata(name)` — Create named metadata container (e.g., "llvm.ident")
- `get_named_metadata(name)` — Retrieve named metadata (raises `KeyError` if missing)
- `add_debug_info(kind, operands)` — Add DWARF debug info (e.g., DIFile, DICompileUnit)

### Module Properties
- `data_layout` — Target data layout string
- `triple` — Target triple (e.g., "x86_64-unknown-linux-gnu")

### Serialization

> [!Note]
> **IR text output** can be saved to `.ll` files, passed to `llvm.parse_assembly()` in the binding layer, or compiled with `llc` / `opt` command-line tools.

- `__str__()` — Convert to LLVM IR text format (human-readable assembly)

## Code Example

```python
from llvmlite import ir

# Create module
module = ir.Module(name="example")
module.triple = "x86_64-unknown-linux-gnu"

# Define function type and add to module
int32 = ir.IntType(32)
fnty = ir.FunctionType(int32, (int32, int32))
func = ir.Function(module, fnty, "add")

# Add global variable
global_var = ir.GlobalVariable(module, int32, "counter")
global_var.initializer = int32(0)

# Print IR
print(module)
```

## Connections

- Contains [[llvmlite-ir-values]] (functions, globals, metadata)
- Functions contain basic blocks built with [[llvmlite-ir-builder]]
- Module IR text is parsed by [[llvmlite-binding-modules]]
- Target data layout comes from [[llvmlite-binding-target]]

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/ir/modules.html

Back to [[llvmlite-IR-Layer-MoC]]
