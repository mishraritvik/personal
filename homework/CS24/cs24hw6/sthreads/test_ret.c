#include <stdio.h>
#include "sthread.h"

static void thread(void * arg) {
    int i, iter = *((int *) arg);
    for (i = 0; i < iter; ++i) {
        printf("Iteration %d of %d\n", i + 1, iter);
        sthread_yield();
    }
}

int main(int argc, char **argv) {
    int a = 5, b = 10, c = 15;
    sthread_create(thread, (void *) &a);
    sthread_create(thread, (void *) &b);
    sthread_create(thread, (void *) &c);
    sthread_start();
    return 0;
}
