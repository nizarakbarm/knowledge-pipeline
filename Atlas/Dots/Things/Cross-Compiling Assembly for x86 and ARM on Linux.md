---
created: 2026-08-10
up:
  - "[[Reverse Engineering MOC]]"
related:
  - "[[x86-processor-modes]]"
in:
  - "[[Atlas]]"
tags:
  - assembly
  - cross-compilation
  - linux
  - toolchains
  - development
---

# Cross-Compiling Assembly for x86 and ARM on Linux

## Summary

**Cross-compilation** generates machine code for a target architecture different from the host. On Linux, two toolchain families handle this: GNU cross binutils/gcc (separate tools per architecture) and LLVM/Clang (single driver with multiple backends). Both produce valid object files or executables from the same assembly source.

## Key Points

- **Target triple** format: `<arch>-<vendor>-<os>-<abi>` (e.g., `x86_64-linux-gnu`, `aarch64-linux-gnu`)
- **GNU approach**: Install architecture-specific `binutils-<target>` and `gcc-<target>` packages; invoke `<target>-as`, `<target>-ld`
- **LLVM approach**: Single `clang` binary with `--target=<triple>` flag; no additional packages for supported architectures
- **Cross-running** (executing ARM binaries on x86 host) requires **qemu-user** — separate from cross-compilation

## Details

### Option A: GNU Cross Toolchains

GNU binutils provides separate assembler and linker binaries per target:

```bash
# Install ARM64 cross toolchain (Debian/Ubuntu)
sudo apt install binutils-aarch64-linux-gnu gcc-aarch64-linux-gnu

# Assemble for ARM64
aarch64-linux-gnu-as foo.s -o foo.o

# Link
aarch64-linux-gnu-ld foo.o -o foo_arm

# x86_64: native tools
as foo.s -o foo.o
ld foo.o -o foo_x86

# 32-bit x86: add -m32 + multilib
gcc -m32 -c foo.s -o foo.o
```

> [!NOTE]- When to use GNU cross toolchains
> - Building **complete binaries** (objects + linking + libraries)
> - Need GCC-specific features (e.g., `__attribute__`, inline asm integration)
> - Prefer stable, well-tested toolchain for production builds

### Option B: LLVM/Clang Multi-Target

Clang is a single binary that compiles to multiple architectures via the `--target` flag:

```bash
# Assemble for ARM64 (no extra packages needed)
clang --target=aarch64-linux-gnu -c foo.s -o foo.o

# Assemble for x86_64
clang --target=x86_64-linux-gnu -c foo.s -o foo.o

# Also works for eBPF
clang --target=bpf -c foo.bpf -o foo.bpf.o
```

> [!NOTE]- When to use LLVM/Clang
> - Compiling **assembly to object files** (`.s` → `.o`) — simplest path
> - Multiple architectures from one install, no package management overhead
> - eBPF targets (`--target=bpf`) — same toolchain family

### Running Cross-Compiled Binaries

Cross-compiling does **not** enable execution. To run ARM binaries on x86 host, use user-mode emulation:

```bash
# Install qemu-user
sudo apt install qemu-user

# Run ARM64 binary on x86_64 host
qemu-aarch64 -L /usr/aarch64-linux-gnu ./foo_arm
```

> [!WARNING]- Cross-compiling ≠ cross-running
> Cross-compilation produces binaries for the target architecture. To **execute** them on a different architecture, you need an emulator (qemu-user) or native hardware. These are separate concerns.

## Cheatsheet

| Task | GNU | LLVM/Clang |
|------|-----|------------|
| Assemble `.s` → `.o` | `<target>-as foo.s -o foo.o` | `clang --target=<triple> -c foo.s -o foo.o` |
| Link `.o` → binary | `<target>-ld foo.o -o out` | `clang --target=<triple> foo.o -o out` |
| Install | `apt install binutils-<target>` | Pre-installed or `apt install clang` |
| eBPF | N/A | `clang --target=bpf -c foo.s -o foo.o` |
| Run on different arch | N/A (need emulator) | N/A (need emulator) |

## Source

Raw material: conversation about cross-compilation mechanisms for x86 and ARM assembly on Linux, 2026-08-10.

## Connections

- **Questions raised:** How do assemblers handle architecture-specific syntax (AT&T vs Intel for x86, ARM vs AArch64)?
- **Related:** [[x86-processor-modes]] — x86 operating modes relevant to assembly
- **Applies to:** embedded systems, multi-architecture CI/CD, kernel/driver work, and any project shipping binaries for multiple ISAs
