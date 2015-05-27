/*
 * General implementation of semaphores.
 *
 *--------------------------------------------------------------------
 * Adapted from code for CS24 by Jason Hickey.
 * Copyright (C) 2003-2010, Caltech.  All rights reserved.
 */

#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <assert.h>

#include "sthread.h"
#include "semaphore.h"

/*
 * Struct used to form the queue of threads that the semaphore has. Implemented
 * as a linked list.
 */
struct thread_node {
    Thread * thread;
    thread_node * next;
};

/*
 * The semaphore data structure contains:
 *     int i              : the count of the semaphore
 *     thread_node * head : head of the linked list containing threads
 *     thread_node * tail : tail of the linked list containing threads
 */
struct _semaphore {
    int i;
    thread_node * head;
    thread_node * tail;
};

/************************************************************************
 * Top-level semaphore implementation.
 */

/*
 * Allocate a new semaphore.  The initial value of the semaphore is
 * specified by the argument.
 */
Semaphore *new_semaphore(int init) {
    /* Allocate memory for the new semaphore. */
    Semaphore *semp = (Semaphore *) malloc(sizeof(Semaphore));

    /* Check that allocation worked. */
    if (semp == NULL) {
        printf("Allocating a new Semaphore did not work.\n");
    }

    /* Set the intiial number of the semaphore. */
    semp->i = init;

    /* No threads, so set head and tail of queue to NULL. */
    semp->head = NULL;
    semp->tail = NULL;

    return semp;
}

/*
 * Decrement the semaphore.
 * This operation must be atomic, and it blocks iff the semaphore is zero.
 */
void semaphore_wait(Semaphore *semp) {
    /* TODO */
    if (semp->i == 0) {
        //TODO do something like waiting
    }

    /* Decrement semaphore count as another thread is running. */
    semp->i--;
}

/*
 * Increment the semaphore.
 * This operation must be atomic.
 */
void semaphore_signal(Semaphore *semp) {
    /* Incrememnt semaphore count as thread is no longer running. */
    semp->i++;

    /* Find a blocked thread to run. */
    //TODO
}

