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
  - eflags
  - eip
  - rip
  - control-registers
  - flags"
---

# EFLAGS and EIP

## EFLAGS Register

The **EFLAGS register** (in 32‑bit mode) or **RFLAGS** (in 64‑bit mode, where the upper 32 bits are reserved/zero) is a special‑purpose register that holds a collection of single‑bit **status** and **control** flags. These flags are set or cleared by most arithmetic, logical, and comparison instructions, and they are read by conditional jumps and other control‑flow decisions. In reverse engineering, understanding EFLAGS is essential for interpreting the logic of a program and for following the flow of execution.

## Overview

- **Width:** 32 bits (EFLAGS) in protected mode; extended to 64 bits (RFLAGS) in long mode, but only the lower 32 bits are defined.
- **Access:**  
  - Whole register: `PUSHFD`/`POPFD` (32‑bit), `PUSHFQ`/`POPFQ` (64‑bit)  
  - Individual flags: `LAHF`/`SAHF` (load/store AH into flags), `STC`, `CLC`, `CMC` (carry), `STD`, `CLD` (direction), etc.
- **Purpose:** To record outcomes (carry, zero, overflow, sign) and to control processor behaviour (single‑step, interrupt enable, direction).

## Key flags and their bit positions

Below is a table of the most important flags, grouped by function. Flags marked with ★ are the ones you will encounter constantly in normal application code.

| Bit | Abbr. | Name | Purpose / Typical use |
|-----|-------|------|-----------------------|
| 0★  | CF    | **Carry Flag** | Set if an unsigned operation generates a carry out of the most significant bit (addition) or a borrow (subtraction). Used by unsigned conditional jumps (`JB`/`JC`, `JNB`/`JNC`). Also captures the bit shifted out of `SHL`/`SHR`/`ROR`/`ROL`. |
| 2★  | PF    | **Parity Flag** | Set if the low byte of the result has an **even** number of 1‑bits. Rarely used in modern code (sometimes for simple checksums or antiforensics). |
| 4   | AF    | **Auxiliary Carry Flag** | Indicates a carry or borrow from bit 3 to bit 4; used by decimal adjust instructions (`DAA`, `DAS`, `AAA`, `AAS`). Almost never seen in user‑mode code. |
| 6★  | ZF    | **Zero Flag** | Set if the result of an operation is **zero**. The most commonly tested flag – equality checks (`JE`/`JZ`), loop counters, etc. |
| 7★  | SF    | **Sign Flag** | Set to the most significant bit of the result, i.e., the sign bit when interpreting the result as a signed value. Used by signed conditional jumps (`JS`, `JNS`) and as a fast copy of the sign without a full compare. |
| 8★  | TF    | **Trap Flag** | When set (1), the processor generates a debug exception after **every** instruction (single‑step). Debuggers use this for tracing. |
| 9★  | IF    | **Interrupt Enable Flag** | If set, maskable hardware interrupts (IRQs) are enabled. Cleared by `CLI`, set by `STI`. In ring‑0 code (kernel), you will often see `CLI`/`STI` pairs. User‑mode code cannot usually modify this flag. |
| 10★ | DF    | **Direction Flag** | Controls the direction of string instructions (`MOVS`, `LODS`, `STOS`, `CMPS`, `SCAS`). `DF=0` → auto‑increment (forward), `DF=1` → auto‑decrement (backward). Set/cleared by `STD`/`CLD`. |
| 11★ | OF    | **Overflow Flag** | Set if a **signed** arithmetic operation generates an overflow (result too large or too small for the destination). Used by signed conditional jumps (`JO`, `JNO`). |
| 12‑13 | IOPL | **I/O Privilege Level** | Defines the privilege level (ring) needed to execute `IN`, `OUT`, `CLI`, `STI`. Normally 0, but can be raised to allow user‑mode drivers direct port access. |
| 14   | NT   | **Nested Task** | Used for protected‑mode task switching; rarely seen today. |
| 16   | RF   | **Resume Flag** | Suppresses debug exceptions for one instruction after a debug exception handler returns (`IRETD`), so you can step over an instruction without immediately re‑trapping. |
| 17   | VM   | **Virtual‑8086 Mode** | Set by the OS to indicate that the CPU is in virtual‑8086 mode (running a real‑mode program inside protected mode). |
| 18   | AC   | **Alignment Check** | If set and the AM bit in CR0 is set, memory references are checked for alignment; unaligned accesses cause an exception when CPL=3. |
| 19   | VIF  | **Virtual Interrupt Flag** | Shadow copy of IF used in virtual‑8086 mode. |
| 20   | VIP  | **Virtual Interrupt Pending** | Indicates a pending interrupt in virtual‑8086 mode. |
| 21   | ID   | **ID Flag** | If this bit can be toggled by software, the `CPUID` instruction is supported. |

