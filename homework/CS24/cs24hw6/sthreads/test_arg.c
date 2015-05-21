#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "sthread.h"


/* Helper function that increments. */
static void thread(void *arg) {
    *((int *) arg) += 1;
    sthread_yield();
}

int main(int argc, char **argv) {
    int i, n = rand() % 10, local_counter = 0, thread_counter = 0;

    /* Create threads that all increment the same number. */
    for (i = 0; i < n; ++i) {
        sthread_create(thread, (void *) &thread_counter);
        local_counter++;
    }

    /* Start all threads. */
    sthread_start();

    /* Make sure that it incremented properly. */
    assert(local_counter == thread_counter);

    return 0;
}
