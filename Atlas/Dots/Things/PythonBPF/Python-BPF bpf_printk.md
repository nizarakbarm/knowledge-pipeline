---
created: 2026-05-11
up:
  - "[[eBPF MOC]]"
related:
  - "[[Architecture]]"
  - "[[Python-BPF Compiler Limitations]]"
  - "[[BCC vs Python-BPF bpf_printk Comparison]]"
in:
  - "[[Atlas]]"
tags: [ebpf, python-bpf, bpf-printk, debugging, helpers, tracing]
---

# Python-BPF bpf_printk

In Python-BPF, `bpf_printk` is called using Python's `print()` inside a `@bpf` function. The compiler remaps it to BPF helper ID 6, generates LLVM IR via `inttoptr` + variadic `call`, and output is read from `/sys/kernel/tracing/trace_pipe` using `trace_pipe()` from `pythonbpf.utils`.

## Key Points

- `print("msg")` and `print(f"val={x}")` are the only syntax needed — no import, no extra wrapper
- Hard limit: **≤ 3 format variables** per call (kernel eBPF verifier constraint, enforced at `printk_formatter.py:54`)
- Output is read with `trace_pipe()` (blocks until Ctrl+C) or `trace_fields()` (structured line parser)
- pylibbpf does **not** handle trace_pipe — that is `pythonbpf.utils`'s responsibility

## Details

### Usage Pattern

```python
from pythonbpf import BPF, bpf, section
from pythonbpf.utils import trace_pipe
from ctypes import c_void_p, c_int32

@bpf
@section("tracepoint/syscalls/sys_enter_openat")
def handler(ctx: c_void_p) -> c_int32:
    print("openat triggered")           # plain string
    print(f"PID: {pid()}")              # f-string, 1 variable
    print(f"r15={r15} r14={r14} r13={r13}")  # f-string, 3 variables (max)
    return c_int32(0)

b = BPF()
b.load_and_attach()
trace_pipe()   # blocks here; prints output as tracepoint fires
```

**Trigger (separate terminal):**
```bash
touch /tmp/test   # fires the tracepoint once
```

### How the Compiler Translates `print()`

**Registration:** `@HelperHandlerRegistry.register("print")` in `bpf_helper_handler.py:140`

When `expr_pass.py:700` encounters an `ast.Call` named `print`, it routes to `bpf_printk_emitter`:

1. **Plain string** → appends `\n\0`, stores as LLVM global constant
2. **F-string** → `printk_formatter.py` walks the `JoinedStr` AST, maps each interpolated value to a printf specifier
3. **IR emission:**
   ```
   fn_ptr = inttoptr(i64 6, fn_type*)      ; helper ID 6 = bpf_printk
   call fn_ptr(fmt_ptr, fmt_size, ...args)  ; variadic tail call
   ```

### Format Specifier Mapping

| LLVM IR type | printf specifier |
|---|---|
| `i64` | `%lld` |
| `i32` | `%d` |
| `i8*` / `char[]` | `%s` |

### Reading Output

**`pythonbpf/utils.py:4–11`**

```python
def trace_pipe():
    subprocess.run(["cat", "/sys/kernel/tracing/trace_pipe"])
    # Blocks until Ctrl+C

def trace_fields():
    # Parses each line into: (task, pid, cpu, flags, timestamp, message)
```

### Example Files in Repo

| File | What it shows |
|---|---|
| `examples/hello_world.py:13` | Minimal `print("Hello, World!")` |
| `examples/kprobes.py:8,16` | `print` inside a kprobe handler |
| `tests/passing_tests/vmlinux/register_state_dump.py:32–38` | F-string with multiple register values |

## Connections

- [[Architecture]] — the `print()` call sits in the AST→IR stage (Step 3 of the pipeline)
- [[Python-BPF Compiler Limitations]] — related gap: `ctx.args[0]` subscript also lives in `expr_pass.py`
