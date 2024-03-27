#include <stdio.h>

struct Hel {
    void (*printHello)();
};

void printHello() {
    printf("hello\n");
}
