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
  - data-types
  - assembly
  - byte
  - word
  - dword
  - qword"
---

# x86 Data Types

In x86/x64 assembly language, **data types** are defined by their **size in bits** rather than by intrinsic properties like “integer” or “floating‑point.” The same register or memory location can be interpreted as a signed integer, unsigned integer, pointer, or anything else, depending on the instructions that operate on it. However, there are well‑established names for the common bit‑widths that every reverse engineer must know cold.

## The fundamental sizes

| Name           | Bit‑width | Byte‑width | Typical uses (32/64‑bit code) |
|----------------|-----------|------------|-------------------------------|
| **Byte**       | 8         | 1          | Characters (ASCII/UTF‑8), Boolean flags, small counters, byte‑packed structures |
| **Word**       | 16        | 2          | Short integers, segment selectors, legacy calls, UTF‑16 characters, some flags |
| **Doubleword** (DWORD) | 32 | 4        | Standard integers, pointers in 32‑bit mode, colour values, `int`/`long` on most 32‑bit platforms |
| **Quadword**   | 64        | 8          | Long long integers, 64‑bit pointers (`void*` in 64‑bit mode), double‑precision floating‑point, `RFLAGS` |
| **Double Quadword** (OWORD) | 128 | 16 | SSE packed integers/floats, XMM register contents, 128‑bit atomic operations |
| **TBYTE / TWORD** | 80     | 10         | x87 floating‑point registers (extended precision), legacy BCD values |
| **YMMWORD**    | 256       | 32         | AVX/AVX2 packed floats/integers (YMM registers) |
| **ZMMWORD**    | 512       | 64         | AVX‑512 packed floats/integers (ZMM registers) |

> **Note:** The “Double Quadword” (OWORD) is not formally an addressable memory unit in older x86, but modern instruction sets (SSE, AVX) bring it into common use. Byte, word, dword, and qword are the most frequent in everyday reverse engineering.

## Mnemonics and operand size specifiers

In assembly source (Intel syntax), you must often tell the assembler the size of an operand when it’s ambiguous (e.g., a memory reference that doesn’t involve a register of known width). You do this with a **size directive**:

| Directive | Size |
|-----------|------|
| `BYTE PTR`  | 1 byte |
| `WORD PTR`  | 2 bytes |
| `DWORD PTR` | 4 bytes |
| `QWORD PTR` | 8 bytes |
| `XMMWORD PTR`, `YMMWORD PTR`, etc. | 16/32/64 bytes |

Examples:
```asm
MOV  BYTE PTR [EBX], 0x41     ; store a single byte
MOV  WORD PTR [EAX], CX       ; store a 16‑bit value
MOV  DWORD PTR [ESI], EAX     ; store a 32‑bit value
CALL DWORD PTR [EBP+8]        ; call through a 32‑bit function pointer
```

In AT&T syntax, operand size is indicated by instruction suffixes: `movb` (byte), `movw` (word), `movl` (long/dword), `movq` (quadword). In disassemblers, the synthetic `mov` without suffix can be ambiguous; always check the operands to infer the width.

## How size inference works in practice

When a CPU register is one of the operands, its name usually implies the size, removing the need for a `PTR` specifier:

- **8‑bit:** `AL`, `BL`, `CL`, `DL`, `SIL`, `DIL`, `R8B`…  
- **16‑bit:** `AX`, `BX`, `CX`, `DX`, `SI`, `DI`, `R8W`…  
- **32‑bit:** `EAX`, `EBX`, `ECX`, `EDX`, `ESI`, `EDI`, `R8D`…  
- **64‑bit:** `RAX`, `RBX`, `RCX`, `RDX`, `RSI`, `RDI`, `R8`…  

For example, `MOV EAX, [ESI]` is clearly a 32‑bit load because `EAX` is a 32‑bit register. `MOV [ESI], AL` is an 8‑bit store because `AL` is 8‑bit. `MOVZX EAX, BYTE PTR [ECX]` uses `BYTE PTR` because the source is a memory byte, even though the destination `EAX` is 32‑bit.

## Endianness

x86/x64 is **little‑endian**: the least significant byte of a multi‑byte value is stored at the lowest memory address.  
For example, the dword `0x12345678` stored at address `0x1000` appears in memory as:
```
0x1000: 78
0x1001: 56
0x1002: 34
0x1003: 12
```

When you see a sequence of bytes in a disassembler’s memory dump, you must mentally reverse them (or rely on the disassembler’s view) to obtain the integer value. This is crucial when manually decoding data sections or when writing exploit payloads.

