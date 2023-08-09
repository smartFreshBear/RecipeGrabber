import copy
import time
import logging
import pickle
import requests
from json import JSONDecodeError
import re
from nltk.stem import PorterStemmer
from abc import ABC, abstractmethod

HEBREW_NLP_END_POINT = 'https://hebrew-nlp.co.il/service/morphology/normalize'
ps = PorterStemmer()


class Stemmer(ABC):

    @abstractmethod
    def stemmify(self, table):
        pass

    @abstractmethod
    def prepare_stem_mapping(self, text_to_stem_list):
        pass


class StemmerHebrew(Stemmer):
    def __init__(self):
        pass

    def prepare_stem_mapping(self, text_to_stem_list):
        cleaned_text = [self.clean_text(text) for text in text_to_stem_list]
        words = [word for words_of_row in cleaned_text for word in words_of_row]
        attention_seekers = list(filter(lambda word: word not in from_word_to_stem_cache, words))

        try:
            if attention_seekers:

                request = {
                    'token': 'vhZZt9hGGX20aUW',
                    'type': 'SEARCH',
                    'text': ' ## '.join(attention_seekers)
                }

                response = requests.post(HEBREW_NLP_END_POINT, json=request)
                json_response = response.json()
                flatten_lst_of_words = [item for sublist in json_response for item in sublist]
                answer_from_api = ''.join(flatten_lst_of_words).split('##')
                for i in range(len(attention_seekers)):
                    from_word_to_stem_cache[attention_seekers[i]] = answer_from_api[i]
                return answer_from_api

        except JSONDecodeError as jsonExc:
            logging.info("had a problem parsing this row {} \n more info: {}".format(row, jsonExc))

    def stemmify(self, table):
        stemmed_table = copy.deepcopy(table)
        only_text_respective = [row[0] for row in stemmed_table]
        self.prepare_stem_mapping(only_text_respective)

        for row_i in range(len(stemmed_table)):
            stemmed_table[row_i][0] = self.convert_all_text_to_stem_only(only_text_respective[row_i])
        return stemmed_table

    def load_from_word_to_stem(self):
        try:
            with open('data.pkl', 'rb') as handle:
                global from_word_to_stem_cache
                from_word_to_stem_cache = pickle.load(handle)

        except Exception:
            logging.error('load_cache error')
            from_word_to_stem_cache = {}
        return from_word_to_stem_cache

    def convert_all_text_to_stem_only(self, text):
        return [''.join(from_word_to_stem_cache.get(word, '')) for word in text.split()]

    def clean_text(self, text):
        purified_text = re.sub(r'[^\w\s]', '', text)
        return purified_text.split()

    def periodically_save_cache(self):
        cycle_time_to_save_cache = 60 * 60
        while True:
            # Wait for new data to accumulate
            time.sleep(cycle_time_to_save_cache)

            # Save to disk
            with open('data.pkl', 'wb') as handle:
                pickle.dump(from_word_to_stem_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)


class StemmerEnglish(Stemmer):
    def __init__(self):
        pass

    def prepare_stem_mapping(self, text_to_stem_list):
        cleaned_text = [self.clean_text(text) for text in text_to_stem_list]
        words = [word for words_of_row in cleaned_text for word in words_of_row]
        for i in range(len(words)):
            words[i] = ps.stem(words[i])
        return words

    def stemmify(self, table):
        stemmed_table = copy.deepcopy(table)
        only_text_respective = [row[0] for row in stemmed_table]
        self.prepare_stem_mapping(only_text_respective)

        for row_i in range(len(stemmed_table)):
            stemmed_table[row_i][0] = self.convert_all_text_to_stem_only(only_text_respective[row_i])
        return stemmed_table

    def convert_all_text_to_stem_only(self, text):
        text = text.split()
        text = self.prepare_stem_mapping(text)
        return text

    def clean_text(self, text):
        purified_text = re.sub(r'[^\w\s]', '', text)
        return purified_text.split()

