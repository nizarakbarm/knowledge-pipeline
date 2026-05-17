---
created: 2026-05-11
up:
  - "[[eBPF MOC]]"
related:
  - "[[LLVM Modular Compiler Infrastructure]]"
  - "[[BCC vs Python-BPF Benchmark Plan]]"
  - "[[Architecture]]"
in:
  - "[[Atlas]]"
tags: [ebpf, python-bpf, compiler, llvm, ast, limitations]
---

# Python-BPF Compiler Limitations

Two confirmed gaps in Python-BPF's AST→IR translation layer prevent array subscripting and atomic map operations. Both failures traced to `pythonbpf/expr/expr_pass.py` — the bottleneck is not the struct definitions or the parser, but the expression evaluator.

Audit cross-validated against local repo + `vmdevnull` on 2026-05-10.

## Key Points

- **`ctx.args[0]` not supported** — `eval_expr` (lines 654–730) has no `ast.Subscript` branch; falls to `return None` at line 730; no GEP instruction emitted
- **Atomic `+=` not supported** — `op_map` at line 227 maps `ast.Add → builder.add`; zero `atomicrmw` in the entire codebase
- Both confirmed in `tests/test_config.toml` xfail registry at `level = "ir"` (IR generation failure, not `llc`)

## Details

### Limitation 1 — Array Subscript (`ctx.args[0]`)

`ctx.args[0]` parses as `Subscript(Attribute(Name('ctx'), 'args'), Constant(0))`. The `Attribute` node resolves correctly to an IR pointer to the array, but the surrounding `Subscript` wrapper has no handler in `eval_expr`:

```
ast.Name       → line 664
ast.Constant   → line 666
ast.Call       → line 668
ast.Attribute  → line 708
ast.BinOp      → line 712
ast.Compare    → line 721
ast.UnaryOp    → line 723
ast.BoolOp     → line 725
               → return None  (line 730)  ← Subscript falls here
```

The parser correctly identifies `args` as `ctypes.Array` (`class_handler.py:273–276`), and the remote `vmdevnull` vmlinux.py defines it as `ctypes.c_uint64 * 6` — both correct. The gap is exclusively in `expr_pass.py`.

**Fix:** Insert `elif isinstance(expr, ast.Subscript):` between lines 725–729, emitting `builder.gep(ptr, [idx])` followed by `builder.load`.

### Limitation 2 — Non-Atomic Map Operations

`op_map` in `expr_pass.py:226–238` maps all arithmetic operators to plain LLVM instructions:

```python
ast.Add: builder.add   # plain 'add', NOT 'atomicrmw add'
```

A map counter increment (`count += 1`) compiles to a load → add → store sequence with a race window. Between the `load` and `store`, another CPU can modify the same entry — lost updates result.

`HashMap` in `maps.py:1–27` exposes only `lookup`, `delete`, `update` — no `atomic_add` or `increment`.

BCC equivalent: `__sync_fetch_and_add(count, 1)` → single `atomicrmw add ... seq_cst` instruction.

**Fix:** Use `builder.atomic_rmw("add", ptr, val, "seq_cst")` for map value writes; add `atomic_add` method to `HashMap`.

## Connections

  - [[Kernel Memory Access BCC vs Python-BPF vs libbpf CO-RE]] — Comparison of kernel memory access approaches including Python-BPF's probe_read helper
  - [[BCC vs Python-BPF Benchmark Plan]] — benchmark scope constrained by Limitation 1 (no `ctx.args[]` access in Python-BPF program)
  - [[Architecture]] — pipeline overview of AST→IR→llc stages where these gaps sit
  - [[LLVM Modular Compiler Infrastructure]] — GEP and atomicrmw are standard LLVM IR primitives
