import threading
import time

print_lock = threading.Lock()

def philosopher_eats(index_philosopher, left_fork, right_fork):
    while True:
        with print_lock:
            print(f"Философ №{index_philosopher} размышляет")
        time.sleep(3)  # имитация процесса размышления
        left_fork.acquire()
        with print_lock:
            print(f"Философ №{index_philosopher} взял левую вилку")
        right_fork.acquire()
        with print_lock:
            print(f"Философ №{index_philosopher} взял правую вилку")
            print(f"Философ №{index_philosopher} осуществляем приём пищи")
        time.sleep(1)
        left_fork.release()
        with print_lock:
            print(f"Философ №{index_philosopher} положил левую вилку")
        right_fork.release()
        with print_lock:
            print(f"Философ №{index_philosopher} положил правую вилку")



def main():
    countOfPhilosophers = 5
    forks = [threading.Lock() for _ in range(countOfPhilosophers)]
    threadsPhilosopher = list()
    for index in range(countOfPhilosophers):
        threadPhilosopher = threading.Thread(target=philosopher_eats, args=(index,forks[index],forks[(index + 1) % countOfPhilosophers] ))
        threadPhilosopher.start()
        threadsPhilosopher.append(threadPhilosopher)
    for thread in threadsPhilosopher:
        thread.join()
    print("Конец программы!")


if __name__ == '__main__':
    main()
