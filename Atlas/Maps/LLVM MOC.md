---
created: 2026-05-01
up:
  - "[[Things]]"
in:
  - "[[Atlas/Maps/Maps]]"
tags:
  - moc
  - llvm
  - compiler
  - infrastructure
  - toolchain
---

# LLVM MOC

A Map of Content for LLVM (Low Level Virtual Machine) — modular compiler and toolchain infrastructure.

## Core Concepts
- [[LLVM Modular Compiler Infrastructure]] — Modular compiler infrastructure overview
- [[LLVM Sub-Projects Overview]] — Detailed overview of LLVM sub-projects (Core, Clang, Flang, LLDB, libc++, compiler-rt)
- [[Compiler Intermediate Representation]] — Deep dive into compiler IR, SSA form, abstraction levels, and LLVM IR specifics
- [[LLVM External Language Ecosystem]] — External language adopters (Rust, Julia, Lua, Swift, etc.)
- [[LLVM License Apache 2.0 with Exceptions]] — License framework with GPLv2 compatibility and compiled output exceptions
- [[LLVM Toolchain Performance Benchmarks]] — Performance analysis of LLD, LLDB, and BOLT
- [[MLIR Multi-Level Intermediate Representation]] — MLIR for heterogeneous hardware and DSLs
- [[LLVM 2026 Release Roadmap]] — 2026 release schedule for branches 22.1.x and 23.1.x

## Sub-Projects
- **Clang** — C/C++/Objective-C compiler frontend
- **Flang** — Fortran compiler frontend  
- **LLD** — High-performance linker
- **LLDB** — Debugger built on LLVM components
- **MLIR** — Multi-Level Intermediate Representation
- **BOLT** — Binary optimizer and layout tool

## Related Topics
- [[eBPF MOC]] — eBPF uses LLVM for compilation to BPF bytecode
- [[Systems MOC (kit)]] — Complex systems and emergent behavior
- [[Things]] — All things in the Ideaverse

## Questions
- How does LLVM IR compare to GCC's GIMPLE or JVM bytecode?
- What makes MLIR distinct from LLVM IR?
- How does the LLVM backend target eBPF specifically?
