---
created: 2026-02-09
up:
  - "[[PythonBPF]]"
related:
  - "[[Architecture]]"
  - "[[Python-BPF Compiler Limitations]]"
in:
  - "[[Atlas]]"
tags:
  - ebpf
  - python-bpf
  - setup
  - opensuse
  - installation
---

# PythonBPF Setup

> **Parent note**: [[PythonBPF]] — Main overview, architecture, and design rationale

## Overview

Platform-specific setup instructions for PythonBPF and pylibbpf.

**PythonBPF** generates eBPF programs directly from Python using LLVM object files ([llvmlite IR layer](https://llvmlite.readthedocs.io/en/latest/user-guide/ir/index.html)).

**Key features:**
- Maps
- Helpers
- Global definitions for BPF

**Companion project**: [pylibbpf](https://github.com/pythonbpf/pylibbpf) — Python bindings for libbpf (required for object loading and execution)

---

## Dependencies

- `bpftool`
- `clang`
- Python >= 3.8
- `pylibbpf`

```bash
pip install pythonbpf pylibbpf
```

---

## Platform-Specific Installation

### OpenSUSE

```bash
# Install system dependencies
zypper install -y bpftool clang

# Add LLVM repository
zypper addrepo -f https://download.opensuse.org/repositories/devel:/tools:/compiler/16.0/ devel_tools_compiler
zypper --gpg-auto-import-keys ref
zypper install llvm21 clang21 lld21 libclang-cpp2

# Install Python packages
pip install pythonbpf pylibbpf ctypeslib2
```

### Post-Install (All Platforms)

Generate `vmlinux.py` for your kernel:

```bash
tools/vmlinux-gen.py
```

Copy to examples directory:

```bash
cp vmlinux.py BCC-Examples/
```

---

## Verification

After installation, verify with:

```python
from pythonbpf import bpf, section, BPF
print("PythonBPF installed successfully")
```

---

## Related
- [[PythonBPF]] — Main overview and architecture
- [[Architecture]] — Detailed pipeline breakdown
- [[Python-BPF Compiler Limitations]] — Known limitations
