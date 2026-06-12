---
created: 2026-05-25
up:
  - "[[llvmlite-User-Guide-MoC]]"
related:
  - "[[llvmlite-binding-init-ffi]]"
  - "[[llvmlite-ir-types]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - deprecation
  - migration
---

# llvmlite Deprecation Notices

Deprecation notices for features being removed in future llvmlite versions.

## Summary

Documents deprecated features and provides migration guidance for code using obsolete APIs.

## Deprecation of LLVM Initialization

Manual initialization functions are deprecated in favor of automatic initialization.

### Deprecated
```python
from llvmlite import binding as llvm
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
```

### Modern Usage
```python
# No manual initialization needed
# Components initialize automatically on first use
from llvmlite import binding as llvm

# Direct usage
module = llvm.parse_assembly(ir_text)
```

## Deprecation of Typed Pointers

Typed pointers are being phased out in favor of opaque pointers.

### Background
LLVM has transitioned from typed pointers to opaque pointers. Typed pointers explicitly specify the pointee type, while opaque pointers do not.

### Typed Pointer (Deprecated)
```python
from llvmlite import ir
int32 = ir.IntType(32)
ptr = ir.PointerType(int32)  # Typed: knows it points to i32
```

### Opaque Pointer (Modern)
```python
from llvmlite import ir
ptr = ir.PointerType()  # Opaque: no pointee type
```

### Migration Options

**Option 1: Environment Variable**
```bash
export LLVMLITE_ENABLE_IR_LAYER_TYPED_POINTERS=0
```

**Option 2: Python Attribute**
```python
import llvmlite
llvmlite.ir_layer_typed_pointers_enabled = False
```

### Impact
- Affects all pointer type creation in IR layer
- Requires updates to code using `PointerType(pointee)`
- May require explicit type information in GEP instructions

## Timeline

- Typed pointers: Deprecated in llvmlite 0.44, removal planned for 0.46+
- Manual initialization: Soft deprecation, automatic initialization preferred

## Connections

- [[llvmlite-binding-init-ffi]] for initialization details
- [[llvmlite-ir-types]] for pointer type construction
- [[llvmlite-llvm20]] for LLVM 20 specific changes

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/deprecation.html

Back to [[llvmlite-User-Guide-MoC]]
