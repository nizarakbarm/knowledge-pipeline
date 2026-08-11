---
created: 2026-08-10
up:
  - "[[Reverse Engineering MOC]]"
related:
  - "[[x86-processor-modes]]"
  - "[[Cross-Compiling Assembly for x86 and ARM on Linux]]"
in:
  - "[[Things]]"
tags:
  - assembly
  - x86
  - arm
  - cisc
  - risc
  - memory-operand
  - load-store
---

# x86 Memory Operands vs ARM Load-Store

## Summary

**Incrementing a value in memory:** x86 does it in **one instruction** (`inc dword ptr [eax]`) because CISC allows a memory operand — the CPU reads, modifies, and writes memory in a single operation. ARM (RISC, load-store architecture) needs **three instructions**: load into a register, increment, store back. Memory is touched only through explicit `LDR`/`STR`.

## The Evidence

Same operation, both architectures (compilable sources: `Extras/assembly/cmp_inc_x86.s`, `Extras/assembly/cmp_inc_arm.s`):

**ARM32 (Thumb)** — 3 instructions, 6 bytes:
```
01: 1B 68         LDR      R3, [R3]       ; read the value at address R3
02: 5A 1C         ADDS     R2, R3, #1     ; add 1 to it
03: 1A 60         STR      R2, [R3]       ; write updated value back to address R3
```

**x86 (32-bit)** — 1 instruction, 2 bytes:
```
01: FF 00         inc      dword ptr [eax]  ; directly increment value at address EAX
```

Verified: both assemble under `clang --target=armv7-linux-gnueabihf` / `clang --target=i386-linux-gnu`; objdump shows the exact bytes above (`681b 1c5a 601a` in little-endian display = `1B 68 / 5A 1C / 1A 60`).

## Why the Difference

- **CISC (x86):** arithmetic instructions accept *memory operands*. The `INC`/`ADD` unit performs read-modify-write against RAM directly — no register round-trip. `MOVS` goes further: it can read *and* write memory in one instruction (string copy).
- **RISC (ARM):** load-store architecture — arithmetic operates on registers only; memory access is restricted to dedicated `LDR`/`STR`. Compilers emit the 3-instruction sequence automatically.
- **Trade-off:** x86's density (2 bytes vs 6) and fewer instructions vs ARM's simpler, more regular pipeline (fixed-width decode, no memory in the ALU path → higher clock efficiency).

## Implications

- **Disassembly reading:** on ARM, a single C-level `*ptr += 1` appears as 3 instructions — don't misread it as 3 operations.
- **Perf analysis:** instruction counts are not comparable across ISAs; x86's 1 instruction costs more cycles than any one ARM instruction.
- **SMP caveat:** a plain `inc [eax]` is not atomic across cores — x86 needs the `LOCK` prefix; ARM needs `LDREX`/`STREX` or `LDXR`/`STXR`. Neither architecture gets atomicity for free from the single-instruction form.

## Connections

- **Related:** [[x86-processor-modes]] — the operating modes these encodings run in
- **Related:** [[Cross-Compiling Assembly for x86 and ARM on Linux]] — compiling the same source for both targets
- **Compilable sources:** `Extras/assembly/cmp_inc_x86.s`, `Extras/assembly/cmp_inc_arm.s` (compile: `clang --target=i386-linux-gnu -c cmp_inc_x86.s`, `clang --target=armv7-linux-gnueabihf -c cmp_inc_arm.s`)
