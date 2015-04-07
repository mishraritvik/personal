#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>

#include "ffunc.h"


/* This function takes an array of single-precision floating point values,
 * and computes a sum in the order of the inputs.  Very simple.
 */
float fsum(FloatArray *floats) {
    float sum = 0;
    int i;

    for (i = 0; i < floats->count; i++) {
        sum += floats->values[i];
    }

    return sum;
}


/*
   To get a more accurate summation, we will use the Kahan Summation
   Algorithm. What this does is separately store the summation of the smaller
   values and then add them after adding the larger parts so that the
   significance of the smaller parts are kept.

   Why it works:
   Algebraically, we notice that this algorithm should not result in anything
   different than naively summing all the input numbers. However, in each
   iteration we are keeping track of the correction factor which is the
   significant numbers that are lost in the floating point addition.
*/
float my_fsum(FloatArray *floats) {
    float sum = 0.0, c = 0.0, y, t;
    int i;

    for (i = 0; i < floats->count; i++) {
        y = floats->values[i] - c;
        t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }

    return sum;
}


int main() {
    FloatArray floats;
    float sum1, sum2, sum3, my_sum;

    load_floats(stdin, &floats);
    printf("Loaded %d floats from stdin.\n", floats.count);

    /* Compute a sum, in the order of input. */
    sum1 = fsum(&floats);

    /* Use my_fsum() to compute a sum of the values.  Ideally, your
     * summation function won't be affected by the order of the input floats.
     */
    my_sum = my_fsum(&floats);

    /* Compute a sum, in order of increasing magnitude. */
    sort_incmag(&floats);
    sum2 = fsum(&floats);

    /* Compute a sum, in order of decreasing magnitude. */
    sort_decmag(&floats);
    sum3 = fsum(&floats);

    /* %e prints the floating-point value in full precision,
     * using scientific notation.
     */
    printf("Sum computed in order of input:  %e\n", sum1);
    printf("Sum computed in order of increasing magnitude:  %e\n", sum2);
    printf("Sum computed in order of decreasing magnitude:  %e\n", sum3);
    printf("Sum computed using Kahan Summation Algorithm:  %e\n", my_sum);

    /* TODO:  UNCOMMENT
    printf("My sum:  %e\n", my_sum);
    */

    return 0;
}

