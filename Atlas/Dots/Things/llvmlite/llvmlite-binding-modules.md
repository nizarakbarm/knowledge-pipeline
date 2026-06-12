---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-ir-modules]]"
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-passmanager]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - modules
  - parsing
---

# llvmlite Binding Modules

Module parsing, verification, and operations for the LLVM binding layer.

## Summary

Provides functions to parse LLVM IR text and bitcode into module objects, verify module correctness, and link modules together.

## Key Concepts

### Parsing

`parse_assembly(llvm_ir)` — Parse LLVM IR text string
- Returns Module object
- Raises RuntimeError on parse failure

`parse_bitcode(bitcode)` — Parse LLVM bitcode (bytes)
- Returns Module object
- `bitcode` is bytes object containing LLVM bitcode

### Module Verification

`module.verify()` — Verify module correctness
- Returns None on success
- Raises RuntimeError with diagnostic message on failure

### Module Properties

- `module.name` — Module name
- `module.data_layout` — Data layout string
- `module.triple` — Target triple string
- `module.triple = 'x86_64-unknown-linux-gnu'` — Set target triple

### Linking

`link_modules(dst, src)` — Link source module into destination
- `dst` — Destination module (modified in place)
- `src` — Source module (consumed/destroyed)

### Serialization

- `module.as_bitcode()` — Serialize to bitcode (bytes)
- `str(module)` — Serialize to LLVM IR text

## Code Example

```python
from llvmlite import binding as llvm

# Parse IR text
llvm_ir = """
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
"""
module = llvm.parse_assembly(llvm_ir)

# Verify
module.verify()

# Link another module
module2 = llvm.parse_assembly("define i32 @sub(i32 %a, i32 %b) { ... }")
llvm.link_modules(module, module2)

# Get bitcode
bitcode = module.as_bitcode()

# Print IR
print(module)
```

## Connections

- Parses IR from [[llvmlite-ir-builder]] output
- Used by [[llvmlite-binding-engine]] for JIT compilation
- Verification prerequisite for [[llvmlite-binding-passmanager]]
- Target triple comes from [[llvmlite-binding-target]]

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/modules.html

Back to [[llvmlite-Binding-Layer-MoC]]
