#
# Keep a pointer to the main scheduler context.
# This variable should be initialized to %esp;
# which is done in the __sthread_start routine.
#
        .data
        .align 4
scheduler_context:      .long   0

#
# __sthread_schedule is the main entry point for the thread
# scheduler.  It has three parts:
#
#    1. Save the context of the current thread on the stack.
#       The context includes only the integer registers
#       and EFLAGS.
#    2. Call __sthread_scheduler (the C scheduler function),
#       passing the context as an argument.  The scheduler
#       stack *must* be restored by setting %esp to the
#       scheduler_context before __sthread_scheduler is
#       called.
#    3. __sthread_scheduler will return the context of
#       a new thread.  Restore the context, and return
#       to the thread.
#
        .text
        .align 4
        .globl __sthread_schedule
__sthread_schedule:

        pushl   %ebp    # Save the branch pointer so we can restore it for
        pushl   %eax    #   sthread_yield() returns to the right place, then
        pushl   %ebx    #   save all the other non-stack pointer registers so
        pushl   %ecx    #   the thread's state can be restored
        pushl   %edx
        pushl   %esi
        pushl   %edi

        pushfl          # Save the eflags register
        # # Save the process state (all registers and flags) onto its stack
        # pushfl
        # push    %eax
        # push    %ebx
        # push    %ecx
        # push    %edx
        # push    %esi
        # push    %edi
        # push    %ebp

        # Call the high-level scheduler with the current context as an argument
        movl    %esp, %eax
        movl    scheduler_context, %esp
        pushl   %eax
        call    __sthread_scheduler

        # The scheduler will return a context to start.
        # Restore the context to resume the thread.
__sthread_restore:

        movl    %eax, %esp      # Move the stack pointer to the new context

        popfl           # Restore the eflags register

        popl    %edi    # Restore all the other registers
        popl    %esi
        popl    %edx
        popl    %ecx
        popl    %ebx
        popl    %eax
        popl    %ebp    # Restore the branch pointer for sthreads_yield()

        ret             # Returns to f on the first time this is called,
                        #   otherwise to sthreads_yield()

        # # go to new stack
        # mov     %eax, %esp

        # # Restore all process state (all registers and flags) from stack
        # pop     %ebp
        # pop     %edi
        # pop     %esi
        # pop     %edx
        # pop     %ecx
        # pop     %ebx
        # pop     %eax
        # popfl

        # ret

#
# Initialize a process context, given:
#    1. the stack for the process
#    2. the function to start
#    3. its argument
# The context should be consistent with the context
# saved in the __sthread_schedule routine.
#
# A pointer to the newly initialized context is returned to the caller.
# (This is the stack-pointer after the context has been set up.)
#
# This function is described in more detail in sthread.c.
#
#
        .globl __sthread_initialize_context
__sthread_initialize_context:

        pushl   %ebp            # Set up the stack frame
        movl    %esp, %ebp

        movl    8(%ebp), %esp   # Move the stack pointer to the new context

        pushl   16(%ebp)        # Push the thread's argument to the stack
        pushl   $__sthread_finish       # Set the thread to return to
                                        #   __sthread_finish when done
        pushl   12(%ebp)        # Push the pointer to the thread's function

        pushl   $0      # The first time this thread is initialized, it will
        pushl   $0      #   fill in its registers with all these zeros, although
        pushl   $0      #   it doesn't really matter what goes here since at the
        pushl   $0      #   start of execution it only cares about its argument,
        pushl   $0      #   and __sthread_finish() doesn't need the branch
        pushl   $0      #   pointer since it just calls __sthread_schedule() to
        pushl   $0      #   switch to another thread
        pushl   $0

        movl    %esp, %eax      # Set up this context to be returned

        movl    %ebp, %esp      # Restore the stack frame and return
        popl    %ebp

        ret

        # push    %ebp
        # mov     %esp, %ebp

        # # go to new stack
        # mov     8(%ebp), %esp

        # # push arg on to stack
        # push    16(%ebp)

        # # put return location on stack
        # push    $__sthread_finish

        # # push fp on to stack
        # push    12(%ebp)

        # # need to push dummy values as if pushing registers
        # pushfl
        # push    %eax
        # push    %ebx
        # push    %ecx
        # push    %edx
        # push    %esi
        # push    %edi
        # push    %ebp

        # # return stack pointer
        # mov     %esp, %eax

        # mov     %ebp, %esp
        # pop     %ebp
        # ret

#
# The start routine initializes the scheduler_context variable,
# and calls the __sthread_scheduler with a NULL context.
# The scheduler will return a context to resume.
#
        .globl __sthread_start
__sthread_start:
        # Remember the context
        movl    %esp, scheduler_context

        # Call the scheduler with no context
        pushl   $0
        call    __sthread_scheduler

        # Restore the context returned by the scheduler
        jmp     __sthread_restore
