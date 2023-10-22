import threading
import zipfile
import requests
import os
from utils.ThreadWithReturnValue import ThreadWithReturnValue
from bs4 import BeautifulSoup
import re

print_lock = threading.Lock()


def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]
        return lines


def download_content_by_url(url):
    try:
        with print_lock:
            print(f"Start downloading: {url}")
        response = requests.get(url)
        with print_lock:
            print(f"Download complete: {url}")
        return response.content
    except requests.exceptions:
        with print_lock:
            print(f"Ошибка при скачивании контента с url: {url}")
        return None


def parsingContent(list_content):
    href_to_images = list()
    for content in list_content:
        if content is not None:
            soup = BeautifulSoup(str(content), "html.parser")
            all_a_tags = soup.find_all('a')
            for a_tag in all_a_tags:
                href = a_tag.get("href")
                pattern = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|ico)$"
                if href is not None and href is not "" and re.search(pattern, href):
                    href_to_images.append(href)
    if len(href_to_images) > 0:
        directory_for_saving_images = "images"
        if not os.path.isdir(directory_for_saving_images):
            os.makedirs(directory_for_saving_images, exist_ok=True)
        with print_lock:
            print("Downloading images...")
        threads_downloading_images = list()
        for href in href_to_images:
            thread = ThreadWithReturnValue(target=download_image, args=(href, directory_for_saving_images))
            threads_downloading_images.append(thread)
            thread.start()
        paths_to_downloaded_images = list()
        for thread in threads_downloading_images:
            paths_to_downloaded_images.append(thread.join())
        with print_lock:
            print("Done")
        zipImages("images.zip", paths_to_downloaded_images)
    else:
        with print_lock:
            print("Гиперссылки с адресами изображений не были найдены!")


def zipImages(name_archive_for_image, paths_to_downloading_images):
    print("Adding images to archive...")
    with zipfile.ZipFile(name_archive_for_image, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in paths_to_downloading_images:
            archive.write(file, os.path.basename(file))
    print("Done")

def download_image(href_image,folder):
    try:
        response = requests.get(href_image)
        file_name = os.path.basename(href_image).strip()
        full_path_to_file = f"{folder}/{file_name}"
        with open(full_path_to_file, 'wb') as file:
            file.write(response.content)
        return full_path_to_file
    except Exception:
        pass

def main():
    filename_with_urls = "urls.txt"
    if not os.path.isfile(filename_with_urls):
        print(f"Файл с набором URL - адресов {filename_with_urls} отсутствует в рабочей директории {os.getcwd()}")
        exit(-1)
    urls = read_file(filename_with_urls)
    if len(urls) < 10:
        print(f"В файле {filename_with_urls} должно быть не менее 10 ссылок!")
        return
    threads_downloading_content_by_urls = list()
    for url in urls:
        thread = ThreadWithReturnValue(target=download_content_by_url, args=(url,))
        threads_downloading_content_by_urls.append(thread)
        thread.start()
    results_downloading_content_from_urls = list()
    for thread in threads_downloading_content_by_urls:
        results_downloading_content_from_urls.append(thread.join())
    thread_parsing_content = threading.Thread(target=parsingContent, args=(results_downloading_content_from_urls,))
    thread_parsing_content.start()
    thread_parsing_content.join()
    print("Program end")

if __name__ == '__main__':
    main()
