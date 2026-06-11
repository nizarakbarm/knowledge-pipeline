---
created: 2026-05-25
up:
  - "[[LLVM MOC]]"
related: []
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - moc
  - compiler
  - python
---

# llvmlite User Guide v0.46.0

A Map of Content for llvmlite v0.46.0 — Python bindings for LLVM IR and JIT compilation.

## Architecture Overview

![[llvmlite-architecture.canvas]]

*Interactive canvas: zoom, pan, and click nodes to navigate. The canvas provides a zoomable visual map of all llvmlite components with color-coded layers and cross-layer connections.*

## IR Layer — llvmlite.ir

The IR layer provides pure Python classes to build LLVM intermediate representation without calling into LLVM directly.

- [[llvmlite-ir-types]] — Atomic, pointer, aggregate, and function types
- [[llvmlite-ir-values]] — Constants, instructions, global values, metadata
- [[llvmlite-ir-modules]] — Module structure, functions, global variables
- [[llvmlite-ir-builder]] — IRBuilder for constructing instructions
- [[llvmlite-ir-examples]] — Example: defining a simple function

## Binding Layer — llvmlite.binding

The binding layer provides Python wrappers around LLVM C++ API functionality.

- [[llvmlite-binding-init-ffi]] — Initialization and finalization
- [[llvmlite-binding-dynamic-libraries]] — Dynamic libraries and symbols
- [[llvmlite-binding-target]] — Target information and target data
- [[llvmlite-binding-context]] — LLVM context management
- [[llvmlite-binding-modules]] — Module operations and verification
- [[llvmlite-binding-value-references]] — Value references
- [[llvmlite-binding-type-references]] — Type references
- [[llvmlite-binding-engine]] — Execution engine and JIT compilation
- [[llvmlite-binding-object-file]] — Object file handling
- [[llvmlite-binding-passmanager]] — Optimization passes
- [[llvmlite-binding-analysis]] — Analysis utilities
- [[llvmlite-binding-pass-timings]] — Pass timing information
- [[llvmlite-binding-misc]] — Miscellaneous utilities
- [[llvmlite-binding-examples]] — Example: compiling a simple function

## Notices

- [[llvmlite-deprecation]] — Deprecation notices (LLVM initialization, typed pointers)
- [[llvmlite-llvm20]] — LLVM 20 compatibility notes (llvmlite 0.45+)

## Source

- Documentation: https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/index.html
- Version: v0.46.0

## Related Topics

- [[LLVM MOC]] — Parent: LLVM compiler infrastructure
- [[LLVM Modular Compiler Infrastructure]] — LLVM core concepts
- [[eBPF MOC]] — eBPF uses LLVM for compilation

Back to [[LLVM MOC]]
