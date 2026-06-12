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
  - profiling
  - pass-timings
---

# llvmlite Pass Timings

Pass execution timing and profiling for LLVM optimization pipeline.

## Summary

Provides utilities to measure and report the execution time of individual optimization passes.

## Key Concepts

### Timing Infrastructure

`set_pass_timings_enabled(enabled)` — Enable/disable pass timing
- `enabled` — Boolean to toggle timing collection

`get_pass_timings()` — Retrieve timing results
- Returns structured timing data

### Timing Report Format

Pass timings include:
- Pass name
- Execution time (wall clock and CPU time)
- Call count
- Per-invocation averages

### Usage Pattern

```python
from llvmlite import binding as llvm

# Enable timing
llvm.set_pass_timings_enabled(True)

# Run optimization pipeline
pm = llvm.create_pass_manager()
pm.add_instruction_combining_pass()
pm.add_gvn_pass()
pm.run(module)

# Get timing report
timings = llvm.get_pass_timings()
print(timings)
```

## Performance Analysis

Pass timings help identify:
- Bottlenecks in optimization pipeline
- Expensive passes that may be optional
- Trade-offs between optimization level and compile time

## Connections

- Works with [[llvmlite-binding-passmanager]] optimization passes
- Helps tune [[llvmlite-binding-engine]] JIT compilation speed

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/pass_timings.html

Back to [[llvmlite-Binding-Layer-MoC]]
