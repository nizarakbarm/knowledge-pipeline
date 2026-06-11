---
created: 2026-05-25
up:
  - "[[llvmlite-User-Guide-MoC]]"
related: []
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - moc
  - compiler
---

# llvmlite Binding Layer

The `llvmlite.binding` module provides Python wrappers around LLVM C++ API functionality. Only a subset of the LLVM API is mirrored — those parts proven useful for implementing Numba's JIT compiler.

## Overview

The binding layer enables direct interaction with the LLVM library for:
- Module parsing and verification
- Target machine configuration
- JIT compilation and execution
- Optimization passes
- Object file generation

## Components

### Setup and Configuration
- [[llvmlite-binding-init-ffi]] — LLVM initialization and finalization
- [[llvmlite-binding-dynamic-libraries]] — Dynamic library loading and symbol resolution
- [[llvmlite-binding-target]] — Target triple, target machine, target data
- [[llvmlite-binding-context]] — LLVM context management

### Module and Value Operations
- [[llvmlite-binding-modules]] — Module parsing, verification, linking
- [[llvmlite-binding-value-references]] — Value references and uses
- [[llvmlite-binding-type-references]] — Type references and mappings

### Compilation and Execution
- [[llvmlite-binding-engine]] — Execution engine and JIT compilation
- [[llvmlite-binding-object-file]] — Object file emission and handling

### Optimization and Analysis
- [[llvmlite-binding-passmanager]] — Optimization pass management
- [[llvmlite-binding-analysis]] — Analysis utilities (branch probability, etc.)
- [[llvmlite-binding-pass-timings]] — Pass execution timing information

### Utilities
- [[llvmlite-binding-misc]] — Miscellaneous utilities
- [[llvmlite-binding-examples]] — Complete example: compiling a simple function

## Key Concepts

### C++ API Mirroring
The binding layer closely mirrors LLVM C++ API concepts. Functions and classes map directly to their LLVM counterparts.

### JIT Compilation Workflow
1. Parse IR module using [[llvmlite-binding-modules]]
2. Create execution engine via [[llvmlite-binding-engine]]
3. Run optimization passes through [[llvmlite-binding-passmanager]]
4. Generate machine code or object files

## Cross-Layer Connections

- IR text from [[llvmlite-ir-builder]] is parsed here
- Types from [[llvmlite-ir-types]] map to [[llvmlite-binding-type-references]]
- Values from [[llvmlite-ir-values]] map to [[llvmlite-binding-value-references]]
- [[llvmlite-binding-target]] provides target data for type sizing

Back to [[llvmlite-User-Guide-MoC]]
