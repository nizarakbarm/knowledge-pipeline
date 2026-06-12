---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-passmanager]]"
  - "[[llvmlite-binding-engine]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - analysis
  - optimization
---

# llvmlite Analysis Utilities

Analysis utilities for LLVM optimization and code generation.

## Summary

Provides analysis passes and utilities to gather information about module structure, control flow, and execution patterns.

## Key Concepts

### Branch Probability

`BranchProbabilityInfo()` — Analyze branch probabilities
- Provides probability information for conditional branches
- Used by optimization passes to make informed decisions

### Block Frequency

`BlockFrequencyInfo()` — Analyze basic block execution frequency
- Estimates how often each block executes
- Used for hot/cold code partitioning

### Loop Analysis

`LoopInfo()` — Analyze loop structure
- Identifies natural loops in control flow graph
- Provides loop nesting information

### Dominator Analysis

`DominatorTree()` — Compute dominator tree
- Identifies dominance relationships between basic blocks
- Essential for many optimization passes

### Alias Analysis

`add_basic_alias_analysis_pass(pm)` — Add basic alias analysis
`add_type_based_alias_analysis_pass(pm)` — Add TBAA

## Code Example

```python
from llvmlite import binding as llvm

# Parse module
module = llvm.parse_assembly("""
define i32 @foo(i32 %n) {
entry:
  %cmp = icmp sgt i32 %n, 0
  br i1 %cmp, label %loop, label %exit

loop:
  %i = phi i32 [0, %entry], [%next, %loop]
  %next = add i32 %i, 1
  %cond = icmp slt i32 %next, %n
  br i1 %cond, label %loop, label %exit

exit:
  ret i32 0
}
""")

# Create pass manager with analysis
pm = llvm.create_pass_manager()
pm.add_loop_unroll_pass()
pm.run(module)
```

## Connections

- Used by [[llvmlite-binding-passmanager]] for optimization decisions
- Provides data for [[llvmlite-binding-engine]] code generation

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/analysis-utilities.html

Back to [[llvmlite-Binding-Layer-MoC]]
