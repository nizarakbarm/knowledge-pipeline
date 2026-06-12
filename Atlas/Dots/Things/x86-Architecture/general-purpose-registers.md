---
created: 2026-06-09
up:
  - "[[Reverse Engineering MOC]]"
related:
  - "[[x86 Architecture]]"
in:
  - "[[Library]]"
tags:
  - "x86
  - registers
  - gpr
  - eax
  - rax
  - assembly"
---

# General Purpose Registers

The x86/x64 architecture provides a set of **general‑purpose registers (GPRs)** that hold integer data, addresses, and temporary results. Their number, width, and naming depend on the current processor mode (16/32/64‑bit). For reverse engineering, you’ll most often encounter them in 32‑bit (IA‑32) and 64‑bit (x86‑64) code.

## Number of GPRs

| Mode            | Count | Register set                                                                                                                                                         |
|-----------------|-------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 16‑bit (8086)   | 8     | AX, BX, CX, DX, SI, DI, BP, SP                                                                                                                                       |
| 32‑bit (IA‑32)  | 8     | EAX, EBX, ECX, EDX, ESI, EDI, EBP, ESP (the 16‑bit registers **extended** to 32 bits)                                                                               |
| 64‑bit (x86‑64) | 16    | RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP, **R8–R15** (the existing eight registers **extended** to 64 bits, plus eight brand‑new registers)                           |

So in a modern 64‑bit environment, you have **16 full‑width integer GPRs** at your disposal.

## Register bit‑level accesses

Each register can be addressed in parts of different sizes. The naming convention reveals how many lower bits you are reading or writing.

### Classic 8 registers (and their aliases)

| 64‑bit | 32‑bit | 16‑bit | 8‑bit (low) | 8‑bit (high) | Notes                                                                                 |
|--------|--------|--------|--------------|--------------|---------------------------------------------------------------------------------------|
| RAX    | EAX    | AX     | AL           | AH           | Accumulator – used for arithmetic, I/O, return values                                 |
| RBX    | EBX    | BX     | BL           | BH           | Base – sometimes used as a base pointer, callee‑saved                                 |
| RCX    | ECX    | CX     | CL           | CH           | Count – shift amounts, loop counter, string operations                                |
| RDX    | EDX    | DX     | DL           | DH           | Data – extension for multiplication/division, I/O port addresses                      |
| RSI    | ESI    | SI     | SIL          | *n/a*        | Source Index – pointer for string/memory operations                                   |
| RDI    | EDI    | DI     | DIL          | *n/a*        | Destination Index – pointer for string/memory operations                              |
| RBP    | EBP    | BP     | BPL          | *n/a*        | Base Pointer – usually points to the base of the current stack frame                  |
| RSP    | ESP    | SP     | SPL          | *n/a*        | Stack Pointer – always points to the top of the stack                                 |

- **High 8‑bit halves (AH, BH, CH, DH)** are available only in 32‑bit mode (and 16‑bit).  
  In 64‑bit mode they are **inaccessible when a REX prefix is present**, but can still be used in certain rare situations without a REX prefix.
- **SIL, DIL, BPL, SPL** – the low 8 bits of ESI/EDI/EBP/ESP – were introduced with x86‑64. Previously you could only reference them as full 16/32/64‑bit or via memory.
- **Zero‑extension effect:**  
  Writing to any **32‑bit** register (e.g., `MOV EAX, ...`) in 64‑bit mode **automatically zero‑extends** into the upper 32 bits of the corresponding 64‑bit register. Writing to a 8‑ or 16‑bit register **leaves the upper bits unchanged**.

### New registers (R8–R15)

These follow a uniform naming scheme:

| 64‑bit | 32‑bit | 16‑bit | 8‑bit   |
|--------|--------|--------|---------|
| R8     | R8D    | R8W    | R8B     |
| R9     | R9D    | R9W    | R9B     |
| R10    | R10D   | R10W   | R10B    |
| R11    | R11D   | R11W   | R11B    |
| R12    | R12D   | R12W   | R12B    |
| R13    | R13D   | R13W   | R13B    |
| R14    | R14D   | R14W   | R14B    |
| R15    | R15D   | R15W   | R15B    |

There are **no high‑byte aliases** for R8–R15.

## Typical usage of each register (historical/conventional)

Even though all registers can be used for general purposes, compilers and calling conventions assign them specific roles. Recognizing these roles will dramatically speed up your reverse‑engineering efforts.

| Register | Traditional Role                                                                                                                      |
|----------|---------------------------------------------------------------------------------------------------------------------------------------|
| **RAX**  | **Accumulator** – arithmetic results, function **return values**, I/O instructions (`IN`/`OUT`), CPUID leaf selector                  |
| **RBX**  | **Base** – often used as a data pointer; **callee‑saved** (must be preserved across calls)                                           |
| **RCX**  | **Count** – loop counter (`LOOP`), shift amount (`SHL`/`SHR`/`ROR`/`ROL`), `REP` prefix for string operations, first integer argument |
| **RDX**  | **Data** – high‑order bits of multiplication/division, second integer argument, I/O port number in `IN`/`OUT`                        |
| **RSI**  | **Source Index** – source pointer for `MOVS`/`LODS`/`CMPS`; second function argument in 64‑bit System V ABI                        |
| **RDI**  | **Destination Index** – destination pointer for `STOS`/`MOVS`/`CMPS`; first function argument in 64‑bit System V ABI                |
| **RBP**  | **Base Pointer** – often used to mark the stack frame base, giving access to function arguments and local variables; **callee‑saved**  |
| **RSP**  | **Stack Pointer** – always points to the last pushed value; used implicitly by `PUSH`, `POP`, `CALL`, `RET`, etc.                      |
| **R8–R15** | Purely general‑purpose – used for extra arguments, temporary values, or as callee‑saved registers depending on the ABI            |

In the **Microsoft x64 calling convention**, the first four integer arguments go into **RCX, RDX, R8, R9**; any additional arguments are passed on the stack. In the **System V AMD64 ABI** (used on Linux/macOS), the order is **RDI, RSI, RDX, RCX, R8, R9**.

## Why this matters in reverse engineering

- **Function prologues/epilogues:** Seeing `PUSH RBP` / `MOV RBP, RSP` reveals a standard stack frame; the absence of these may indicate `-fomit-frame-pointer` or the use of RBP as a general register.  
- **Calling conventions:** Identifying which registers are used for arguments helps you quickly map function parameters.  
- **Data movement:** Recognizing `LEA RAX, [RCX+RDX*4]` as address calculation tells you the code is likely indexing an array.  
- **Optimised code:** Modern compilers freely use R8–R15 for any purpose, so you’ll often see them holding loop counters or temporary pointers instead of the classic RCX/RSI/RDI.

If you have any notes in your workspace that cover calling conventions, stack frame analysis, or disassembly patterns, I can search them to give you concrete examples. Otherwise, this summary should give you a solid foundation for reading x86/x64 machine code.
