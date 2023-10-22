import os
import threading
from concurrent.futures import ThreadPoolExecutor
import shutil
import sys


global_count_tasks = 0
global_variable_lock = threading.Lock()


def copyFile(source_path, destination_path):
    global global_count_tasks
    shutil.copy2(source_path, destination_path)
    with global_variable_lock:
        global_count_tasks -= 1


def copyDirectory(path_directory):
    global global_count_tasks
    os.makedirs(path_directory, exist_ok=True)
    with global_variable_lock:
        global_count_tasks -= 1


def travel_directory(source_directory, destination_directory, executor):
    global global_count_tasks
    if os.path.isdir(source_directory):
        folder_name_from_src = os.path.basename(source_directory)  # название папки из source directory
        current_dest_folder = os.path.join(destination_directory, folder_name_from_src)
        if not os.path.exists(current_dest_folder):
            executor.submit(copyDirectory, current_dest_folder)
            with global_variable_lock:
                global_count_tasks += 1
        for item_folder in os.listdir(source_directory):
            full_path_item = os.path.join(source_directory, item_folder)
            if os.path.isdir(full_path_item):
                executor.submit(travel_directory, full_path_item, current_dest_folder, executor)
                with global_variable_lock:
                    global_count_tasks += 1
            elif os.path.isfile(full_path_item):
                dest_file_path = os.path.join(current_dest_folder, item_folder)
                executor.submit(copyFile, full_path_item, dest_file_path)
                with global_variable_lock:
                    global_count_tasks += 1
    with global_variable_lock:
        global_count_tasks -= 1


def main():
    N = None
    if len(sys.argv) != 3:
        print("Недостаточно параметров командной строки.")
        exit(-1)
    source_directory = sys.argv[1]
    destination_directory = os.getcwd()
    if not os.path.isdir(source_directory):
        print(f"Папки по пути: {source_directory} не существует!")
        exit(-1)
    if source_directory == destination_directory:
        print("Путь к исходной директории и директории назначения одинаков.")
        exit(-1)
    try:
        N = int(sys.argv[2])
        if N <= 0:
            raise ValueError("введено неверное значение для переменной N - количество пулов потоков.\n N должно быть "
                             "положительным целым числом больше 0")
    except ValueError as ex:
        print(f"Ошибка: {ex}")
        exit(-1)
    global global_count_tasks
    destination_directory = os.getcwd()
    with ThreadPoolExecutor(max_workers=N) as executor:
        executor.submit(travel_directory, source_directory, destination_directory, executor)
        global_count_tasks += 1
        while global_count_tasks != 0:
            pass


if __name__ == '__main__':
    main()
