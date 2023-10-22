import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import zipfile
import re
from aiofiles import open as aio_open


def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


async def download_url(session, url):
    try:
        async with session.get(url) as response:
            print(f"Start downloading: {url}")
            content = await response.text()
            # Обработка загруженных данных, если необходимо
            print(f"Download complete: {url}")
            return content
    except Exception as ex:
        print(f"Error: {ex}")
        return None


async def parse_image_urls_and_download_images(contents):
    hrefs_images = list()
    for content in contents:
        if content is not None:
            soup = BeautifulSoup(str(content), "html.parser")
            all_a_tags = soup.find_all('a')
            for a_tag in all_a_tags:
                href = a_tag.get("href")
                pattern = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|ico)$"
                if href is not None and href is not "" and re.search(pattern, href):
                    hrefs_images.append(href)
    if len(hrefs_images) > 0:
        output_dir_images = "images"
        if not os.path.isdir(output_dir_images):
            os.makedirs(output_dir_images, exist_ok=True)
        tasks = list()
        print("Downloading images...")
        async with aiohttp.ClientSession() as session:
            for image_url in hrefs_images:
                tasks.append(downloadImage(session, image_url, output_dir_images))
            img_paths = await asyncio.gather(*tasks)
        print("Done")
        return img_paths
    else:
        print("Гиперссылки с адресами изображений не были найдены!")
        return list()


async def downloadImage(session, href_image, output_dir):
    async with session.get(href_image) as response:
        content = await response.read()
        filename = os.path.join(output_dir, os.path.basename(href_image))
        async with aio_open(filename, 'wb') as f:
            await f.write(content)
        return filename


def create_zip_archive(zip_file, paths_files):
    with zipfile.ZipFile(zip_file, 'w') as archive:
        for path in paths_files:
            archive.write(path, os.path.basename(path))


async def main():
    filename_with_urls = "urls.txt"
    if not os.path.isfile(filename_with_urls):
        print(f"Файл с набором URL - адресов {filename_with_urls} отсутствует в рабочей директории {os.getcwd()}")
        exit(-1)
    urls = read_urls_from_file(filename_with_urls)
    if len(urls) < 10:
        print(f"В файле {filename_with_urls} должно быть не менее 10 ссылок!")
        return
    tasks_download_content = list()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks_download_content.append(download_url(session, url))
        contents = await asyncio.gather(*tasks_download_content)
    paths_to_images = await parse_image_urls_and_download_images(contents)
    name_zip = "images.zip"
    if len(paths_to_images) >0:
        print("Adding images to archive...")
        create_zip_archive(name_zip, paths_to_images)
        print("Done")
    else:
        print("No images for archiving")


if __name__ == '__main__':
    asyncio.run(main())
