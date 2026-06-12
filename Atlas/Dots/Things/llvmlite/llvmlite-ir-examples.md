---
created: 2026-05-25
up:
  - "[[llvmlite-IR-Layer-MoC]]"
related:
  - "[[llvmlite-ir-types]]"
  - "[[llvmlite-ir-values]]"
  - "[[llvmlite-ir-modules]]"
  - "[[llvmlite-ir-builder]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - ir
  - examples
  - tutorial
---

# llvmlite IR Examples

Complete example demonstrating how to define a simple function using the llvmlite IR layer.

## Summary

This example shows the full workflow: creating a module, defining types, building a function with basic blocks, adding instructions, and serializing to LLVM IR text.

## Example: Defining a Simple Function

```python
from llvmlite import ir

# Create a module
module = ir.Module(name="example")

# Define types
int32 = ir.IntType(32)
double = ir.DoubleType()

# Define function: int32 sum(double, int32*)
fnty = ir.FunctionType(int32, (double, int32.as_pointer()))
func = ir.Function(module, fnty, "sum")

# Name the arguments
func.args[0].name = "x"
func.args[1].name = "y_ptr"

# Create basic block
block = func.append_basic_block("entry")
builder = ir.IRBuilder(block)

# Load value from pointer
y = builder.load(func.args[1], name="y")

# Convert double to int32
x_int = builder.fptosi(func.args[0], int32, name="x_int")

# Add
result = builder.add(x_int, y, name="result")

# Return
builder.ret(result)

# Print the generated IR
print(module)
```

### Generated LLVM IR

```llvm
; ModuleID = "example"
target triple = "unknown-unknown-unknown"

define i32 @sum(double %x, i32* %y_ptr) {
entry:
  %y = load i32, i32* %y_ptr
  %x_int = fptosi double %x to i32
  %result = add i32 %x_int, %y
  ret i32 %result
}
```

## Key Steps

1. **Create module** — `ir.Module(name="example")`
2. **Define types** — `ir.IntType(32)`, `ir.DoubleType()`
3. **Create function** — `ir.Function(module, fnty, "sum")`
4. **Name arguments** — `func.args[0].name = "x"`
5. **Add basic block** — `func.append_basic_block("entry")`
6. **Create builder** — `ir.IRBuilder(block)`
7. **Build instructions** — `builder.load()`, `builder.fptosi()`, `builder.add()`
8. **Return** — `builder.ret(result)`
9. **Serialize** — `print(module)`

## Connections

- Uses [[llvmlite-ir-types]] for type definitions
- Uses [[llvmlite-ir-values]] for constants and arguments
- Uses [[llvmlite-ir-modules]] for module container
- Uses [[llvmlite-ir-builder]] for instruction construction
- IR output can be passed to [[llvmlite-binding-modules]] for compilation

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/ir/examples.html

Back to [[llvmlite-IR-Layer-MoC]]
