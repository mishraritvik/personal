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
 *     thread_node * head : head of the linked list containing blocked threads
 *     thread_node * tail : tail of the linked list containing blocked threads
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
        printf("Semaphore was not allocated.\n");
    }

    /* Set the intiial number of the semaphore. */
    semp->i = init;

    /* Queue is empty so set head and tail of queue to NULL. */
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
    while (semp->i == 0) {
        /* Semaphore cannot handle another thread, so block it. */
        /* Need to lock before blocking so that multiple threads do not access
         * the queue at the same time. */
        __sthread_lock();
        sthread_block();

        /* Add to queue of blocked threads. */
        thread_node * new_thread = (thread_node *) malloc(sizeof(thread_node));

        /* The thread to be held is the currently executing one. */
        new_thread->thread = sthread_current();

        /* Will be at the end of queue so next is NULL. */
        new_thread->next = NULL;

        /* Add to queue. */
        if (semp->head == NULL) {
            /* Empty queue, head and tail are new value. */
            semp->head = new_thread;
            semp->tail = semp->head;
        }
        else {
            /* This will be the next of tail, and new tail. */
            semp->tail->next = new_thread;
            semp->tail = semp->tail->next;
        }
    }

    /* Decrement semaphore count. */
    semp->i--;
}

/*
 * Increment the semaphore.
 * This operation must be atomic.
 */
void semaphore_signal(Semaphore *semp) {
    /* Incrememnt semaphore count. */
    semp->i++;

    /* Get next in queue to run. */
    if (semp->head == NULL) {
        /* Queue empty! Do nothing. */
    }
    else {
        thread_node * old_head = semp->head;

        /* Unblock the head. */
        sthread_unblock(old_head->thread);

        /* Remove from queue and free. */
        semp->head = semp->head->next;
        free(old_head);
    }
}

