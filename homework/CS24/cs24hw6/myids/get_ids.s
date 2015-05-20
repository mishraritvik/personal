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

    # move user id location to register
    mov  8(%ebp), %ecx
    # put 24 in %eax to get user id
    mov  $24, %eax
    # make system call
    int  $0x80
    # move user id to memory location
    mov  %eax, (%ecx)

    # move group id location to register
    mov  12(%ebp), %ecx
    # put 47 in %eax to get group id
    mov $47, %eax
    # make system call
    int  $0x80
    # move group id to memory location
    mov  %eax, (%ecx)

    mov  %ebp, %esp
    pop  %ebp
    ret
