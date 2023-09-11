from abc import ABC, abstractmethod
import numpy as np
import re


class Vectorizer(ABC):
    TOP_WORD_NUM = 1500
    EXTRA_FEATURES_NUM = 15

    NEW_LINE_TO_WORD_RATIO_IDX = TOP_WORD_NUM + 1
    QUESTION_MARKS_VALUES_IDX = NEW_LINE_TO_WORD_RATIO_IDX + 1
    EXCLAMATION_MARKS_VALUES_IDX = QUESTION_MARKS_VALUES_IDX + 1
    DOT_MARKS_VALUES_IDX = EXCLAMATION_MARKS_VALUES_IDX + 1
    COLON_MARKS_VALUES_IDX = DOT_MARKS_VALUES_IDX + 1
    SLASH_MARKS_VALUES_IDX = COLON_MARKS_VALUES_IDX + 1
    DASH_MARKS_VALUES_IDX = SLASH_MARKS_VALUES_IDX + 1
    COMMA_MARKS_VALUES_IDX = DASH_MARKS_VALUES_IDX + 1
    PERCENT_MARKS_VALUES_IDX = COMMA_MARKS_VALUES_IDX + 1
    DIGITS_TO_WORDS_RATIO_IDX = PERCENT_MARKS_VALUES_IDX + 1

    FROM_NAME_TO_LABELS = {}

    def example_to_vector(self, txt, top_instruc_dict, top_ingred_dict):
        pass

    def vectorize(self, stemmed_table, top_words, index_of_mark):
        lst_of_top = list(top_words.keys())

        vectorized_table = stemmed_table
        training_set_size = len(vectorized_table)
        training_examples_matrix = np.zeros((training_set_size, self.TOP_WORD_NUM + self.EXTRA_FEATURES_NUM))
        labels = np.zeros((training_set_size, 1))

        for i in range(1, training_set_size):
            row = vectorized_table[i]
            if len(row) == 3:
                txt = row[0]
                numed_txt = []
                for word in txt:
                    if word in lst_of_top:
                        numed_txt.append(lst_of_top.index(word))
                labels[i] = stemmed_table[i][index_of_mark]
                training_examples_matrix[i][numed_txt] = 1

        return training_examples_matrix, labels

    @staticmethod
    def calculate_amount_of_words(table):
        for row in table:
            row.append(len(row[0].split(' ')))

    def enrich_tables_vector(self, table, vectorized_ingred, vectorized_instr):
        Vectorizer.calculate_amount_of_words(table)
        self.enrich_vectors(table, vectorized_ingred)
        self.enrich_vectors(table, vectorized_instr)

    def enrich_vectors(self, table, vectorized):
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.NEW_LINE_TO_WORD_RATIO_IDX, '\n')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.EXCLAMATION_MARKS_VALUES_IDX, '!')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.QUESTION_MARKS_VALUES_IDX, '?')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.DOT_MARKS_VALUES_IDX, '.')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.COLON_MARKS_VALUES_IDX, ':')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.SLASH_MARKS_VALUES_IDX, '/')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.DASH_MARKS_VALUES_IDX, '-')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.COMMA_MARKS_VALUES_IDX, ',')
        Vectorizer.enrich_count_char_for_index(vectorized, table, self.PERCENT_MARKS_VALUES_IDX, '%')
        self.enrich_ratio_word_to_numbers(vectorized, table)

    @staticmethod
    def enrich_count_char_for_index(vectorized_instr, table, index, char):
        for i in range(len(table)):
            row = table[i]
            vectorized_instr[i][index] = (row[0].count(char) / int(row[3]))

    def enrich_ratio_word_to_numbers(self, vectorized_instr, table):
        for i in range(len(table)):
            row = table[i]
            amount_of_words = int(row[3])
            numbers = re.findall(r'\d+', row[0])
            vectorized_instr[i][self.DIGITS_TO_WORDS_RATIO_IDX] = Vectorizer.count_amount_of_n_digits(numbers,
                                                                                                1) / amount_of_words
            vectorized_instr[i][self.DIGITS_TO_WORDS_RATIO_IDX + 1] = Vectorizer.count_amount_of_n_digits(numbers,
                                                                                                    2) / amount_of_words
            vectorized_instr[i][self.DIGITS_TO_WORDS_RATIO_IDX + 2] = Vectorizer.count_amount_of_n_digits(numbers,
                                                                                                    3) / amount_of_words
            vectorized_instr[i][self.DIGITS_TO_WORDS_RATIO_IDX + 3] = Vectorizer.count_amount_of_n_digits(numbers,
                                                                                                    4) / amount_of_words
            vectorized_instr[i][self.DIGITS_TO_WORDS_RATIO_IDX + 4] = Vectorizer.count_amount_of_n_digits(numbers,
                                                                                                    5) / amount_of_words

    @staticmethod
    def count_amount_of_n_digits(numbers, digit_count):
        return len(list((filter((lambda n: len(n) == digit_count), numbers))))

