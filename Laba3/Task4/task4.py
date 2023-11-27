import math
import cv2
from numba import cuda
import numpy as np
import numba
import os
import uuid
import matplotlib.pyplot as plt
size_local_array = 0


@cuda.jit
def median_filter_kernel(input_array, output_array, width_image, height_image,
                         window_size_func):
    '''number_thread_x = cuda.threadIdx.x
    number_thread_y = cuda.threadIdx.y
    number_block_x = cuda.blockIdx.x
    number_block_y = cuda.blockIdx.y
    count_blocks_x = cuda.blockDim.x
    count_blocks_y = cuda.blockDim.y
    center_x = number_thread_x + number_block_x * count_blocks_x
    center_y = number_thread_y + number_block_y * count_blocks_y'''
    center_x, center_y = cuda.grid(2)
    print(center_x, center_y)
    half_size = window_size_func // 2
    left = center_x - half_size
    top = center_y - half_size
    right = center_x + half_size + 1  # +1 для включения правой границы
    bottom = center_y + half_size + 1
    if center_x - half_size >= 0 and center_y - half_size >= 0 \
            and center_x + half_size < width_image and center_y + half_size < height_image:  # отсекаем края
        window_values = cuda.local.array(shape=size_local_array, dtype=numba.int64)
        index = 0
        for index_x in range(left, right):
            for index_y in range(top, bottom):
                if 0 <= index_x < width_image and 0 <= index_y < height_image:
                    window_values[index] = input_array[index_y, index_x]
                    index += 1
        for i in range(len(window_values)):
            for j in range(0, len(window_values) - i - 1):
                if window_values[j] > window_values[j + 1]:
                    window_values[j], window_values[j + 1] = window_values[j + 1], window_values[j]
        # print(center_x, center_y, left, right, top, bottom, window_values[index // 2])
        if len(window_values) % 2 == 1:
            output_array[center_y, center_x] = window_values[len(window_values) // 2]
        else:
            mid1 = window_values[len(window_values) // 2]
            mid2 = window_values[len(window_values) // 2 - 1]
            output_array[center_y, center_x] = (mid1 + mid2) / 2
    cuda.syncthreads()


def median_filter(input_array, window_size, width_image, height_image):
    # Перемещение данных на устройство CUDA
    input_array_device = cuda.to_device(input_array)

    # Создание массива для результата
    # output_array = np.zeros_like(input_array)
    output_array = np.copy(input_array)
    output_array_device = cuda.to_device(output_array)
    count_thread_by_one_axis = 16
    # Задание конфигурации сетки и блока
    threads_per_block = (count_thread_by_one_axis, count_thread_by_one_axis)
    blockspergrid_x = math.ceil(input_array.shape[1] / threads_per_block[0])
    blockspergrid_y = math.ceil(input_array.shape[0] / threads_per_block[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)
    global size_local_array
    size_local_array = window_size * window_size
    # Запуск ядра CUDA
    median_filter_kernel[blockspergrid, threads_per_block](input_array_device, output_array_device,
                                                           width_image, height_image,
                                                           window_size)
    # Копирование данных обратно на хост
    filtered_output_array = output_array_device.copy_to_host()
    return filtered_output_array


def getInfoDivice():
    gpu = cuda.get_current_device()
    print("name = %s" % gpu.name)
    print("maxThreadsPerBlock = %s" % str(gpu.MAX_THREADS_PER_BLOCK))
    print("maxBlockDimX = %s" % str(gpu.MAX_BLOCK_DIM_X))
    print("maxBlockDimY = %s" % str(gpu.MAX_BLOCK_DIM_Y))
    print("maxBlockDimZ = %s" % str(gpu.MAX_BLOCK_DIM_Z))
    print("maxGridDimX = %s" % str(gpu.MAX_GRID_DIM_X))
    print("maxGridDimY = %s" % str(gpu.MAX_GRID_DIM_Y))
    print("maxGridDimZ = %s" % str(gpu.MAX_GRID_DIM_Z))
    print("maxSharedMemoryPerBlock = %s" % str(gpu.MAX_SHARED_MEMORY_PER_BLOCK))
    print("asyncEngineCount = %s" % str(gpu.ASYNC_ENGINE_COUNT))
    print("canMapHostMemory = %s" % str(gpu.CAN_MAP_HOST_MEMORY))
    print("multiProcessorCount = %s" % str(gpu.MULTIPROCESSOR_COUNT))
    print("warpSize = %s" % str(gpu.WARP_SIZE))
    print("unifiedAddressing = %s" % str(gpu.UNIFIED_ADDRESSING))
    print("pciBusID = %s" % str(gpu.PCI_BUS_ID))
    print("pciDeviceID = %s" % str(gpu.PCI_DEVICE_ID))


def contains_only_english_chars(file_path):
    # Проверить, что все символы в пути являются английскими буквами
    return all(ord(char) < 128 for char in file_path)


def main():
    if cuda.is_available():
        getInfoDivice()
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
        print(f"Путь к изображения: {image_path}")
        original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # загружаем изображение в черно-белом формате
        print("-----Характеристики изображения-----")
        height, width = original_image.shape
        print(f"Ширина: {width} пикселей")
        print(f"Высота: {height} пикселей")
        while True:
            try:
                window_size = int(input("Задайте размер окна фильтрации: "))
                if window_size <= 0:
                    raise Exception("размер окна фильтрации должен быть больше 0")
                break
            except Exception as ex:
                print(f"Ошибка: {ex}. Повторите попытку!")

        filtered_image = median_filter(original_image, window_size, width, height)

        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')

        plt.subplot(1, 2, 2)
        print(filtered_image)
        plt.imshow(filtered_image, cmap='gray')
        plt.title('Filtered Image')
        plt.show()
        file_extension = image_path.lower().split('.')[-1]
        full_path_image_save = str(uuid.uuid4()) + "." + file_extension
        cv2.imwrite(full_path_image_save, filtered_image)
    else:
        print("Видеоустройство для обработки CUDA недоступно!")

if __name__ == '__main__':
    main()
