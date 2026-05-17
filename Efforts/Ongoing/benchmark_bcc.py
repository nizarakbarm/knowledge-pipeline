#!/usr/bin/env python3
"""
BCC Benchmark Loader
Tracepoint: sys_enter_openat
Trigger: touch /tmp/bench_test
"""

from bcc import BPF

prog = r"""
#include <linux/bpf.h>

int handle_tp(void *ctx) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 process_id = (u32)pid_tgid;
    u32 uid = (u32)bpf_get_current_uid_gid();
    
    // Check if this is our trigger file (simplified - just log all openat)
    bpf_trace_printk("BCC: openat triggered by PID %d\n", process_id);
    
    return 0;
}
"""

b = BPF(text=prog)
b.attach_tracepoint(tp="syscalls:sys_enter_openat", fn_name="handle_tp")

try:
    b.trace_print()
except KeyboardInterrupt:
    pass
