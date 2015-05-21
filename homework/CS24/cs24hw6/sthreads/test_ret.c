#include <stdio.h>
#include <stdlib.h>
#include "sthread.h"

/* Helper function that loops and prints. */
static void thread(void * arg) {
    int i, iter = *((int *) arg);
    for (i = 0; i < iter; ++i) {
        printf("Iteration %d of %d\n", i + 1, iter);
        sthread_yield();
    }
}

int main(int argc, char **argv) {
    int a = rand() % 5, b = rand() % 10, c = rand() % 15;

    /* Create multiple threads all looping and printing values. */
    sthread_create(thread, (void *) &a);
    sthread_create(thread, (void *) &b);
    sthread_create(thread, (void *) &c);

    /* Start all threads. */
    sthread_start();

    return 0;
}
