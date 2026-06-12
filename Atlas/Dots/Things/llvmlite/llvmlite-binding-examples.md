---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-init-ffi]]"
  - "[[llvmlite-binding-target]]"
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-passmanager]]"
  - "[[llvmlite-ir-examples]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - examples
  - tutorial
---

# llvmlite Binding Examples

Complete example demonstrating JIT compilation of LLVM IR using the llvmlite binding layer.

## Summary

This example shows the full workflow: parsing IR, creating a target machine, setting up an execution engine, running optimization passes, and calling the compiled function.

## Example: Compiling a Simple Function

```python
import ctypes
from llvmlite import binding as llvm

# LLVM IR for a simple function
llvm_ir = """
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
"""

# Parse IR
module = llvm.parse_assembly(llvm_ir)
module.verify()

# Get target
target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine(opt_level=2)

# Create execution engine
engine = llvm.create_mcjit_compiler(module, target_machine)

# Run optimization passes
pm = llvm.create_pass_manager()
pm.add_instruction_combining_pass()
pm.add_reassociate_pass()
pm.add_gvn_pass()
pm.add_cfg_simplification_pass()
pm.run(module)

# Finalize
engine.finalize_object()

# Get function address and call
addr = engine.get_function_address("add")
cfunc = ctypes.CFUNCTYPE(
    ctypes.c_int32, ctypes.c_int32, ctypes.c_int32
)(addr)

print(f"5 + 3 = {cfunc(5, 3)}")
```

## Key Steps

1. **Parse IR** — `llvm.parse_assembly(llvm_ir)`
2. **Verify** — `module.verify()`
3. **Get target** — `llvm.Target.from_default_triple()`
4. **Create target machine** — `target.create_target_machine()`
5. **Create engine** — `llvm.create_mcjit_compiler(module, target_machine)`
6. **Optimize** — Run passes via pass manager
7. **Finalize** — `engine.finalize_object()`
8. **Get address** — `engine.get_function_address("add")`
9. **Call** — Use ctypes to call compiled function

## Connections

- Uses [[llvmlite-binding-modules]] for IR parsing
- Uses [[llvmlite-binding-target]] for target machine
- Uses [[llvmlite-binding-engine]] for JIT compilation
- Uses [[llvmlite-binding-passmanager]] for optimization
- IR can come from [[llvmlite-ir-builder]] output

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/examples.html

Back to [[llvmlite-Binding-Layer-MoC]]
