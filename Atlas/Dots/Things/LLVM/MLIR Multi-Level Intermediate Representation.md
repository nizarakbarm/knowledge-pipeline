---
created: 2026-05-01
up:
  - "[[LLVM MOC]]"
  - "[[Things]]"
related:
  - "[[LLVM Modular Compiler Infrastructure]]"
  - "[[LLVM Sub-Projects Overview]]"
  - "[[LLVM IR]]"
in:
  - "[[Atlas/Dots/Things/LLVM]]"
tags:
  - llvm
  - mlir
  - compiler
  - heterogeneous-computing
  - dsl
---

# MLIR — Multi-Level Intermediate Representation

## Summary

MLIR is an LLVM subproject providing a **reusable and extensible compiler infrastructure** designed to address software fragmentation across heterogeneous hardware. It enables a unified compilation pipeline where multiple hardware targets share the same infrastructure, dramatically reducing the cost of building domain-specific compilers (DSLs) while supporting advanced transformations like DMA insertion, cache management, and polyhedral loop optimization.

## Key Points

- **Unified hybrid IR** supports both common infrastructure and hardware-specific operations — multiple targets leverage the same compiler passes and tools for high ROI
- **Heterogeneous code generation** includes DMA insertion, explicit cache management, memory tiling, and vectorization for 1D/2D register architectures
- **HPC loop optimizations** leverage fusion, loop interchange, and polyhedral primitives for performance-critical workloads
- **DSL backbone** natively represents complex dataflow graphs (e.g., TensorFlow) with dynamic shapes, user-extensible operations, and transformations like quantization for deep learning
- **Multithreading-by-design** solves LLVM IR limitations through limited SSA scope and explicit symbol references instead of cross-function use-def chains
- **Intentional scope boundaries** — MLIR delegates low-level machine code generation (register allocation, instruction scheduling) to the LLVM backend

## Details

### Heterogeneous Hardware Strategy

MLIR's core innovation is a **common hybrid intermediate representation** that enables a unified compiler infrastructure while allowing hardware-specific operations to coexist. This design means:

- Compiler passes and tooling investments apply across **multiple target architectures** (CPUs, GPUs, TPUs, FPGAs, custom accelerators)
- Hardware vendors can define **dialects** — self-contained IR extensions with their own operations, types, and transformations
- **Lowering transformations** progressively map high-level operations to hardware-specific primitives:
  - **DMA insertion** for explicit data movement between memory hierarchies
  - **Explicit cache management** for architectures with software-controlled caches
  - **Memory tiling** to optimize cache locality and reduce memory bandwidth pressure
  - **Vectorization** targeting both 1D SIMD and 2D matrix/register architectures

### Domain-Specific Language Support

MLIR serves as the **backbone for DSL compilation**, dramatically reducing the engineering overhead of building specialized compilers:

- Can natively represent **complex dataflow graphs** such as TensorFlow computation graphs
- Supports **dynamic shapes** — tensors with dimensions unknown at compile time
- Enables **user-extensible operations** so domain experts can define custom primitives
- Supports high-level **graph transformations** including quantization for deep learning inference optimization

### Technical Design Decisions

MLIR was built incorporating lessons from **LLVM IR, XLA HLO, and Swift SIL**:

| Design Challenge | MLIR Approach | LLVM IR Limitation |
|-----------------|---------------|-------------------|
| Multithreading | Limited SSA scope + explicit symbol references | Cross-function use-def chains prevent simultaneous multi-function compilation |
| Extensibility | Dialect system for domain-specific operations | Monolithic IR design |
| Verification | Rigorous IR specification with built-in verifier | Less formalized specification |
| Testing | FileCheck-based testing infrastructure | Same, inherited from LLVM |

### Intentional Non-Goals

MLIR explicitly avoids low-level machine code generation responsibilities:

- **Register allocation** — delegated to LLVM backend
- **Instruction scheduling** — delegated to LLVM backend
- Focus remains on **mid-level and high-level transformations** where domain and hardware semantics are still explicit

## Connections

- **Questions this raises**: How do MLIR dialects compose when targeting systems with multiple heterogeneous accelerators? What is the performance overhead of MLIR's progressive lowering compared to hand-tuned vendor compilers?
- **Related to**: [[LLVM IR]], [[TensorFlow]], [[Polyhedral Compilation]], [[Heterogeneous Computing]], [[Domain-Specific Languages]]
- **Applies to**: Building compilers for AI accelerators, HPC toolchain development, embedded systems with custom DSPs, graph optimization for deep learning frameworks
- **Contrast with**: [[LLVM IR]] — LLVM IR is lower-level and target-agnostic; MLIR operates at multiple abstraction levels and embraces hardware-specific operations through dialects

## Source

Distilled from raw MLIR technical documentation on heterogeneous architecture compilation, domain-specific compiler infrastructure, and LLVM subproject design principles.
