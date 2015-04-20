/*! \file
 * Implementation of a simple memory allocator.  The allocator manages a small
 * pool of memory, provides memory chunks on request, and reintegrates freed
 * memory back into the pool.
 *
 * Adapted from Andre DeHon's CS24 2004, 2006 material.
 * Copyright (C) California Institute of Technology, 2004-2010.
 * All rights reserved.
 */

#include <stdio.h>
#include <stdlib.h>

#include "myalloc.h"


/*!
 * These variables are used to specify the size and address of the memory pool
 * that the simple allocator works against.  The memory pool is allocated within
 * init_myalloc(), and then myalloc() and free() work against this pool of
 * memory that mem points to.
 */
int MEMORY_SIZE;
unsigned char *mem;

// used for beaders and footers of blocks
struct header {
    // data is positive if allocated, negative if free
    int data;
};

/* TODO:  The unacceptable allocator uses an external "free-pointer" to track
 *        where free memory starts.  If your allocator doesn't use this
 *        variable, get rid of it.
 *
 *        You can declare data types, constants, and statically declared
 *        variables for managing your memory pool in this section too.
 */
static unsigned char *freeptr;
static unsigned int header_size = sizeof(struct header);


/*!
 * This function initializes both the allocator state, and the memory pool.  It
 * must be called before myalloc() or myfree() will work at all.
 *
 * Note that we allocate the entire memory pool using malloc().  This is so we
 * can create different memory-pool sizes for testing.  Obviously, in a real
 * allocator, this memory pool would either be a fixed memory region, or the
 * allocator would request a memory region from the operating system (see the
 * C standard function sbrk(), for example).
 */
void init_myalloc() {
    /*
     * Allocate the entire memory pool, from which our simple allocator will
     * serve allocation requests.
     */
    mem = (unsigned char *) malloc(MEMORY_SIZE);
    if (mem == 0) {
        fprintf(stderr,
                "init_myalloc: could not get %d bytes from the system\n", MEMORY_SIZE);
        abort();
    }

    freeptr = mem;

    if (MEMORY_SIZE < 2 * header_size) {
        printf("Total memory not large enough to hold two ends.\n");
        abort();
    }

    struct header start, end;
    start.data = -(MEMORY_SIZE - 2 * header_size);
    end.data = -(MEMORY_SIZE - 2 * header_size);

    *((struct header *) freeptr) = start;
    *((struct header *) ((void *) freeptr + MEMORY_SIZE -
        header_size)) = end;
}

void status() {
    unsigned char * current = freeptr;
    int offset = 0, curr_size;
    while (1) {
        curr_size = ((struct header *) current)->data;

        if (curr_size < 0) {
            printf("%d: free %d (+ 8) bytes\n", offset, -curr_size);
        }
        else {
            printf("%d: using %d (+ 8) bytes\n", offset, curr_size);
        }

        offset += abs(curr_size) + 2 * header_size;

        // if gone beyond the end, return 0 as no blocks found
        if (offset >= MEMORY_SIZE) {
            return;
        }

        // move forward to next header
        current = ((void *) freeptr) + offset;
    }
}

int aligned_size(int size) {
    if (size % 4 == 0) {
        return size;
    }
    return size + (4 - (size % 4));
}

/*!
 * Attempt to allocate a chunk of memory of "size" bytes.  Return 0 if
 * allocation fails.
 */
unsigned char *myalloc(int size) {

    size = aligned_size(size);
    unsigned char * current = freeptr;
    int offset = 0, curr_size, needed_size = size + 2 * header_size;

    printf("requesting\n");

    while (1) {
        curr_size = ((struct header *) current)->data;
        // check if block is free and big enough
        if ((curr_size < 0) && (abs(curr_size) >= size)) {
            printf("allocating\n");
            // can allocate here!
            // put header and footer for the block
            struct header start, end;
            end.data = size;
            start.data = size;

            *((struct header *) current) = start;
            *((struct header *) ((void *) current + size + header_size)) = end;

            if (abs(curr_size) > needed_size) {
                printf("extra free block\n");
                printf("size of extra free: %d, start: %d, end: %d\n",
                    abs(curr_size) - needed_size,
                    offset + needed_size,
                    offset + abs(curr_size) + header_size);
                // put header and footer for remaining free block
                struct header start, end;
                start.data = -(abs(curr_size) - needed_size);
                end.data = -(abs(curr_size) - needed_size);

                *((struct header *) ((void *) current + needed_size)) = start;
                *((struct header *) ((void *) current + abs(curr_size) +
                    header_size)) = end;
            }

            status();
            // return pointer to beginning of the payload
            return (unsigned char *) ((void *) current + header_size);
        }
        else {
            // cannot allocate here! find next header
            offset += abs(curr_size) + 2 * header_size;
            printf("continue to %d\n", offset);

            // if gone beyond the end, return 0 as no blocks found
            if (offset >= MEMORY_SIZE - 2 * header_size) {
                return 0;
            }

            // move forward to next header
            current = ((void *) freeptr) + offset;
        }
    }
}


/*!
 * Free a previously allocated pointer.  oldptr should be an address returned by
 * myalloc().
 */
void myfree(unsigned char *oldptr) {
    printf("freeing!\n");
    int size, new_size, start_offset;
    struct header * prev_end, * next_end, * curr_end, new_start, new_end;

    curr_end = (struct header *) ((void *) oldptr - header_size);
    prev_end = (struct header *) ((void *) oldptr - 2 * header_size);
    next_end = (struct header *) ((void *) oldptr + size + header_size);

    size = curr_end->data;

    printf("free size: %d\n", size);

    if (((struct header *) prev_end)->data > 0) {
        if (((struct header *) next_end)->data > 0) {
            // join all three
            start_offset = -(2 * header_size + abs(prev_end->data));
            new_size = 4 * header_size + abs(prev_end->data) + abs(next_end->data) + abs(curr_end->data);
        }
        else {
            // join with prev
            start_offset = -(2 * header_size + abs(prev_end->data));
            new_size = 2 * header_size + abs(prev_end->data) + abs(curr_end->data);
        }
    }
    else {
        if (((struct header *) next_end)->data > 0) {
            // join with next
            start_offset = 0;
            new_size = 2 * header_size + abs(next_end->data) + abs(curr_end->data);
        }
        else {
            // no joining, just switch to free by changing sign of data
            curr_end->data *= -1;
            ((struct header *) ((void *) oldptr + size))->data *= -1;
        }
    }
    new_start.data = -new_size;
    new_end.data = -new_size;
    *((struct header *) ((void *) oldptr + start_offset)) = new_start;
    *((struct header *) ((void *) oldptr + start_offset + new_size + header_size)) = new_end;
    status();
}

