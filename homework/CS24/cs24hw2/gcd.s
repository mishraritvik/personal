segment .text
global calc_gcd
calc_gcd:
enter 0,0
mov %ecx, 2
/* ----------------------
 * Compute abs x and y
   ---------------------- */
compute_abs:
fild dword [%ebp+8]
fabs
fist dword [%ebp+8]
add $4, %ebp
loop compute_abs
sub $8, %ebp

xor %edx, %edx
mov %eax, [%ebp+8]
mov %ebx, [%ebp+12]
cmp %eax, %ebx
jg again
xchg %eax, %ebx

/* ----------------------
 * Perform looping operation
 * = x % y
 * = y; y = n; if y!=0 repeat
  ---------------------- */
again:
div %ebx ; quotient in eax, remainder in edx(n).
mov %eax, %ebx ; x = y
mov %ebx, %edx ; y = n
xor %edx, %edx
cmp %ebx, 0
jnz again
leave
ret
