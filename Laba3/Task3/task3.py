import math

import matplotlib.pyplot as plt
import numpy as np
from numba import cuda


def createRandomData(count_rows, min_value_1, max_value_1, min_value_2, max_value_2):
    np.random.seed(42)
    data_1 = np.random.uniform(low=min_value_1, high=max_value_1, size=(count_rows, 1))
    data_2 = np.random.uniform(low=min_value_2, high=max_value_2, size=(count_rows, 1))

    # Объединение массивов по второй оси (столбцам)
    data = np.concatenate((data_1, data_2), axis=1)
    return data


def visualizationInitialData(data):
    print("Исходные данные")
    print(data)
    plt.scatter(data[:, 0], data[:, 1], alpha=0.7)
    plt.title('Исходные данные')
    plt.show()


def k_means_cuda(data, count_clusters, max_iterations=100, tol=1e-4):
    centroids = data[np.random.choice(data.shape[0], count_clusters, replace=False)]
    labels = np.empty(data.shape[0], dtype=np.int32)
    prev_centroids = centroids.copy()
    device_data = cuda.to_device(data)
    device_labels = cuda.to_device(labels)
    device_centroids = cuda.to_device(centroids)

    threads_block = 16
    if data.shape[0] % threads_block == 0:
        blocks_in_grid = data.shape[0] // threads_block
    else:
        blocks_in_grid = data.shape[0] // threads_block +1
    for _ in range(max_iterations):
        k_means_kernel[blocks_in_grid, threads_block](
            device_data, device_centroids, device_labels
        )
        labels = device_labels.copy_to_host()
        centroids = device_centroids.copy_to_host()
        # Пересчет центроидов
        for i in range(centroids.shape[0]):
            count = 0
            for j in range(data.shape[0]):
                if labels[j] == i:
                    count += 1
                    for l in range(data.shape[1]):
                        centroids[i, l] += data[j, l]
            if count > 0:
                for l in range(data.shape[1]):
                    centroids[i, l] /= count

        if np.linalg.norm(centroids - prev_centroids) < tol:
            break
        prev_centroids = centroids.copy()
    return centroids, labels


@cuda.jit()
def k_means_kernel(data, centroids, labels):
    index = cuda.grid(1)
    count_rows, count_elements_in_row = data.shape
    count_clusters = centroids.shape[0]
    print(count_rows)
    print(count_elements_in_row)
    if index < count_rows:
        min_distance = np.inf
        for j in range(count_clusters):
            distance = 0.0
            for l in range(count_elements_in_row):
                distance += (data[index, l] - centroids[j, l]) ** 2
            # Присваиваем кластер с минимальным расстоянием
            if j == 0 or distance < min_distance:
                min_distance = distance
                labels[index] = j
    cuda.syncthreads()


def input_value_for_count_elements_for_random_data():
    while True:
        try:
            count_rows = int(input("Введите количество элементов для генерации случайных данных: "))
            if count_rows < 5:
                raise Exception("минимальное количество элементов - 5")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return count_rows


def input_value_for_min_value_X():
    while True:
        try:
            min_value_X = int(input("Введите минимальное значение X для генерируемых данных: "))
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return min_value_X


def input_value_for_max_value_X(min_value_X):
    while True:
        try:
            max_value_X = int(input("Введите максимальное значение X для генерируемых данных: "))
            if max_value_X < min_value_X:
                raise Exception("максимальное значение X для генерируемых данных не может быть больще минимального "
                                "значения X")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return max_value_X


def input_value_for_min_value_Y():
    while True:
        try:
            min_value_Y = int(input("Введите минимальное значение Y для генерируемых данных: "))
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return min_value_Y


def input_value_for_max_value_Y(min_value_Y):
    while True:
        try:
            max_value_Y = int(input("Введите максимальное значение Y для генерируемых данных: "))
            if max_value_Y < min_value_Y:
                raise Exception("максимальное значение Y для генерируемых данных не может быть больще минимального "
                                "значения Y")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return max_value_Y


def input_count_clusters(count_data):
    while True:
        try:
            count_clusters = int(input("Введите количество кластеров: "))
            if count_clusters > count_data:
                raise Exception("количество кластеров не может быть больше количества данных в наборе данных")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return count_clusters


def input_max_count_iteration():
    while True:
        try:
            count_iteration = int(input("Введите максимальное количество итераций: "))
            if count_iteration <= 0:
                raise Exception("максимальное количество итераций должно быть больше нуля")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return  count_iteration


def input_value_tolerance():
    while True:
        try:
            tolerance = float(input("Введите значение для точности: "))
            if tolerance >= 1 or tolerance <= 0:
                raise Exception("значение точности должно находится в диапазоне (0;1)")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return tolerance


def main():
    count_rows = input_value_for_count_elements_for_random_data()
    min_value_X = input_value_for_min_value_X()
    max_value_X = input_value_for_max_value_X(min_value_X)
    min_value_Y = input_value_for_min_value_Y()
    max_value_Y = input_value_for_max_value_Y(min_value_Y)
    randomData = createRandomData(count_rows, min_value_X, max_value_X, min_value_Y, max_value_Y)
    copyRandomData = randomData.copy()
    #visualizationInitialData(randomData)
    number_clusters = input_count_clusters(count_rows)
    max_iteration = input_max_count_iteration()
    tolerance = input_value_tolerance()
    centroids, labels = k_means_cuda(randomData, number_clusters, max_iteration, tolerance)
    plt.subplot(1, 2, 1)
    plt.scatter(copyRandomData[:, 0], copyRandomData[:, 1], alpha=0.7)
    plt.title('Исходные данные')
    plt.subplot(1, 2, 2)
    plt.scatter(randomData[:, 0], randomData[:, 1], c=labels, cmap='viridis', alpha=0.7)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
    plt.title('K-Means Clustering')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
