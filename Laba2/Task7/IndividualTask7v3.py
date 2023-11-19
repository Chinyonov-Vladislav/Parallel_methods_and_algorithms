import sys
from mpi4py import MPI
import numpy as np
import soundfile as sf
import time
import os


def calculate_energy(segment_signal):
    return np.sum(segment_signal ** 2)


def my_zero_cross_rate(segment_signal):
    count = 0
    for index in range(0, len(segment_signal)):
        if segment_signal[index][0] < 0 and segment_signal[index][1] == 0.0:
            count += 1
            continue
        if segment_signal[index][0] * segment_signal[index][1] < 0:
            count += 1
    return count / len(segment_signal)


def main():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
        if len(sys.argv) != 4:
            print(
                "Usage: mpiexec -n 4 IndividualTask7v2.py <path to wav-file> <window_size> <shift_size>")
            sys.exit(1)
        try:
            audio_file_path = sys.argv[1]
            window_size = int(sys.argv[2])
            shift_size = int(sys.argv[3])
            for index_proc in range(1, size):
                comm.send(window_size, dest=index_proc, tag=1)
                comm.send(shift_size, dest=index_proc, tag=2)
        except Exception as ex:
            print(f"Ошибка: {ex}")
            comm.Abort()
            sys.exit(1)
        if not os.path.isfile(audio_file_path):
            print(f"File: {audio_file_path} not exist.")
            comm.Abort()
            sys.exit(1)
        if not audio_file_path.endswith(".wav"):
            print(f"The file on the path: {audio_file_path} is not .wav file")
            comm.Abort()
            sys.exit(1)

        audio_data, sample_rate = sf.read(audio_file_path)

        if len(audio_data) < 180 * sample_rate:
            print("Audio duration is less the 3 minutes")
            comm.Abort()
            sys.exit(1)

        # разделение данных на процессы
        data_per_process = len(audio_data) // size
    else:
        audio_data = None
        data_per_process = None
        window_size = comm.recv(source=0, tag=1)
        shift_size = comm.recv(source=0, tag=2)

    audio_data = comm.bcast(audio_data, root=0)
    data_per_process = comm.bcast(data_per_process, root=0)

    start_time = time.time()

    start_index = rank * data_per_process
    end_index = start_index + data_per_process
    energy_results = list()
    zcr_results = list()

    while start_index + window_size < end_index:
        frame = audio_data[start_index:start_index + window_size]
        energy_results.append(calculate_energy(frame))
        zcr_results.append(my_zero_cross_rate(frame))
        start_index += shift_size

    gathered_energy = comm.gather(energy_results, root=0)
    gathered_zcr = comm.gather(zcr_results, root=0)

    end_time = time.time()

    if rank == 0:
        all_energy = [item for sublist in gathered_energy for item in sublist]
        all_zcr = [item for sublist in gathered_zcr for item in sublist]

        print(f"Energy =  {sum(all_energy)}")
        print(f"ZCR = {sum(all_zcr)}")

        print(f"Time execution = {(end_time - start_time):.6f} seconds")


if __name__ == '__main__':  # mpiexec -n 4 python IndividualTask7v3.py "E:\Магистратура\2 курс\Параллельные методы и алгоритмы\Лаба 2\Lab2\Task7\sample.wav" 1024 512
    main()
