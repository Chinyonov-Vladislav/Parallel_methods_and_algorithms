import threading
import random

def partition(nums, low, high):
    i = low - 1
    pivot = nums[high]

    for j in range(low, high):
        if nums[j] <= pivot:
            i = i + 1
            nums[i], nums[j] = nums[j], nums[i]

    nums[i + 1], nums[high] = nums[high], nums[i + 1]
    return i + 1


def quick_sort(nums, low, high):
    if low < high:
        pi = partition(nums, low, high)
        # Create two threads to sort the two halves of the array concurrently
        left_thread = threading.Thread(target=quick_sort, args=(nums, low, pi - 1))
        right_thread = threading.Thread(target=quick_sort, args=(nums, pi + 1, high))
        # Start the threads
        left_thread.start()
        right_thread.start()
        # Wait for both threads to finish
        left_thread.join()
        right_thread.join()


def main():
    while True:
        try:
            count_elements = int(input("Введите количество элементов массива: "))
            if count_elements <= 0:
                raise ValueError("Количество элементов массива должно быть положительным числом больше 0")
            break
        except ValueError as e:
            print(f"Ошибка: {e}. Повторите попытку!")
    ##################
    list_numbers = list()
    for _ in range(count_elements):
        list_numbers.append(random.randint(0, 100))
    print(f"Исходный массив: {list_numbers}")
    quick_sort(list_numbers, 0, len(list_numbers) - 1)
    print("Отсортированный массив:", list_numbers)


if __name__ == '__main__':
    main()
