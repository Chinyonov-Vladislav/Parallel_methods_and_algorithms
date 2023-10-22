import threading
import time
import random

print_lock = threading.Lock()


def philosopher_eats(index, left_fork, right_fork):
    while True:
        with print_lock:
            print(f"Философ №{index} размышляет")
        time.sleep(random.randrange(1, 6))  # имитация процесса размышления
        if left_fork.acquire(blocking=False):
            with print_lock:
                print(f"Философ №{index} взял левую вилку")
            if right_fork.acquire(blocking=False):
                with print_lock:
                    print(f"Философ №{index} взял правую вилку")
                    print(f"Философ №{index} ест")
                time.sleep(random.randrange(1, 6))  # имитация процесса приема пищи
                with print_lock:
                    print(f"Философ №{index} закончил приём пищи")
                right_fork.release()
                with print_lock:
                    print(f"Философ №{index} взял положил правую вилку")
            left_fork.release()
            with print_lock:
                print(f"Философ №{index} взял положил левую вилку")


def main():
    countOfPhilosophers = 5
    threadsPhilosopher = list()
    forks = [threading.Lock() for _ in range(countOfPhilosophers)]
    for index in range(countOfPhilosophers):
        threadPhilosopher = threading.Thread(target=philosopher_eats,
                                             args=(index, forks[index], forks[(index + 1) % countOfPhilosophers]))
        threadPhilosopher.start()
        threadsPhilosopher.append(threadPhilosopher)
    for thread in threadsPhilosopher:
        thread.join()


if __name__ == '__main__':
    main()
