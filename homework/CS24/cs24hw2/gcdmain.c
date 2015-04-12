#include <stdio.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage: %s [non-negative integer] [non-negative integer]\n",
            argv[0]);
        return 0;
    }

    int a = atoi(argv[1]), b = atoi(argv[2]);

    if ((a < 0) || (b < 0)) {
        printf("Argument must be a non-negative integer.\n");
        return 0;
    }

    if (a > b) {
        printf("%d\n", gcd(a, b));
    }
    else {
        printf("%d\n", gcd(b, a));
    }

    return 1;
}
