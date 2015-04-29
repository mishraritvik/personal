# my_setjmp:
# puts information neccessary to reinstate execution state (stack and registers)
# into memory address provided as input.
# args:
#     8(%ebp): beginning of memory address for execution state to be saved at
.globl my_setjmp


# my_longjmp:
# restores information saved by my_setjmp in order to reinstate execution state.
# args:
#     8(%ebp): beginning of memory address where execution state is saved.
#     12(%ebp): return value.
.globl my_longjmp


my_setjmp:
  # push old base pointer and make current stack new base
  push  %ebp
  mov   %esp, %ebp

  # move arg (mem location where execution state should go) into register
  mov   8(%ebp), %eax

  # put stack pointer at first position in execution state memory
  mov   %esp, (%eax)

  # put base pointer at second position in execution state memory
  # have to move base pointer to register in order to move to memory
  mov   %ebp, %ecx
  mov   %ecx, 4(%eax)

  # put caller's return address at third position in execution state memory
  # have to move return address to register in order to move to memory
  mov   4(%ebp), %ecx
  mov   %ecx, 8(%eax)

  # save all callee-saved registers in execution state memory (pos 4 - 6)
  mov   %ebx, 12(%eax)
  mov   %esi, 16(%eax)
  mov   %edi, 20(%eax)

  # Set eax (return val) to 0
  mov   $0, %eax

  # pop local stack and old base pointer
  mov   %ebp, %esp
  pop   %ebp
  ret


my_longjmp:
  # push old base pointer and make current stack new base
  push  %ebp
  mov   %esp, %ebp

  # get address of memory block into register
  mov   8(%ebp), %eax

  # put back stack pointer and return address
  mov   (%eax), %esp
  mov   4(%eax), %ebp

  # put caller's return address back in place
  mov   8(%eax), %ecx
  mov   %ecx, 4(%ebp)

  # put callee-saved registers values back to the original registers
  mov   12(%eax), %ebx
  mov   16(%eax), %esi
  mov   20(%eax), %edi

  # set eax (return val) to 1 (if arg is 0) or n (if arg is n)
  # put 1 in edx because cmove needs registers, cannot give it $1
  mov   $1, %ecx
  mov   12(%ebp), %eax
  test  $0, %eax
  cmove %ecx, %eax

  # pop local stack and old base pointer
  mov   %ebp, %esp
  pop   %ebp
  ret
