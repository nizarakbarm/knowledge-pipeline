---
created: 2026-05-25
up:
  - "[[llvmlite-IR-Layer-MoC]]"
related:
  - "[[llvmlite-ir-types]]"
  - "[[llvmlite-ir-builder]]"
  - "[[llvmlite-binding-value-references]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - ir
  - values
  - ssa
---

# llvmlite IR Values

Values represent the data and code entities within an LLVM module. Every instruction, constant, global variable, and function argument is a value.

## Summary

The value hierarchy includes constants, global values, instructions, metadata, and basic blocks. Values support arithmetic, logical, comparison, and cast operations through the `_ConstOpMixin` base class.

## Key Concepts

### Base Value Class

> [!Note]
> **SSA Form:** LLVM IR uses Static Single Assignment — each value is assigned exactly once, creating a directed acyclic graph (DAG) of computations.

`Value` is the base class for all IR values. Every value has:
- `name` — SSA register name (e.g., `%sum`, `%i.1`)
- `type` — Type from the [[llvmlite-ir-types]] hierarchy

### Constants
`Constant(typ, constant)` — Literal values

> [!Note]
> **`Undefined`** — Special value representing LLVM's `undef` (uninitialized / "don't care"). The optimizer can choose any value, enabling maximum optimization flexibility.

`llvmlite.ir.Undefined` — Maps to LLVM's `undef` value
- IntType accepts Python int/bool
- Float/DoubleType accepts Python float
- Aggregate types accept sequences matching element types
- `Constant.literal_array(elements)` — Array constructor
- `Constant.literal_struct(elements, packed)` — Struct constructor
- `gep(indices)` — Calculate element address (pointer arithmetic)

> [!Note]
> **GEP (GetElementPtr)** computes memory addresses without loading data — it's how you index arrays, access struct fields, and traverse pointers in LLVM IR.

> [!Note]
> **Python type mapping:**
> - `IntType` → Python `int` or `bool`
> - `FloatType`/`DoubleType` → Python `float`
> - `ArrayType` → sequence of values or `bytearray`
> - All types accept `Undefined` (→ LLVM `undef`) and `None` (→ `zeroinitializer`)

**BlockAddress** — Constant representing address of a basic block
- `function` — Function containing the block
- `basic_block` — The target basic block

> [!Note]
> **BlockAddress** enables computed gotos and jump tables — useful for interpreter dispatch loops and state machines.

### Operations (_ConstOpMixin)

> [!Note]
> **_ConstOpMixin** is the base class for `Constant` and `GlobalValue`. It provides arithmetic, logical, comparison, and cast operations. Do not instantiate directly.

