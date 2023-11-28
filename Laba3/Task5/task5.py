import math
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2
from numba import cuda
import uuid


@cuda.jit()
def sobel_filter_kernel(original_image_array, filtered_image_array):
    center_x, center_y = cuda.grid(2) # Получение координаты текущего потока на GPU

    # Проверка на нахождение внутри границ изображения
    if 0 < center_x < original_image_array.shape[1] - 1 and 0 < center_y < original_image_array.shape[0] - 1:
        Gx = 0
        Gy = 0

        # Проход по окрестности 3x3 вокруг текущего пикселя
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Получение значений цветового канала для текущего пикселя
                pixel = original_image_array[center_y + i, center_x + j]
                r, g, b = pixel[0], pixel[1], pixel[2]
                intensity = r + g + b
                # Вычисление взвешенных значений градиентов в направлениях x и y
                weight_x = j if j == 0 else 2 * j
                weight_y = i if i == 0 else 2 * i

                Gx += weight_x * intensity
                Gy += weight_y * intensity
        # Вычисление длины вектора градиента и нормализация
        length = math.sqrt(float((Gx * Gx) + (Gy * Gy)))
        length = int(length / 4328 * 255)
        # Присвоение полученного значения отфильтрованному пикселю
        for index in range(3):
            filtered_image_array[center_y, center_x][index] = length
    else:
        # Заполнение нулями для пикселей на границах изображения
        for index in range(3):
            filtered_image_array[center_y, center_x][index] = 0


def sobel_filter_cuda(original_image_array):
    input_array_device = cuda.to_device(original_image_array)

    # Создание массива для результата
    # output_array = np.zeros_like(input_array)
    output_array = np.copy(original_image_array)
    output_array_device = cuda.to_device(output_array)
    count_thread_by_one_axis = 16
    # Задание конфигурации сетки и блока
    threads_per_block = (count_thread_by_one_axis, count_thread_by_one_axis)
    blockspergrid_x = math.ceil(original_image_array.shape[1] / threads_per_block[0])
    blockspergrid_y = math.ceil(original_image_array.shape[0] / threads_per_block[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    sobel_filter_kernel[blockspergrid, threads_per_block](input_array_device, output_array_device)
    # Копирование данных обратно на хост
    filtered_output_array = output_array_device.copy_to_host()
    return filtered_output_array

def contains_only_english_chars(file_path):
    # Проверить, что все символы в пути являются английскими буквами
    return all(ord(char) < 128 for char in file_path)

def main():
    if cuda.is_available():
        while True:
            try:
                image_path = input("Введите название файла-изображения в рабочей папке или полный путь к изображению: ")
                if not contains_only_english_chars(image_path):
                    raise Exception("в пути должны быть только английские символы")
                if not os.path.isfile(image_path):
                    raise Exception(f"отсутствует файл по пути {image_path}")
                image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
                # Получить расширение файла
                file_extension = image_path.lower().split('.')[-1]
                if file_extension not in image_extensions:
                    raise Exception(f"файл по пути {image_path} не является изображением")
                break
            except Exception as ex:
                print(f"Ошибка: {ex}. Повторите попытку!")
        original_image = cv2.imread(image_path)
        try:
            print("-----Характеристики изображения-----")
            height, width, channels = original_image.shape
            print(f"Ширина: {width} пикселей")
            print(f"Высота: {height} пикселей")
            print(f"Количество каналов цвета: {channels}")
            if channels != 3:
                print("Количество каналов цвета должно быть 3 - RGB")
                sys.exit(1)
        except Exception as ex:
            print(ex)
            sys.exit(1)
        print(original_image)
        filtered_image = sobel_filter_cuda(original_image)

        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')

        plt.subplot(1, 2, 2)
        plt.imshow(filtered_image)
        plt.title('Filtered Image')
        plt.show()
        file_extension = image_path.lower().split('.')[-1]
        full_path_image_save = str(uuid.uuid4()) + "." + file_extension
        cv2.imwrite(full_path_image_save, filtered_image)
    else:
        print("Видеоустройство для обработки CUDA недоступно!")


if __name__ == '__main__':
    main()
