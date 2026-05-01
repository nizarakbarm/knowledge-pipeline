---
created: 2026-05-01
up:
  - "[[LLVM MOC]]"
related:
  - "[[LLVM Modular Compiler Infrastructure]]"
in:
  - "[[Atlas/Dots/Things/LLVM]]"
tags:
  - llvm
  - license
  - apache-2.0
  - open-source
  - legal
---

# LLVM License — Apache 2.0 with LLVM Exceptions

## Summary

The LLVM project uses a customized **Apache 2.0 License with LLVM exceptions**, a deliberate legal framework that addresses two critical limitations of standard Apache 2.0: **GPLv2 compatibility** and **compiled output freedom**. This license transition from the earlier University of Illinois/NCSA Open Source License enables broader adoption across both open-source and proprietary ecosystems.

## Key Points

- **License basis**: All LLVM code — including sub-projects like **LLDB**, **BOLT**, **Clang**, **MLIR**, and **Flang** — is licensed under Apache 2.0 with project-specific exceptions
- **Historical transition**: LLVM migrated from the **University of Illinois/NCSA Open Source License** to the current Apache 2.0-based framework
- **GPLv2 compatibility exception**: Resolves the patent retaliation clause incompatibility between Apache 2.0 and GPLv2, permitting linking and combining LLVM code with GPLv2 code without violating either license
- **Compiled output exemption** ("Runtime" exception): Binaries compiled using LLVM **do not inherit** the LLVM license or attribution requirements, enabling proprietary and closed-source commercial applications without forced Apache 2.0 copyright notices

## Details

### The Two LLVM Exceptions

The standard Apache 2.0 license contains provisions that create friction in two specific scenarios critical to compiler infrastructure. LLVM's exceptions surgically remove these barriers:

**1. GPLv2 Compatibility Exception**

Standard Apache 2.0 is technically incompatible with GPLv2 due to differences in patent retaliation clauses. This creates a legal paradox: combining Apache 2.0 code with GPLv2 code potentially violates one or both licenses. LLVM's first exception explicitly permits linking and combining LLVM's Apache 2.0 code with GPLv2-licensed code, resolving this incompatibility without requiring downstream projects to relicense.

**2. Compiled Output Exemption (Runtime Exception)**

Standard open-source licenses typically impose attribution and license notice requirements on derivative works. For a compiler, this creates a problematic scenario: every binary produced by LLVM would theoretically need to carry Apache 2.0 notices. LLVM's second exception states that compiled binaries using LLVM do **not** inherit the LLVM license requirements. This means:

- Proprietary software compiled with `clang`/`lld` requires **no attribution** to LLVM
- Closed-source commercial applications face **no license contamination**
- LLVM functions as infrastructure — a tool — rather than a component whose license propagates to output

### Scope of Coverage

The license applies uniformly across the LLVM umbrella:
- Core LLVM libraries and IR
- Clang compiler frontend
- LLDB debugger
- LLD linker
- MLIR multi-level IR
- BOLT binary optimizer
- All other official sub-projects

## Connections

- **Questions this raises**: How do these exceptions compare to GCC's GPL with Runtime Library Exception? What legal risks remain when combining LLVM with other copyleft licenses beyond GPLv2?
- **Related to**: [[LLVM Modular Compiler Infrastructure]], [[Open Source Licensing]], [[GPL Compatibility]], [[Compiler Toolchains]]
- **Applies to**: Choosing compilers for proprietary products, understanding license obligations when shipping binaries, combining LLVM components with GPLv2 kernel code (e.g., Linux kernel modules)
- **Contrast with**: Standard Apache 2.0 (no exceptions), GPLv3 (strong copyleft), GCC's GPL+Runtime Library Exception

## Source

- Distilled from raw license overview data
- **Caveat**: Specific exception text not verified from primary LLVM legal documents; external knowledge supplemented. For authoritative text, consult [llvm.org](https://llvm.org) official license page or the `LICENSE.TXT` in the LLVM monorepo.