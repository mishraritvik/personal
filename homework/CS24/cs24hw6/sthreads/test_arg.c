#include <stdio.h>
#include "sthread.h"

/**
 * This function reads a counter variable, prints its value and indicates that
 * it did the printing, then increments it and yields execution, finally
 * returning when the counter variable is at least 6.
 */
static void thread1(void *arg) {
    // Cast the argument to an int * so we can manipulate its value
    int *counter = (int *) arg;
    while (*counter < 6) {
        printf("Counter = %d in thread 1, incrementing\n", *counter);
        *counter += 1;
        sthread_yield();
    }
}

/**
 * This function reads a counter variable, prints its value and indicates that
 * it did the printing, then increments it and yields execution, finally
 * returning when the counter variable is at least 6.
 */
static void thread2(void *arg) {
    // Cast the argument to an int * so we can manipulate its value
    int *counter = (int *) arg;
    while (*counter < 6) {
        printf("Counter = %d in thread 2, incrementing\n", *counter);
        *counter += 1;
        sthread_yield();
    }
}

/**
 * This program initializes a counter variable to 0, and then has two threads
 * take turns printing its value and incrementing it, until they both return
 * once it reaches a value of 6.
 */
int main(int argc, char **argv) {
    int counter = 0;
    sthread_create(thread1, (void *) &counter);
    sthread_create(thread2, (void *) &counter);
    sthread_start();
    return 0;
}
