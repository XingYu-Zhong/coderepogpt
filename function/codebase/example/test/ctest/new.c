#include <stdio.h>

struct Hel {
    void (*printHello)();
};

void test() {
    struct Hel test;
    test.printHello();
}
