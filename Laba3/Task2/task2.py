from numba import cuda
import numpy as np
import time


@cuda.jit
def merge_sort(arr, output_array):
    thread_id = cuda.threadIdx.x
    block_size = cuda.blockDim.x
    total_count_threads = block_size * cuda.gridDim.x
    stride = len(arr) // total_count_threads
    start_index = min(thread_id * stride, len(arr))
    finish_index = min(start_index + stride, len(arr))
    if thread_id == total_count_threads - 1:
        finish_index = len(arr)
    part_array_for_current_thread = arr[start_index:finish_index]
    sorted_part_array = True
    if len(part_array_for_current_thread) > 1:
        for index in range(1, len(part_array_for_current_thread)):  # проверка отсортированности массива
            if part_array_for_current_thread[index - 1] > part_array_for_current_thread[index]:
                sorted_part_array = False
                break
    if sorted_part_array is False:
        for i in range(finish_index - 1):  # сортировка текущей части общего массива на потоке CUDA
            for j in range(start_index, finish_index - i - 1):
                if arr[j] > arr[j + 1]:
                    # Обмен элементов, если они стоят в неправильном порядке
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
    cuda.syncthreads()
    print(thread_id, stride, start_index, finish_index)
    if thread_id % 2 == 0:
        index_global_array = thread_id * stride
        start_index_left = min(thread_id * stride, len(arr))
        finish_index_left = min(thread_id * stride + stride, len(arr))
        start_index_right = min(thread_id * stride + stride, len(arr))
        finish_index_right = min(thread_id * stride + 2 * stride, len(arr))
        if total_count_threads % 2 == 0:
            if thread_id == total_count_threads - 2:
                finish_index_right = len(arr)
        else:
            if thread_id == total_count_threads - 1:
                finish_index_right = len(arr)
        left = arr[start_index_left:finish_index_left]
        right = arr[start_index_right:finish_index_right]
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                output_array[index_global_array] = left[i]
                i += 1
            else:
                output_array[index_global_array] = right[j]
                j += 1
            index_global_array += 1
        while i < len(left):
            output_array[index_global_array] = left[i]
            i += 1
            index_global_array += 1
        while j < len(right):
            output_array[index_global_array] = right[j]
            j += 1
            index_global_array += 1
    cuda.syncthreads()


def generateList(count_elements, min, max):
    data = np.random.randint(low=min, high=max, size=(count_elements))
    return data


def merge_sort_cuda(array, count_threads):
    output_array = array.copy()
    while count_threads != 1:
        device_array = cuda.to_device(array)
        device_output_array = cuda.to_device(output_array)
        merge_sort[1, count_threads](device_array, device_output_array)
        array = device_array.copy_to_host()
        output_array = device_output_array.copy_to_host()
        count_threads //= 2
    return output_array


def input_count_elements_in_array():
    while True:
        try:
            count_elements = int(input("Введите количество элементов в массиве: "))
            if count_elements <= 0:
                raise Exception("количество элементов в массиве должно быть больше 0")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return count_elements


def input_min_value_in_array():
    while True:
        try:
            min_value = int(input("Введите минимальное значения для генератора случайных чисел: "))
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return min_value


def input_max_value_in_array(min_value):
    while True:
        try:
            max_value = int(input("Введите максимальное значения для генератора случайных чисел: "))
            if min_value >= max_value:
                raise Exception("максимальное значение для генератора случайных чисел должно быть больше миниального")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return max_value


def input_count_threads(count_elements_array):
    while True:
        try:
            count_threads = int(input("Введите количество потоков: "))
            if count_threads <= 0:
                raise Exception("количество потоков должно быть больше 0")
            if count_threads > count_elements_array:
                raise Exception("количество потоков не может превышать количество элементов в массиве")
            break
        except Exception as ex:
            print(f"Ошибка: {ex}. Повторите попытку!")
    return count_threads


def merge_sort_one_thread(arr):
    if len(arr) <= 1:
        return arr

    # Разделяем массив пополам
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # Рекурсивно применяем сортировку слиянием к двум половинам
    left_half = merge_sort_one_thread(left_half)
    right_half = merge_sort_one_thread(right_half)

    # Объединяем отсортированные половины
    return merge_one_thread(left_half, right_half)


def merge_one_thread(left, right):
    result = []
    i = j = 0

    # Сравниваем элементы и объединяем в отсортированный массив
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Добавляем оставшиеся элементы (если есть)
    result.extend(left[i:])
    result.extend(right[j:])

    return result


def main():
    count_elements = input_count_elements_in_array()
    min_value = input_min_value_in_array()
    max_value = input_max_value_in_array(min_value)
    data = generateList(count_elements, min_value, max_value)
    number_threads = input_count_threads(count_elements)
    initial_data = data.copy()
    start_time = time.time()
    sorted_array = np.array(merge_sort_cuda(data, number_threads))
    end_time = time.time()
    print("-----CUDA-----")
    print(f"Исходный массив: {initial_data}")
    print(f"Отсортированный массив: {sorted_array}")
    print("Время выполнения:", end_time - start_time, "seconds")
    start_time = time.time()
    sorted_array_one_thread = merge_sort_one_thread(initial_data)
    end_time = time.time()
    print("-----Однопоточный режим-----")
    print(f"Исходный массив: {initial_data}")
    print(f"Отсортированный массив: {sorted_array_one_thread}")
    print("Время выполнения:", end_time - start_time, "seconds")


if __name__ == '__main__':
    main()
