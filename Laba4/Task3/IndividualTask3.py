from mrjob.job import MRJob
import re

from mrjob.step import MRStep


class MRMostUsedWords(MRJob):

    def mapper_get_words(self, _, line):
        words = re.findall(r'\b\w+\b', line.lower())
        for word in words:
            yield word, 1

    def combiner(self, key, values):
        yield key, sum(values)

    def reducer_count_words(self, key, values):
        yield None, (key, sum(values))

    def reducer_find_top_words(self, _, values):
        N = int(self.options.N)
        top_words = sorted(values, key=lambda x: x[1], reverse=True)
        if N < len(top_words):
            for word, count in top_words[:N]:
                yield word, count
        else:
            for word, count in top_words:
                yield word, count

    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_words,
                   combiner=self.combiner,
                   reducer=self.reducer_count_words),
            MRStep(reducer=self.reducer_find_top_words)
        ]

    def configure_args(self):
        super(MRMostUsedWords, self).configure_args()
        self.add_passthru_arg('--N', default=10, type=int, help='Number of top words to find')


if __name__ == '__main__':
    MRMostUsedWords.run() #python IndividualTask3.py input.txt --N 5

