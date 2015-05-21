#include <stdio.h>
#include <stdlib.h>
#include "sthread.h"


static void thread(void *arg) {
    printf("%d\n", *((int *) arg));
    *((int *) arg) += 1;
    printf("%d\n", *((int *) arg));
    sthread_yield();
}

/**
 * This program initializes a counter variable to 0, and then has two threads
 * take turns printing its value and incrementing it, until they both return
 * once it reaches a value of 6.
 */
int main(int argc, char **argv) {
    int i, n = rand() % 100, local_counter = 0, thread_counter = 0;

    for (i = 0; i < n; ++i) {
        sthread_create(thread, (void *) &thread_counter);
        local_counter++;
    }

    sthread_start();

    printf("%d\n", thread_counter);

    if (local_counter == thread_counter) {
        printf("Pass.\n");
    }
    else {
        printf("Fail.\n");
    }

    return 0;
}
