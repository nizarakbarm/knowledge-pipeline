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
  - msr
  - model-specific-registers
  - kernel
  - hardware"
---

# MSR

**Model‑Specific Registers (MSRs)** are a set of 64‑bit registers built into x86/x64 CPUs that allow the kernel to control and inspect low‑level processor features. Unlike general‑purpose or control registers, MSRs vary in number and function between different processor families (hence “model‑specific”). They are the primary interface for enabling extended instructions, configuring memory management, performance monitoring, power management, and security mitigations.

As a reverse engineer, you will encounter MSRs when analysing kernel‑mode code (drivers, rootkits), inspecting system‑call mechanisms, debugging performance counters, or checking for virtualisation. They are a vital layer between the hardware and the kernel, and understanding them is key to grasping how modern x86 systems really work.

---

## Accessing MSRs

- **Instructions:**  
  - `RDMSR` – read the MSR specified in `ECX` (index) into `EDX:EAX` (high : low 32 bits).  
  - `WRMSR` – write `EDX:EAX` into the MSR specified in `ECX`.

- **Privilege:** These are **privileged** instructions; they can only be executed when `CPL = 0` (ring 0). Attempting to execute them in user mode raises a general protection fault (#GP).

- **Indexing:** Each MSR has a unique 32‑bit address. These addresses are documented in the Intel/AMD software developer manuals, but they may differ between models or be implementation‑specific for certain debug MSRs.

- **User‑mode access:** On Linux, the `msr` kernel module allows user‑space tools to read/write MSRs via `/dev/cpu/*/msr` (root only). Performance‑monitoring MSRs are also exposed through the `perf_event_open` syscall.

---

## Major categories of MSRs

| Category | Purpose | Examples |
|----------|---------|----------|
| **Control & status** | Enable fundamental architecture modes (IA‑32e, NX, SYSCALL), set up system‑call targets, control cache behaviour | `IA32_EFER`, `IA32_STAR`, `IA32_LSTAR`, `IA32_SFMASK`, `IA32_SYSENTER_CS/EIP/ESP` |
| **Memory management** | Define memory type ranges (MTRRs), page attribute table (PAT), control speculative execution / prefetching | `IA32_MTRR_PHYSBASEn`, `IA32_MTRR_PHYSMASKn`, `IA32_PAT`, `IA32_CR_PAT` |
| **Performance monitoring** | Select events to count, read performance counters, set up fixed‑function counters | `IA32_PERFEVTSELn`, `IA32_PMCn`, `IA32_FIXED_CTR_CTRL`, `IA32_PERF_GLOBAL_CTRL` |
| **Local APIC & interrupts** | Configure the local Advanced Programmable Interrupt Controller (APIC), set timer, handle IPIs | `IA32_APIC_BASE`, `IA32_X2APIC_*` (e.g., ID, LVT, EOI) |
| **Debugging & tracing** | Store last branch records (LBR), branch trace store (BTS), data breakpoints, processor trace | `MSR_LBR_SELECT`, `MSR_LASTBRANCH_n_FROM_IP`, `MSR_LASTBRANCH_n_TO_IP` |
| **Power & thermal management** | Control P‑states (frequency), C‑states (idle), turbo boost, voltage | `IA32_PERF_STATUS`, `IA32_PERF_CTL`, `MSR_TURBO_RATIO_LIMIT` |
| **Virtualisation (VMX)** | Set VMX operation fields, manage virtual machine control structure (VMCS) pointer, handle VM exits/entries | `IA32_VMX_BASIC`, `IA32_VMX_PINBASED_CTLS`, `IA32_VMX_PROCBASED_CTLS`, guest/host state selectors |
| **Security mitigations** | Enable firmware‑based defence against speculative execution attacks (Spectre, Meltdown) | `IA32_SPEC_CTRL`, `IA32_PRED_CMD`, `IA32_ARCH_CAPABILITIES` |
| **Miscellaneous** | Time stamp counter (TSC), platform information, microcode update, BIOS‑configurable features | `IA32_TIME_STAMP_COUNTER`, `IA32_PLATFORM_ID`, `IA32_BIOS_UPDT_TRIG` |

---

## Key MSRs a reverse engineer should know

Below are some of the most commonly encountered MSRs, their indices (where standardised), and their use.

| MSR name | Index (hex) | Role |
|----------|-------------|------|
| **IA32_EFER** | `0xC0000080` | **Extended Feature Enable Register** – controls `LME` (Long Mode Enable, bit 8), `SCE` (SYSCALL Enable, bit 0), `NXE` (No‑Execute Enable, bit 11). You must enable this to enter 64‑bit mode and to use the `SYSCALL` instruction. |
| **IA32_STAR** | `0xC0000081` | **System call target address** – stores the 48‑bit `SYSCALL` entry point and the CS/SS selectors for return. In 64‑bit mode, the high 32 bits hold the kernel `CS`/`SS`, the low 32 bits hold the user `CS`/`SS`. |
| **IA32_LSTAR** | `0xC0000082` | **Long System Call Target Address** – the 64‑bit `RIP` loaded on `SYSCALL`. On `SYSRET`, the CPU returns to whichever address the kernel placed in `RCX` before executing `SYSRET`. |
| **IA32_CSTAR** | `0xC0000083` | **Compatibility System Call Target Address** – used for 32‑bit compatibility mode calls via `SYSCALL`. Rarely relevant on modern 64‑bit systems. |
| **IA32_FMASK** | `0xC0000084` | **Flags Mask** – a mask applied to `RFLAGS` when entering the kernel via `SYSCALL`, typically clearing `IF`, `TF`, `DF`, etc. |
| **IA32_SYSENTER_EIP** | `0x176` | **Legacy SYSENTER entry point** – used by 32‑bit kernels (and some 64‑bit ones) to handle `SYSENTER` calls. |
| **IA32_APIC_BASE** | `0x1B` | **APIC Base Address** – holds the physical base of the local APIC registers and the global enable bit (bit 11). Rootkits sometimes relocate the APIC to hide or intercept interrupts. |
| **IA32_MTRR_DEF_TYPE** | `0x2FF` | **Default memory type** – defines the caching behaviour (uncacheable, write‑back, etc.) for physical regions not covered by the fixed‑range MTRRs. Often manipulated by drivers to map device memory. |
| **IA32_PAT** | `0x277` | **Page Attribute Table** – extends the caching control offered by the `PWT`/`PCD` bits in page tables, allowing finer granularity (8 types) per page. |
| **IA32_PERF_GLOBAL_CTRL** | `0x38F` | **Performance counter enable** – per‑core control that enables each of the general‑purpose or fixed‑function performance counters. Useful for profiling. |
| **IA32_SPEC_CTRL** | `0x48` | **Speculation Control** – used to mitigate Spectre/Meltdown; sets the Indirect Branch Restricted Speculation (IBRS) and Single Thread Indirect Branch Predictors (STIBP) bits. |
| **IA32_VMX_BASIC** | `0x480` | **VMX capabilities** – reports whether VMX is supported, size of VMCS region, etc. |

---

## MSRs in reverse engineering: real‑world scenarios

1. **System‑call tracing**  
   When you disassemble kernel initialisation code (e.g., `nt!KiSystemStartup` on Windows), you will see `WRMSR` setting `IA32_LSTAR` to `KiSystemCall64`. If a rootkit wants to intercept all system calls, it can replace this value with its own handler. Watching for `WRMSR` to that address is a classic kernel‑debugging technique.

2. **Rootkit detection**  
   Rootkits often modify `IA32_SYSENTER_EIP`, `IA32_LSTAR`, or `IA32_EFER` (to disable NX). By dumping these MSRs (e.g., using `rdmsr` in a kernel debugger) and comparing to known‑good values, you can spot tampering. For example, if `IA32_EFER.NXE` is cleared, the kernel loses its ability to mark memory as non‑executable, making buffer‑overflow exploits easier.

3. **Virtualisation analysis**  
   VM‑aware malware or anti‑debug tools may read VMX‑related MSRs (like `IA32_VMX_BASIC`) to detect if they are running inside a hypervisor. Alternatively, a hypervisor (like Hyper‑V or KVM) sets certain MSRs to control guest behaviour. Seeing unexpected values in these registers can reveal a virtualised environment.

4. **Performance profiling**  
   During reverse engineering of a complex algorithm, you might use hardware performance counters to identify hotspots. Understanding the MSR interface allows you to program these counters directly or interpret what a tool (like `perf` or Intel VTune) is doing.

5. **Firmware and boot analysis**  
   BIOS/UEFI and early boot code configure MTRRs and the PAT to set up memory caching rules before the OS loads. By tracing these MSR writes, you can understand how physical memory is mapped and debug DMA or memory‑corruption issues.

6. **Security mitigation bypass**  
   Exploit developers study `IA32_SPEC_CTRL` and similar MSRs to find ways to bypass speculative‑execution protections. Understanding these MSRs is vital for evaluating the effectiveness of a security patch.

---

## Security considerations

- **Lock bits:** Many control MSRs have bits that can be set to **lock** the current configuration until the next reset. For example, `IA32_FEATURE_CONTROL` has a lock bit that, once set, prevents any further changes to the register. This is used by BIOS to prevent malicious kernel code from disabling VMX or SMX after boot.

- **Privilege check:** As noted, `RDMSR`/`WRMSR` require `CPL=0`. However, a hypervisor can intercept these instructions and emulate them, altering what the guest kernel “sees”. This is the basis of nested virtualisation and also a potential hooking point for anti‑cheat systems.

- **Side‑channel attacks:** Some MSRs (like `IA32_ARCH_CAPABILITIES`) advertise hardware’s ability to mitigate side‑channel attacks. A missing or unexpected MSR value can indicate a system is vulnerable.

---

## Quick reference: how to dump MSRs

- **Windows kernel debugger (WinDbg):**  
  ```
  rdmsr <index>
  ```
- **Linux command line (with `msr‑tools`):**  
  ```bash
  rdmsr <index>
  wrmsr <index> <value>
  ```
- **Live kernel debugger (e.g., livekd) or via `/dev/cpu/*/msr`** (with `sudo modprobe msr`).

---

MSRs are the “backstage” controls of the CPU. While user‑mode code never sees them directly, they shape every aspect of execution – from the memory map to the speed of each instruction. In reverse engineering, the ability to read, interpret, and reason about MSR values separates a surface‑level analysis from a deep, hardware‑aware investigation.

If you have any specific MSR‑related reverse‑engineering examples in your workspace (like a rootkit that hooks `LSTAR` or a driver tweaking MTRRs), I can search for them and walk through what’s happening in the code. Otherwise, this overview should give you a solid foundation for the next step in your studies!
