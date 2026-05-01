---
created: 2026-05-01
up:
  - "[[LLVM MOC]]"
  - "[[Things]]"
related:
  - "[[LLVM Sub-Projects Overview]]"
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[eBPF Tutorial - Overview]]"
  - "[[CO-RE (Compile Once - Run Everywhere)]]"
  - "[[PythonBPF]]"
  - "[[BTF (BPF Type Format)]]"
  - "[[libbpf Framework]]"
in:
  - "[[Things]]"
  - "[[LLVM]]"
tags:
  - llvm
  - compiler
  - infrastructure
  - toolchain
---

# LLVM - Modular Compiler Infrastructure

## Summary

**LLVM** is a collection of modular compiler and toolchain technologies built around a language-independent intermediate representation (IR). Originally developed at the University of Illinois, it has grown into a massive umbrella project supporting everything from JIT compilation for scripting languages to optimizing Fortran for supercomputers.

## Key Points

- **Not an acronym**: LLVM is a brand name, not an abbreviation
- **Origin**: University of Illinois research project focused on modern **SSA-based compilation**
- **Core design**: Built around **LLVM IR** — a source- and target-independent intermediate representation with a powerful optimizer
- **Scope**: Massive umbrella project encompassing sub-projects like **Clang**, **Flang**, **LLD**, **LLDB**, **MLIR**, and **BOLT**
- **Universal reach**: Handles use cases ranging from **Lua JIT** to **supercomputer Fortran**
- **Recognition**: First developer meetings held in **2007**; received the **ACM Software System Award in 2012**

## Details

### Architecture Philosophy

LLVM was designed to decouple the frontend (parsing source languages) from the backend (generating target machine code) through a well-defined intermediate representation. This modularity enables:

- **Language independence**: Any programming language can compile to LLVM IR
- **Target independence**: The same IR can be optimized once and then lowered to any architecture
- **Reusable components**: Optimizers, code generators, and analysis tools shared across languages

### Sub-Project Ecosystem

| Sub-project | Purpose |
|-------------|---------|
| **Clang** | C/C++/Objective-C compiler frontend |
| **Flang** | Fortran compiler frontend |
| **LLD** | High-performance linker |
| **LLDB** | Debugger built on LLVM components |
| **MLIR** | Multi-Level Intermediate Representation for domain-specific compilers |
| **BOLT** | Binary optimizer and layout tool |

### Compilation Spectrum

LLVM supports both **static compilation** (ahead-of-time) and **dynamic compilation** (JIT — Just-In-Time). This dual capability means it powers:

- Browser JavaScript engines (via JIT)
- Kernel eBPF programs (via LLVM backend)
- High-performance scientific computing (via Fortran/Flang)
- Embedded systems and GPUs (via various backends)

## Connections

- **Questions this raises**: How does LLVM IR compare to other intermediate representations like GCC's GIMPLE or JVM bytecode? What makes MLIR distinct from LLVM IR?
- **Related to**: [[Compiler Design]], [[SSA Form]], [[Intermediate Representation]], [[eBPF]]
- **Applies to**: Building new programming languages, optimizing existing ones, cross-platform toolchain development, kernel programming (eBPF)
- **Contrast with**: Traditional monolithic compilers (e.g., GCC pre-modularization)

## Source

Distilled from raw overview data — self-captured knowledge capture on compiler infrastructure.
