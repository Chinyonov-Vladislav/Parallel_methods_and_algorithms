from mpi4py import MPI
import sys
import math
import time

def sum_range(start, end):
    partial_sum = 0.0
    if start is not None and end is not None:
        for i in range(start, end):
            partial_sum += math.pow(-1.0, i) / (2 * i + 1)
    return partial_sum


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    start_time = time.time()
    local_start = None
    local_end = None
    if rank == 0:
        if len(sys.argv) is not 2:
            print("invalid number of command line arguments! Try again!")
            exit(-1)
        count_iteration = None
        try:
            count_iteration = int(sys.argv[1])
            if count_iteration <= 0:
                raise Exception("the number of iterations must be a positive number greater than 0!")
        except Exception as ex:
            print(f"Error: {ex}")
            comm.Abort()
        if count_iteration >= size:  # все процессы получют хотя бы 1 итерацию
            count_iteration_per_process = count_iteration // size
            for index_proc in range(1, size):
                start_for_proc = index_proc * count_iteration_per_process
                end_for_proc = start_for_proc + count_iteration_per_process
                if index_proc == size - 1:
                    end_for_proc = count_iteration
                comm.send(start_for_proc, dest=index_proc, tag=1)
                comm.send(end_for_proc, dest=index_proc, tag=2)
            local_start = 0
            local_end = count_iteration_per_process
        else:  # процессов больше, чем итераций. Не все процессы получат задачу
            for index_proc in range(1, size):
                if index_proc < count_iteration:
                    comm.send(index_proc, dest=index_proc, tag=1)
                    comm.send(index_proc + 1, dest=index_proc, tag=2)
                else:
                    comm.send(None, dest=index_proc, tag=1)
                    comm.send(None, dest=index_proc, tag=2)
            local_start = 0
            local_end = 1
    if rank != 0:
        local_start = comm.recv(source=0, tag=1)
        local_end = comm.recv(source=0, tag=2)
    print(f"Rank = {rank}, Start= {local_start}, End= {local_end}")
    local_sum = sum_range(local_start, local_end)
    all_sums = comm.gather(local_sum, root=0)
    if rank == 0:
        pi = sum(all_sums)
        print("Formula", end=": ")
        for i in range(int(sys.argv[1])):
            numerator = math.pow(-1.0, i)
            denominator = (2 * i + 1)
            if numerator * denominator >= 0:
                print("+", end="")
            else:
                print("-", end="")
            if numerator < 0:
                numerator *= -1
            if denominator < 0:
                denominator *= -1
            print(f"{numerator}/{denominator}", end="")
            if i == int(sys.argv[1]) - 1:
                print()
        end_time = time.time()
        print(f"PI number for {sys.argv[1]} iterations: {4*pi}")
        print(f"Count MPI Process = {size}. Time execution = {(end_time - start_time):.6f} seconds")


if __name__ == '__main__':
    main() #mpiexec -n 4 python IndividualTask5v2.py 1000
