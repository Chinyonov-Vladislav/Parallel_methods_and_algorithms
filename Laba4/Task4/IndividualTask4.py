from mrjob.job import MRJob
import re

from mrjob.step import MRStep


class MRWordPairsCount(MRJob):
    def mapper(self, _, line):
        words = re.findall(r'\b\w+\b', line.lower())
        for index in range(len(words) - 1):
            yield (words[index], words[index + 1]), 1

    def reducer_count_pair(self, pair, counts):
        yield None, (pair, sum(counts))

    def reducer_top_pair(self, _, values):
        N = int(self.options.N)
        sorted_pairs = sorted(values, key=lambda item: item[1], reverse=True)
        if N < len(sorted_pairs):
            for key, value in sorted_pairs[:N]:
                yield key, value
        else:
            for key, value in sorted_pairs:
                yield key, value

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reducer_count_pair),
            MRStep(reducer=self.reducer_top_pair)
        ]

    def configure_args(self):
        super(MRWordPairsCount, self).configure_args()
        self.add_passthru_arg('--N', default=10, type=int, help='Count')


if __name__ == '__main__':
    MRWordPairsCount().run() #python IndividualTask4.py input.txt --N 5
