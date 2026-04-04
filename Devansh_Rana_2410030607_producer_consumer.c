#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>

int *buffer;
int BUFFER_SIZE;
int in = 0, out = 0;
int n; // number of items

sem_t mutex, empty, full;

// Producer
void* producer(void* arg) {
    int item;

    for(int i = 0; i < n; i++) {
        item = rand() % 100;

        sem_wait(&empty);
        sem_wait(&mutex);

        buffer[in] = item;
        printf("Produced: %d at %d\n", item, in);
        in = (in + 1) % BUFFER_SIZE;

        sem_post(&mutex);
        sem_post(&full);
    }
    return NULL;
}

// Consumer
void* consumer(void* arg) {
    int item;

    for(int i = 0; i < n; i++) {
        sem_wait(&full);
        sem_wait(&mutex);

        item = buffer[out];
        printf("Consumed: %d from %d\n", item, out);
        out = (out + 1) % BUFFER_SIZE;

        sem_post(&mutex);
        sem_post(&empty);
    }
    return NULL;
}

int main() {
    pthread_t p, c;

    // Input
    printf("Enter buffer size: ");
    scanf("%d", &BUFFER_SIZE);

    printf("Enter number of items to produce: ");
    scanf("%d", &n);

    buffer = (int*)malloc(BUFFER_SIZE * sizeof(int));

    // Initialize semaphores
    sem_init(&mutex, 0, 1);
    sem_init(&empty, 0, BUFFER_SIZE);
    sem_init(&full, 0, 0);

    // Create threads
    pthread_create(&p, NULL, producer, NULL);
    pthread_create(&c, NULL, consumer, NULL);

    // Wait for completion
    pthread_join(p, NULL);
    pthread_join(c, NULL);

    // Cleanup
    sem_destroy(&mutex);
    sem_destroy(&empty);
    sem_destroy(&full);
    free(buffer);

    return 0;
}