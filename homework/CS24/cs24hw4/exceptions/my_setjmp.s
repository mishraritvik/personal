.globl my_setjmp
.globl my_longjmp

#define OFF_ESP 0

# my_setjmp
#
# args:
#     8(%ebp) = memory location of array holding execution state.
#
# eax always has 0 at the end.

# my_longjmp
#
#
#

my_setjmp:
    push  %ebp              # standard set up
    mov   %esp, %ebp
    push  %ecx              # pushing these two as they will be used
    push  %edx
    mov   8(%ebp), %edx                # %edx = M[8 + %ebp] = address of array
    mov   %esp, (%edx)                 # M[%edx] = %esp =>
                                       # first element of int array is the
                                       # current stack pointer (do this before
                                       # we push stuff onto the stack)
    mov   %ebp, %ecx                   # Use %ecx as temp variable
    mov   %ecx, 4(%edx)                # M[%edx + 4] = M[%esp] =>
                                       # second element of int array is %ebp
    mov   4(%ebp), %ecx
    mov   %ecx, 8(%edx)                # M[%edx + 8] = retr address =>
                                       # third element of int array is the
                                       # caller's return address
    mov   %esi, 12(%edx)               # M[%edx + 12] = %esi =>
                                       # fourth element of int array is the
                                       # callee-save register %esi
    mov   %edi, 16(%edx)               # M[%edx + 16] = %edi =>
                                       # fifth element of int array is the
                                       # callee-save register %edi
    mov   %ebx, 20(%edx)               # M[%edx + 20] = %ebx =>
                                       # sixth element of int array is the
                                       # callee-save register %ebx
    mov   $0, %eax          # set eax to 0
    pop   %edx              # popping callee values back into registers
    pop   %ecx
    mov   %ebp, %esp        # stnadard ending
    pop   %ebp
    ret

my_longjmp:
    push  %ebp              # standard set up
    mov   %esp, %ebp
    movl  $1, %ecx                     # Use to possibly move 1 into %eax
    mov   8(%ebp), %edx                # %edx = M[8 + %ebp] = address of array
    mov   12(%ebp), %eax               # %eax = M[%ebp + 12] = ret
    cmpl  $0, %eax                     # See if %eax = 0
    cmove %ecx, %eax                   # If %eax = 0, make %eax = 1
    mov   12(%edx), %esi               # Restore %esi
    mov   16(%edx), %edi               # Restore %edi
    mov   20(%edx), %ebx               # Restore %ebx
    mov   4(%edx), %ebp                # Restore %ebp
    mov   (%edx), %esp                 # %esp = first element of buf array =>
                                       # restoring %esp
    mov   8(%edx), %ecx                # %ecx = M[%edx + 8] = return address
    mov   %ecx, 4(%ebp)                # Move return address to right above %ebp
    mov   %ebp, %esp                   # standard ending
    pop   %ebp
    ret
