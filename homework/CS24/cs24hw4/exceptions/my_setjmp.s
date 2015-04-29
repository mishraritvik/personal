# my_setjmp:
# puts information neccessary to reinstate execution state into memory address
# provided as input. Saves ebx, esi, edi, esp, ebp, and caller's return address.
# args:
#     8(%ebp): beginning of memory address for execution state to be saved at
.globl my_setjmp


# my_longjmp:
# restores information saved by my_setjmp in order to reinstate execution state.
# this includes: ebx, esi, edi, esp, ebp, and caller's return address.
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

  # put callee-saved registers in execution state memory (pos 1 - 3)
  mov   %ebx, 0(%eax)
  mov   %esi, 4(%eax)
  mov   %edi, 8(%eax)

  # put base pointer and stack pointer in execution state memory (pos 4 - 5)
  mov   %ebp, 12(%eax)
  mov   %esp, 16(%eax)

  # put caller's return address at sixth position in execution state memory
  # have to move return address to register in order to move to memory
  mov   4(%ebp), %ecx
  mov   %ecx, 20(%eax)

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

  # put callee-saved registers values back to the original registers
  mov   0(%eax), %ebx
  mov   4(%eax), %esi
  mov   8(%eax), %edi

  # put back base pointer and stack pointer
  mov   12(%eax), %ebp
  mov   16(%eax), %esp

  # put caller's return address back
  mov   20(%eax), %ecx
  mov   %ecx, 4(%ebp)

  # set eax (return val) to 1 (if arg is 0) or n (if arg is n)
  # put 1 in ecx because cmove needs registers, cannot give it 1
  mov   $1, %ecx
  mov   12(%ebp), %eax
  cmp   $0, %eax
  cmove %ecx, %eax

  # pop local stack and old base pointer
  mov   %ebp, %esp
  pop   %ebp
  ret
