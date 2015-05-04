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
    unsigned char instr_byte, instr_byte2;

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
    // read operation
    operation = instr_byte >> 4;
    if (operation == OP_DONE) {
        // done
    }
    else if (operation <= OP_SHR) {
        // one-byte operation
        dst_write = WRITE_REG;
    }
    else if (operation == OP_BRA) {
        // BRA
    }
    else if (operation == OP_BRZ) {
        // BRZ
    }
    else if (operation == OP_BNZ) {
        // BNZ
    }
    else if (operation <= OP_BNZ) {
        // two-byte operation
        dst_write = WRITE_REG;

        // get second instruction byte
        incrPC(pc);
        ifetch(is);
        instr_byte2 = pin_read(d->input);

        // check src1_isreg
        src1_isreg = (instr_byte & 0x8) >> 3;

        // set dst

        // set src
        if (src1_isreg) {
            // set src1_addr
        }
        else {
            // set src1_const
        }
    }
    else {
        printf("invalid operation: %lu\n", operation);
    }
    // check if 1 or 2 byte
    // if two byte, incrPC and ifetch and pin_read
    // decode instruction, set:
    // - operation
    // - src1_addr
    // - src1_const
    // - src1_isreg
    // - src2_addr
    // - dst_write
    // - branch_addr

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