## Alignment

Modern x86 CPUs **allow** unaligned access for most data sizes (a dword can be read from an address not divisible by 4), but **alignment improves performance**. A few rules:

- **Byte** – Always aligned (any address).
- **Word** – Best when address % 2 == 0.
- **Dword** – Best when address % 4 == 0. However, unaligned dword access rarely causes a fault in user mode unless the `AC` flag and alignment checking are enabled (usually only in ring‑0).
- **Qword** – Best when address % 8 == 0.
- **SIMD (XMM/MEM128)**: Many SSE instructions **require** 16‑byte alignment when the memory operand uses aligned moves (e.g., `MOVAPS`); otherwise they cause a general‑protection fault (#GP). Unaligned versions (`MOVUPS`) do not fault but are slower.

Compilers often pad structures to guarantee natural alignment for fields, leading to dead bytes. As a reverse engineer, you can spot structure padding and infer field sizes by looking at the alignment‑driven offsets in a disassembly listing.

## Signed vs. unsigned interpretation

The processor doesn’t know whether a byte `0xFF` is signed (‑1) or unsigned (255). The instructions (and the flags they set/test) decide the interpretation:

- **Arithmetic vs. logical shifts:** `SAR` (signed) vs. `SHR` (unsigned).
- **Multiplication/division:** `IMUL`/`IDIV` (signed) vs. `MUL`/`DIV` (unsigned).
- **Conditional jumps after a comparison:**  
  `JG`/`JL` (signed) vs. `JA`/`JB` (unsigned).

So when you see a `CMP` followed by `JG`, you know the programmer treated the value as signed. If you see `JA`, they treated it as unsigned. This is a powerful clue for recovering variable types.

## Common reverse‑engineering patterns

1. **Memory access width reveals variable sizes**  
   - `movzx eax, byte ptr [ecx]` → loading an 8‑bit unsigned integer, maybe a `char`.  
   - `movsx eax, word ptr [ecx]` → loading a 16‑bit signed integer, maybe a `short`.  
   - `mov eax, [ecx]` (no prefix) → loading a 32‑bit integer or pointer.  
   - `mov rax, [rcx]` → loading a 64‑bit integer or pointer.

2. **Stack frame layout**  
   In a typical function prologue:
   ```asm
   push  ebp
   mov   ebp, esp
   sub   esp, 8
   ```
   If you later see `mov dword ptr [ebp-4], 5`, that's a 4‑byte local variable. `mov byte ptr [ebp-5], 1` is likely a 1‑byte local. By tracking the sizes, you can map out the structure of the function’s stack frame.

3. **Structure member offsets**  
   When an instruction uses an index register plus a constant offset, the constant often is the offset of a member within a structure. For example, `mov eax, [esi+14h]` might access a DWORD member at offset 0x14 in a structure that contains various smaller fields before it (bytes/words adding up to 0x14). Knowing that `dword ptr` is 4 bytes can help you guess the layout.

4. **Sign extension vs. zero extension**  
   `movzx` is used when converting an unsigned small type to a larger one; `movsx` for signed. If you see `movsx eax, byte ptr [edx]` right before an arithmetic operation, the value is likely a signed 8‑bit integer.

5. **Floating‑point operations**  
   `qword ptr` often appears with `MOVSD` or `ADDSD` to indicate a scalar double‑precision floating‑point value, while `dword ptr` with `MOVSS` is scalar single‑precision. `OWORD`/`XMMWORD ptr` with `MOVAPS`/`ADDPS` is packed single‑precision floats or integer vectors.

6. **Conditional moves and set instructions**  
   `cmovge eax, ecx` – the width (32 bits) is implied by the registers, so it’s operating on a dword.

## The “Q” suffix and new registers

In 64‑bit mode, you often see instruction suffixes like `MOVQ` (AT&T) or the use of `QWORD PTR` in Intel syntax, but many disassemblers simplify it. Also, the 8 new registers (R8‑R15) have explicit size variants (R8D for dword, R8W for word, R8B for byte). When reverse engineering 64‑bit code, you’ll quickly get used to the fact that operations on `R8` are 64‑bit unless a size override prefix (REX.W=1) implicitly makes them 64‑bit; the disassembler will typically show the proper size based on the used name.

---

If you have any notes or disassembly snippets in your workspace that feature these data types, I can search them and annotate how the sizes are used in practice. Just let me know what you’re working on!
