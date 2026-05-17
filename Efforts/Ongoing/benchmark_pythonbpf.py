#!/usr/bin/env python3
"""
Python-BPF Benchmark Loader
Tracepoint: sys_enter_openat
Trigger: touch /tmp/bench_test
"""

import sys
sys.path.insert(0, '/root/pythonbpf/lib/python3.13/site-packages')

from pythonbpf import bpf, section, bpfglobal, BPF
from pythonbpf.helper import pid, uid
from pythonbpf.utils import trace_pipe
from ctypes import c_void_p, c_int32

@bpf
@section("tracepoint/syscalls/sys_enter_openat")
def handle_tp(ctx: c_void_p) -> c_int32:
    process_id = pid()
    user_id = uid()
    print(f"Python-BPF: openat triggered by PID {process_id}")
    return c_int32(0)

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

b = BPF()
b.load()
b.attach_all()
trace_pipe()
