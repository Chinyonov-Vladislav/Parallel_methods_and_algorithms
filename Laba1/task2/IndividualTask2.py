import os
from queue import Queue
import requests
from bs4 import BeautifulSoup
import re
import threading
import random

path_folder_to_download_images = "images"
queue = Queue()
exit_event = threading.Event()


def producer(url_list: list, identifier):
    print(f"Производитель №{identifier} работает")
    for url in url_list:
        try:
            print(f'Start downloading: {url}')
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.content
            print(f"Finish downloading: {url}")
            for tag_a in BeautifulSoup(html_content, "html.parser").find_all('a'):
                href = tag_a.get("href")
                pattern = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|ico)$"
                if href is not None and href is not "" and re.search(pattern, href):
                    queue.put(href)
        except requests.exceptions.HTTPError as e:
            print(f"При загрузке файла по ссылке {url} произошла ошибка: {e}")
    print(f"Производитель №{identifier} закончил работу")


def consumer(identifier):
    while True:
        print(f"Потребитель №{identifier} работает")
        if exit_event.is_set() and queue.empty():
            print(f"Потребитель №{identifier} уничтожен")
            break
        if not queue.empty():
            url = queue.get()
            try:
                response = requests.get(url)
                response.raise_for_status()
                file_name = os.path.basename(url).strip()
                full_path_to_file = os.path.join(path_folder_to_download_images, file_name)
                with open(full_path_to_file, 'wb') as file:
                    file.write(response.content)
                    print(f"Изображение по ссылке {url} сохранено. Путь: {full_path_to_file}")
            except requests.exceptions.HTTPError as e:
                print(f"При загрузке файла по ссылке {url} произошла ошибка: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")


def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]
        return lines


def main():
    url_filename = "urls.txt"
    if os.path.isfile(url_filename):
        url_list = read_file(url_filename)
        if len(url_list) >= 10:
            if not os.path.exists(path_folder_to_download_images):
                os.makedirs(path_folder_to_download_images)

            N = random.randint(1, len(url_list))  # количество производителей
            M = random.randint(1, len(url_list))  # количество потребителей
            print(f"Количество потоков - производителей = {N}")
            print(f"Количество потоков - потребителей = {M}")
            list_producers = list()
            list_consumers = list()
            part_size = len(url_list) // N
            remain = len(url_list) % N  # Любые остаточные элементы
            start = 0
            for index in range(M):
                consumerThread = threading.Thread(target=consumer, name=f"consumer-{index + 1}", args=(index + 1,))
                list_consumers.append(consumerThread)
                consumerThread.start()
            for index in range(N):
                end = start + part_size + (1 if index < remain else 0)
                current_part = url_list[start:end]
                start = end
                producerThread = threading.Thread(target=producer, name=f"producer-{index + 1}",
                                                  args=(current_part, index + 1,))
                list_producers.append(producerThread)
                producerThread.start()
            for item_producer in list_producers:
                item_producer.join()
            exit_event.set()
            for item_consumer in list_consumers:
                item_consumer.join()
            print("Программа завершилась!")
        else:
            print(f"Количество ссылок в файле {url_filename} должно быть не менее 10 !")
    else:
        print(f"Файл с ссылками {url_filename} отсутствует в рабочей директории!")


if __name__ == '__main__':
    main()
