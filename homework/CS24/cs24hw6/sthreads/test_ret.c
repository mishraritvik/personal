#include <stdio.h>
#include "sthread.h"

static void thread(void * arg) {
    int i, iter = *((int *) arg);
    for (i = 0; i < iter; ++i) {
        printf("Iteration %d of %d\n", i + 1, iter);
    }
}

int main(int argc, char **argv) {
    sthread_create(thread, (void *) 1);
    sthread_create(thread, (void *) 2);
    sthread_create(thread, (void *) 4);
    sthread_create(thread, (void *) 8);
    sthread_start();
    return 0;
}
