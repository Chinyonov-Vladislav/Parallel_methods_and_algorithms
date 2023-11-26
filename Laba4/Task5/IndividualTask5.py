from mrjob.job import MRJob
import re

from mrjob.step import MRStep


class MRWordLengthCount(MRJob):
    def mapper(self, _, line):
        words = re.findall(r'\b\w+\b', line.lower())
        for word in words:
            yield len(word), word

    def reduce_count_word_by_length(self, len_word, words):
        my_dict = dict()
        for word in words:
            if word in my_dict:
                my_dict[word] += 1
            else:
                my_dict[word] = 1
        for word, total_count in my_dict.items():
            yield len_word, (word, total_count)

    def reducer_show_top_words_by_length(self, len_word, word_counts):
        N = int(self.options.N)
        sorted_words = sorted(word_counts, key=lambda item: item[1], reverse=True)
        yield N, f"{len_word} - letter words"
        if N > len(sorted_words):
            for word, count in sorted_words:
                yield word, count
        else:
            for word, count in sorted_words[:N]:
                yield word, count


    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reduce_count_word_by_length),
            MRStep(reducer=self.reducer_show_top_words_by_length)
        ]

    def configure_args(self):
        super(MRWordLengthCount, self).configure_args()
        self.add_passthru_arg('--N', default=10, type=int, help='Count')


if __name__ == '__main__':
    MRWordLengthCount.run() #python "IndividualTask5v2 (+).py" input.txt --N 1
