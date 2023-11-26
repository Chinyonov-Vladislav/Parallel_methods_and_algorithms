import numba
import numpy as np
from numba import cuda
import time

# Количество случайных точек, брошенных внутри квадрата
points_inside_circle = 0


def monte_carlo_pi_one_thread(xy):
    inside_circle = 0
    for i in range(xy.shape[0]):
        coord_x, coord_y = xy[i]
        if coord_x ** 2 + coord_y ** 2 <= 1.0:
            inside_circle += 1
    return inside_circle


@cuda.jit
def monte_carlo_pi(xy, out):
    local_inside_circle = 0
    start = cuda.grid(1) * xy.shape[0] // cuda.gridsize(1)
    end = start + xy.shape[0] // cuda.gridsize(1)
    for i in range(start, end):
        coord_x, coord_y = xy[i]
        # Проверка, попала ли точка внутрь круга
        if coord_x ** 2 + coord_y ** 2 <= 1.0:
            local_inside_circle += 1
    # Суммирование результатов от всех потоков
    cuda.atomic.add(out, 0, local_inside_circle)


def getInfoDevice():
    device = numba.cuda.get_current_device()
    print("Info current device")
    print("Name:", device.name)
    print("Compute capability:", device.compute_capability)
    print("Multiprocessors:", device.MULTIPROCESSOR_COUNT)


def main():
    getInfoDevice()
    while True: # группа потоков на одном многоядерном процессоре
        try:
            blocks_per_grid = int(input("Введите количество блоков в сетки CUDA.\nВведите значение:"))
            if blocks_per_grid <= 0:
                raise Exception("количество блоков в сетки CUDA должно быть больше 0")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    while True:
        try:
            threads_per_block = int(input("Введите количество потоков для каждого блока в сетки CUDA.\nВведите "
                                          "значение:"))
            if threads_per_block <= 0:
                raise Exception("количество потоков для каждого блока в сетки CUDA должно быть больше 0")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    while True: # Количество итераций (точек) для каждого потока
        try:
            iterations_per_thread = int(input("Введите количество итераций для каждого потока в сетки CUDA.\nВведите "
                                          "значение:"))
            if iterations_per_thread <= 0:
                raise Exception("количество итераций для каждого потока в сетки CUDA должно быть больше 0")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    # Генерация случайных координат на CPU
    xy = np.column_stack((
        np.random.uniform(low=-1, high=1, size=iterations_per_thread * threads_per_block * blocks_per_grid),
        np.random.uniform(low=-1, high=1, size=iterations_per_thread * threads_per_block * blocks_per_grid))
    )
    # Выделение памяти для хранения результата
    out = np.zeros(1, dtype=np.int32)

    print("-----CUDA-----")
    # Запуск ядра CUDA
    start_time = time.time()
    monte_carlo_pi[blocks_per_grid, threads_per_block](xy, out)
    end_time = time.time()

    points_inside_circle = out[0]
    print(f"Общее количество точек = {xy.shape[0]}")
    pi_estimate = 4.0 * points_inside_circle / xy.shape[0]
    print("Вычисленнное значение PI:", pi_estimate)
    print("Время выполнения:", end_time - start_time, "seconds")

    print("-----Однопоточный режим-----")
    start_time = time.time()
    points_inside_circle = monte_carlo_pi_one_thread(xy)
    end_time = time.time()
    print(f"Общее количество точек = {xy.shape[0]}")
    pi_estimate = 4.0 * points_inside_circle / xy.shape[0]
    print("Вычисленнное значение PI:", pi_estimate)
    print("Время выполнения:", end_time - start_time, "seconds")


if __name__ == '__main__':
    main()
