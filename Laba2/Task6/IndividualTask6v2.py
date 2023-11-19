import sys
from mpi4py import MPI
import math
import random
import time


def getRandomCoord(radius):
    return random.uniform(-radius, radius), random.uniform(-radius, radius)


def isPointInsideCircle(coord_x, coord_y, radius):
    return math.pow(coord_x, 2) + math.pow(coord_y, 2) <= math.pow(radius, 2)


def find_count_in_circle_in_range(start_range, end_range, radius):
    count_in_circle = 0
    if start_range is not None and end_range is not None:
        for i in range(start_range, end_range):
            coord_x, coord_y = getRandomCoord(radius)
            if isPointInsideCircle(coord_x, coord_y, radius):
                count_in_circle += 1
    return count_in_circle

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    local_start = None
    local_end = None
    radius = None
    start_time = time.time()
    if rank == 0:
        if len(sys.argv) is not 3:
            print("Invalid number of command line arguments! Try again!")
            comm.Abort()
        count_points = None
        try:
            count_points = int(sys.argv[1])
            if count_points <= 0:
                raise Exception("the number of points must be a positive number greater than 0!")
            radius = float(sys.argv[2])
            if radius <= 0:
                raise Exception("the radius of the circle must be a positive number greater than 0!")
        except Exception as ex:
            print(f"Error: {ex}")
            comm.Abort()
        if count_points >= size: # необходимо разделить на процессы, каждый процесс получит как минимум 1
            count_iteration_per_process = count_points // size
            for index_proc in range(1,size):
                start_for_proc = index_proc * count_iteration_per_process
                end_for_proc = start_for_proc + count_iteration_per_process
                if index_proc == size - 1:
                    end_for_proc = count_points
                comm.send(start_for_proc, dest=index_proc, tag=1)
                comm.send(end_for_proc, dest=index_proc, tag=2)
                comm.send(radius, dest=index_proc, tag=3)
            local_start = 0
            local_end = count_iteration_per_process
        else: # процессов больше, чем итераций. Не все процессы получат задачу
            for index_proc in range(1, size):
                if index_proc < count_points:
                    comm.send(index_proc, dest=index_proc, tag=1)
                    comm.send(index_proc + 1, dest=index_proc, tag=2)
                    comm.send(radius, dest=index_proc, tag=3)
                else:
                    comm.send(None, dest=index_proc, tag=1)
                    comm.send(None, dest=index_proc, tag=2)
                    comm.send(None, dest=index_proc, tag=2)
            local_start = 0
            local_end = 1
    if rank != 0:
        local_start = comm.recv(source=0, tag=1)
        local_end = comm.recv(source=0, tag=2)
        radius = comm.recv(source=0, tag=3)
    print(f"Rank = {rank}, Start= {local_start}, End= {local_end}")
    local_count_in_circle = find_count_in_circle_in_range(local_start, local_end, radius)
    all_count_in_circle = comm.gather(local_count_in_circle, root=0)
    if rank == 0:
        result = 4.0*sum(all_count_in_circle)/float(sys.argv[1])
        end_time = time.time()
        print(f"PI number by method Monte-Carlo for {sys.argv[1]} iterations (radius circle = {sys.argv[2]}): {result}")
        print(f"Count MPI Process = {size}. Time execution = {(end_time - start_time):.6f} seconds")

if __name__ == '__main__':
    main() #mpiexec -n 4 python IndividualTask6v2.py 1000 1.0