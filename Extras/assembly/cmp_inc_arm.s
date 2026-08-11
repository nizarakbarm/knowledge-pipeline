# cmp_inc_arm.s — ARM32 (Thumb), as disassembled:
#   01: 1B 68   LDR R3, [R3]     read value at address R3
#   02: 5A 1C   ADDS R2, R3, #1  add 1
#   03: 1A 60   STR R2, [R3]     write back to address R3
# RISC load-store: memory touched only via LDR/STR.
@ NOTE: disassembly reuses R3 for both data and address (decompiler quirk);
# a hand-written version would keep the pointer in a separate register.
    .syntax unified
    .thumb
    .section .text
    .global inc_mem
    .type inc_mem, %function
    .thumb_func
inc_mem:
    ldr  r3, [r3]           @ 1B 68 - read value at [R3]
    adds r2, r3, #1         @ 5A 1C - +1
    str  r2, [r3]           @ 1A 60 - write back
    bx   lr
    .size inc_mem, .-inc_mem
