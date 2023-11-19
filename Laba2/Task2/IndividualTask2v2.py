from mpi4py import MPI
import sys
import time

def is_prime_number(number):
    k = 0
    for i in range(2, number // 2 + 1):
        if number % i == 0:
            k = k + 1
    return k <= 0


def find_primes_in_range(start, end):
    primes = [number for number in range(start, end + 1) if is_prime_number(number)]
    return primes


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    start = 1
    end = None
    start_time = time.time()
    if rank == 0:
        if len(sys.argv) is not 2:
            print("Invalid number of command line arguments! Try again!")
            comm.Abort()
        try:
            end = int(sys.argv[1])
            if end < 1:
                raise Exception("Invalid value for end. End must be greater than 1")
        except Exception as e:
            print(f"Error: {e}")
            comm.Abort()
        chunk_size = (end - start + 1) // size
        for index_proc in range(1,size):
            start_for_proc = start + index_proc * chunk_size
            end_for_proc = start_for_proc + chunk_size - 1
            if index_proc == size - 1:
                end_for_proc = end
            comm.send(start_for_proc, dest=index_proc, tag=1)
            comm.send(end_for_proc, dest=index_proc, tag=2)
        start = start + rank * chunk_size
        end = start + chunk_size - 1
    if rank != 0:
        start = comm.recv(source=0, tag=1)
        end = comm.recv(source=0, tag=2)
    print(f"Rank = {rank}, start = {start}, end = {end}")
    local_primes = find_primes_in_range(start, end)
    all_primes = comm.gather(local_primes, root=0)
    if rank == 0:
        end_time = time.time()
        print(f"Prime numbers in range from {start} to {sys.argv[1]}")
        for rank_prime in all_primes:
            for item in rank_prime:
                print(item)
        print(f"Count MPI Process = {size}. Time execution = {(end_time - start_time):.6f} seconds")

if __name__ == '__main__':
    main() #mpiexec -n 4 python IndividualTask2v2.py 1000
