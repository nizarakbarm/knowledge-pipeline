---
created: 2026-05-25
up:
  - "[[llvmlite-IR-Layer-MoC]]"
related:
  - "[[llvmlite-ir-values]]"
  - "[[llvmlite-ir-modules]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - ir
  - builder
  - instructions
---

# llvmlite IR Builder

The `llvmlite.ir.IRBuilder` class provides helper methods to construct LLVM instructions within basic blocks.

## Summary

IRBuilder simplifies instruction creation by automatically appending instructions to the current basic block and tracking the insertion point.

## Key Concepts

### Builder Creation
`IRBuilder(block)` — Create builder positioned at end of block
- `position_at_end(block)` — Move to end of block
- `position_before(instr)` — Move before instruction

### Arithmetic Instructions
- `add(a, b, name='')` — Integer addition
- `sub(a, b, name='')` — Integer subtraction
- `mul(a, b, name='')` — Integer multiplication
- `udiv(a, b, name='')` — Unsigned division
- `sdiv(a, b, name='')` — Signed division
- `urem(a, b, name='')` — Unsigned remainder
- `srem(a, b, name='')` — Signed remainder

### Floating-Point Instructions
- `fadd(a, b, name='')` — FP addition
- `fsub(a, b, name='')` — FP subtraction
- `fmul(a, b, name='')` — FP multiplication
- `fdiv(a, b, name='')` — FP division
- `frem(a, b, name='')` — FP remainder

### Logical Instructions
- `shl(a, b, name='')` — Left shift
- `lshr(a, b, name='')` — Logical right shift
- `ashr(a, b, name='')` — Arithmetic right shift
- `and_(a, b, name='')` — Bitwise AND
- `or_(a, b, name='')` — Bitwise OR
- `xor(a, b, name='')` — Bitwise XOR

### Comparison Instructions
- `icmp_signed(cmpop, a, b, name='')` — Signed integer compare
- `icmp_unsigned(cmpop, a, b, name='')` — Unsigned integer compare
- `fcmp_ordered(cmpop, a, b, name='')` — Ordered FP compare
- `fcmp_unordered(cmpop, a, b, name='')` — Unordered FP compare

### Cast Instructions
- `trunc(val, typ, name='')` — Truncate integer
- `zext(val, typ, name='')` — Zero-extend integer
- `sext(val, typ, name='')` — Sign-extend integer
- `fptrunc(val, typ, name='')` — Truncate FP
- `fpext(val, typ, name='')` — Extend FP
- `fptoui(val, typ, name='')` — FP to unsigned int
- `fptosi(val, typ, name='')` — FP to signed int
- `uitofp(val, typ, name='')` — Unsigned int to FP
- `sitofp(val, typ, name='')` — Signed int to FP
- `inttoptr(val, typ, name='')` — Integer to pointer
- `ptrtoint(val, typ, name='')` — Pointer to integer
- `bitcast(val, typ, name='')` — Bitwise type cast

### Memory Instructions
- `alloca(typ, size=None, name='')` — Stack allocation
- `load(ptr, name='', align=None)` — Load from pointer
- `store(val, ptr, align=None)` — Store to pointer
- `gep(ptr, indices, inbounds=False, name='')` — Get element pointer

### Terminator Instructions
- `ret(value=None)` — Return
- `ret_void()` — Void return
- `branch(target)` — Unconditional branch
- `cbranch(cond, trueblk, falseblk)` — Conditional branch
- `switch(value, default)` — Switch statement
- `indirect_branch(ptr, possible_dests)` — Indirect branch
- `unreachable()` — Unreachable marker

### Function Call
- `call(fn, args, name='', cconv=None, tail=False, fastmath=())` — Function call

### PHI and Exception Handling
- `phi(typ, name='')` — PHI node
- `landingpad(typ, cleanup=False, name='')` — Landing pad
- `resume(typ, val)` — Resume exception

### Other
- `select(cond, trueval, falseval, name='')` — Select based on condition
- `extract_value(agg, idx, name='')` — Extract value from aggregate
- `insert_value(agg, val, idx, name='')` — Insert value into aggregate

## Code Example

```python
from llvmlite import ir

module = ir.Module()
int32 = ir.IntType(32)

# Create function
fnty = ir.FunctionType(int32, (int32, int32))
func = ir.Function(module, fnty, "add")

# Build function body
block = func.append_basic_block("entry")
builder = ir.IRBuilder(block)

# Allocate local variable
local = builder.alloca(int32, name="local")

# Add arguments
result = builder.add(func.args[0], func.args[1], name="sum")

# Store and load
builder.store(result, local)
loaded = builder.load(local, name="loaded")

# Return
builder.ret(loaded)
```

## Connections

- Builds [[llvmlite-ir-values]] instructions
- Operates within [[llvmlite-ir-modules]] functions
- Instructions use types from [[llvmlite-ir-types]]

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/ir/ir-builder.html

Back to [[llvmlite-IR-Layer-MoC]]
