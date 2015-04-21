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

/* used for boundary tags of blocks */
struct header {
    /* positive if block is allocated */
    /* negative if block is free */
    /* abs(data) is size of block without headers */
    int data;
};

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
                "init_myalloc: could not get %d bytes from the system\n",
                MEMORY_SIZE);
        abort();
    }

    freeptr = mem;

    /* abort if memory pool is smaller than two headers */
    if (MEMORY_SIZE < 2 * header_size) {
        printf("Total memory not large enough to hold two headers.\n");
        abort();
    }

    /* put boundary tags on the full memory pool to start */
    struct header start, end;

    start.data = -(MEMORY_SIZE - 2 * header_size);
    end.data = -(MEMORY_SIZE - 2 * header_size);

    *((struct header *) freeptr) = start;
    *((struct header *)
        ((void *) freeptr + MEMORY_SIZE - header_size)) = end;
}

/* return smallest multiple of 4 greater than or equal to given size */
int aligned_size(int size) {
    return size + ((4 - (size % 4)) % 4);
}

/*
 * Attempt to allocate a chunk of memory of "size" bytes.  Return 0 if
 * allocation fails.
 *
 * Uses best-fit strategy.
 */
unsigned char *myalloc(int size) {
    /* get aligned size */
    size = aligned_size(size);

    unsigned char * current = freeptr, * best_fit;
    int offset = 0, best_offset = 0, flag = 0,
        needed_size = size + 2 * header_size, curr_size, best_size;

    /* go through all memory looking for best fit */
    while (1) {
        /* get size of current block */
        curr_size = ((struct header *) current)->data;

        /* check if block is free and big enough */
        if ((curr_size < 0) && (abs(curr_size) >= size)) {
            if ((!flag) || ((flag) && (abs(curr_size) < abs(best_size)))) {
                best_size = curr_size;
                best_fit = current;
                best_offset = offset;
                flag = 1;
            }
        }

        /* find next header */
        offset += abs(curr_size) + 2 * header_size;

        /* if gone beyond the end, end while loop */
        if (offset >= MEMORY_SIZE - 2 * header_size) {
            break;
        }

        /* move forward to next header if not beyond end */
        current = ((void *) freeptr) + offset;
    }

    /* if never found a large enough free block, return 0 */
    if (!flag) {
        return 0;
    }

    /* can allocate at best_fit */
    struct header start, end;

    if ((abs(best_size) <= size + 2 * header_size) && (abs(best_size) != size)) {
        /* no space for the extra free block headers so make larger block */
        size = abs(best_size);
    }
    else if (abs(best_size) > size) {
        /* make the extra free block */
        /* put in header and footer for remaining free block */
        struct header start, end;
        start.data = -(abs(best_size) - needed_size);
        end.data = -(abs(best_size) - needed_size);

        *((struct header *) ((void *) best_fit + needed_size)) = start;
        *((struct header *) ((void *) best_fit + abs(best_size) +
            header_size)) = end;
    }

    /* put in header and footer for the alloc block */
    end.data = size;
    start.data = size;
    *((struct header *) best_fit) = start;
    *((struct header *) ((void *) best_fit + size + header_size)) = end;

    /* return pointer to beginning of the payload */
    return (unsigned char *) ((void *) best_fit + header_size);
}


/*
 * Free a previously allocated pointer.  oldptr should be an address returned by
 * myalloc().
 *
 * Coalesces all adjacent free blocks, takes constant time.
 */
void myfree(unsigned char *oldptr) {
    int size, next_size, prev_size, new_size, start_offset, flag = 0;
    struct header * prev_end, * next_end, * curr_end, new_start, new_end;

    /* get header of block being freed */
    curr_end = (struct header *) ((void *) oldptr - header_size);
    size = curr_end->data;

    if (size < 0) {
        /* this is already free, so return */
        return;
    }

    /* get headers of adjacent blocks */
    prev_end = (struct header *) ((void *) curr_end - header_size);
    next_end = (struct header *) ((void *) curr_end + size + 2 * header_size);

    prev_size = prev_end->data;
    next_size = next_end->data;

    /* if at the beginning, do not coalesce with previous */
    if (curr_end == (struct header *) freeptr) {
        prev_size = 0;
    }

    /* if at the end, do not coalesce with next */
    if (next_end == (struct header *) ((void *) freeptr + MEMORY_SIZE)) {
        next_size = 0;
    }

    /* check which of adjacent blocks are free */
    if (prev_size < 0) {
        if (next_size < 0) {
            /* join all three */
            start_offset = -(2 * header_size + abs(prev_size));
            new_size = 4 * header_size + abs(prev_size) +
                abs(next_size) + abs(size);
        }
        else {
            /* join with prev */
            start_offset = -(2 * header_size + abs(prev_size));
            new_size = 2 * header_size + abs(prev_size) +
                abs(size);
        }
    }
    else {
        if (next_size < 0) {
            /* join with next */
            start_offset = 0;
            new_size = 2 * header_size + abs(next_size) +
                abs(size);
        }
        else {
            /* no joining, just switch to free by changing sign of data */
            flag = 1;
            curr_end->data *= -1;
            ((struct header *)
                ((void *) curr_end + size + header_size))->data *= -1;
        }
    }

    /* put in new headers for free block if needed */
    if (!flag) {
        new_start.data = -new_size;
        new_end.data = -new_size;

        *((struct header *)
            ((void *) curr_end + start_offset)) = new_start;
        *((struct header *)
            ((void *) oldptr + start_offset + new_size)) = new_end;
    }
}
