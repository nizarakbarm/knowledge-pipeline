---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-ir-types]]"
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-binding-target]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - types
  - references
---

# llvmlite Type References

Type reference management for LLVM binding layer operations.

## Summary

Provides access to LLVM type objects within parsed modules, enabling type inspection and validation.

## Key Concepts

### Type Objects

Types in parsed IR are represented as opaque handles. The binding layer provides:
- Type enumeration
- Type property queries
- Type comparison

### Common Types

`Type.int(width)` — Integer type
- `width` — Bit width (e.g., 32 for i32)

`Type.float()` — Float type
`Type.double()` — Double type
`Type.void()` — Void type
`Type.pointer(pointee, addrspace=0)` — Pointer type

### Type Properties

- `type.is_pointer` — Whether type is pointer
- `type.is_function` — Whether type is function
- `type.is_struct` — Whether type is struct
- `type.element_type` — Element type (for pointer/array/vector)
- `type.return_type` — Return type (for function)
- `type.argument_types` — Argument types (for function)

### Type Comparison

Types can be compared with `==` operator

## Code Example

```python
from llvmlite import binding as llvm

module = llvm.parse_assembly("""
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
""")

# Get function type
func = module.get_function("add")
fnty = func.type.element_type  # Function type
print(f"Return: {fnty.return_type}")
for i, argty in enumerate(fnty.argument_types):
    print(f"Arg {i}: {argty}")
```

## Connections

- Maps to [[llvmlite-ir-types]] hierarchy
- Used by [[llvmlite-binding-engine]] for type checking
- Used by [[llvmlite-binding-target]] for ABI queries

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/type-references.html

Back to [[llvmlite-Binding-Layer-MoC]]
