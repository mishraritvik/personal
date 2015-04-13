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
    cmpl $0, 12(%ebp)   /* Check if second argument is 0. */
    movl 8(%ebp), %eax  /* Move first argument to eax. */
    jz gcd_return       /* Return if second argument was 0. */
    // jnz gcd_resume   /* Otherwise recursively continue. */

gcd_resume:
    xor %edx, %edx        /* Set edx to 0. */
    divl 12(%ebp)         /* Divide first by second to get remainder. */
    movl 12(%ebp), %ebx   /* Move second argument to register. */
    pushl %edx            /* Put remainder on stack as second argument. */
    pushl %ebx            /* Put second argument on stack as first argument. */
    call gcd              /* Make recursive call. */
    // jnp gcd_return     /* Otherwise recursively continue. */

gcd_return:
    movl %ebp, %esp     /* Pop local stack. */
    popl %ebp           /* Pop old base of frame. */
    ret
