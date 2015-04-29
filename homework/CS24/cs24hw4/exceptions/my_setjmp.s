# my_setjmp:
# puts information neccessary to reinstate execution state (stack and registers)
# into memory address provided as input.
# args:
#     8(%ebp): beginning of memory address for execution state to be saved at
.globl my_setjmp


my_setjmp:
  # push old base pointer and make current stack new base
  push  %ebp
  mov   %esp, %ebp

  # move arg (mem location where execution state should go) into register
  mov   8(%ebp), %ecx

  # put stack pointer at first position in execution state memory block
  mov   %esp, (%ecx)

  # put base pointer at second position in execution state memory block
  # have to move base pointer to temp register (edx) in order to move to memory
  mov   %ebp, %edx
  mov   %edx, 4(%ecx)

  # save all callee-saved registers in execution state memory block (pos 3 - 6)
  mov   %ebp, 8(%ecx)
  mov   %ebx, 12(%ecx)
  mov   %esi, 16(%ecx)
  mov   %edi, 20(%ecx)

  # Set eax (return val) to 0
  mov   $0, %eax

  # pop local stack and old base pointer
  mov   %ebp, %esp
  pop   %ebp
  ret


# my_longjmp:
# restores information saved by my_setjmp in order to reinstate execution state.
# args:
#     8(%ebp): beginning of memory address where execution state is saved.
#     12(%ebp): return value.
.globl my_longjmp


my_longjmp:
  # push old base pointer and make current stack new base
  push  %ebp
  mov   %esp, %ebp

  # get address of memory block into register
  mov   8(%ebp), %ecx

  # set eax (return val) to 1 (if arg is 0) or n (if arg is n)
  mov   12(%ebp), %eax
  cmp   $0, %eax
  cmove $1, %eax

  # put back stack pointer and return address
  mov   (%ecx), %edx
  mov   4(%ecx), %esp

  # put callee-saved registers values back to the original registers
  mov   8(%ecx), %ebp
  mov   12(%ecx), %ebx
  mov   16(%ecx), %esi
  mov   20(%ecx), %edi

  # pop local stack and old base pointer
  mov   %ebp, %esp
  pop   %ebp
  ret
