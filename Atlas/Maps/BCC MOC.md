---
created: 2026-07-03
up:
  - "[[eBPF MOC]]"
  - "[[Things Map]]"
related:
  - "[[PythonBPF MOC]]"
  - "[[Kernel Tracing MOC]]"
in:
  - "[[Atlas/Maps/Maps]]"
tags:
  - map
  - ebpf
  - bcc
  - kernel
  - tracing
  - bpf-compiler-collection
---

# BCC MOC
*The BPF Compiler Collection — eBPF instrumentation via C and Python*

> [!NOTE]- Navigate with your Map of Content
> This MOC covers the BPF Compiler Collection (BCC), a toolkit for creating eBPF programs using a mix of C (for the BPF side) and Python (for user-space orchestration). It is a child of the [[eBPF MOC]] and sibling to [[PythonBPF MOC]].

## Core Concepts

> [!Puzzle]- Probe Types
> Twelve ways to instrument kernel and user-space events, each with different stability guarantees.
> - [[BCC Probe Types]] — Complete probe type cheatsheet (kprobe, tracepoint, uprobe, USDT, kfunc, LSM, BPF iterator)
> - [[BCC Data Helpers]] — Memory read, context access, and utility helpers
> - [[BCC Output Mechanisms]] — `bpf_trace_printk`, `BPF_PERF_OUTPUT`, and `BPF_RINGBUF_OUTPUT`

> [!Box]- Maps and Data Structures
> Shared data structures between kernel BPF and user-space Python.
> - [[BCC Map Types]] — 19 map macros with declarations and defaults
> - [[BCC Map Operations]] — Lookup, update, delete, tail calls, queue/stack operations

> [!Joystick]- Python API
> The `BPF` class and supporting infrastructure for compiling, loading, and managing programs.
> - [[BCC Python API]] — Complete API reference (attachment, polling, map access, batch ops, histograms)

> [!Joystick]- Teaching Workspace
> Reusable course workspace for learning BCC step by step, mirroring the PythonBPF curriculum.
> - [[Teaching/BCC/MISSION|Mission]] — Learning objectives (mirrors PythonBPF curriculum)
> - [[Teaching/BCC/RESOURCES|Resources]] — Curated references and documentation
> - [[Teaching/BCC/GLOSSARY|Glossary]] — Domain terminology
> - [[Teaching/BCC/NOTES|Notes]] — Session notes and preferences
> - [[Teaching/BCC/lessons/0001-first-program|Lesson 0001]] — Your First BCC Program (kprobe + trace_print)
> - [[Teaching/BCC/lessons/0002-hashmap-counters|Lesson 0002]] — HashMap Counters (BPF_HASH + lookup_or_try_init)
- [[Teaching/BCC/lessons/0003-reading-xlated|Lesson 0003]] — Reading bpftool dump xlated (ISA opcodes, stack layout, map patterns)
- [[Teaching/BCC/lessons/0004-memorizing-opcodes|Lesson 0004]] — Memorizing BPF opcode layouts (memory tricks, drill table)
> - [[Teaching/BCC/reference/quickref|Quick Reference]] — Cheatsheet (grows with lessons)

> [!Connect]- Related Concepts
> - [[eBPF MOC]] — Parent: extended Berkeley Packet Filter ecosystem
> - [[PythonBPF MOC]] — Sibling: pure-Python BPF toolkit
> - [[BCC vs Python-BPF Comparisons MOC]] — Systematic benchmark comparison for PyCon TW 2026 talk
