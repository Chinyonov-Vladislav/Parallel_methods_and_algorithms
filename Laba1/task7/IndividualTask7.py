import threading
import math

pi = 0.0
lock = threading.Lock()
print_lock = threading.Lock()


def sum(start, end, identificator):
    global pi
    partial_sum = 0.0
    for i in range(start, end):
        with print_lock:
            print(f"Идентификатор потока = {identificator}, Номер итерации = {i + 1}")
        partial_sum += math.pow(-1.0, i) / (2 * i + 1)
    with lock:
        pi += partial_sum


def main():
    global pi
    print("Формула Лейбница для вычисления числа PI")
    while True:
        try:
            num_threads = int(input("Введите количество потоков: "))  # количество потоков
            if num_threads <= 0:
                raise ValueError
            num_iterations = int(input("Введите количество итераций: "))  # количество итераций ряда
            if num_iterations <= 0:
                raise ValueError
            if num_iterations < num_threads:
                print(
                    "Количество итераций не может быть меньше количества потоков.\n1-Сравнять количество потоков с количеством итераций\n2-1-Сравнять количество итераций с количеством потоков")
                answer = None
                while True:
                    try:
                        answer = int(input("Ваш выбор: "))
                        if answer == 1:
                            num_threads = num_iterations
                        if answer == 2:
                            num_iterations = num_threads
                        else:
                            raise ValueError
                        break
                    except ValueError:
                        print("Неверный выбор. Повторите попытку!")
            break
        except ValueError:
            print("Введено неверное значение. Введите корректное целое положительно число, больше 0")

    if num_iterations >= num_threads:
        threads = list()
        residual_iterations = 0
        if num_iterations % num_threads != 0:
            residual_iterations = num_iterations % num_threads
        with print_lock:
            print(f"residuals = {residual_iterations}")
        iterations_per_thread = num_iterations // num_threads
        for i in range(0, num_threads):
            start = i * iterations_per_thread
            with print_lock:
                print(f"start= {start}")
            end = start + iterations_per_thread
            with print_lock:
                print(f"end= {end}")
            if i == num_threads - 1 and residual_iterations != 0:
                end += residual_iterations
            with print_lock:
                print(f"Количество итераций на потоке №{i} = {end - start}")
            thread = threading.Thread(target=sum, args=(start, end, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        print(f"Результат = {4*pi}")
    else:
        print("Невозможно разделить итерации на потоки!")


if __name__ == '__main__':
    main()
