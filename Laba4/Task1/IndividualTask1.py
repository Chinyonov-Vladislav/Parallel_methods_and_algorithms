from mrjob.job import MRJob
import re
import requests
from bs4 import BeautifulSoup
import os
import zipfile
from mrjob.step import MRStep
import sys
import time


class Download(MRJob):

    def __init__(self, *args, **kwargs):
        super(Download, self).__init__(*args, **kwargs)
        if os.path.isdir(self.options.path):
            self.zip_filename = 'images.zip'
            self.path_of_zip_file = self.options.path
            self.images_dir = os.path.join(self.options.path, "images")
            os.makedirs(self.images_dir, exist_ok=True)
        else:
            sys.exit(-1)

    def mapper(self, _, link):  # скачивание данных по ссылкам
        try:
            response = requests.get(link)
            yield "html_content", str(response.content)
        except Exception as e:
            yield None, str(e)

    def reducer_parsing(self, key, html_content_str):  # парсинг гиперссылок с адресами изображений
        if key == 'html_content':
            for index, content in enumerate(html_content_str):
                try:
                    soup = BeautifulSoup(content, "html.parser")
                    all_a_tags = soup.find_all('a')
                    for a_tag in all_a_tags:
                        href = a_tag.get("href")
                        pattern = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|ico)$"
                        if href is not None and href is not "" and re.search(pattern, href):
                            yield f"image_href_{index}", href
                except Exception as e:
                    yield None, str(e)

    def reducer_download_image(self, key, hrefs_to_image):
        if str(key).startswith('image_href'):
            for href_image in hrefs_to_image:
                try:
                    response = requests.get(href_image)
                    file_name = os.path.basename(href_image).strip()
                    full_path_to_file = os.path.join(self.images_dir, file_name)
                    with open(full_path_to_file, 'wb') as file:
                        file.write(response.content)
                    yield 'path_image_for_archive', full_path_to_file
                except Exception as e:
                    yield None, str(e)

    def reducer_zip_images(self, key, values):
        if key == 'path_image_for_archive':
            with zipfile.ZipFile(os.path.join(self.path_of_zip_file, self.zip_filename), 'w',
                                 zipfile.ZIP_DEFLATED) as archive:
                for file in values:
                    if os.path.exists(file):
                        archive.write(file, os.path.basename(file))
            yield None, None

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reducer_parsing),
            MRStep(reducer=self.reducer_download_image),
            MRStep(reducer=self.reducer_zip_images)
        ]

    def configure_args(self):
        super(Download, self).configure_args()
        self.add_passthru_arg('--path', default=os.getcwd(), type=str, help='Folder to save images')


if __name__ == '__main__':
    Download().run()
    # python IndividualTask1.py urls.txt --path "E:\Магистратура\2 курс\Параллельные методы и алгоритмы\Лаба 4\lab4\Task1"
