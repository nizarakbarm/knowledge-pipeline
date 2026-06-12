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
  - cr-registers
  - paging
  - cr0
  - cr3
  - cr4
  - memory-management"
---

# CR Registers

Control registers (CR0–CR4) are privileged, system‑level registers that control and report the state of the CPU’s key features, including **paging**, protection, caching, and security extensions. They can only be modified by code running at Ring 0 (kernel mode). Understanding them is essential for reverse engineering anything that touches memory management, rootkits, or virtualisation.

## Overview of the control registers

| Register | Primary Function | Relevance to Paging |
|----------|------------------|----------------------|
| **CR0**   | Enables protected mode, paging, caching, and write‑protection | **PG** (bit 31) turns paging on/off; **PE** (bit 0) must be set first; **WP** (bit 16) forces read‑only pages to fault even for supervisor |
| **CR2**   | Stores the **linear address that caused the most recent page fault** | Used by the page‑fault handler (#PF) to know which address was accessed, and whether it was a read or write |
| **CR3**   | **Page‑Directory Base Register** – holds the physical address of the top‑level page table | When paging is enabled, every virtual address is translated using the table pointed to by CR3. Also includes cache control bits (PWT, PCD) for the hierarchy |
| **CR4**   | Enables architectural extensions, many related to paging and memory protection | **PAE** (bit 5) for 36‑bit physical addresses or 64‑bit mode; **PSE** (bit 4) for large pages; **SMEP** (bit 20) / **SMAP** (bit 21) for supervisor access prevention; **PGE** (bit 7) for global pages; etc. |

## CR0 – Paging master switch and protection

Bit‑by‑bit breakdown of the paging‑relevant bits:

- **PE (bit 0, Protection Enable)** – Must be 1 for **any** paging to exist. In real mode (PE=0) paging is impossible. Setting PE=1 puts the CPU into protected mode, from which you can then enable paging.
- **PG (bit 31, Paging Enable)** – When set to 1, the CPU translates every linear address through the page tables. Clearing PG disables paging entirely (the address becomes physical, no translation).  
  🔐 *Enabling paging* typically requires a setup sequence:  
  1. Build page tables in memory.  
  2. Load CR3 with the physical address of the top‑level table.  
  3. Set CR0.PG (and optionally CR0.PE if not already).  
  4. Execute a far jump to flush the prefetch queue.
- **WP (bit 16, Write Protect)** – When set (1), the kernel **cannot** write to read‑only pages even in Ring 0. This is crucial for security and for copy‑on‑write implementations. When WP=0 (the historical default), Ring‑0 code could freely overwrite supposedly read‑only kernel pages – a favourite trick of rootkits and older kernels.

Other CR0 bits like **CD** (cache disable) and **NW** (not write‑through) control caching but are not directly paging‑related; however, they must be managed carefully when setting up page tables to avoid cache incoherency.

## CR2 – The page fault address

CR2 is a **read‑only** (by normal means) register that the CPU loads automatically with the 32‑bit or 64‑bit *linear* address that triggered a page fault (#PF). The page‑fault handler reads CR2 to determine:

- Which address the process tried to access.
- The nature of the fault (by inspecting the error code pushed onto the stack) – e.g., was it a read/write, user/supervisor, instruction fetch?

No paging‑related bits in CR2; it serves as a diagnostic.

## CR3 – The root of the paging hierarchy

CR3 contains the **physical address** of the base of the current paging structure. Its exact format depends on the mode:

- **32‑bit (non‑PAE):** CR3[31:12] points to the **Page Directory** (PDEs); bits 11:0 are flags (PWT, PCD).
- **PAE (32‑bit with physical address extension):** CR3[31:5] points to the **Page Directory Pointer Table** (PDPT); must be 32‑byte aligned.
- **64‑bit (IA‑32e):** CR3[51:12] (or [M‑1:12], where M is the physical address width) points to the **Page Map Level 4 (PML4)** table. Must be 4‑KB aligned.

The two relevant cache‑control bits in all modes:

| Bit | Name | Meaning |
|-----|------|---------|
| 3   | **PWT** (Page‑level Write‑Through) | If set, hierarchy uses write‑through caching |
| 4   | **PCD** (Page‑level Cache Disable) | If set, caching is disabled for the hierarchy |

These bits can be overridden by individual page table entries.

**Context‑switch relevance:** Every time the OS switches to a different process (or kernel context), it loads a new value into CR3. This is how virtual memory spaces are isolated. By observing CR3 writes in a debugger (e.g., `MOV CR3, RAX`), you can spot process switches.

## CR4 – Extensions and paging options

CR4 is a **bitfield** of optional architectural features. The most important paging‑related bits:

| Bit | Name | Description |
|-----|------|-------------|
| 4   | **PSE** (Page Size Extensions) | Enables 4‑MB pages in 32‑bit mode (or 2‑MB pages with PAE). |
| 5   | **PAE** (Physical Address Extension) | Enables the 3‑level (PDPT‑PD‑PT) paging structure in 32‑bit mode that supports 36‑bit physical addresses. In 64‑bit mode, PAE is **mandatory** and always set. |
| 7   | **PGE** (Page Global Enable) | Allows individual pages to be marked *global*; such pages are not flushed from the TLB when CR3 is reloaded, improving performance for kernel pages shared across processes. |
| 14  | **PCID** (Process‑Context Identifiers) | Allows tagging TLB entries with a Process‑Context ID, so they can be retained even when CR3 is changed (when the same process is later restored). |
| 17  | **OSXSAVE** | Indicates the OS supports XSAVE/XRSTOR; indirectly related to memory context saving (but not paging). |
| 20  | **SMEP** (Supervisor Mode Execution Prevention) | Prevents Ring‑0 code from executing instructions on a page marked as *user‑mode* (U/S=1). Mitigates privilege‑escalation exploits. |
| 21  | **SMAP** (Supervisor Mode Access Prevention) | Prevents Ring‑0 code from reading/writing user‑mode pages unless `EFLAGS.AC` is set (or the access is done with wrappers like `STAC`/`CLAC`). Catches kernel bugs/exploits. |
| 22  | **PKE** (Protection Keys for Userspace) | Associates a 4‑bit protection key with user pages, allowing fine‑grained read/write permissions without modifying page tables. |
| 23  | **CET** (Control‑flow Enforcement Technology) | Enables shadow stacks for indirect branch tracking (though more related to control flow than classic paging). |

**Security focus:** When reverse‑engineering modern kernel code (or malware that hooks the kernel), you will often see code reading CR4 to confirm that SMEP/SMAP are disabled (or enabling them to harden the system).

## The bigger picture: how these registers enable paging

1. **Bootstrapping:** The firmware (firmware or bootloader) initially runs in real mode (or flat protected mode without paging). The OS kernel prepares page tables and then sets CR3 to the physical base address of the top‑level table.
2. **Enabling:** CR4.PAE is set (if needed), CR0.PE=1, and then CR0.PG is set. The instruction after `MOV CR0, EAX` (the one that enables paging) must be the same physical and virtual address, so a branch is taken to synchronise.
3. **Translation:** Once PG=1, every memory access goes through the tables rooted at CR3. The CPU walks the hierarchy (PML4 → PDPT → PD → PT) using parts of the virtual address as indices, checking permissions at each level (e.g., supervisor‑only bits, no‑execute bit).
4. **Protection enforcement:**  
   - If a page fault occurs (missing page, protection violation), the CPU saves the faulting address in CR2 and invokes the #PF handler.  
   - CR4.SMEP/SMAP add extra layers – they prevent the kernel from executing user pages or accessing them carelessly.

## Why these registers matter in reverse engineering

- **Rootkit analysis:** Many rootkits patch the kernel by remapping physical pages. You can spot them by watching for unexpected `MOV CR3` instructions or by checking the current CR0.WP bit (if WP is cleared, the kernel can modify read‑only memory silently).
- **Unpacking / dynamic code generation:** Packers that use virtual memory tricks (e.g., allocating memory, writing code, then executing) rely on page table manipulations; breaking on CR3 writes or CR4 modifications can reveal memory‑mapping activity.
- **Virtual machine detection:** Some anti‑debug/anti‑VM checks read CR0 or CR4 bits to detect being inside a hypervisor (e.g., checking the timing of `MOV CRx` instructions).
- **Exploit development:** Understanding CR2 helps when writing shellcode that triggers a page fault to probe kernel addresses, and CR4.SMEP is a critical mitigation to bypass.

## Quick reference table for the key bits

| Register | Bit(s) | Name | Description | Paging role |
|----------|--------|------|-------------|-------------|
| CR0 | 0 | PE | Protection Enable | Must be 1 for paging |
| CR0 | 16 | WP | Write Protect | Prevents even supervisor from writing read‑only pages |
| CR0 | 31 | PG | Paging Enable | Turns on address translation |
| CR2 | all | PFLA | Page Fault Linear Address | Stores faulting address for #PF handler |
| CR3 | 12‑51 | PDB | Page Directory Base | Physical address of top‑level paging structure |
| CR4 | 4 | PSE | Page Size Extensions | Large pages (4 MB / 2 MB) |
| CR4 | 5 | PAE | Physical Address Extension | Enables extended page tables (mandatory for 64‑bit) |
| CR4 | 20 | SMEP | Supervisor Mode Execution Prevention | Stops kernel from executing user‑mode code |
| CR4 | 21 | SMAP | Supervisor Mode Access Prevention | Stops kernel from accessing user‑mode data (unless AC) |

If you’d like to examine a concrete example (e.g., a disassembly snippet of setting up paging, or a page‑fault handler that uses CR2), let me know and I can search your workspace for relevant notes or dummy code to annotate!
