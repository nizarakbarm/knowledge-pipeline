# cmp_inc_arm64.s — AArch64 (ARM64)
# Load-store: same 3-instruction shape as ARM32, 64-bit registers.
#    ldr  w1, [x0]     read value at address X0
#    add  w1, w1, #1   add 1
#    str  w1, [x0]     write back
    .section .text
    .global inc_mem
    .type inc_mem, %function
inc_mem:
    ldr  w1, [x0]           // read value at [X0]
    add  w1, w1, #1         // +1
    str  w1, [x0]           // write back
    ret
    .size inc_mem, .-inc_mem
