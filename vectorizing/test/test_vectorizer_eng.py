import logging
from unittest import TestCase

import stemming.stemming
from vectorizing import vectorizer_eng

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vectorizingEngTest')
vectorizer = vectorizer_eng.VectorizerEng()
stemmer_eng = stemming.stemming.StemmerEnglish()


class TestVectorizerEng(TestCase):

    def test_example_to_vector_eng1(self):
        test_top_instruc_dict = {'great': 1, 'son': 2, 'that': 3, 'fire': 4, 'bro': 5}
        test_top_ingred_dict = {'dumb': 1, 'boys': 2, 'bitch': 3, 'five': 4, 'test': 5}
        text = "i have been here for so long i think im going crazy bitch son bro"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text, test_top_instruc_dict, test_top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [1,4] and vectorized_ingred == [2]

    def test_example_to_vector_eng2(self):
        test_top_instruc_dict = {'if': 1, 'you': 2, 'must': 3, 'bro': 4, 'damn': 5}
        test_top_ingred_dict = {'dumb': 1, 'bitch': 2, 'boys': 3, 'five': 4, 'test': 5}
        text = "bro if you must then lets go"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        test_top_instruc_dict,
                                                                                                        test_top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0, 1, 2, 3] and vectorized_ingred == []

    def test_example_to_vector_eng3(self):
        test_top_instruc_dict = {'think': 1, 'work': 2, 'zero': 3, 'bro': 4, 'damn': 5}
        test_top_ingred_dict = {'dumb': 1, 'bitch': 2, 'boys': 3, 'five': 4, 'test': 5}
        text = "i think its working the second vector should be empty and the first one should be "
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        test_top_instruc_dict,
                                                                                                        test_top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0, 1] and vectorized_ingred == []


def vector_tester(vectorized_text):  # used to shorten the vector for testing
    vector_index = []
    for i in range(len(vectorized_text[1])):
        if vectorized_text[1][i] == 1:
            vector_index.append(i)
    return vector_index
