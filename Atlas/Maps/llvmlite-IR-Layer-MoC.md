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
  - ir
  - moc
  - compiler
---

# llvmlite IR Layer

The `llvmlite.ir` module contains pure Python classes for building LLVM intermediate representation (IR) of native functions. These APIs construct a Python representation of the IR without calling into LLVM directly.

## Overview

The IR layer provides a Pythonic way to construct LLVM IR, similar to LLVM's C++ APIs but entirely in Python. To use this module, familiarity with the LLVM Language Reference is recommended.

## Components

- [[llvmlite-ir-types]] — Type system (atomic, pointer, aggregate, function types)
- [[llvmlite-ir-values]] — Values (constants, arguments, basic blocks, instructions)
- [[llvmlite-ir-modules]] — Modules (functions, global variables, metadata)
- [[llvmlite-ir-builder]] — IRBuilder (instruction construction helpers)
- [[llvmlite-ir-examples]] — Complete example: defining a simple function

## Key Concepts

### Pure Python IR Construction
Unlike the binding layer, `llvmlite.ir` never calls into LLVM C++ APIs. It builds a pure Python representation that can be serialized to LLVM IR text format.

### Type Safety
All values are explicitly typed. Every value has a well-defined type from the [[llvmlite-ir-types]] hierarchy.

### SSA Form
The IR layer maintains SSA (Static Single Assignment) form automatically through the instruction builder pattern.

## Workflow

1. Define types using [[llvmlite-ir-types]]
2. Create a module and functions using [[llvmlite-ir-modules]]
3. Build basic blocks and instructions using [[llvmlite-ir-builder]]
4. Serialize to LLVM IR text
5. Pass to binding layer for compilation/execution

## Cross-Layer Connections

- Types defined here are referenced in [[llvmlite-binding-type-references]]
- Values constructed here map to [[llvmlite-binding-value-references]]
- Modules created here can be parsed by [[llvmlite-binding-modules]]
- IR text output feeds into the binding layer execution engine

Back to [[llvmlite-User-Guide-MoC]]
