import sys

from mpi4py import MPI
import random
import time

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
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    start_time = time.time()
    if rank == 0:
        if len(sys.argv) is not 2:
            print("invalid number of command line arguments! Try again!")
            comm.Abort()
            exit(-1)
        mode = sys.argv[1]
        if mode == 'dev':
            while True:
                try:
                    count_elements = int(input("Enter the number of array elements: "))
                    if count_elements <= 0:
                        raise ValueError("The number of array elements must be a positive number greater than 0")
                    break
                except ValueError as e:
                    print(f"Error: {e}. Try again!")
            list_numbers = list()
            while True:
                try:
                    choice = int(input("Choose the way to fill the array: 1 - manual filling of the array, 2 - automatic "
                                       "filling of the array (random numbers from 1 to 100): "))
                    if choice != 1 and choice != 2:
                        raise ValueError("You entered an incorrect value")
                    break
                except ValueError as e:
                    print(f"Error: {e}. Try again!")
            if choice == 2:
                for _ in range(count_elements):
                    list_numbers.append(random.randint(0, 100))
            else:
                for index in range(count_elements):
                    while True:
                        try:
                            number = int(input(f"Enter {index} element of array: "))
                            list_numbers.append(number)
                            break
                        except ValueError as ex:
                            print(f"Error: {ex}. Try again!")
        elif mode == 'test':
            list_numbers = list()
            for _ in range(25):
                list_numbers.append(random.randint(0, 100))
        else:
            print("Unknown mode")
            comm.Abort()
            sys.exit(1)
        #########################
        print(f"Original Array: {list_numbers}")
        if size <= len(list_numbers):
            count_elements_arrays_per_process = len(list_numbers) // size
            for index_proc in range(1, size):
                start_index_elements_array_for_proc = index_proc * count_elements_arrays_per_process
                end_index_elements_array_for_proc = start_index_elements_array_for_proc + count_elements_arrays_per_process
                if index_proc == size - 1:
                    end_index_elements_array_for_proc = len(list_numbers)
                comm.send(list_numbers[start_index_elements_array_for_proc:end_index_elements_array_for_proc],
                          dest=index_proc,
                          tag=1)
            chunk_array = list_numbers[0:count_elements_arrays_per_process]
        else:
            for index_proc in range(1, size):
                if index_proc < len(list_numbers):
                    comm.send(list_numbers[index_proc: index_proc + 1], dest=index_proc, tag=1)
                else:
                    comm.send(None, dest=index_proc, tag=1)
            chunk_array = list_numbers[0:1]
    else:
        chunk_array = comm.recv(source=0, tag=1)
    chunk_array = merge_sort(chunk_array)
    sorted_arrays = comm.gather(chunk_array, root=0)
    if rank == 0:
        while len(sorted_arrays) != 1:
            right_array = sorted_arrays.pop(len(sorted_arrays) - 1)
            left_array = sorted_arrays.pop(len(sorted_arrays) - 1)
            merged_array = merge(left_array, right_array)
            sorted_arrays.append(merged_array)
        end_time = time.time()
        print(f"Sorted Array: {sorted_arrays[0]}")
        print(f"Count MPI Process = {size}. Time execution = {(end_time - start_time):.6f} seconds")


if __name__ == '__main__':
    main() #mpiexec -n 4 python IndividualTask4.py test
