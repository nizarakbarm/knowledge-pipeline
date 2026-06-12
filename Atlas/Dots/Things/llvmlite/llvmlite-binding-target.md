---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-ir-types]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - target
  - codegen
---

# llvmlite Target Information

Target triple, target machine, and target data management for LLVM code generation.

## Summary

Provides classes to query target architecture information and configure code generation parameters.

## Key Concepts

### Target Triple

`Target.from_default_triple()` — Get target for host platform
`Target.from_triple(triple)` — Get target for specific triple

Target triple format: `arch-vendor-os-environment`
Examples:
- `x86_64-unknown-linux-gnu`
- `x86_64-apple-darwin`
- `aarch64-unknown-linux-gnu`

### Target Machine

`Target.create_target_machine(triple, cpu, features, opt_level, reloc, code_model)`
- `triple` — Target triple string
- `cpu` — CPU name (e.g., "generic", "skylake")
- `features` — CPU features string (e.g., "+avx2")
- `opt_level` — Optimization level (0-3)
- `reloc` — Relocation model (default, static, pic, dynamic_no_pic)
- `code_model` — Code model (default, small, kernel, medium, large)

Methods:
- `emit_object(module)` — Compile module to object code (bytes)
- `emit_assembly(module)` — Compile module to assembly text
- `add_analysis_passes(pass_manager)` — Add target analysis passes

### Target Data

`TargetData(str_repr)` — Target data layout
- `str_repr` — Data layout string (e.g., "e-m:e-p270:32:32-p271:32:32...")

Methods:
- `get_abi_size(type)` — Get ABI size of type in bytes
- `get_abi_alignment(type)` — Get ABI alignment of type in bytes
- `get_pointee_abi_size(type)` — Get size of pointed-to type

## Code Example

```python
from llvmlite import binding as llvm

# Get target for host
target = llvm.Target.from_default_triple()

# Create target machine
target_machine = target.create_target_machine(
    triple="x86_64-unknown-linux-gnu",
    cpu="generic",
    features="",
    opt_level=2,
    reloc="default",
    code_model="default"
)

# Get target data
data_layout = target_machine.get_target_data()

# Query type sizes
int32_size = data_layout.get_abi_size(llvm.IntType(32))
print(f"int32 size: {int32_size} bytes")
```

## Connections

- Used by [[llvmlite-binding-engine]] for JIT compilation
- Used by [[llvmlite-binding-modules]] for module verification
- Target data provides sizes for [[llvmlite-ir-types]] ABI queries

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/target-information.html

Back to [[llvmlite-Binding-Layer-MoC]]
