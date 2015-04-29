OBJS = c_except.o my_setjmp.o ptr_vector.o

CFLAGS=-g
ASFLAGS=-g

check: test_setjmp
	./test_setjmp

test_setjmp: $(OBJS) test_setjmp.o
	$(CC) $(LDFLAGS) $^ -o $@

test_setjmp.c: my_setjmp.h
test_setjmp.o: my_setjmp.s

divider: $(OBJS) divider.o
	$(CC) $(LDFLAGS) $^ -o $@

ptr_vector.c: ptr_vector.h
c_except.c: c_except.h my_setjmp.h
divider.c: c_except.h my_setjmp.h

clean:
	rm -f *.o *~ divider divider.exe test_setjmp