★ = flag frequently encountered during reverse engineering.

## How instructions affect flags

Not every instruction modifies all flags. Knowing the rules helps you understand what a sequence of code is testing.

| Operation type | Flags affected | Notes |
|----------------|----------------|-------|
| `MOV`, `LEA`, `PUSH`, `POP`, `JMP`, `CALL` (not interrupt) | **None** | These do not alter any flags. |
| `ADD`, `SUB`, `ADC`, `SBB`, `CMP`, `NEG` | **OF, SF, ZF, AF, PF, CF** | All six arithmetic flags are updated according to the result. `CMP` is exactly `SUB` but discards the result, so flags are set identically. |
| `INC`, `DEC` | **OF, SF, ZF, AF, PF** | Carry flag is **not** affected (historical quirk of the 8086). |
| `MUL`, `IMUL` (one operand) | **CF, OF** (others undefined) | CF/OF indicate whether the upper half of the result is non‑zero. |
| `DIV`, `IDIV` | **Undefined** (all flags) | Flags become undefined after a divide. |
| `AND`, `OR`, `XOR`, `TEST` | **SF, ZF, PF**; CF and OF are **cleared** | AF becomes undefined. `TEST` is an `AND` that discards the result, so flags behave the same. |
| `SHL`, `SHR`, `SAL`, `SAR`, `ROL`, `ROR`, `RCL`, `RCR` | **CF** (last bit shifted out); **OF** (for single‑bit shifts if sign changed) | For multiple shifts, OF is undefined. |
| `BSF`, `BSR` | **ZF** only | ZF=1 if the source is zero, else 0. Flags like CF, OF, SF are undefined. |
| `CLD`, `STD`, `CLC`, `STC`, `CMC` | Only the specific flag they target | These are explicit flag‑control instructions. |
| `LAHF`/`SAHF` | `SAHF` loads SF, ZF, AF, PF, CF from AH | Used to copy flags to/from a general‑purpose register. |

## EFLAGS in a debugger

Most debuggers display EFLAGS either as a 32‑bit hex value or as a set of one‑letter tokens. For example:

```
EFL 00000246 (   O  D  I  S Z  A  P  C )
                 0  0  1  0 1  0  0  1
```

A common set in x64dbg looks like: `CF=1, PF=1, ZF=1, SF=0, OF=0, DF=0, IF=1`.  
Knowing the bits lets you manually decode the hex value when needed (e.g., reading a dump from a crash).

## Why this matters for reverse engineering

1. **Conditional branches** – Logic such as `if (x == 0)` compiles to a `TEST` or `CMP` followed by a jump like `JZ` or `JE`. By watching the ZF flag, you instantly see which path is taken.

2. **Loop patterns** – `DEC ECX; JNZ ...` relies on ZF. If you see CF used in a loop, it might be a shift‑based bit scanner.

3. **Unsigned vs. signed decisions** – Code using `JB` / `JA` (which test CF and CF+ZF) is comparing numbers as unsigned; code using `JL` / `JG` (which test SF and OF) is comparing as signed. Recognising this helps deduce variable types.

4. **Kernel vs. user mode** – If you see `CLI`/`STI` or `PUSHF`/`POPF` directly altering IF/IOPL, you’re likely looking at ring‑0 code (driver, kernel module) or a very old program that directly accessed hardware.

5. **Malware tricks** – Malware sometimes sets the Trap Flag (TF) to execute code in a single‑stepping debugger differently than under normal execution, or it may manipulate the Direction Flag (DF) to obfuscate string operations.

6. **Patch/chain analysis** – When bypassing a check (e.g., `JNE` → `JMP`), you are essentially forcing a certain flag state to be ignored. Understanding which flags are set by the preceding instruction helps you find the right place to patch.

Mastering EFLAGS will make you much faster at skimming disassembly – you’ll recognise the meaning of a `TEST EAX, EAX` + `JZ` pair in an instant, and you’ll be able to follow complex arithmetic logic without mentally recalculating every operation.

If you have any notes or examples in your workspace (like annotated disassembly snippets), I can search them to show you real‑world flag usage. Otherwise, I hope this overview provides a solid reference!

