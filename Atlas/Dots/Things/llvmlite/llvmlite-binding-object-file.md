---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-target]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - object-file
  - codegen
---

# llvmlite Object File

Object file handling and emission for LLVM compiled code.

## Summary

Provides functionality to emit and inspect object files (ELF, Mach-O, COFF) from compiled LLVM modules.

## Key Concepts

### Object File Emission

`target_machine.emit_object(module)` — Compile module to object file
- Returns bytes containing object file
- Format determined by target triple (ELF/Mach-O/COFF)

### Object File Inspection

`ObjectFileRef(data)` — Parse object file bytes
- `data` — Object file bytes

Methods:
- `sections` — Iterable of sections
- `symbols` — Iterable of symbols

### Section Properties

- `section.name` — Section name
- `section.size` — Section size
- `section.address` — Section address
- `section.data` — Section contents (bytes)

### Symbol Properties

- `symbol.name` — Symbol name
- `symbol.address` — Symbol address
- `symbol.size` — Symbol size

## Code Example

```python
from llvmlite import binding as llvm

# Compile to object file
target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine()

module = llvm.parse_assembly("""
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
""")

# Emit object file
obj_bytes = target_machine.emit_object(module)

# Save to file
with open("output.o", "wb") as f:
    f.write(obj_bytes)

# Inspect object file
obj = llvm.ObjectFileRef(obj_bytes)
for section in obj.sections:
    print(f"Section: {section.name}, Size: {section.size}")
    for symbol in section.symbols:
        print(f"  Symbol: {symbol.name}")
```

## Connections

- Emitted by [[llvmlite-binding-target]] target machine
- Used by [[llvmlite-binding-engine]] for JIT compilation
- Complements [[llvmlite-binding-dynamic-libraries]] for linking

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/object-file.html

Back to [[llvmlite-Binding-Layer-MoC]]
