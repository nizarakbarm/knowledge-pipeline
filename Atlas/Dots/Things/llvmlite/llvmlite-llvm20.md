---
created: 2026-05-25
up:
  - "[[llvmlite-User-Guide-MoC]]"
related:
  - "[[llvmlite-deprecation]]"
  - "[[LLVM 2026 Release Roadmap]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - llvm-20
  - compatibility
---

# llvmlite LLVM 20 Compatibility

Compatibility notes for LLVM 20 and llvmlite 0.45+.

## Summary

Documents specific changes and known issues when using llvmlite with LLVM 20.

## LLVM 20 Changes

### Build System Update
LLVM 20 introduced changes to the CMake build system that affect how llvmlite compiles against LLVM.

### Specific Changes

1. **Opaque Pointers Mandatory**
   - Typed pointers fully removed
   - All pointer operations use opaque pointers
   - See [[llvmlite-deprecation]] for migration guide

2. **API Changes**
   - Some LLVM C++ APIs changed signatures
   - llvmlite 0.45+ updated to match

3. **New Pass Manager**
   - Legacy pass manager deprecated
   - New pass manager (PassBuilder) recommended

### Known Issues

**Materialization Issues**
- Some JIT compilation scenarios may encounter materialization errors
- Workaround: Use object caching or pre-compiled objects

**Platform-Specific Issues**
- macOS: Code signing requirements may affect JIT
- Windows: SEH handling changes

## Migration Guide

### From llvmlite 0.44 to 0.45+

1. **Update pointer code**
   ```python
   # Old
   ptr = ir.PointerType(int32)
   
   # New
   ptr = ir.PointerType()
   ```

2. **Check pass manager usage**
   ```python
   # Old (still works but deprecated)
   pm = llvm.create_pass_manager()
   
   # New (recommended)
   # Use PassBuilder API when available
   ```

3. **Verify target triple**
   - LLVM 20 may have different default triples
   - Explicitly set target triple if needed

## Version Matrix

| llvmlite | LLVM | Status |
|----------|------|--------|
| 0.44.x | 19.x | Current stable |
| 0.45+ | 20.x | LLVM 20 support |
| 0.46+ | 20.x | Opaque pointers only |

## Connections

- [[llvmlite-deprecation]] for detailed migration guide
- [[LLVM 2026 Release Roadmap]] for LLVM release schedule
- [[llvmlite-binding-init-ffi]] for initialization changes

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/llvm20.html

Back to [[llvmlite-User-Guide-MoC]]
