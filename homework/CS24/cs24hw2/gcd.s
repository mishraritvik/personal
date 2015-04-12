/*
 * Assume a >= b for gcd.
 *
 * gcd(a, b):
 *     if b = 0:
 *         return a
 *     return gcd(b, remainder(a, b))
 */

.globl gcd
.text
    .align 4

gcd:
    pushl %ebp          /* Push old base pointer. */
    movl %esp, %ebp     /* Current stack is new base. */
    cmpl $0, 12(%ebp)
    movl 8(%ebp), %eax
    jz gcd_return
    // jnz gcd_resume

gcd_resume:
    xor %edx, %edx
    // movl 8(%ebp), %eax
    divl 12(%ebp)
    movl 12(%ebp), %ebx
    pushl %edx
    pushl %ebx
    call gcd
    // jnp gcd_return

gcd_return:
    movl %ebp, %esp     /* Pop local stack. */
    popl %ebp           /* Pop old base of frame. */
    ret
