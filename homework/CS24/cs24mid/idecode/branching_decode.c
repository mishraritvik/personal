/*! \file
 *
 * This file contains the definitions for the instruction decoder for the
 * branching processor.  The instruction decoder extracts bits from the current
 * instruction and turns them into separate fields that go to various functional
 * units in the processor.
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "branching_decode.h"
#include "register_file.h"
#include "instruction.h"

/* constants used for getting information from bytes */
#define ADDR_MASK 0x07
#define BRA_MASK  0x0F
#define ISREG_LOC 3
#define OP_LOC    4

/*
 * Branching Instruction Decoder
 *
 *  The Instruction Decoder extracts bits from the instruction and turns
 *  them into separate fields that go to various functional units in the
 *  processor.
 */


/*!
 * This function dynamically allocates and initializes the state for a new
 * branching instruction decoder instance.  If allocation fails, the program is
 * terminated.
 */
Decode * build_decode() {
    Decode *d = malloc(sizeof(Decode));
    if (!d) {
        fprintf(stderr, "Out of memory building an instruction decoder!\n");
        exit(11);
    }
    memset(d, 0, sizeof(Decode));
    return d;
}


/*!
 * This function frees the dynamically allocated instruction-decoder instance.
 */
void free_decode(Decode *d) {
    free(d);
}


/*!
 * This function decodes the instruction on the input pin, and writes all of the
 * various components to output pins.  Other components can then read their
 * respective parts of the instruction.
 *
 * NOTE:  the busdata_t type is defined in bus.h, and is simply
 *        an unsigned long.
 */
void fetch_and_decode(InstructionStore *is, Decode *d, ProgramCounter *pc) {
    /* This is the current instruction byte we are decoding. */
    unsigned char instr_byte;

    /* The CPU operation the instruction represents.  This will be one of the
     * OP_XXXX values from instruction.h.
     */
    busdata_t operation;

    /* Source-register values, including defaults for src1-related values. */
    busdata_t src1_addr = 0, src1_const = 0, src1_isreg = 1;
    busdata_t src2_addr = 0;

    /* Destination register.  For both single-argument and two-argument
     * instructions, dst == src2.
     */
    busdata_t dst_addr = 0;

    /* Flag controlling whether the destination register is written to.
     * Default value is to *not* write to the destination register.
     */
    busdata_t dst_write = NOWRITE_REG;

    /* The branching address loaded from a branch instruction. */
    busdata_t branch_addr = 0;

    /* All instructions have at least one byte, so read the first byte. */
    ifetch(is);   /* Cause InstructionStore to push out the instruction byte */
    instr_byte = pin_read(d->input);

    /*=====================================================*/
    /* TODO:  Fill in the implementation of the multi-byte */
    /*        instruction decoder.                         */
    /*=====================================================*/
    /* read operation */
    operation = instr_byte >> OP_LOC;

    /* decode remaining bytes based on operation */
    if (operation == OP_DONE) {
        /* done, nothing to set besides operation */
    }
    else if (operation <= OP_SHR) {
        /* one-byte operation */
        dst_write = WRITE_REG;
        src2_addr = instr_byte & ADDR_MASK;
    }
    else if ((operation == OP_BRA) || (operation == OP_BRZ)
        || (operation == OP_BNZ)) {
        /* set branch addr */
        branch_addr = instr_byte & BRA_MASK;
    }
    else if (operation <= OP_BNZ) {
        /* must be a two-byte operation */
        dst_write = WRITE_REG;

        /* check src1_isreg */
        src1_isreg = (instr_byte >> ISREG_LOC) & 0x01;

        /* set dst */
        src2_addr = instr_byte & ADDR_MASK;

        /* get second instruction byte */
        incrPC(pc);
        ifetch(is);
        instr_byte = pin_read(d->input);

        /* set src */
        src1_const = instr_byte;
        if (src1_isreg) {
            src1_addr = instr_byte & ADDR_MASK;
        }
    }
    else {
        printf("invalid operation: %lu\n", operation);
    }

    /* All decoded!  Write out the decoded values. */

    pin_set(d->cpuop,       operation);

    pin_set(d->src1_addr,   src1_addr);
    pin_set(d->src1_const,  src1_const);
    pin_set(d->src1_isreg,  src1_isreg);

    pin_set(d->src2_addr,   src2_addr);

    /* For this processor, like IA32, dst is always src2. */
    pin_set(d->dst_addr,    src2_addr);
    pin_set(d->dst_write,   dst_write);

    pin_set(d->branch_addr, branch_addr);
}
