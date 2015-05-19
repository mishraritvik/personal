# get_ids
# Puts the user id and group id in the specified memory locations.
#
# args:
#     8(%ebp)  : memory location for user id
#     12(%ebp) : memory location for group id
#
# returns:
#     nothing. puts desired values in given memory locations.

.globl get_ids

get_ids:
    push %ebp
    mov  %esp, %ebp

    # move args to registers
    mov  8(%ebp), %ecx
    mov  12(%ebp), %edx

    # get user id, put in desired location
    # TODO
    mov  X, (%ecx)

    # get group id, put in desired location
    # TODO
    mov  X, (%edx)

    mov  %ebp, %esp
    pop  %ebp
    ret
