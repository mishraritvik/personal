# draw_pixel:
#     draws given pixel by putting value in array
# args:
#     8(%ebp)  : pointer to screen object
#     12(%ebp) : x value of location of pixel
#     16(%ebp) : y value of location of pixel
#     20(%ebp) : color value of pixel
#     24(%ebp) : depth value of pixel
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

    # check that x is valid
    cmp  %ebx, %esi
    jle  draw_done      # go to done if x >= width

    # check that y is valid
    cmp  %ebx, %edi
    jle  draw_done      # go to done if y >= height

    # compute 1D location of pixel (width * y + x)
    imul %esi, %ecx
    add  %ebx, %ecx

    # move depth, value to registers
    mov  20(%ebp), %ebx # value
    mov  24(%ebp), %edx # depth

    # temporarily push on stack and pop later
    push %ebx

    # move current depth to register
    movb 9(%eax, %ecx, 2), %bl

    # check if depth is in front of current pixel
    cmp  %dl, %bl
    jg   draw_done      # go to done if depth < current depth

    # popping after temporary push
    pop  %ebx

    # put values in array to overwite old pixel
    # movb %bl, 8(%eax, %ecx, 2) # value
    # movb %dl, 9(%eax, %ecx, 2) # depth


draw_done:
    # Restore callee-saved registers
    pop  %edi
    pop  %esi
    pop  %ebx

    # clean up stack frame
    mov  %ebp, %esp
    pop  %ebp

    ret
