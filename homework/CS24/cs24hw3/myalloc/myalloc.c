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

struct block_end {
    /*
     contents of data:
     bit 1: 1 if header, 0 if footer
     bit 2: 1 if allocated, 0 if free
     bit 3 - 16: size
     */
    unsigned short data;
};

/* TODO:  The unacceptable allocator uses an external "free-pointer" to track
 *        where free memory starts.  If your allocator doesn't use this
 *        variable, get rid of it.
 *
 *        You can declare data types, constants, and statically declared
 *        variables for managing your memory pool in this section too.
 */
static unsigned char *freeptr;
#define HEADER_MASK 0x8000
#define ALLOC_MASK  0x4000
#define SIZE_MASK   0x3FFF


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

    /* TODO:  You can initialize the initial state of your memory pool here. */
    freeptr = mem;

    if (MEMORY_SIZE < 2 * sizeof(unsigned short)) {
        printf("Total memory not large enough to hold two ends.\n");
    }

    struct block_end * header, * footer;
    footer->data = (unsigned short) MEMORY_SIZE;
    header->data = footer->data | HEADER_MASK;

    // TODO put two block_ends to cover the entire memory at the beginning
}


/*!
 * Attempt to allocate a chunk of memory of "size" bytes.  Return 0 if
 * allocation fails.
 */
unsigned char *myalloc(int size) {

    unsigned char * current = freeptr;
    unsigned short header, alloc, data;

    while (1) {
        header = *((unsigned short *) current) & HEADER_MASK;
        alloc  = *((unsigned short *) current) & ALLOC_MASK;
        data   = *((unsigned short *) current) & SIZE_MASK;

        if (header) {
            if (!(alloc || (data < size))) {
                // can allocate!
                // put header and footer for the block
                // return pointer to beginning of the payload
            }
            else {
                // cannot allocate! move forward to next header
                current = ((void *) current) + 2 * sizeof(unsigned short) + data;
            }
        }
        else {
            // weird...should be at a header
            printf("not at header\n");
        }
    }
}


/*!
 * Free a previously allocated pointer.  oldptr should be an address returned by
 * myalloc().
 */
void myfree(unsigned char *oldptr) {
    // join with free blocks before or after
    // flip allocated bit
}

