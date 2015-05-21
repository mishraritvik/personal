#include <stdio.h>
#include "sthread.h"

// static void thread(void * arg) {
//     int i, iter = *((int *) arg);
//     for (i = 0; i < iter; ++i) {
//         printf("Iteration %d of %d\n", i + 1, iter);
//     }
// }

// int main(int argc, char **argv) {
//     sthread_create(thread, (void *) 1);
//     sthread_create(thread, (void *) 2);
//     sthread_create(thread, (void *) 4);
//     sthread_create(thread, (void *) 8);
//     sthread_start();
//     return 0;
// }

/**
 * This function takes a pointer to an integer value and does that many
 * iterations of a loop in which it prints the current progress as
 * loop counter/total iterations it's doing.
 */
static void thread(void *arg) {
    // Dereference the argument representing the number of iterations to do
    int max = *((int *) arg);
    for (int i = 1; i <= max; i++) {
        printf("Current loop progress: %d/%d\n", i, max);
        sthread_yield();
    }
}

/**
 * This program initializes four threads to run for 10, 20, 30, and 40
 * iterations respectively of a loop that simply prints out the thread's current
 * progress, and they each return one by one as their iteration cap is met.
 */
int main(int argc, char **argv) {
    int maxes[4] = {10, 20, 30, 40};
    sthread_create(thread, (void *) maxes);
    sthread_create(thread, (void *) (maxes + 1));
    sthread_create(thread, (void *) (maxes + 2));
    sthread_create(thread, (void *) (maxes + 3));
    sthread_start();
    return 0;
}
