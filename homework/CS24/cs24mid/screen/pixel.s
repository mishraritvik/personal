# draw_pixel:
#     draws given pixel by putting value in array
# args:
#     8(%ebp)  : pointer to screen object
#     12(%ebp) : x value of location of pixel
#     16(%ebp) : y value of location of pixel
#     20(%ebp) : color value of pixel
#     21(%ebp) : depth value of pixel
# rets:
#     none.

.globl draw_pixel

draw_pixel:
    # set up stack frame
    push %ebp
    mov  %esp, %ebp

    # save callee-saved registers
    push %ebx
    push %esi
    push %edi

    # move screen, x, y to registers
    mov 8(%ebp), %eax   # screen
    mov 12(%ebp), %ebx  # x
    mov 16(%ebp), %ecx  # y

    # move width, height to registers
    mov  0(%eax), %esi  # width
    mov  4(%eax), %edi  # height

    # temporarily push on stack and pop later
    push %eax
    mov  $0, %eax

    # check that x is valid
    cmp  %ebx, %esi
    jle  draw_done      # go to done if width <= x

    cmp %ebx, %eax
    jg  draw_done       # go to done if 0 > x

    # check that y is valid
    cmp  %ecx, %edi
    jle  draw_done      # go to done if height <= y

    cmp %ecx, %eax
    jg  draw_done       # go to done if 0 > y

    # popping after temporary push
    pop  %eax

    # compute 1D location of pixel (width * y + x)
    imul %esi, %ecx
    add  %ebx, %ecx

    # move depth, value to registers
    movb 20(%ebp), %bl  # value
    movb 21(%ebp), %dl  # depth

    # temporarily push on stack and pop later
    push %ebx

    # move current depth to register
    movb 9(%eax, %ecx, 2), %bl

    # check if depth is in front of current pixel
    # cmp  %dl, %bl
    # jl   draw_done      # go to done if current depth < depth

    # popping after temporary push
    pop  %ebx

    # put values in array to overwite old pixel
    movb %bl, 8(%eax, %ecx, 2) # value
    movb %dl, 9(%eax, %ecx, 2) # depth

draw_done:
    # Restore callee-saved registers
    pop  %edi
    pop  %esi
    pop  %ebx

    # clean up stack frame
    mov  %ebp, %esp
    pop  %ebp

    ret
