#include <stdio.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s [non-negative integer]\n", argv[0]);
        return 0;
    }

    int n = atoi(argv[1]);

    if (n < 0) {
        printf("Argument must be a non-negative integer.");
        return 0;
    }

    printf("%d\n", fact(n));
    return 1;
}
