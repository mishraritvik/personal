#include <stdio.h>
#include "my_setjmp.h"

// declarations of all test and helper functions
void f1(jmp_buf buf, int x);
void f2(jmp_buf buf, int x);

void test_setjmp_return();
void test_longjmp_return();
void test_nested();
void test_multiple_funcs();
void test_local_variables();

// helper functions for tests
void f1(jmp_buf buf, int x) {
    f2(buf, x);
}

void f2(jmp_buf buf, int x) {
    longjmp(buf, x);
}

// test return value of setjmp
void test_setjmp_return() {
    printf("Testing setjmp return value.\n");
    static jmp_buf buf;
    int e = setjmp(buf);

    if (e == 0) {
        printf("setjmp(buf) returns 0: PASS\n");
    }
    else {
        printf("setjmp(buf) returns %d: FAIL\n", e);
    }
}

void test_longjmp_return() {
    printf("Testing longjmp return value.\n");
    // test 0 case
    static jmp_buf buf;
    int e1 = setjmp(buf);

    if (e1 == 0) {
        longjmp(buf, 0);
    }

    if (e1 == 1) {
        printf("longjmp(buf, 0) returns 1: PASS\n");
    }
    else {
        printf("setjmp(buf, 0) returns %d: FAIL\n", e1);
    }

    // test n case
    int e2 = setjmp(buf), n = 7;

    if (e2 == 0) {
        longjmp(buf, n);
    }

    if (e2 == n) {
        printf("longjmp(buf, %d) returns %d: PASS\n", n, e2);
    }
    else {
        printf("setjmp(buf, %d) returns %d: FAIL\n", n, e2);
    }
}

// test if it works with nested try catch
void test_nested() {
    static jmp_buf buf1, buf2, buf3;
    int e1 = setjmp(buf1), e2 = setjmp(buf2), e3 = setjmp(buf3);

    longjmp(buf1, 0);
    longjmp(buf2, 1);
    longjmp(buf3, 2);

    if (e1 == 1 && e2 == 1 && e3 == 2) {
        printf("works with nested jumps: PASS\n");
    }
    else {
        printf("does not work with nested jumps: FAIL\n");
    }
}

// test it if works across multiple functions
void test_multiple_funcs() {
    static jmp_buf buf;
    int e = setjmp(buf);

    if (e == 0) {
        f1(buf, 0);
    }

    if (e == 1) {
        printf("works across multiple functions: PASS\n");
    }
    else {
        printf("does not work across multiple functions: FAIL\n");
    }
}

// test if it corrupts local variables
void test_local_variables() {
    static jmp_buf env;

    int a = 0;
    int e = setjmp(env);
    int b = 0;

    if (e == 0) {
        a = 1;
        b = 1;
        longjmp(env, 4);
    }

    if (a == 1 && b == 1 && e == 4) {
        printf("does not corrupt local variables: PASS\n");
    }
    else {
        printf("does corrupt local variables: FAIL\n");
    }
}


int main() {
    // run all tests
    test_setjmp_return();
    test_longjmp_return();
    test_nested();
    test_multiple_funcs();
    test_local_variables();

    return 1;
}