## EIP (Instruction Pointer)

The **EIP register** (Extended Instruction Pointer) is the 32‑bit version of the x86 instruction pointer, which holds the **linear address of the next instruction to be executed**. In 16‑bit real mode it is called **IP** (16‑bit), in 64‑bit long mode it is extended to **RIP**. The instruction pointer is the central piece of hardware that drives the processor’s control flow — it determines what happens **next** at the machine level.

## Role and behavior

| Aspect | Explanation |
|--------|-------------|
| **Sequential execution** | After fetching and executing an instruction, the CPU automatically increments (E)IP by the length of that instruction, so it points to the following one. |
| **Control‑flow changes** | Instructions like `JMP`, `Jcc` (conditional jumps), `CALL`, `RET`, `IRET`, `SYSCALL`, and `SYSENTER` modify (E)IP explicitly, either by loading a new value directly or by pushing / popping it onto the stack. |
| **Branch prediction** | Modern CPUs internally rename and speculatively execute instructions ahead of the architecturally visible (E)IP, but the architectural (E)IP remains the official “commit point” — when a misprediction occurs, the pipeline is flushed and architectural (E)IP is restored. |
| **Exception / interrupt handling** | When an interrupt or exception occurs, the CPU saves the current (E)IP (along with CS and EFLAGS) onto the stack and loads a new value from the Interrupt Descriptor Table (IDT). The `IRET` instruction later restores it. |
| **Security** | (E)IP cannot be directly written by a `MOV` instruction (it is not a general‑purpose register). This forces all control‑flow transfers to go through well‑defined operations, though exploits like buffer overflows still hijack (E)IP indirectly by corrupting a saved return address on the stack. |
| **Debugging & tracing** | Debuggers use (E)IP as the “current position” pointer; breakpoints are implemented by replacing the instruction at (E)IP with `INT 3`. Tracing (single‑step) uses the Trap Flag (TF) in EFLAGS to pause execution after each instruction and report the new (E)IP. |

## Addressing modes and size prefixes

- In **16‑bit mode** (real mode), IP is 16 bits wide; addresses wrap around at 64 KB within a segment.
- In **32‑bit protected mode**, EIP is 32 bits wide, allowing a flat 4 GB address space (extended by paging).
- In **64‑bit long mode**, RIP is 64 bits wide, but only 48‑bit canonical addresses are used in practice.

The **EIP‑relative addressing** (available in 32‑bit mode for `CALL` and `JMP` and generally in 64‑bit mode for many instructions) allows compact, position‑independent code: the address is calculated as `[RIP + displacement]`.

## Common uses in reverse engineering

1. **Identifying function entries** – A `CALL` instruction pushes the return address (next EIP) onto the stack. By following the target EIP, you locate the function. The `RET` at the end uses that saved return address to go back.

2. **Tracing code paths** – When stepping through a binary, watching how EIP changes reveals the real execution flow, including taken branches and obfuscated control transfers (e.g., `PUSH`/`RET` instead of `JMP`).

3. **Detecting unpacked/packed code** – Packed executables often execute a small stub that writes new code to memory and then jumps to it by modifying EIP (e.g., via `JMP EAX` or `RET`). Setting a breakpoint on the original entry point and watching for a sudden EIP change into a newly written area is a classic unpacking technique.

4. **Vulnerability analysis** – In a stack‑buffer overflow, the return address (the saved EIP) is overwritten. By monitoring where EIP ends up, you can control the crash and, eventually, code execution.

5. **Calling conventions** – Understanding how `CALL`/`RET` manipulate EIP helps you map out function prologues and epilogues, and separate functions from inline data.

## Summary

| Register | Mode | Width | Purpose |
|----------|------|-------|---------|
| IP       | 16‑bit real / VM86 | 16 bits | Next instruction offset (within a segment) |
| EIP      | 32‑bit protected | 32 bits | Next instruction linear address |
| RIP      | 64‑bit long (x86‑64) | 64 bits | Next instruction linear address (only lower 48 bits used) |

In essence, **(E)IP is the “neck” of the CPU highway** — every instruction fetches from it, every branch repoints it, and every security boundary eventually depends on controlling where it can go. As a reverse engineer, you will spend a large amount of time tracking EIP/RIP values in a debugger to understand program logic and spot malicious behaviour.

If you have any disassembly examples in your workspace that illustrate EIP manipulation (like `JMP` tables or `RET`‑based obfuscation), I can search for them and walk through them with you.


