# cmp_inc_x86.s — x86 (32-bit, Intel syntax)
# Single-instruction memory increment: CISC direct memory operand.
# Encoding: FF 00  =  inc dword ptr [eax]
    .intel_syntax noprefix
    .section .text
    .global inc_mem
    .type inc_mem, @function
inc_mem:
    inc dword ptr [eax]     # FF 00 — read-modify-write in ONE instruction
    ret
    .size inc_mem, .-inc_mem
