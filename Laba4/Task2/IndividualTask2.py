from mrjob.job import MRJob
import re


class MRWordCount(MRJob):

    def mapper(self, _, line):
        # Разделяем строку на слова
        words = re.findall(r"\b\w+\b", line.lower())  # возможно переделать регулярное выражение

        # Отправляем пары (слово, 1) для каждого слова
        for word in words:
            yield word, 1

    def reducer(self, word, counts):
        # Считаем общее количество для каждого слова
        yield word, sum(counts)


if __name__ == '__main__':
    MRWordCount.run()
    #python IndividualTask2.py my.txt
