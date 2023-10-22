import threading
import random

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        left_thread = threading.Thread(target=merge_sort, args=(left_half,))
        right_thread = threading.Thread(target=merge_sort, args=(right_half,))

        left_thread.start()
        right_thread.start()

        left_thread.join()
        right_thread.join()

        # Merge the sorted halves
        merge(arr, left_half, right_half)


def merge(arr, left, right):
    i = j = k = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1

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
    # Example usage
    print("Original array:", list_numbers)

    merge_sort(list_numbers)

    print("Sorted array:", list_numbers)

if __name__ == "__main__":
    main()