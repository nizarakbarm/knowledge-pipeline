#!/usr/bin/env python3
"""
Create atomic notes from Open Notebook research results
Follows LYT principles and Ideaverse frontmatter standards
"""
import json
import os
from pathlib import Path

VAULT = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5"

# Read all research results
results = {}
for i in range(8):
    f = f"/tmp/q{i}.json"
    if os.path.exists(f):
        with open(f) as fh:
            data = json.load(fh)
            results[data['question']] = data['answer']

print(f"Loaded {len(results)} research results")

# Define notes
notes = []

# Note 1: x86 Processor Modes
q = "What are the two modes of x86 processor and what are the differences between them?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/x86-processor-modes.md",
        "title": "x86 Processor Modes",
        "content": results[q],
        "tags": ["x86", "processor-modes", "real-mode", "protected-mode", "long-mode"],
        "up": "[[x86 Architecture]]",
        "related": ["[[ring-levels]]", "[[general-purpose-registers]]", "[[eflags-and-eip]]", "[[cr-registers]]", "[[msr]]", "[[x86-data-types]]"]
    })

# Note 2: Ring Levels
q = "What are the ring levels in x86/x64 architecture and what is the usage of each ring level?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/ring-levels.md",
        "title": "Ring Levels",
        "content": results[q],
        "tags": ["x86", "ring-levels", "privilege", "kernel", "user-mode"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[general-purpose-registers]]", "[[cr-registers]]", "[[msr]]"]
    })

# Note 3: General Purpose Registers
q = "How many general purpose registers (GPR) are there in x86/x64? What are the types based on bit division (8-bit, 16-bit, 32-bit, 64-bit) and what is the purpose of each register?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/general-purpose-registers.md",
        "title": "General Purpose Registers",
        "content": results[q],
        "tags": ["x86", "registers", "gpr", "eax", "rax", "assembly"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[ring-levels]]", "[[eflags-and-eip]]", "[[x86-data-types]]"]
    })

# Note 4: EFLAGS and EIP
q = "What is the EFLAGS register and what are its key flags?"
eflags_content = results.get(q, "")
q2 = "What is EIP (Instruction Pointer) and what is its role?"
eip_content = results.get(q2, "")
if eflags_content or eip_content:
    combined = ""
    if eflags_content:
        combined += f"## EFLAGS Register\n\n{eflags_content}\n\n"
    if eip_content:
        combined += f"## EIP (Instruction Pointer)\n\n{eip_content}\n\n"
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/eflags-and-eip.md",
        "title": "EFLAGS and EIP",
        "content": combined,
        "tags": ["x86", "eflags", "eip", "rip", "control-registers", "flags"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[general-purpose-registers]]", "[[cr-registers]]", "[[msr]]"]
    })

# Note 5: CR Registers
q = "What are CR registers (CR0, CR3, CR4) and how do they relate to paging?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/cr-registers.md",
        "title": "CR Registers",
        "content": results[q],
        "tags": ["x86", "cr-registers", "paging", "cr0", "cr3", "cr4", "memory-management"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[ring-levels]]", "[[eflags-and-eip]]", "[[msr]]"]
    })

# Note 6: MSR
q = "What are MSR (Model Specific Registers) and what are they used for?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Atlas/Dots/Things/x86-Architecture/msr.md",
        "title": "MSR",
        "content": results[q],
        "tags": ["x86", "msr", "model-specific-registers", "kernel", "hardware"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[ring-levels]]", "[[cr-registers]]", "[[eflags-and-eip]]"]
    })

# Note 7: x86 Data Types
q = "What are the common data types in x86/x64 assembly (byte, word, dword, qword)?"
if q in results:
    notes.append({
        "path": f"{VAULT}/Library/Tech/Reverse Engineering/x86-data-types.md",
        "title": "x86 Data Types",
        "content": results[q],
        "tags": ["x86", "data-types", "assembly", "byte", "word", "dword", "qword"],
        "up": "[[x86 Architecture]]",
        "related": ["[[x86-processor-modes]]", "[[general-purpose-registers]]", "[[x86-data-types]]"]
    })

# Create MOC
moc_path = f"{VAULT}/Atlas/Maps/Reverse Engineering MOC.md"
moc_content = """# Reverse Engineering MOC

Map of Content for reverse engineering and x86 architecture knowledge.

## x86 Architecture

- [[x86-processor-modes]] - Real, Protected, and Long Mode
- [[ring-levels]] - Privilege rings 0-3
- [[general-purpose-registers]] - GPR set and bit divisions
- [[eflags-and-eip]] - Status flags and instruction pointer
- [[cr-registers]] - Control registers for paging
- [[msr]] - Model Specific Registers
- [[x86-data-types]] - Assembly data types

## Resources

- Open Notebook: [reverse engineering](https://nbai.nizarakbar.com) (external source)
"""

# Write all notes
for note in notes:
    os.makedirs(os.path.dirname(note["path"]), exist_ok=True)
    frontmatter = f"""---
created: 2026-06-09
up:
  - "[[Reverse Engineering MOC]]"
related:
  - "[[x86 Architecture]]"
in:
  - "[[Library]]"
tags:
  - "{'\n  - '.join(note['tags'])}"
---

# {note['title']}

{note['content']}
"""
    with open(note["path"], "w") as f:
        f.write(frontmatter)
    print(f"Created: {note['path']}")

# Write MOC
os.makedirs(os.path.dirname(moc_path), exist_ok=True)
moc_frontmatter = """---
created: 2026-06-09
up:
  - "[[Things]]"
related:
  - "[[x86 Architecture]]"
in:
  - "[[Atlas]]"
tags:
  - "reverse-engineering"
  - "moc"
---
"""
with open(moc_path, "w") as f:
    f.write(moc_frontmatter + "\n" + moc_content)
print(f"Created: {moc_path}")

print(f"\n=== Done: {len(notes)} atomic notes + 1 MOC created ===")
