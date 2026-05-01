---
created: 2026-05-01
up:
  - "[[LLVM MOC]]"
  - "[[Things]]"
related:
  - "[[LLVM Modular Compiler Infrastructure]]"
  - "[[Clang]]"
  - "[[LLDB]]"
in:
  - "[[Things]]"
  - "[[LLVM]]"
tags:
  - llvm
  - compiler
  - toolchain
  - sub-project
---

# LLVM Sub-Projects Overview

## Summary

LLVM is an umbrella project comprising specialized sub-projects that together form a complete compiler and toolchain ecosystem. Each component targets a specific layer of the compilation pipeline — from source language frontends to runtime libraries and debugging tools.

## Key Points

- **LLVM Core** provides the foundational optimizer and code generator built around **LLVM IR**, a source/target-independent SSA-based intermediate representation
- **Clang** is the native C/C++/Objective-C frontend, prioritizing fast compilation and actionable diagnostics
- **Flang** is a modern Fortran compiler supporting standards from **Fortran 77 through Fortran 2023**, with OpenMP offload to CPUs and GPUs
- **LLDB** is a next-generation debugger leveraging LLVM/Clang libraries for faster symbol loading and memory efficiency than GDB
- **libc++** is a standard-conformant, high-performance C++ standard library implementation
- **compiler-rt** supplies low-level runtime routines and sanitizers (AddressSanitizer, ThreadSanitizer, MemorySanitizer, DataFlowSanitizer)

## Details

### LLVM Core

The heart of the project. LLVM Core is a **source- and target-independent optimizer** and code generation framework for popular CPU architectures.

- Built around **LLVM IR** — a well-specified, SSA-based intermediate representation
- **Modular design** enables inventing new languages or porting existing compilers without rewriting backend code
- Provides the shared infrastructure that all other LLVM sub-projects build upon

### Clang

LLVM's native compiler frontend for C-based languages.

- Supports **C, C++, and Objective-C**
- Optimized for **fast compile times** and **high-quality error/warning messages**
- Serves as a platform for source-level tools: **Clang Static Analyzer**, **clang-tidy**, and other AST-based utilities

### Flang

A modern Fortran compiler with runtime support.

- Supports **Fortran 2023** and maintains **legacy compatibility back to Fortran 77**
- Implements **OpenMP** parallelism across both CPUs and GPUs
- Designed for **high-performance computing**, including supercomputer workloads

### LLDB

A next-generation, high-performance native debugger.

- Deeply integrated with **LLVM/Clang libraries** — reuses ASTs, expression parser, JIT compilation, and disassembler
- **Faster and more memory-efficient than GDB** when loading debug symbols
- Provides a modern debugging experience built on the same codebase as the compiler

### libc++

A standard-conformant implementation of the C++ Standard Library.

- Designed for **high performance** and standards compliance
- Full support for **C++11 and C++14** features
- Provides a modern alternative to libstdc++

### compiler-rt

Low-level runtime support and dynamic testing infrastructure.

- Provides **code generator routines** (e.g., `__fixunsdfdi`) injected when target hardware lacks native instructions
- Supplies **runtime libraries for sanitizers**:
  - **AddressSanitizer** — detects memory errors
  - **ThreadSanitizer** — detects data races
  - **MemorySanitizer** — detects uninitialized memory reads
  - **DataFlowSanitizer** — tracks data flow through programs

## Connections

- **Questions this raises**: How do the sanitizers in compiler-rt compare to Valgrind's approach? What is the relationship between libc++ and libc++abi?
- **Related to**: [[Compiler Frontend]], [[Compiler Backend]], [[SSA Form]], [[Static Analysis]], [[Debuggers]]
- **Applies to**: Building cross-language toolchains, HPC compilation pipelines, memory-safe systems programming
- **Contrast with**: GCC's monolithic architecture where frontend/backend/runtime are less cleanly separated

## Source

Distilled from raw LLVM sub-project documentation — technical reference capture on compiler infrastructure components.
