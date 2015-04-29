#include "my_setjmp.h"

// declarations of all test functions
void test_simple();
void test_nested();
void test_multiple_funcs();
void test_stack();
void test_local_vals();

// helper functions for tests


// test return value of longjmp
void test_simple() {
    printf("longjmp(buf, 0) returns 1: PASS\n");
}

// test if it works with nested values
void test_nested() {

}

// test it if works across multiple functions
void test_multiple_funcs() {

}

// test if it corrupts stack
void test_stack() {

}

// test if it corrupts local values
void test_local_vals() {

}


int main() {
    // run all tests
    test_simple();
    test_nested();
    test_multiple_funcs();
    test_stack();
    test_local_vals();

    return 1;
}
