/* This file contains IA32 assembly-language implementations of three
 * basic, very common math operations.
 */

/* Common Theme
 * All three of these implementation avoid using jumps; instead, they use
 * compare and test. There are two reasons for this. One is that jumps are
 * slower than these operations. The other is that jumps change the execution
 * time for the code depending on the input, while using compare and test means
 * that every line is still executed, keeping the run time constant.
 */

    .text

/*====================================================================
 * int f1(int x, int y)
 *
 * This operation does min(x, y), returning x if x < y, and y if
 * y <= x.
 * Does this by initially putting y in eax, then if y > x it puts x in eax.
 */
.globl f1
f1:
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %edx   /* Move x to edx. */
	movl	12(%ebp), %eax  /* Move y to eax. */
	cmpl	%edx, %eax      /* Set ZF if eax > edx. */
	cmovg	%edx, %eax      /* If ZF, put edx in eax. */
	popl	%ebp
	ret


/*====================================================================
 * int f2(int x)
 *
 * This operation does abs(x), returning x if x is non-negative and -x if
 * x is negative.
 * Does this by xor-ing with all 1's if negative (switches every bit) or all
 * 0's if positive (does nothing) then adds 1 if negative and adds 0 if
 * positive. Since the way to negate is switching every bit and adding 1, this
 * exactly accomplishes that.
 */
.globl f2
f2:
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax   /* Move x to eax. */
	movl	%eax, %edx      /* Move eax to edx. */
	sarl	$31, %edx       /* -1 if negative, 0 if positive. */
	xorl	%edx, %eax      /* If negative, flips every bit. */
	subl	%edx, %eax      /* If negative, adds 1. */
	popl	%ebp
	ret


/*====================================================================
 * int f3(int x)
 *
 * This operation does sign(x), returning -1 if x is negative and 1 if x
 * is positive.
 * By shifting right 31 times, the value becomes -1 or 0 because it is just
 * the sign bit that is kept. Then, it checks if it was 0 (meaning positive)
 * and if so puts a 1 in place of the 0. Otherwise leaves it as -1.
 */
.globl f3
f3:
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %edx   /* Move x to edx. */
	movl	%edx, %eax      /* Move edx to eax. */
	sarl	$31, %eax       /* -1 if negative, 0 if positive. */
	testl	%edx, %edx      /* 0 if edx is 0, set ZF flag */
	movl	$1, %edx        /* Set edx to 1. */
	cmovg	%edx, %eax      /* If ZF was set, move 1 to eax. */
	popl	%ebp
	ret

