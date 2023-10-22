import threading
import time
import random

# Define the maximum number of customers and the number of chairs in the waiting room
MAX_CUSTOMERS = 10
NUM_CHAIRS = 3

# Define the semaphores for the barber, the customers, and the mutex
barber_semaphore = threading.Semaphore(0)
customer_semaphore = threading.Semaphore(0)
mutex = threading.Semaphore(1)


waiting_customers = []


def barber():
    while True:
        print("The barber is sleeping...")
        barber_semaphore.acquire()
        mutex.acquire()
        if len(waiting_customers) > 0:
            customer = waiting_customers.pop(0)
            print(f"The barber is cutting hair for customer {customer}")
            mutex.release()
            time.sleep(random.randint(1, 5))
            print(f"The barber has finished cutting hair for customer {customer}")
            customer_semaphore.release()
        else:
            mutex.release()


def customer(index):
    global waiting_customers
    time.sleep(random.randint(1, 5))
    mutex.acquire()
    if len(waiting_customers) < NUM_CHAIRS:
        waiting_customers.append(index)
        print(f"Customer {index} is waiting in the waiting room")
        mutex.release()
        barber_semaphore.release()
        customer_semaphore.acquire()
        print(f"Customer {index} has finished getting a haircut")
    else:
        print(f"Customer {index} is leaving because the waiting room is full")
        mutex.release()

def main():

    barber_thread = threading.Thread(target=barber)

    customer_threads = []
    for i in range(MAX_CUSTOMERS):
        customer_threads.append(threading.Thread(target=customer, args=(i,)))

    barber_thread.start()
    for thread in customer_threads:
        thread.start()
        
if __name__ == '__main__':
    main()