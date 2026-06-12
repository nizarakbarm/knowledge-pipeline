---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-ir-values]]"
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-binding-engine]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - values
  - references
---

# llvmlite Value References

Value reference management for LLVM binding layer operations.

## Summary

Provides access to LLVM value objects within modules, enabling inspection and manipulation of values in parsed IR.

## Key Concepts

### Value References

Values in parsed modules are represented as opaque handles. The binding layer provides functions to:
- Enumerate values in a module
- Query value properties (name, type)
- Replace uses of values

### Global Value Access

`module.global_values` — Iterable of all global values
- Functions, global variables, aliases

`function.arguments` — Iterable of function arguments

### Value Properties

- `value.name` — Value name (string)
- `value.type` — Value type (Type object)
- `value.is_global` — Whether value is global

### Use Iteration

`value.uses` — Iterable of uses of this value
- Each use has `user` (instruction) and `operand_no`

## Code Example

```python
from llvmlite import binding as llvm

module = llvm.parse_assembly("""
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
""")

# Iterate global values
for gv in module.global_values:
    print(f"Name: {gv.name}, Type: {gv.type}")

# Get function
func = module.get_function("add")
for arg in func.arguments:
    print(f"Arg: {arg.name}, Type: {arg.type}")
```

## Connections

- Maps to [[llvmlite-ir-values]] concepts
- Used by [[llvmlite-binding-engine]] for function lookup
- Used by [[llvmlite-binding-modules]] for module inspection

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/value-references.html

Back to [[llvmlite-Binding-Layer-MoC]]
