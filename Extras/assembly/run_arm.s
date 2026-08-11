# run_arm.s — ARM32 executable demo of the load-store increment
# Increment a counter in .data via the 3-instruction load-store sequence,
# then exit(0). Link with -nostdlib -static; run under qemu-arm on aarch64.
    .section .text
    .global _start
    .type _start, %function
_start:
    ldr  r0, =counter
    ldr  r3, [r0]           @ read value at counter
    adds r2, r3, #1         @ +1
    str  r2, [r0]           @ write back
    mov  r7, #1             @ exit syscall
    svc  0
    .size _start, .-_start

    .section .data
counter:
    .word 41
