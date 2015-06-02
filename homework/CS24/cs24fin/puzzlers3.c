int main() {
    int val = 2;
    printf("%d", 0); fflush(stdout);
    if (fork() == 0) {
        val++;
        printf("%d", val);
        fflush(stdout);
    }
    else {
        val--;
        printf("%d", val); fflush(stdout); wait(NULL);
    }
    val++; printf("%d", val); fflush(stdout); exit(0);
}
