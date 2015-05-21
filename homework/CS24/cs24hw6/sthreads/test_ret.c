#include <stdio.h>
#include <stdlib.h>
#include "sthread.h"

static void thread(void * arg) {
    int i, iter = *((int *) arg);
    for (i = 0; i < iter; ++i) {
        printf("Iteration %d\n", i);
    }
}

int main(int argc, char **argv) {
    sthread_create(thread, (void *) 1);
    sthread_create(thread, (void *) 2);
    sthread_create(thread, (void *) 3);
    sthread_create(thread, (void *) 4);
    sthread_start();
    return 0;
}
