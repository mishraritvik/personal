/*
 * Assume a >= b for gcd.
 *
 * remainder(a, b):
 *     if a < b:
 *         return a
 *     return remainder(a - b, b)
 *
 * gcd(a, b):
 *     if b = 0:
 *         return a
 *     return gcd(b, remainder(a, b))
 */

.globl gcd
.text
    .align 4


remainder:

remainder_resume:

remainder_return:

gcd:

gcd_resume:

gcd_return:
