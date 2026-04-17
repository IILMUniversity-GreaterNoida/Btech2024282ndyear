#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

int buffer[10];
int in = 0, out = 0;
int n = 5;   // number of items
int BUFFER_SIZE = 3;

HANDLE mutex, empty, full;

// Producer
DWORD WINAPI producer(LPVOID param) {
    int item;
    for (int i = 0; i < n; i++) {
        item = rand() % 100;

        WaitForSingleObject(empty, INFINITE);
        WaitForSingleObject(mutex, INFINITE);

        buffer[in] = item;
        printf("Produced: %d at %d\n", item, in);
        in = (in + 1) % BUFFER_SIZE;

        ReleaseMutex(mutex);
        ReleaseSemaphore(full, 1, NULL);

        Sleep(500);
    }
    return 0;
}

// Consumer
DWORD WINAPI consumer(LPVOID param) {
    int item;
    for (int i = 0; i < n; i++) {

        WaitForSingleObject(full, INFINITE);
        WaitForSingleObject(mutex, INFINITE);

        item = buffer[out];
        printf("Consumed: %d from %d\n", item, out);
        out = (out + 1) % BUFFER_SIZE;

        ReleaseMutex(mutex);
        ReleaseSemaphore(empty, 1, NULL);

        Sleep(500);
    }
    return 0;
}

int main() {
    HANDLE p, c;

    mutex = CreateMutex(NULL, FALSE, NULL);
    empty = CreateSemaphore(NULL, BUFFER_SIZE, BUFFER_SIZE, NULL);
    full = CreateSemaphore(NULL, 0, BUFFER_SIZE, NULL);

    p = CreateThread(NULL, 0, producer, NULL, 0, NULL);
    c = CreateThread(NULL, 0, consumer, NULL, 0, NULL);

    WaitForSingleObject(p, INFINITE);
    WaitForSingleObject(c, INFINITE);

    CloseHandle(mutex);
    CloseHandle(empty);
    CloseHandle(full);

    return 0;
}