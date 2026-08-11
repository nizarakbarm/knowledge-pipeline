# run_arm64.s — AArch64 executable demo of the load-store increment
# Increment a .data counter via ldr/add/str, then exit(0).
# Native on aarch64 hosts — no qemu needed. Syscall: x8=93 (exit), svc 0.
    .section .text
    .global _start
    .type _start, %function
_start:
    ldr  x0, =counter
    ldr  w1, [x0]           // read value at counter
    add  w1, w1, #1         // +1
    str  w1, [x0]           // write back
    mov  x8, #93            // exit syscall (aarch64)
    svc  0
    .size _start, .-_start

    .section .data
counter:
    .word 41
