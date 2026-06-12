---
created: 2026-05-25
up:
  - "[[llvmlite-Binding-Layer-MoC]]"
related:
  - "[[llvmlite-binding-modules]]"
  - "[[llvmlite-binding-engine]]"
  - "[[llvmlite-binding-analysis]]"
in:
  - "[[Atlas]]"
tags:
  - llvmlite
  - llvm
  - bindings
  - optimization
  - pass-manager
---

# llvmlite Pass Manager

Optimization pass management for LLVM modules.

## Summary

Provides classes to configure and run optimization passes on LLVM modules before compilation or execution.

## Key Concepts

### Pass Manager

`create_pass_manager()` — Create module pass manager
`create_function_pass_manager(module)` — Create function pass manager

### Optimization Levels

`PassManagerBuilder()` — Configure optimization pipeline
- `opt_level` — Optimization level (0-3)
- `size_level` — Size optimization level (0-2)
- `populate_module_pass_manager(pm)` — Populate module passes
- `populate_function_pass_manager(pm)` — Populate function passes

### Common Passes

- `add_constant_merge_pass()` — Merge duplicate constants
- `add_dead_arg_elimination_pass()` — Remove dead arguments
- `add_function_inlining_pass()` — Inline functions
- `add_global_dce_pass()` — Dead code elimination
- `add_global_optimizer_pass()` — Optimize global variables
- `add_ipsccp_pass()` — Interprocedural sparse conditional constant propagation
- `add_dead_code_elimination_pass()` — Remove dead code
- `add_aggressive_dce_pass()` — Aggressive dead code elimination
- `add_instruction_combining_pass()` — Combine instructions
- `add_jump_threading_pass()` — Jump threading
- `add_licm_pass()` — Loop invariant code motion
- `add_loop_unroll_pass()` — Loop unrolling
- `add_loop_rotation_pass()` — Loop rotation
- `add_sccp_pass()` — Sparse conditional constant propagation
- `add_sroa_pass()` — Scalar replacement of aggregates
- `add_type_based_alias_analysis_pass()` — Type-based alias analysis
- `add_basic_alias_analysis_pass()` — Basic alias analysis

### Target-Specific Passes

`target_machine.add_analysis_passes(pm)` — Add target analysis passes

## Code Example

```python
from llvmlite import binding as llvm

# Parse module
module = llvm.parse_assembly("""
define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}
""")

# Create pass manager
pm = llvm.create_pass_manager()

# Add optimization passes
pm.add_instruction_combining_pass()
pm.add_reassociate_pass()
pm.add_gvn_pass()
pm.add_cfg_simplification_pass()

# Run passes
pm.run(module)

# Verify
module.verify()
```

## Connections

- Optimizes [[llvmlite-binding-modules]] before execution
- Used by [[llvmlite-binding-engine]] for JIT optimization
- Analysis passes from [[llvmlite-binding-analysis]]

## Source

- https://llvmlite.readthedocs.io/en/v0.46.0/user-guide/binding/optimization-passes.html

Back to [[llvmlite-Binding-Layer-MoC]]
