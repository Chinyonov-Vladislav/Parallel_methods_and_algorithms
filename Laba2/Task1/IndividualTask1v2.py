from mpi4py import MPI
import requests
import os
import re
from bs4 import BeautifulSoup
import zipfile
import time
import sys


name_folder_for_images = "images"
zip_name = "images.zip"

def read_file(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def download_by_url(url):
    try:
        print(f"Start downloading: {url}")
        response = requests.get(url)
        print(f"Downloading complete: {url}")
        return response.content
    except requests.exceptions:
        print(f"Error downloading from a link: {url}")


def parsing_html_content(all_htmls_content):
    href_to_images = list()
    for content in all_htmls_content:
        soup = BeautifulSoup(str(content), "html.parser")
        all_a_tags = soup.find_all('a')
        for a_tag in all_a_tags:
            href = a_tag.get("href")
            pattern = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|ico)$"
            if href is not None and href is not "" and re.search(pattern, href):
                href_to_images.append(href)
    return href_to_images


def download_image(url_image):
    try:
        if url_image is not None:
            response = requests.get(url_image)
            file_name = os.path.basename(url_image).strip()
            full_path_to_file = f"{name_folder_for_images}/{file_name}"
            with open(full_path_to_file, 'wb') as file:
                file.write(response.content)
            return full_path_to_file
        return None
    except requests.exceptions.HTTPError:
        print(f"Error downloading image by url: {url_image} ")
        return None


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    start_time = time.time()
    if rank == 0:
        filename_with_urls = "urls.txt"
        if not os.path.isfile(filename_with_urls):
            print(f"Error: file {filename_with_urls} not found in working directory {os.getcwd()}")
            comm.Abort()
            sys.exit(1)
        urls = read_file(filename_with_urls)
        if len(urls) == 0:
            print(f"Error: file {filename_with_urls} not contains urls")
            comm.Abort()
            sys.exit(1)
        if len(urls) >= size:  # распределить ссылки на все процессы. Каждому процессу достанется как минимум 1 ссылка
            chunk_size = len(urls) // size
            remains = len(urls) % size
            count_remain = 0
            for index_proc in range(1, size):
                start_index = index_proc * chunk_size
                end_index = (index_proc + 1) * chunk_size
                chunk_array = urls[start_index:end_index]
                if 0 < remains != count_remain:
                    chunk_array.append(urls[index_proc * -1])
                    count_remain += 1
                comm.send(chunk_array, dest=index_proc, tag=1)
        else:  # распределить ссылки на все процессы. Каждому процессу достанется как минимум 1 ссылка
            index_url = 1
            for index_proc in range(1, size):
                if index_url < len(urls):
                    comm.send(urls[index_url:index_url + 1], dest=index_proc, tag=1)
                    index_url += 1
                else:
                    comm.send(list(), dest=index_proc, tag=1)
    else:
        urls = []
    comm.Barrier()
    if rank == 0:
        if len(urls) >= size:
            chunk_size = len(urls) // size
            local_urls = urls[0: chunk_size]
        else:
            local_urls = urls[0:1]
    else:
        local_urls = comm.recv(source=0, tag=1)
    print(f"Rank = {rank}, urls = {local_urls}")
    downloaded_data_list_current_proccess = list()
    for url in local_urls:
        data = download_by_url(url)
        downloaded_data_list_current_proccess.append(data)
    downloaded_data_by_all_urls = comm.gather(downloaded_data_list_current_proccess, root=0)
    if rank == 0:  # только 0 процесс совершает парсинг
        href_to_images = parsing_html_content(downloaded_data_by_all_urls)
        if len(href_to_images) == 0:
            comm.Abort()
        if not os.path.isdir(name_folder_for_images):
            os.makedirs(name_folder_for_images, exist_ok=True)
        if len(href_to_images) >= size:
            chunk_size = len(href_to_images) // size
            remains = len(href_to_images) % size
            count_remain = 0
            for index_proc in range(1, size):
                start_index = index_proc * chunk_size
                end_index = (index_proc + 1) * chunk_size
                chunk_array_hrefs = href_to_images[start_index:end_index]
                if 0 < remains != count_remain:
                    chunk_array_hrefs.append(href_to_images[index_proc * -1])
                    count_remain += 1
                comm.send(chunk_array_hrefs, dest=index_proc, tag=1)
        else:
            index_href = 1
            for index_proc in range(1, size):
                if index_href < len(href_to_images):
                    comm.send(href_to_images[index_href:index_href + 1], dest=index_proc, tag=1)
                    index_href += 1
                else:
                    comm.send(list(), dest=index_proc, tag=1)
    else:
        href_to_images = list()
    comm.Barrier()
    if rank == 0:
        if len(href_to_images) >= size:
            chunk_size = len(href_to_images) // size
            local_href_images = href_to_images[0: chunk_size]
        else:
            local_href_images = href_to_images[0:1]
    else:
        local_href_images = comm.recv(source=0, tag=1)
    print(f"Rank = {rank}, local_href_images = {local_href_images}")
    paths_to_downloaded_images = list()
    print(f"Downloading images on rank = {rank}")
    for href_image in local_href_images:
        path = download_image(href_image)
        paths_to_downloaded_images.append(path)
    print(f"Done downloading images on rank = {rank}")
    paths_to_all_downloaded_images = comm.gather(paths_to_downloaded_images, root=0)
    if rank == 0:
        print("Adding images to archive...")
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as archive:
            for array in paths_to_all_downloaded_images:
                for item in array:
                    if item is not None:
                        archive.write(item, os.path.basename(item))
        end_time = time.time()
        print("Done")
        print(f"Count MPI Process = {size}. Time execution = {(end_time - start_time):.6f} seconds")
        print(f"Process rank = {rank} end!")


if __name__ == '__main__':
    main()  # mpiexec -n 4 python IndividualTask1v2.py
