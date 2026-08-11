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

## Reproducing on ARM Linux (aarch64, e.g. Alpine 3.24)

On ARM hardware, the ARM side is **native** — the x86 side is the cross-compile:

```bash
apk add clang llvm binutils          # Alpine: one install covers both arches (binutils optional — llvm-objdump reads both)
cd Extras/assembly

# ARM (native, aarch64) — 3-instruction load-store sequence
clang --target=aarch64-linux-gnu -c cmp_inc_arm64.s -o arm.o
objdump -d arm.o                     # GNU objdump handles the native arch

# x86 (cross: clang backend only, no sysroot needed for -c)
clang --target=i386-linux-gnu -c cmp_inc_x86.s -o x86.o
llvm-objdump -d x86.o                # GNU objdump cannot read foreign arch; llvm-objdump can

# expected: arm.o → ldr/add/str (3 insns, 16 B) · x86.o → ff 00 incl (%eax) (1 insn, 2 B)
```

Two ARM sources: `cmp_inc_arm64.s` (native aarch64 — `ldr w1,[x0] / add / str`) and `cmp_inc_arm.s` (ARM32 Thumb — the exact `1B 68 / 5A 1C / 1A 60` bytes from The Evidence, needs `--target=armv7-linux-gnueabihf`). Same load-store shape, different encodings. Reverse direction of the macOS host: there x86 was native and ARM cross — the `--target` mechanism is identical both ways.

> [!WARNING]- Wrong file for the target — the #1 mistake
> `clang --target=aarch64-linux-gnu comp_inc_arm.s` (ARM32 Thumb source) fails with
> `error: invalid operand for instruction` on `LDR R3, [R3]` — the aarch64 assembler rejects
> 32-bit registers outright. This is not a typo; ARM32 and AArch64 are different ISAs.
> Match source to target: ARM32 source → `--target=armv7-linux-gnueabihf`, AArch64 source → `--target=aarch64-linux-gnu`. Add `-c` (assemble only) unless you have a sysroot to link against.

**Runnable version** (ARM32, exits cleanly — `ldr/adds/str` plus the exit syscall; counter in `.data`, no dereference of unmapped addresses). Source: `Extras/assembly/run_arm.s`:

```asm
# run_arm.s — increment a .data counter via the load-store sequence, then exit(0)
    .section .text
    .global _start
    .type _start, %function
_start:
    ldr  r0, =counter
    ldr  r3, [r0]           # read value at counter
    adds r2, r3, #1         # +1
    str  r2, [r0]           # write back
    mov  r0, #0             # exit code 0 (exit() reads r0!)
    mov  r7, #1             # exit syscall
    svc  0
    .size _start, .-_start

    .section .data
counter:
    .word 41
```

```bash
apk add lld qemu-arm            # Alpine; Debian/Ubuntu: qemu-user (lld ships ld.lld for the cross-link)
clang --target=armv7-linux-gnueabihf -nostdlib -static run_arm.s -o run_arm
qemu-arm ./run_arm; echo "exit=$?"    # aarch64 host cannot run ARM32 natively
```

> [!INFO]- Why qemu? ARM64 hardware ≠ ARM32 execution
> Your Alpine host is **aarch64**; `run_arm` is **armv7 (32-bit)**. ARM64 CPUs can run ARM32 via the AArch32 state, but only when the kernel ships `CONFIG_COMPAT` (32-bit syscall layer). Alpine/cloud kernels often omit it → `execve` refuses the ARM32 ELF → the shell falls back to interpreting it as a script (`syntax error: unexpected word`). `qemu-arm` is user-mode emulation — it sidesteps the kernel entirely, which is why the ARM32 binary needs it on a 64-bit host.

**Prefer native? Use the aarch64 build** — runs directly, no qemu (source `Extras/assembly/run_arm64.s`):

```bash
clang --target=aarch64-linux-gnu -nostdlib -static run_arm64.s -o run_arm64
./run_arm64; echo "exit=$?"
```

Same 3-instruction load-store increment (`ldr w1,[x0] / add / str`), aarch64 registers and exit syscall (`x8=93` instead of `r7=1`).

| host | `run_arm.s` (ARM32) | `run_arm64.s` (aarch64) |
|---|---|---|
| aarch64 Linux (Alpine) | needs `qemu-arm` (kernel `CONFIG_COMPAT` often absent) | **native, just run** |
| ARM32 host | native | won't run |
| x86 host | `qemu-arm` | `qemu-aarch64` |

`objdump -d` disassembly of `run_arm.o` shows the 3-instruction increment (`ldr r3,[r0]` / `adds r2,r3,#1` / `str r2,[r0]`) — note this build emits **ARM-state** encodings (`e5903000`-style, 32-bit) unless the source carries `.thumb`; Thumb gives the `1B 68 / 5A 1C / 1A 60` bytes from The Evidence. Either state proves the load-store shape. The `.o` is *not* executable — link first (the `-nostdlib -static` step above).

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
- **Compilable sources:** `Extras/assembly/cmp_inc_x86.s` (`--target=i386-linux-gnu`), `cmp_inc_arm.s` (ARM32 Thumb, `--target=armv7-linux-gnueabihf`), `cmp_inc_arm64.s` (aarch64, `--target=aarch64-linux-gnu`)
