---
created: 2026-07-24
tags:
  - map
  - moc
  - ebpf
  - benchmark
in: "[[Atlas/Maps/Maps]]"
up: "[[PyCon-TW-2026]]"
cssclasses:
  - moc-collide
---

# BCC vs Python-BPF — All Comparison Notes

*Systematic comparison of BCC and Python-BPF eBPF frameworks for PyCon TW 2026 talk*

> [!NOTE]- Navigate with your Map of Content
> Use this MOC to find any benchmark, investigation, or reference related to the BCC vs Python-BPF comparison. Sections group by investigation type, framework internals, and talk materials.

## Investigation Encounter (Main)

| Note | Content |
|------|---------|
| [[map_1_perf.py BCC vs pythonbpf comparison]] | Central investigation — struct_parser, overflow, time -v, probes |

## Benchmarks

| Note | Topic |
|------|-------|
| [[tracepoint_1 97-char string pythonbpf vs BCC full comparison]] | Long string edge case |
| [[pythonbpf vs BCC strace diff with and without attach]] | strace comparison |
| [[bpf Syscall Comparison Python-BPF vs BCC vs Eunomia]] | 3-way syscall comparison |
| [[Measuring bpf Syscall Time]] | bpf syscall timing |
| [[Bytecode and JIT Comparison]] | xlated/JIT instruction diff |
| [[Syscall and Startup Comparison]] | Startup overhead comparison |
| [[Perf Buffer Overflow Mechanics]] | Ring/perf buffer overflow analysis |
| [[Perf Buffer Call Path]] | Call path tracing |
| [[Embedded Counter Benchmark]] | Counter benchmark results |
| [[Python-BPF Struct-in-Map Value — llc Bug & Benchmark]] | Struct map value: llc GEP bug, read-then-update fix, 8.6µs/ev |
| [[BPF map vs stack memory safety]] | Memory safety |
| [[BCC vs Python-BPF bpf_printk Comparison]] | bpf_printk |
| [[BPF Syscall-Only — kallsyms Symbol Resolution Overhead]] | /proc/kallsyms ~10k reads |
| [[BPF Syscall-Only — BCC In-Process Clang Compilation Path]] | Clang fork overhead |
| [[BPF Syscall-Only — Memory Footprint]] | Memory comparison |

## Bytecode & JIT

| Note | Topic |
|------|-------|
| [[Capturing JIT Dump of Short-Lived BPF Program]] | JIT dump capture method |
| [[BPF Perf Profiling Per-Instruction Cost]] | Per-instruction cost |
| [[eBPF Instruction Cost Is Not Uniform]] | Non-uniform cost finding |
| [[tp_openat JIT instruction cost measurement]] | JIT cost measurement |

## PythonBPF Framework

### Architecture

| Note | Topic |
|------|-------|
| [[PythonBPF.md]] | Main overview |
| [[Python-BPF v0.1.9 Architecture Analysis]] | v0.1.9 architecture |
| [[PythonBPF Compilation Pipeline]] | AST → llvmlite → BPF bytecode |
| [[PythonBPF Structs]] | Struct type handling |
| [[PythonBPF Maps]] | BPF map operations |
| [[PythonBPF Helper Functions]] | Built-in helper coverage |
| [[PythonBPF Decorator System]] | `@bpf`, `@struct`, `@map` decorators |
| [[Architecture.md]] | Architecture notes |

### Compiler Internals

| Note | Topic |
|------|-------|
| [[load_struct_field Implementation]] | vmlinux struct field access codegen |
| [[Generated LLVM IR for probe_read_kernel]] | passthrough + helper 113 LLVM IR |
| [[struct_pt_regs in vmlinux.py]] | KPROBE context struct layout |
| [[pythonbpf BTF Profiling Investigation]] | BTF profiling |
| [[Practical Introduction to Python AST (Laurent Direr)]] | AST intro |
| [[Python AST - Source References]] | AST references |
| [[llvmlite Binding Layer - Chat Synthesis]] | llvmlite binding |
| [[llvmlite IR Layer - Chat Synthesis]] | llvmlite IR |

### Limitations

| Note | Limitation |
|------|------------|
| [[Python-BPF Compiler Limitations]] | Full list of gaps |
| [[Python-BPF All Workarounds for struct_pt_regs]] | Section union workaround |
| [[Python-BPF Cannot Create Buffer Arrays Inside BPF Functions]] | Array inside struct limitation |
| [[Python-BPF RecursionError with Multiple Sections Using Union Structs]] | Recursion bug |
| [[Python-BPF Debug Info Recursion Bug with Union Types]] | Debug info recursion |
| [[PythonBPF Register Access in ctx and The Argument Mapping]] | Argument mapping |
| [[Python-BPF Probe Read of ctx.si Returns Garbage]] | probe_read + ctx.si gotcha |

## BCC Framework

| Note | Topic |
|------|-------|
| [[BCC eBPF]] | BCC architecture overview |
| [[BCC.md]] | BCC general reference |
| [[BCC Python API]] | API reference |
| [[BCC Output Mechanisms]] | Output mechanisms |
| [[BCC Map Operations]] | Map operations |
| [[BCC Map Types]] | Map types |
| [[BCC Data Helpers]] | Data helpers |
| [[BCC Probe Types]] | Probe types |
| [[Install BCC at Opensuse Leap 16.0]] | Installation guide |
| [[Legacy framing ioctl vs LINK_CREATE is libbpf terminology]] | attach method comparison |

## Talk Materials

| Note | Content |
|------|---------|
| [[Spaces/PyCon-TW-2026/ebpf-slides-structure]] | Slide structure (20 slides) |
| [[Spaces/PyCon-TW-2026/fresh-benchmark-results]] | Latest benchmark numbers |

## Efforts

| Note | Phase |
|------|-------|
| [[Efforts/Ongoing/Compare BCC and Python BPF]] | Ongoing comparison |
| [[Efforts/Ongoing/py-spy BCC vs Python-BPF Deep Analysis]] | Deep analysis |
| [[Efforts/Ongoing/py-spy BCC Flame Graph Analysis]] | Flame graph |
| [[Efforts/On/BCC vs Python-BPF Benchmark Plan]] | Benchmark plan |

## Related Tutorials

| Note | Framework |
|------|-----------|
| [[eBPF Tutorial - Overview]] | General eBPF |
| [[Python-BPF Tutorial - Kprobe Unlink]] | PBPF |
| [[Python-BPF probe_read and probe_read_str Usage with c_void_p]] | PBPF |
| [[PythonBPF Setup]] | PBPF setup |
| [[Python-BPF bpf_printk]] | PBPF |

> [!Connect]- Related Concepts
> - [[eBPF MOC]] — General eBPF knowledge
> - [[BCC MOC]] — BCC-specific notes
> - [[PythonBPF MOC]] — PythonBPF-specific notes
> - [[PyCon-TW-2026]] — Talk planning Space
