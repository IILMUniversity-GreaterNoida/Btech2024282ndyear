#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

// ─── Globals ─────────────────────────────────────────────────
int *buffer;
int in  = 0;
int out = 0;
int BUFFER_SIZE;
int TOTAL_ITEMS;

HANDLE mutex;
HANDLE empty;
HANDLE full;

// ─── Producer ────────────────────────────────────────────────
DWORD WINAPI producer(LPVOID arg) {
    int item;

    for (int i = 0; i < TOTAL_ITEMS; i++) {
        item = rand() % 100;

        WaitForSingleObject(empty, INFINITE);
        WaitForSingleObject(mutex, INFINITE);

        buffer[in] = item;
        printf("[Producer] Inserted: %d at index %d\n", item, in);
        in = (in + 1) % BUFFER_SIZE;

        ReleaseSemaphore(mutex, 1, NULL);
        ReleaseSemaphore(full,  1, NULL);

        Sleep(1000);
    }

    printf("[Producer] Done producing.\n");
    return 0;
}

// ─── Consumer ────────────────────────────────────────────────
DWORD WINAPI consumer(LPVOID arg) {
    int item;

    for (int i = 0; i < TOTAL_ITEMS; i++) {

        WaitForSingleObject(full,  INFINITE);
        WaitForSingleObject(mutex, INFINITE);

        item = buffer[out];
        printf("[Consumer] Removed:   %d from index %d\n", item, out);
        out = (out + 1) % BUFFER_SIZE;

        ReleaseSemaphore(mutex, 1, NULL);
        ReleaseSemaphore(empty, 1, NULL);

        Sleep(2000);
    }

    printf("[Consumer] Done consuming.\n");
    return 0;
}

// ─── Main ─────────────────────────────────────────────────────
int main() {
    HANDLE threads[2];

    // ─── User Input ──────────────────────────────────────────
    printf("=== Producer Consumer Problem ===\n\n");

    printf("Enter buffer size: ");
    scanf("%d", &BUFFER_SIZE);

    printf("Enter total items to produce: ");
    scanf("%d", &TOTAL_ITEMS);

    // Dynamically allocate buffer based on user input
    buffer = (int *)malloc(BUFFER_SIZE * sizeof(int));

    printf("\nBuffer Size: %d | Total Items: %d\n", BUFFER_SIZE, TOTAL_ITEMS);
    printf("-------------------------\n\n");

    // ─── Semaphore Setup ─────────────────────────────────────
    mutex = CreateSemaphore(NULL, 1,           1,           NULL);
    empty = CreateSemaphore(NULL, BUFFER_SIZE, BUFFER_SIZE, NULL);
    full  = CreateSemaphore(NULL, 0,           BUFFER_SIZE, NULL);

    // ─── Thread Creation ─────────────────────────────────────
    threads[0] = CreateThread(NULL, 0, producer, NULL, 0, NULL);
    threads[1] = CreateThread(NULL, 0, consumer, NULL, 0, NULL);

    // ─── Wait for both to finish ─────────────────────────────
    WaitForMultipleObjects(2, threads, TRUE, INFINITE);

    // ─── Cleanup ─────────────────────────────────────────────
    free(buffer);
    CloseHandle(mutex);
    CloseHandle(empty);
    CloseHandle(full);
    CloseHandle(threads[0]);
    CloseHandle(threads[1]);

    printf("\n[Main] All done. Program exiting cleanly.\n");
    return 0;
}