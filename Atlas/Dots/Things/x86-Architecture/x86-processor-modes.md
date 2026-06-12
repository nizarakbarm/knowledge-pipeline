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
  - processor-modes
  - real-mode
  - protected-mode
  - long-mode"
---

# x86 Processor Modes

While the x86 architecture includes several processor modes (Real, Protected, Virtual‑8086, System Management Mode, and Long Mode), they can be **logically grouped** into two primary operating modes that form the backbone of all x86/x64 computing:

- **Real Mode** – the legacy 16‑bit environment that every x86 CPU starts in at power‑on.  
- **Protected Mode** – the modern, full‑featured 32/64‑bit environment that provides memory protection, virtual memory, and privilege rings. (Long Mode is an extension of Protected Mode, enabling 64‑bit execution.)

The other modes (VM86, SMM) are **sub‑modes** that rely on the basic framework of Real or Protected mode. For a reverse engineer, understanding the difference between Real Mode and Protected Mode is fundamental, because the same raw bytes can mean completely different things depending on which mode the CPU is in.

---

## Comparison Table

| Feature | Real Mode | Protected Mode (32‑bit) | Long Mode (64‑bit Protected) |
|---------|-----------|--------------------------|------------------------------|
| **Native bit width** | 16‑bit (registers, data bus) | 32‑bit | 64‑bit |
| **Address space** | 1 MB (20‑bit physical) via segmentation (segment × 16 + offset) | 4 GB virtual per process, physical up to 4 GB (or 64 GB with PAE) | Up to 256 TB virtual (48‑bit canonical), physical up to 4 PB |
| **Memory model** | Segmented only (CS, DS, ES, SS) | Flat with optional segmentation; paging strongly recommended | Flat, segmentation mostly ignored (except FS/GS); paging mandatory |
| **Memory protection** | None – any program can access any address, overwrite the interrupt table, etc. | Four privilege rings (0–3), segment descriptors (limit, access rights), read/write/execute page controls | Same ring model, plus NX bit, SMEP/SMAP, and other modern protections; user/supervisor page isolation |
| **Default operand size** | 16‑bit (can prefix to 32‑bit with 0x66) | 32‑bit (can prefix to 16‑bit with 0x66) | 32‑bit (can prefix to 64‑bit with REX.W) |
| **Default address size** | 16‑bit (can prefix to 32‑bit with 0x67) | 32‑bit (can prefix to 16‑bit with 0x67) | 64‑bit (can prefix to 32‑bit with 0x67) |
| **Registers** | AX, BX, CX, DX, SI, DI, BP, SP, IP, FLAGS (16‑bit) | EAX, EBX, … EIP, EFLAGS (32‑bit) | RAX, RBX, … R8‑R15, RIP, RFLAGS (64‑bit) |
| **Paging** | Not possible | Optional (enabled via CR0.PG) – enables virtual memory, demand paging, copy‑on‑write | Mandatory (always enabled), with up to four‑level hierarchical page tables |
| **Privileged instructions** | All instructions can be executed (no concept of user/kernel) | `LGDT`, `MOV CRX`, `CLI`, `STI`, etc. only at CPL=0 | Same, with additional protected instructions (`SWAPGS`, `WRMSR` with some restrictions) |
| **Interrupt handling** | IVT (Interrupt Vector Table) at physical 0x0000: vector → CS:IP | IDT (Interrupt Descriptor Table) in kernel memory, can specify privilege level and trap/interrupt gate type | Same IDT with 64‑bit extended gates (IST for stack switching, etc.) |
| **Multitasking** | None built‑in (single‑tasking or cooperative) | Hardware task switching via TSS (rarely used); software context switching via stack manipulation | Same TSS structure but used primarily for stack switching (IST); software context switching dominant |
| **Typical use** | Bootloaders, BIOS calls, legacy DOS applications | Modern 32‑bit operating systems (Windows 9x/NT, Linux 32‑bit), many user‑mode applications | Current 64‑bit operating systems and applications; runs 32‑bit code in Compatibility Mode |
| **Entry point after reset** | Real mode; code at `FFFFFFF0h` (or `FFFF0h`) starts executing with CS=0xF000, IP=0xFFF0 | Must be entered from real mode by setting CR0.PE then far jump | Must be entered from protected mode by setting EFER.LME, CR0.PG, then far jump |

---

## Key details for reverse engineering

### 1. Real mode code vs. Protected mode code
Because the default operand size differs, the same opcode sequence may disassemble differently. For example:
- `B8 90 90 90 90` in real mode → `MOV AX, 0x9090` (2‑byte immediate) and next instruction at offset +3.  
- Same bytes in 32‑bit protected mode → `MOV EAX, 0x90909090` (4‑byte immediate) at offset +5.

A disassembler needs to know the current mode to produce correct output. In real mode, prefixes `0x66` (operand size override) and `0x67` (address size override) appear frequently when code accesses 32‑bit registers or addresses.

### 2. Segmentation vs. paging
- **Real mode** address calculation: `physical = segment_register * 16 + offset`. You’ll see a lot of segment:offset arithmetic when analyzing boot sectors or BIOS code.
- **Protected mode** (with paging off): the segment base from the GDT/LDT is added to the offset, but most OSes set base=0 for a flat model. If paging is on, each linear address is further translated through the page tables rooted at CR3.

### 3. Protection boundaries
In protected mode, attempts to execute privileged instructions or access out‑of‑limit segments cause a general protection fault (#GP). In real mode, these instructions execute without fault. This difference is exploited by rootkits that temporarily drop to real mode to bypass kernel protections.

### 4. Long mode compatibility sub‑mode
Under a 64‑bit OS, 32‑bit code runs in **Compatibility Mode**, which is essentially Protected Mode (32‑bit) with the same segmentation and paging rules, but under the 64‑bit OS’s page tables. This means that when you reverse a 32‑bit application on Windows 10 x64, you’re really looking at Protected Mode instructions with 32‑bit semantics.

### 5. Mode transitions
You may see explicit mode switches in disassembly:
- **Real → Protected:** sequence of `MOV CR0, EAX` with PE bit set, followed by `JMP` to flush the prefetch queue.
- **Protected → Long:** `MOV ECX, 0xC0000080; RDMSR; BTS EAX, 8; WRMSR` (set EFER.LME) then `MOV CR0, ...` to enable paging.

Understanding these sequences helps you identify bootloader or kernel initialisation code.

---

## Summary

The “two modes” traditionally taught are **Real Mode** and **Protected Mode**. They embody the shift from a simple, unprotected single‑tasking environment (16‑bit, 1 MB) to a modern, protected multi‑tasking environment (32‑bit or 64‑bit, virtual memory, rings). Long Mode is the 64‑bit extension of Protected Mode, retaining the same fundamental protection and paging concepts. As a reverse engineer, you need to recognise the mode to correctly interpret instructions and to understand how the runtime environment constrains the code you’re analyzing.

If you have any disassembly snippets or notes in your workspace that show these mode differences in practice, I can search for them and walk through the translation.
