/*
 * Define a bounded buffer containing records that describe the
 * results in a producer thread.
 *
 *--------------------------------------------------------------------
 * Adapted from code for CS24 by Jason Hickey.
 * Copyright (C) 2003-2010, Caltech.  All rights reserved.
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <memory.h>

#include "sthread.h"
#include "bounded_buffer.h"
#include "semaphore.h"

/*
 * The bounded buffer data.
 */
struct _bounded_buffer {
    /* The maximum number of elements in the buffer */
    int length;

    /* The index of the first element in the buffer */
    int first;

    /* The number of elements currently stored in the buffer */
    int count;

    /* The values in the buffer */
    BufferElem *buffer;

    /* Semaphore used to count taken spots in buffer. */
    Semaphore * taken;

    /* Semaphore used to count open spots in buffer. */
    Semaphore * open;

    /* Semaphore (mutex) used to make sure only one thread accesses buffer. */
    Semaphore * access;

};

/*
 * For debugging, ensure that empty slots in the buffer are
 * set to a default value.
 */
static BufferElem empty = { -1, -1, -1 };

/*
 * Allocate a new bounded buffer.
 */
BoundedBuffer *new_bounded_buffer(int length) {
    BoundedBuffer *bufp;
    BufferElem *buffer;
    int i;

    /* Allocate the buffer */
    buffer = (BufferElem *) malloc(length * sizeof(BufferElem));
    bufp = (BoundedBuffer *) malloc(sizeof(BoundedBuffer));
    if (buffer == 0 || bufp == 0) {
        fprintf(stderr, "new_bounded_buffer: out of memory\n");
        exit(1);
    }

    /* Initialize */

    memset(bufp, 0, sizeof(BoundedBuffer));

    for (i = 0; i != length; i++)
        buffer[i] = empty;

    bufp->length = length;
    bufp->buffer = buffer;

    /*
     * Initialize the semaphores. To start, 0 spots are taken and length spots
     * are open.
     */
    bufp->taken = new_semaphore(0);
    bufp->open = new_semaphore(length);
    bufp->access = new_semaphore(1);

    return bufp;
}

/*
 * Add an integer to the buffer.  Yield control to another
 * thread if the buffer is full.
 */
void bounded_buffer_add(BoundedBuffer *bufp, const BufferElem *elem) {
    /*
     * Wait until the buffer has space by waiting on the open semaphore (there
     * must be an open spot to add an element). Need to wait on access as well
     * to make sure only one thread is changing the buffer at a time.
     */
    semaphore_wait(bufp->open);
    semaphore_wait(bufp->access);

    /* Now the buffer has space so add element. */
    bufp->buffer[(bufp->first + bufp->count) % bufp->length] = *elem;
    bufp->count++;

    /*
     * One more spot is taken in buffer so add to taken semaphore. Also, no
     * longer accessing the buffer so signal to access.
     */
    semaphore_signal(bufp->taken);
    semaphore_signal(bufp->access);
}

/*
 * Get an integer from the buffer.  Yield control to another
 * thread if the buffer is empty.
 */
void bounded_buffer_take(BoundedBuffer *bufp, BufferElem *elem) {
    /*
     * Wait until the buffer has a value to retrieve by waiting on the taken
     * semaphore (there must be an element to take). Need to wait on access as
     * well to make sure only one thread is changing the buffer at a time.
     */
    semaphore_wait(bufp->taken);
    semaphore_wait(bufp->access);

    /* Copy the element from the buffer, and clear the record. */
    *elem = bufp->buffer[bufp->first];
    bufp->buffer[bufp->first] = empty;
    bufp->count--;
    bufp->first = (bufp->first + 1) % bufp->length;

    /*
     * One more spot is open in buffer so add to open semaphore. Also, no longer
     * accessing the buffer so signal to access.
     */
    semaphore_signal(bufp->open);
    semaphore_signal(bufp->access);
}

