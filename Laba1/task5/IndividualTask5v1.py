# В данной реализации исходный массив

import random
from utils.ThreadWithReturnValue import ThreadWithReturnValue

def merge(left, right):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1
    return merged


def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    left = merge_sort(left)
    right = merge_sort(right)
    merged = merge(left, right)
    return merged


def main():
    while True:
        try:
            count_elements = int(input("Введите количество элементов массива: "))
            if count_elements <= 0:
                raise ValueError("Количество элементов массива должно быть положительным числом больше 0")
            while True:
                try:
                    count_threads = int(input("Введите желаемое количество потоков: "))
                    if count_threads <= 0:
                        raise ValueError("Количество потоков должно быть больше 0")
                    break
                except ValueError as e:
                    print(f"Ошибка: {e}. Повторите попытку!")
            if count_threads > count_elements:
                raise ValueError(
                    "Количество элементов в массиве должно быть больше или равно количеству потоков")
            break
        except ValueError as e:
            print(f"Ошибка: {e}. Повторите попытку!")
    list_numbers = list()
    for _ in range(count_elements):
        list_numbers.append(random.randint(0, 100))
    if len(list_numbers) <= 1:
        print(list_numbers)
        return
    print(f"Исходный массив: {list_numbers}")
    size_list_for_thread = len(list_numbers) // count_threads

    sublists_numbers = [list_numbers[i * size_list_for_thread:(i + 1) * size_list_for_thread] for i in
                        range(count_threads)]
    # Если длина list_numbers не делится равномерно на count_threads, добавляем остаток к последнему подсписку
    if len(list_numbers) % count_threads != 0:
        sublists_numbers[-1].extend(list_numbers[size_list_for_thread * count_threads:])
    for index, sublist in enumerate(sublists_numbers):
        print(f"Index Thread = {index}, Sublist = {sublist}")
    list_of_threads = list()
    for sublist_numbers in sublists_numbers:
        # thread = threading.Thread(target=merge_sort, args=(sublist_numbers,))
        thread = ThreadWithReturnValue(target=merge_sort, args=(sublist_numbers,))
        thread.start()
        list_of_threads.append(thread)
    sorted_sublists = list()
    for thread in list_of_threads:
        sorted_sublists.append(thread.join())
    print("Отсортированные списки")
    for item in sorted_sublists:
        print(item)
    print("-------------")
    if len(sorted_sublists) <= 3:
        merged = sorted_sublists[0]
        for sublist in sorted_sublists[1:]:
            if sublist is not None and type(sublist) is list:
                merged = merge(merged, sublist)
    else:
        list_threads_merge = list()
        while len(sorted_sublists) > 1:
            for index in range(0, len(sorted_sublists) - 1, 2):
                thread_merge = ThreadWithReturnValue(target=merge,
                                                     args=(sorted_sublists[index], sorted_sublists[index + 1]))
                thread_merge.start()
                list_threads_merge.append(thread_merge)
            last_sorted_array = sorted_sublists[len(sorted_sublists) - 1] if len(sorted_sublists) % 2 != 0 else None
            sorted_sublists.clear()
            for thread in list_threads_merge:
                sorted_sublists.append(thread.join())
            list_threads_merge.clear()
            if last_sorted_array is not None:
                sorted_sublists.append(last_sorted_array)
            # print(f"Отсортированные списки = {sorted_sublists}")
        merged = sorted_sublists[0]
    print(f"Отсортированный массив: {merged}")

if __name__ == '__main__':
    main()