**Integer arithmetic** (returns Integer result):
- `add(other)` — Self + other
- `sub(other)` — Self - other
- `mul(other)` — Self × other
- `udiv(other)` — Unsigned division (treats operands as non-negative)
- `sdiv(other)` — Signed division (two's complement)
- `urem(other)` — Unsigned remainder
- `srem(other)` — Signed remainder
- `neg()` — Negate self

> [!Warning]
> **Signed vs Unsigned:** `udiv`/`urem` treat numbers as non-negative (0 to 2^n-1). `sdiv`/`srem` use two's complement (-2^(n-1) to 2^(n-1)-1). Using `udiv` on negative numbers produces incorrect results.

**Integer logical** (bitwise operations):
- `shl(other)` — Left shift by `other` bits
- `ashr(other)` — Arithmetic right shift (preserves sign bit, for signed values)
- `lshr(other)` — Logical right shift (fills with 0s, for unsigned values)
- `or_(other)` — Bitwise OR
- `and_(other)` — Bitwise AND
- `xor(other)` — Bitwise XOR

**Floating-point arithmetic**:
- `fadd(other)` — FP addition
- `fsub(other)` — FP subtraction
- `fmul(other)` — FP multiplication
- `fdiv(other)` — FP division
- `frem(other)` — FP remainder

**Comparisons** (returns i1 boolean):
- `icmp_signed(cmpop, other)` — Signed integer compare. `cmpop` ∈ `<`, `<=`, `==`, `!=`, `>=`, `>`
- `icmp_unsigned(cmpop, other)` — Unsigned integer compare
- `fcmp_ordered(cmpop, other)` — FP ordered compare (false if either operand is NaN)
- `fcmp_unordered(cmpop, other)` — FP unordered compare (true if either operand is NaN)

> [!Note]
> **NaN handling:** `fcmp_ordered` returns false for NaN comparisons, while `fcmp_unordered` returns true. Use `ordered` for strict equality checks, `unordered` for "is this possibly equal?" checks.

**Integer casts**:
- `trunc(typ)` — Truncate to smaller integer type (e.g., i32 → i8, drops high bits)
- `zext(typ)` — Zero-extend to larger integer type (pads with 0s, for unsigned)
- `sext(typ)` — Sign-extend to larger integer type (replicates sign bit, for signed)
- `bitcast(typ)` — Reinterpret bits as different pointer type (same size)

**Floating-point casts**:
- `fptrunc(typ)` — Truncate to smaller FP type (e.g., double → float, may lose precision)
- `fpext(typ)` — Extend to larger FP type (e.g., float → double)

**Integer ↔ Floating-point conversion**:
- `fptoui(typ)` — FP to unsigned integer (truncates toward zero)
- `uitofp(typ)` — Unsigned integer to FP
- `fptosi(typ)` — FP to signed integer (truncates toward zero)
- `sitofp(typ)` — Signed integer to FP

**Integer ↔ Pointer conversion**:
- `inttoptr(typ)` — Integer to pointer (e.g., for address arithmetic)
- `ptrtoint(typ)` — Pointer to integer (e.g., for hashing addresses)

### Global Values

> [!Note]
> **Linkage** controls symbol visibility across modules: `"external"` (visible everywhere), `"internal"` (module-private), `"private"` (file-local), `"linkonce"` (mergeable duplicates).

`GlobalValue` base class — All module-level symbols (variables, functions)
- `linkage` — Visibility: `"external"` (public), `"internal"` (module-private), `"private"` (file-local), `"linkonce"` (mergeable)
- `storage_class` — Windows DLL linkage: `"dllimport"` (import from DLL), `"dllexport"` (export to DLL)
- `section` — Place symbol in specific ELF/Mach-O section (e.g., `".rodata"` for read-only data)

**GlobalVariable(module, typ, name, addrspace=0)** — Module-level variable

> [!Note]
> **Global variables** live outside functions and persist for the program's lifetime. The returned value is a pointer — use `load()`/`store()` to access contents.

- `initializer` — Initial value (Constant or None for uninitialized)
- `global_constant` — If True, treated as immutable (like C `const`)
- `align` — Override default alignment (e.g., 16 for SIMD data)
- `unnamed_addr` — Enable deduplication (merge identical constants to save memory)
- `set_metadata(name, node)` — Attach debug info metadata (e.g., variable name, source location)

**Function(module, typ, name)** — Callable subroutine

> [!Note]
> **Declaration vs Definition:** Declaration = external/forward reference (no body). Definition = full implementation (has basic blocks). Both have the same type signature.

- `append_basic_block(name)` — Add control flow block
- `insert_basic_block(before, name)` — Insert block before existing one
- `args` — Tuple of Argument instances
- `attributes` — Function attributes (e.g., "alwaysinline", "noreturn")
- `calling_convention` — ABI convention (e.g., "fastcc", "cold")
- `is_declaration` — True if no basic blocks (external function)
- `set_metadata(name, node)` — Attach debug info (e.g., function name, source file)

### Arguments
`Argument` — Function parameter with type and optional attributes

> [!Note]
> **Argument attributes** control calling convention behavior: `"zeroext"` (zero-extend), `"signext"` (sign-extend), `"byval"` (pass by value), `"sret"` (struct return pointer).

- `add_attribute(attr)` — Add parameter attribute

### Basic Blocks

> [!Note]
> **Basic block = straight-line code.** A sequence of instructions with a single entry point and a single exit (terminator instruction). The last instruction must be a branch, return, or unreachable.

`Block` — Control flow node containing sequential instructions
- `function` — Parent function reference
- `is_terminated` — Whether last instruction is a terminator (branch/return)
- `terminator` — The control flow instruction ending this block
- `replace(old, new)` — Replace `old` instruction with `new` and automatically patch all references throughout the entire function

### Instructions

> [!Note]
> **Instructions = computation nodes.** Every instruction produces a value (except terminators) and can be used as an operand in other instructions. Do not instantiate directly — use `IRBuilder` methods.

`Instruction` base class:
- `set_metadata(name, node)` — Attach debug info to this instruction
- `replace_usage(old, new)` — Update all references to use a different operand
- `function`, `module` — Parent references for easy traversal

Special instruction types:
- `PredictableInstr` — Branch/switch with probability hints for optimization
- `SwitchInstr` — Multi-way branch with `add_case(value, block)`
- `IndirectBranch` — Jump through function pointer (computed goto)
- `PhiInstr` — Merge values from multiple predecessor blocks (SSA join point)
- `LandingPad` — Exception handler entry point with catch/filter clauses

### Metadata

> [!Note]
> **Metadata hierarchy:** `MetaDataString` (raw text) → `MDValue` (node) → `NamedMetaData` (collection). `DIValue` stores DWARF debug descriptors. `DIToken` represents enum values (e.g., `DW_LANG_Python`).

- `MetaDataString(module, value)` — Raw string for debug info
- `MDValue` — Metadata node (created via `Module.add_metadata()`)
- `DIValue` — Debug info descriptor (created via `Module.add_debug_info()`)
- `DIToken(value)` — Enumeration token (e.g., `'DW_LANG_Python'`)
- `NamedMetaData` — Named collection (e.g., "llvm.ident")

### Exception Handling

> [!Note]
> **Landing pads** catch C++ exceptions. `CatchClause` compares exception type. `FilterClause` checks if exception type is in an allowed list.

- `CatchClause(value)` — Compare exception typeinfo
- `FilterClause(value)` — Check exception against type list

## Code Example

```python
from llvmlite import ir

module = ir.Module(name="example")
int32 = ir.IntType(32)

# Global variable
global_var = ir.GlobalVariable(module, int32, "counter")
global_var.initializer = int32(0)

# Function
fnty = ir.FunctionType(int32, (int32, int32))
func = ir.Function(module, fnty, "add")
block = func.append_basic_block("entry")
builder = ir.IRBuilder(block)
result = builder.add(func.args[0], func.args[1])
builder.ret(result)
```

## Connections

- All values have types from [[llvmlite-ir-types]]
- Instructions are built using [[llvmlite-ir-builder]]
- Global values live in [[llvmlite-ir-modules]]
- Value references in binding layer: [[llvmlite-binding-value-references]]

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/ir/values.html

Back to [[llvmlite-IR-Layer-MoC]]
